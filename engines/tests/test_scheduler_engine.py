"""
Unit tests for the Heuristic Scheduler Engine.

Tests cover:
    • Basic scheduling of single and multiple appointments
    • Hard-constraint enforcement (no overlaps, working hours)
    • Priority ordering (higher priority → earlier slots)
    • Emergency preemption of lower-priority appointments
    • Vet competence & room capability filtering
    • Preferred-vet soft constraint
    • Edge cases (empty input, infeasible, full schedule)
    • Utilisation metric correctness
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from engines.scheduler_engine import (
    AppointmentRequest,
    ObjectiveWeights,
    Priority,
    Room,
    ScheduledSlot,
    SchedulerEngine,
    Veterinarian,
)

# -- helpers ----------------------------------------------------------------

DAY = datetime(2026, 3, 4)
DAY_START = DAY.replace(hour=8, minute=0)
DAY_END = DAY.replace(hour=18, minute=0)


def _vet(vid: str = "V1", comps: set[str] | None = None,
         start: datetime = DAY_START,
         end: datetime = DAY_END) -> Veterinarian:
    return Veterinarian(
        vet_id=vid, name=f"Dr {vid}",
        available_from=start, available_until=end,
        competencies=comps or {"general"},
    )


def _room(rid: str = "R1", caps: set[str] | None = None) -> Room:
    return Room(room_id=rid, name=f"Room {rid}",
                capabilities=caps or {"general"})


def _appt(aid: str, dur: int = 30,
           priority: Priority = Priority.ROUTINE_CHECKUP,
           req_type: str = "general",
           pref_vet: str | None = None) -> AppointmentRequest:
    return AppointmentRequest(
        appointment_id=aid, pet_id=f"pet-{aid}",
        duration_minutes=dur, priority=priority,
        required_type=req_type, preferred_vet_id=pref_vet,
    )


def _engine(vets=None, rooms=None, **kw) -> SchedulerEngine:
    return SchedulerEngine(
        veterinarians=vets or [_vet()],
        rooms=rooms or [_room()],
        day_start=DAY_START, day_end=DAY_END,
        local_search_iterations=0,
        **kw,
    )


# -- tests ------------------------------------------------------------------

class TestBasicScheduling(unittest.TestCase):
    """Single-appointment, simple scenarios."""

    def test_single_appointment_is_scheduled(self):
        engine = _engine()
        result = engine.schedule([_appt("A1", dur=30)])
        self.assertEqual(len(result.scheduled), 1)
        self.assertEqual(len(result.unscheduled), 0)
        slot = result.scheduled[0]
        self.assertEqual(slot.appointment_id, "A1")
        self.assertEqual(slot.duration_minutes, 30)

    def test_empty_input_returns_empty(self):
        engine = _engine()
        result = engine.schedule([])
        self.assertEqual(result.scheduled, [])
        self.assertEqual(result.unscheduled, [])
        self.assertEqual(result.objective_score, 0.0)

    def test_scheduled_within_working_hours(self):
        engine = _engine()
        result = engine.schedule([_appt("A1", dur=60)])
        slot = result.scheduled[0]
        self.assertGreaterEqual(slot.start, DAY_START)
        self.assertLessEqual(slot.end, DAY_END)


class TestConstraints(unittest.TestCase):
    """Hard-constraint enforcement."""

    def test_no_vet_overlap(self):
        """Two appointments on the same vet must not overlap."""
        engine = _engine(vets=[_vet("V1")], rooms=[_room("R1"), _room("R2")])
        result = engine.schedule([
            _appt("A1", dur=60),
            _appt("A2", dur=60),
        ])
        self.assertEqual(len(result.scheduled), 2)
        a1, a2 = sorted(result.scheduled, key=lambda s: s.start)
        if a1.vet_id == a2.vet_id:
            self.assertLessEqual(a1.end, a2.start)

    def test_no_room_overlap(self):
        """Two appointments in the same room must not overlap."""
        engine = _engine(vets=[_vet("V1"), _vet("V2")], rooms=[_room("R1")])
        result = engine.schedule([
            _appt("A1", dur=60),
            _appt("A2", dur=60),
        ])
        self.assertEqual(len(result.scheduled), 2)
        a1, a2 = sorted(result.scheduled, key=lambda s: s.start)
        if a1.room_id == a2.room_id:
            self.assertLessEqual(a1.end, a2.start)

    def test_competence_filter(self):
        """Only qualified vets can handle specialised appointment types."""
        engine = _engine(
            vets=[_vet("V1", {"general"}), _vet("V2", {"surgery"})],
            rooms=[_room("R1", {"general", "surgery"})],
        )
        result = engine.schedule([_appt("A1", req_type="surgery")])
        self.assertEqual(len(result.scheduled), 1)
        self.assertEqual(result.scheduled[0].vet_id, "V2")

    def test_infeasible_type_not_scheduled(self):
        """Appointment requiring unavailable competence is unscheduled."""
        engine = _engine(
            vets=[_vet("V1", {"general"})],
            rooms=[_room("R1", {"general"})],
        )
        result = engine.schedule([_appt("A1", req_type="exotic")])
        self.assertEqual(len(result.scheduled), 0)
        self.assertIn("A1", result.unscheduled)


class TestPriority(unittest.TestCase):
    """Priority-based ordering."""

    def test_higher_priority_scheduled_earlier(self):
        engine = _engine()
        result = engine.schedule([
            _appt("LO", dur=30, priority=Priority.ROUTINE_CHECKUP),
            _appt("HI", dur=30, priority=Priority.URGENT),
        ])
        self.assertEqual(len(result.scheduled), 2)
        hi = next(s for s in result.scheduled if s.appointment_id == "HI")
        lo = next(s for s in result.scheduled if s.appointment_id == "LO")
        self.assertLessEqual(hi.start, lo.start)


class TestEmergencyPreemption(unittest.TestCase):
    """Emergency preemption behaviour."""

    def test_emergency_preempts_routine(self):
        """Emergency should be placed even when schedule is nearly full."""
        # Fill the day with routine 30-min slots → 20 slots in 10 hours
        vets = [_vet("V1")]
        rooms = [_room("R1")]
        engine = _engine(vets=vets, rooms=rooms)

        # Create enough routine appointments to fill the day
        routines = [_appt(f"R{i}", dur=30, priority=Priority.ROUTINE_CHECKUP)
                    for i in range(20)]
        result1 = engine.schedule(routines)

        # Now add an emergency
        all_appts = routines + [
            _appt("EM1", dur=30, priority=Priority.EMERGENCY)
        ]
        engine2 = _engine(vets=vets, rooms=rooms)
        result2 = engine2.schedule(all_appts)

        em_slots = [s for s in result2.scheduled
                    if s.appointment_id == "EM1"]
        self.assertEqual(len(em_slots), 1, "Emergency must be scheduled")

    def test_emergency_gets_early_slot(self):
        engine = _engine()
        result = engine.schedule([
            _appt("EM", dur=30, priority=Priority.EMERGENCY),
            _appt("RU", dur=30, priority=Priority.ROUTINE_CHECKUP),
        ])
        em = next(s for s in result.scheduled if s.appointment_id == "EM")
        ru = next(s for s in result.scheduled if s.appointment_id == "RU")
        self.assertLessEqual(em.start, ru.start)


class TestMultiResource(unittest.TestCase):
    """Scheduling across multiple vets and rooms."""

    def test_parallel_scheduling(self):
        """With 2 vets and 2 rooms, 4 concurrent 30-min appointments fit."""
        engine = _engine(
            vets=[_vet("V1"), _vet("V2")],
            rooms=[_room("R1"), _room("R2")],
        )
        result = engine.schedule([_appt(f"A{i}", dur=30) for i in range(4)])
        self.assertEqual(len(result.scheduled), 4)
        self.assertEqual(len(result.unscheduled), 0)

    def test_utilisation_reported(self):
        engine = _engine(
            vets=[_vet("V1"), _vet("V2")],
            rooms=[_room("R1"), _room("R2")],
        )
        result = engine.schedule([_appt("A1", dur=60)])
        self.assertIn("V1", result.vet_utilisation)
        self.assertIn("V2", result.vet_utilisation)
        # One vet should have non-zero utilisation
        total_util = sum(result.vet_utilisation.values())
        self.assertGreater(total_util, 0)


class TestPreferredVet(unittest.TestCase):

    def test_preference_honoured_when_possible(self):
        engine = _engine(
            vets=[_vet("V1"), _vet("V2")],
            rooms=[_room("R1")],
        )
        result = engine.schedule([_appt("A1", dur=30, pref_vet="V2")])
        self.assertEqual(result.scheduled[0].vet_id, "V2")


class TestExistingSlots(unittest.TestCase):

    def test_existing_slots_respected(self):
        engine = _engine()
        existing = [ScheduledSlot(
            appointment_id="E1", vet_id="V1", room_id="R1",
            start=DAY_START, end=DAY_START + timedelta(minutes=60),
            priority=Priority.ROUTINE_CHECKUP,
        )]
        result = engine.schedule([_appt("A1", dur=30)], existing=existing)
        a1 = result.scheduled[0] if result.scheduled[0].appointment_id == "A1" \
            else result.scheduled[1]
        self.assertGreaterEqual(a1.start, existing[0].end)


class TestEdgeCases(unittest.TestCase):

    def test_constructor_rejects_no_vets(self):
        with self.assertRaises(ValueError):
            SchedulerEngine([], [_room()], DAY_START, DAY_END)

    def test_constructor_rejects_no_rooms(self):
        with self.assertRaises(ValueError):
            SchedulerEngine([_vet()], [], DAY_START, DAY_END)

    def test_constructor_rejects_bad_time_range(self):
        with self.assertRaises(ValueError):
            SchedulerEngine([_vet()], [_room()], DAY_END, DAY_START)

    def test_appointment_longer_than_day(self):
        engine = _engine()
        result = engine.schedule([_appt("BIG", dur=700)])
        self.assertEqual(len(result.scheduled), 0)
        self.assertIn("BIG", result.unscheduled)


if __name__ == "__main__":
    unittest.main()
