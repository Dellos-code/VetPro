"""
Heuristic Scheduler Engine — Multi-Constraint Appointment Optimizer
====================================================================

Mathematical Model
------------------
This is a **Constraint-Satisfaction / Optimization Problem (CSP)** with the
following formal structure:

**Decision variables**
    For each appointment *i*, assign a tuple (v_i, r_i, t_i) where
    v_i ∈ V (veterinarian), r_i ∈ R (room), t_i ∈ T (start-time slot).

**Hard constraints**
    C1  No vet overlap:    ∀ i≠j, if v_i = v_j then [t_i, t_i+d_i) ∩ [t_j, t_j+d_j) = ∅
    C2  No room overlap:   ∀ i≠j, if r_i = r_j then [t_i, t_i+d_i) ∩ [t_j, t_j+d_j) = ∅
    C3  Working-hours:     t_i ≥ day_start  AND  t_i + d_i ≤ day_end
    C4  Vet competence:    v_i ∈ qualified(a_i.type)

**Soft objectives** (weighted sum → minimise)
    O1  Minimise total "dead time" per vet  (idle gaps between appointments)
    O2  Maximise room utilisation  ≡  Minimise unused room-minutes
    O3  Respect appointment priorities  (emergencies scheduled first)
    O4  Minimise total makespan  (earliest finish for all appointments)

**Priority model**
    Each appointment carries an integer priority p_i ∈ {1..5}:
        5 = EMERGENCY (preempts routine)
        4 = URGENT
        3 = FOLLOW_UP
        2 = ROUTINE_MEDICAL
        1 = ROUTINE_CHECKUP

Algorithm
---------
1. **Sort** appointments by descending priority, then ascending duration (SJF
   within the same priority level).
2. **Greedy construction**: For each appointment, evaluate every feasible
   (vet, room, time-slot) triple.  Score each triple with the weighted
   objective function and pick the best.
3. **Emergency preemption**: If an EMERGENCY arrives and no feasible slot
   exists, the engine identifies the lowest-priority non-emergency appointment
   that can be displaced.  The displaced appointment is re-queued and
   re-scheduled after the emergency is placed.
4. **Local search refinement** (optional, bounded iterations): Swap-based
   neighbourhood search tries pairwise appointment swaps to reduce the
   objective.

Complexity
----------
Greedy pass: O(N · M · K · S) where S = number of time slots.
Local search: O(I · N²) where I = iteration cap.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Domain value objects
# ---------------------------------------------------------------------------

class Priority(IntEnum):
    """Appointment clinical priority (higher value = more urgent)."""
    ROUTINE_CHECKUP = 1
    ROUTINE_MEDICAL = 2
    FOLLOW_UP = 3
    URGENT = 4
    EMERGENCY = 5


@dataclass
class Veterinarian:
    """A veterinarian resource with availability window and competencies."""
    vet_id: str
    name: str
    available_from: datetime
    available_until: datetime
    competencies: set[str] = field(default_factory=lambda: {"general"})

    def is_available(self, start: datetime, end: datetime) -> bool:
        """Check whether the vet's working window covers [start, end)."""
        return self.available_from <= start and end <= self.available_until


@dataclass
class Room:
    """A clinic room / surgical table."""
    room_id: str
    name: str
    capabilities: set[str] = field(default_factory=lambda: {"general"})


@dataclass
class AppointmentRequest:
    """An unscheduled appointment that the engine must place."""
    appointment_id: str
    pet_id: str
    duration_minutes: int
    priority: Priority = Priority.ROUTINE_CHECKUP
    required_type: str = "general"
    preferred_vet_id: Optional[str] = None
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None


@dataclass
class ScheduledSlot:
    """The result of scheduling: an appointment bound to vet, room, time."""
    appointment_id: str
    vet_id: str
    room_id: str
    start: datetime
    end: datetime
    priority: Priority

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)


@dataclass
class ScheduleResult:
    """Full output of the scheduling engine."""
    scheduled: list[ScheduledSlot]
    unscheduled: list[str]
    vet_utilisation: dict[str, float]
    room_utilisation: dict[str, float]
    total_dead_time_minutes: float
    objective_score: float


# ---------------------------------------------------------------------------
# Objective-function weights (tunable)
# ---------------------------------------------------------------------------

@dataclass
class ObjectiveWeights:
    """Weights for the multi-criteria objective (all ≥ 0)."""
    w_dead_time: float = 0.40
    w_room_idle: float = 0.20
    w_priority_delay: float = 0.30
    w_makespan: float = 0.10


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _time_slots(day_start: datetime, day_end: datetime,
                granularity_minutes: int) -> list[datetime]:
    """Generate candidate start times at *granularity_minutes* intervals."""
    slots: list[datetime] = []
    t = day_start
    while t < day_end:
        slots.append(t)
        t += timedelta(minutes=granularity_minutes)
    return slots


def _overlaps(s1: datetime, e1: datetime, s2: datetime, e2: datetime) -> bool:
    """Check whether two half-open intervals [s1,e1) and [s2,e2) overlap."""
    return s1 < e2 and s2 < e1


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class SchedulerEngine:
    """
    Heuristic Scheduler Engine
    ==========================

    Solves the multi-constraint appointment scheduling problem described
    in the module docstring.

    Usage
    -----
    >>> engine = SchedulerEngine(
    ...     veterinarians=[vet1, vet2],
    ...     rooms=[room_a, room_b],
    ...     day_start=datetime(2026, 3, 4, 8, 0),
    ...     day_end=datetime(2026, 3, 4, 18, 0),
    ... )
    >>> result = engine.schedule(appointments)
    >>> for slot in result.scheduled:
    ...     print(slot)

    Parameters
    ----------
    veterinarians : list[Veterinarian]
    rooms : list[Room]
    day_start, day_end : datetime
        Boundaries of the scheduling horizon.
    slot_granularity_minutes : int
        Resolution of the time grid (default 15 min).
    weights : ObjectiveWeights
        Objective-function weight vector.
    local_search_iterations : int
        Max iterations for the improvement phase (0 = skip).
    """

    def __init__(
        self,
        veterinarians: list[Veterinarian],
        rooms: list[Room],
        day_start: datetime,
        day_end: datetime,
        slot_granularity_minutes: int = 15,
        weights: Optional[ObjectiveWeights] = None,
        local_search_iterations: int = 200,
    ) -> None:
        if not veterinarians:
            raise ValueError("At least one veterinarian is required")
        if not rooms:
            raise ValueError("At least one room is required")
        if day_end <= day_start:
            raise ValueError("day_end must be after day_start")

        self._vets = {v.vet_id: v for v in veterinarians}
        self._rooms = {r.room_id: r for r in rooms}
        self._day_start = day_start
        self._day_end = day_end
        self._granularity = slot_granularity_minutes
        self._weights = weights or ObjectiveWeights()
        self._ls_iters = local_search_iterations

        self._time_slots = _time_slots(day_start, day_end,
                                       slot_granularity_minutes)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def schedule(
        self,
        appointments: list[AppointmentRequest],
        existing: Optional[list[ScheduledSlot]] = None,
    ) -> ScheduleResult:
        """
        Schedule a batch of appointment requests.

        Parameters
        ----------
        appointments : list[AppointmentRequest]
            Requests to schedule.
        existing : list[ScheduledSlot], optional
            Already-committed slots (immovable).  The engine will avoid
            conflicts with these but will not attempt to reschedule them.

        Returns
        -------
        ScheduleResult
            Contains the scheduled slots, any unschedulable IDs,
            utilisation metrics, and the objective score.
        """
        if not appointments:
            return ScheduleResult(
                scheduled=[], unscheduled=[], vet_utilisation={},
                room_utilisation={}, total_dead_time_minutes=0.0,
                objective_score=0.0,
            )

        placed: list[ScheduledSlot] = list(existing) if existing else []
        unscheduled: list[str] = []

        # Phase 1 — Greedy construction (priority-ordered)
        sorted_appts = sorted(
            appointments,
            key=lambda a: (-a.priority, a.duration_minutes),
        )

        deferred: list[AppointmentRequest] = []

        for appt in sorted_appts:
            slot = self._find_best_slot(appt, placed)
            if slot is not None:
                placed.append(slot)
            elif appt.priority >= Priority.EMERGENCY:
                # Phase 2 — Emergency preemption
                slot = self._preempt_and_place(appt, placed, deferred)
                if slot is not None:
                    placed.append(slot)
                else:
                    unscheduled.append(appt.appointment_id)
            else:
                deferred.append(appt)

        # Re-attempt deferred appointments
        for appt in sorted(deferred,
                           key=lambda a: (-a.priority, a.duration_minutes)):
            slot = self._find_best_slot(appt, placed)
            if slot is not None:
                placed.append(slot)
            else:
                unscheduled.append(appt.appointment_id)

        # Phase 3 — Local search refinement
        if self._ls_iters > 0:
            placed = self._local_search(placed, existing or [])

        # Compute metrics
        return self._build_result(placed, unscheduled)

    def schedule_emergency(
        self,
        emergency: AppointmentRequest,
        current_schedule: list[ScheduledSlot],
    ) -> ScheduleResult:
        """
        Insert a single emergency into an existing schedule.

        This is a convenience wrapper that forces the priority to EMERGENCY
        and delegates to :meth:`schedule` with preemption enabled.
        """
        emergency.priority = Priority.EMERGENCY
        # Separate immovable (already started) from movable
        now = datetime.now()
        immovable = [s for s in current_schedule if s.start <= now]
        movable = [s for s in current_schedule if s.start > now]

        # Convert movable slots back to requests so they can be rearranged
        movable_requests = [
            AppointmentRequest(
                appointment_id=s.appointment_id,
                pet_id="",
                duration_minutes=s.duration_minutes,
                priority=s.priority,
            )
            for s in movable
        ]

        all_requests = [emergency] + movable_requests
        return self.schedule(all_requests, existing=immovable)

    # ------------------------------------------------------------------
    # Greedy slot finder
    # ------------------------------------------------------------------

    def _find_best_slot(
        self,
        appt: AppointmentRequest,
        placed: list[ScheduledSlot],
    ) -> Optional[ScheduledSlot]:
        """
        Evaluate all feasible (vet, room, time) triples and return the
        one with the lowest marginal cost, or None if infeasible.

        Scoring function per triple (v, r, t):
            score = w1·gap_before(v,t) + w2·room_idle(r,t)
                  + w3·priority_delay(t) + w4·makespan(t+d)

        Where gap_before counts idle minutes between the previous
        appointment on vet v and start time t.
        """
        best_slot: Optional[ScheduledSlot] = None
        best_score = math.inf
        duration = timedelta(minutes=appt.duration_minutes)

        for vet_id, vet in self._vets.items():
            # Vet competence check (C4)
            if appt.required_type not in vet.competencies:
                continue
            # Vet preference bonus
            pref_bonus = -5.0 if appt.preferred_vet_id == vet_id else 0.0

            for room_id, room in self._rooms.items():
                # Room capability check
                if appt.required_type not in room.capabilities:
                    continue

                for t in self._time_slots:
                    start = t
                    end = start + duration

                    # Hard constraints ----------------------------------
                    # C3: working hours
                    if not vet.is_available(start, end):
                        continue
                    if end > self._day_end:
                        continue

                    # Appointment-specific time window
                    if appt.earliest_start and start < appt.earliest_start:
                        continue
                    if appt.latest_end and end > appt.latest_end:
                        continue

                    # C1: vet overlap
                    if any(_overlaps(start, end, s.start, s.end)
                           for s in placed if s.vet_id == vet_id):
                        continue

                    # C2: room overlap
                    if any(_overlaps(start, end, s.start, s.end)
                           for s in placed if s.room_id == room_id):
                        continue

                    # Scoring -------------------------------------------
                    gap = self._gap_before_vet(vet_id, start, placed)
                    r_idle = self._room_idle(room_id, start, placed)
                    pri_delay = (start - self._day_start).total_seconds() / 60
                    makespan = (end - self._day_start).total_seconds() / 60

                    score = (
                        self._weights.w_dead_time * gap
                        + self._weights.w_room_idle * r_idle
                        + self._weights.w_priority_delay * pri_delay
                              / max(appt.priority, 1)
                        + self._weights.w_makespan * makespan
                        + pref_bonus
                    )

                    if score < best_score:
                        best_score = score
                        best_slot = ScheduledSlot(
                            appointment_id=appt.appointment_id,
                            vet_id=vet_id,
                            room_id=room_id,
                            start=start,
                            end=end,
                            priority=appt.priority,
                        )

        return best_slot

    # ------------------------------------------------------------------
    # Emergency preemption
    # ------------------------------------------------------------------

    def _preempt_and_place(
        self,
        emergency: AppointmentRequest,
        placed: list[ScheduledSlot],
        deferred: list[AppointmentRequest],
    ) -> Optional[ScheduledSlot]:
        """
        Displace the lowest-priority non-emergency appointment to make
        room for *emergency*.  The displaced appointment is added to
        *deferred* for later re-scheduling.
        """
        # Candidates for displacement: non-emergency, sorted by priority ASC
        candidates = sorted(
            [s for s in placed if s.priority < Priority.EMERGENCY],
            key=lambda s: (s.priority, -s.duration_minutes),
        )

        for victim in candidates:
            # Temporarily remove victim
            placed.remove(victim)
            slot = self._find_best_slot(emergency, placed)
            if slot is not None:
                deferred.append(AppointmentRequest(
                    appointment_id=victim.appointment_id,
                    pet_id="",
                    duration_minutes=victim.duration_minutes,
                    priority=victim.priority,
                ))
                return slot
            # Victim could not be displaced usefully — restore
            placed.append(victim)

        return None

    # ------------------------------------------------------------------
    # Local search improvement
    # ------------------------------------------------------------------

    def _local_search(
        self,
        placed: list[ScheduledSlot],
        immovable: list[ScheduledSlot],
    ) -> list[ScheduledSlot]:
        """
        Swap-based neighbourhood search.

        For up to *_ls_iters* iterations, try swapping the (vet, room,
        time) assignment between two movable appointments.  Accept the
        swap only if it improves the objective and preserves feasibility.
        """
        immovable_ids = {s.appointment_id for s in immovable}
        best_obj = self._objective(placed)

        for _ in range(self._ls_iters):
            improved = False
            movable = [s for s in placed
                       if s.appointment_id not in immovable_ids]
            for i in range(len(movable)):
                for j in range(i + 1, len(movable)):
                    a, b = movable[i], movable[j]
                    # Only swap if durations are compatible with each
                    # other's time boundaries
                    new_a_end = a.start + timedelta(minutes=b.duration_minutes)
                    new_b_end = b.start + timedelta(minutes=a.duration_minutes)

                    if new_a_end > self._day_end or new_b_end > self._day_end:
                        continue

                    # Swap vet+room+time
                    trial = copy.deepcopy(placed)
                    idx_a = next(k for k, s in enumerate(trial)
                                 if s.appointment_id == a.appointment_id)
                    idx_b = next(k for k, s in enumerate(trial)
                                 if s.appointment_id == b.appointment_id)

                    trial[idx_a] = ScheduledSlot(
                        a.appointment_id, b.vet_id, b.room_id,
                        b.start, b.start + timedelta(minutes=a.duration_minutes),
                        a.priority,
                    )
                    trial[idx_b] = ScheduledSlot(
                        b.appointment_id, a.vet_id, a.room_id,
                        a.start, a.start + timedelta(minutes=b.duration_minutes),
                        b.priority,
                    )

                    if not self._is_feasible(trial):
                        continue

                    obj = self._objective(trial)
                    if obj < best_obj:
                        placed = trial
                        best_obj = obj
                        improved = True
                        break
                if improved:
                    break
            if not improved:
                break

        return placed

    # ------------------------------------------------------------------
    # Feasibility check
    # ------------------------------------------------------------------

    def _is_feasible(self, slots: list[ScheduledSlot]) -> bool:
        """Verify all hard constraints hold for a candidate schedule."""
        for i, a in enumerate(slots):
            vet = self._vets.get(a.vet_id)
            if vet and not vet.is_available(a.start, a.end):
                return False
            if a.end > self._day_end or a.start < self._day_start:
                return False
            for j in range(i + 1, len(slots)):
                b = slots[j]
                if a.vet_id == b.vet_id and _overlaps(a.start, a.end,
                                                       b.start, b.end):
                    return False
                if a.room_id == b.room_id and _overlaps(a.start, a.end,
                                                         b.start, b.end):
                    return False
        return True

    # ------------------------------------------------------------------
    # Objective function & metrics
    # ------------------------------------------------------------------

    def _objective(self, slots: list[ScheduledSlot]) -> float:
        """
        Compute the scalar objective value for a complete schedule.

        Objective = w1·Σ_v(dead_time_v) + w2·Σ_r(idle_r)
                  + w3·Σ_i(start_delay_i / priority_i)
                  + w4·makespan
        """
        if not slots:
            return 0.0

        total_dead = 0.0
        total_room_idle = 0.0
        total_priority_delay = 0.0

        # Dead time per vet
        for vet_id in self._vets:
            vet_slots = sorted(
                [s for s in slots if s.vet_id == vet_id],
                key=lambda s: s.start,
            )
            for k in range(1, len(vet_slots)):
                gap = (vet_slots[k].start - vet_slots[k - 1].end
                       ).total_seconds() / 60
                total_dead += max(0.0, gap)

        # Room idle (same logic per room)
        for room_id in self._rooms:
            room_slots = sorted(
                [s for s in slots if s.room_id == room_id],
                key=lambda s: s.start,
            )
            for k in range(1, len(room_slots)):
                gap = (room_slots[k].start - room_slots[k - 1].end
                       ).total_seconds() / 60
                total_room_idle += max(0.0, gap)

        # Priority delay
        for s in slots:
            delay = (s.start - self._day_start).total_seconds() / 60
            total_priority_delay += delay / max(s.priority, 1)

        # Makespan
        makespan = max(
            (s.end - self._day_start).total_seconds() / 60 for s in slots
        )

        return (
            self._weights.w_dead_time * total_dead
            + self._weights.w_room_idle * total_room_idle
            + self._weights.w_priority_delay * total_priority_delay
            + self._weights.w_makespan * makespan
        )

    def _gap_before_vet(self, vet_id: str, start: datetime,
                        placed: list[ScheduledSlot]) -> float:
        """Minutes of idle gap on *vet_id* immediately before *start*."""
        vet_slots = [s for s in placed if s.vet_id == vet_id and s.end <= start]
        if not vet_slots:
            return (start - self._day_start).total_seconds() / 60
        last_end = max(s.end for s in vet_slots)
        return (start - last_end).total_seconds() / 60

    def _room_idle(self, room_id: str, start: datetime,
                   placed: list[ScheduledSlot]) -> float:
        """Minutes of idle gap on *room_id* immediately before *start*."""
        room_slots = [s for s in placed
                      if s.room_id == room_id and s.end <= start]
        if not room_slots:
            return (start - self._day_start).total_seconds() / 60
        last_end = max(s.end for s in room_slots)
        return (start - last_end).total_seconds() / 60

    # ------------------------------------------------------------------
    # Result builder
    # ------------------------------------------------------------------

    def _build_result(
        self,
        placed: list[ScheduledSlot],
        unscheduled: list[str],
    ) -> ScheduleResult:
        """Assemble the final ScheduleResult with utilisation metrics."""
        horizon_minutes = (
            (self._day_end - self._day_start).total_seconds() / 60
        )

        # Vet utilisation = busy minutes / horizon
        vet_util: dict[str, float] = {}
        for vet_id in self._vets:
            busy = sum(
                s.duration_minutes for s in placed if s.vet_id == vet_id
            )
            vet_util[vet_id] = round(busy / horizon_minutes, 4) if horizon_minutes else 0.0

        # Room utilisation
        room_util: dict[str, float] = {}
        for room_id in self._rooms:
            busy = sum(
                s.duration_minutes for s in placed if s.room_id == room_id
            )
            room_util[room_id] = round(busy / horizon_minutes, 4) if horizon_minutes else 0.0

        # Total dead time across vets
        total_dead = 0.0
        for vet_id in self._vets:
            vet_slots = sorted(
                [s for s in placed if s.vet_id == vet_id],
                key=lambda s: s.start,
            )
            for k in range(1, len(vet_slots)):
                gap = (vet_slots[k].start - vet_slots[k - 1].end
                       ).total_seconds() / 60
                total_dead += max(0.0, gap)

        return ScheduleResult(
            scheduled=sorted(placed, key=lambda s: s.start),
            unscheduled=unscheduled,
            vet_utilisation=vet_util,
            room_utilisation=room_util,
            total_dead_time_minutes=round(total_dead, 2),
            objective_score=round(self._objective(placed), 4),
        )
