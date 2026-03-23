"""
FastAPI REST wrapper for the VetPro algorithmic engines.

Exposes the SchedulerEngine and InventoryEngine as JSON-over-HTTP
endpoints so the Java/Spring Boot backend (or any frontend) can
invoke them as a micro-service.

Run
---
    uvicorn engines.api:app --host 0.0.0.0 --port 8081 --reload
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engines.scheduler_engine import (
    AppointmentRequest,
    ObjectiveWeights,
    Priority,
    Room,
    ScheduledSlot,
    SchedulerEngine,
    Veterinarian,
)
from engines.inventory_engine import (
    InventoryEngine,
    MedicationProfile,
)

app = FastAPI(
    title="VetPro Algorithmic Engines API",
    version="1.0.0",
    description="Heuristic Scheduler & Stochastic Inventory micro-service",
)


# ====================================================================
# Pydantic request / response schemas
# ====================================================================

# --- Scheduler ---

class VetSchema(BaseModel):
    vet_id: str
    name: str
    available_from: datetime
    available_until: datetime
    competencies: list[str] = ["general"]


class RoomSchema(BaseModel):
    room_id: str
    name: str
    capabilities: list[str] = ["general"]


class AppointmentRequestSchema(BaseModel):
    appointment_id: str
    pet_id: str
    duration_minutes: int = Field(gt=0)
    priority: int = Field(ge=1, le=5, default=1)
    required_type: str = "general"
    preferred_vet_id: Optional[str] = None
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None


class ExistingSlotSchema(BaseModel):
    appointment_id: str
    vet_id: str
    room_id: str
    start: datetime
    end: datetime
    priority: int = 1


class ScheduleRequestSchema(BaseModel):
    veterinarians: list[VetSchema]
    rooms: list[RoomSchema]
    day_start: datetime
    day_end: datetime
    appointments: list[AppointmentRequestSchema]
    existing_slots: list[ExistingSlotSchema] = []
    slot_granularity_minutes: int = Field(default=15, ge=5, le=60)
    local_search_iterations: int = Field(default=200, ge=0)


class ScheduledSlotResponse(BaseModel):
    appointment_id: str
    vet_id: str
    room_id: str
    start: datetime
    end: datetime
    priority: int
    duration_minutes: int


class ScheduleResponseSchema(BaseModel):
    scheduled: list[ScheduledSlotResponse]
    unscheduled: list[str]
    vet_utilisation: dict[str, float]
    room_utilisation: dict[str, float]
    total_dead_time_minutes: float
    objective_score: float


# --- Inventory ---

class MedicationProfileSchema(BaseModel):
    medication_id: str
    name: str
    current_stock: int = Field(ge=0)
    avg_daily_demand: float = Field(ge=0)
    lead_time_mean_days: float = Field(gt=0, default=5.0)
    lead_time_std_days: float = Field(ge=0, default=1.5)
    unit_cost: float = Field(ge=0, default=1.0)


class ForecastRequestSchema(BaseModel):
    medications: list[MedicationProfileSchema]
    target_service_level: float = Field(gt=0, lt=1, default=0.95)
    num_simulations: int = Field(ge=100, default=10_000)
    seed: Optional[int] = None


class ForecastItemResponse(BaseModel):
    medication_id: str
    name: str
    current_stock: int
    stockout_probability: float
    optimal_reorder_point: int
    safety_stock: int
    recommended_order_quantity: int
    expected_demand_during_lead: float
    std_demand_during_lead: float
    days_of_cover: float
    service_level_achieved: float
    var_95: float
    var_99: float
    capital_at_risk: float


class ForecastResponseSchema(BaseModel):
    forecasts: list[ForecastItemResponse]
    critical_items: list[ForecastItemResponse]
    total_capital_at_risk: float
    simulation_count: int


class SensitivityRequestSchema(BaseModel):
    medication: MedicationProfileSchema
    service_levels: list[float] = [0.90, 0.92, 0.95, 0.97, 0.99]
    num_simulations: int = Field(ge=100, default=10_000)
    seed: Optional[int] = None


# ====================================================================
# Endpoints
# ====================================================================

@app.post("/api/engine/schedule", response_model=ScheduleResponseSchema)
def schedule_appointments(req: ScheduleRequestSchema):
    """
    Solve the multi-constraint appointment scheduling problem.
    """
    vets = [
        Veterinarian(
            vet_id=v.vet_id, name=v.name,
            available_from=v.available_from,
            available_until=v.available_until,
            competencies=set(v.competencies),
        )
        for v in req.veterinarians
    ]
    rooms = [
        Room(room_id=r.room_id, name=r.name,
             capabilities=set(r.capabilities))
        for r in req.rooms
    ]
    appointments = [
        AppointmentRequest(
            appointment_id=a.appointment_id,
            pet_id=a.pet_id,
            duration_minutes=a.duration_minutes,
            priority=Priority(a.priority),
            required_type=a.required_type,
            preferred_vet_id=a.preferred_vet_id,
            earliest_start=a.earliest_start,
            latest_end=a.latest_end,
        )
        for a in req.appointments
    ]
    existing = [
        ScheduledSlot(
            appointment_id=s.appointment_id,
            vet_id=s.vet_id, room_id=s.room_id,
            start=s.start, end=s.end,
            priority=Priority(s.priority),
        )
        for s in req.existing_slots
    ]

    engine = SchedulerEngine(
        veterinarians=vets, rooms=rooms,
        day_start=req.day_start, day_end=req.day_end,
        slot_granularity_minutes=req.slot_granularity_minutes,
        local_search_iterations=req.local_search_iterations,
    )
    result = engine.schedule(appointments, existing=existing or None)

    return ScheduleResponseSchema(
        scheduled=[
            ScheduledSlotResponse(
                appointment_id=s.appointment_id,
                vet_id=s.vet_id, room_id=s.room_id,
                start=s.start, end=s.end,
                priority=s.priority,
                duration_minutes=s.duration_minutes,
            )
            for s in result.scheduled
        ],
        unscheduled=result.unscheduled,
        vet_utilisation=result.vet_utilisation,
        room_utilisation=result.room_utilisation,
        total_dead_time_minutes=result.total_dead_time_minutes,
        objective_score=result.objective_score,
    )


@app.post("/api/engine/inventory/forecast",
           response_model=ForecastResponseSchema)
def forecast_inventory(req: ForecastRequestSchema):
    """
    Run Monte Carlo inventory forecast for one or more medications.
    """
    profiles = [
        MedicationProfile(
            medication_id=m.medication_id, name=m.name,
            current_stock=m.current_stock,
            avg_daily_demand=m.avg_daily_demand,
            lead_time_mean_days=m.lead_time_mean_days,
            lead_time_std_days=m.lead_time_std_days,
            unit_cost=m.unit_cost,
        )
        for m in req.medications
    ]

    engine = InventoryEngine(
        target_service_level=req.target_service_level,
        num_simulations=req.num_simulations,
        seed=req.seed,
    )
    batch = engine.forecast_batch(profiles)

    def _to_response(f):
        return ForecastItemResponse(**f.__dict__)

    return ForecastResponseSchema(
        forecasts=[_to_response(f) for f in batch.forecasts],
        critical_items=[_to_response(f) for f in batch.critical_items],
        total_capital_at_risk=batch.total_capital_at_risk,
        simulation_count=batch.simulation_count,
    )


@app.post("/api/engine/inventory/sensitivity")
def sensitivity_analysis(req: SensitivityRequestSchema):
    """
    Evaluate reorder points at multiple service-level targets for a
    single medication.  Returns a map of service_level → forecast.
    """
    profile = MedicationProfile(
        medication_id=req.medication.medication_id,
        name=req.medication.name,
        current_stock=req.medication.current_stock,
        avg_daily_demand=req.medication.avg_daily_demand,
        lead_time_mean_days=req.medication.lead_time_mean_days,
        lead_time_std_days=req.medication.lead_time_std_days,
        unit_cost=req.medication.unit_cost,
    )
    engine = InventoryEngine(
        target_service_level=0.95,
        num_simulations=req.num_simulations,
        seed=req.seed,
    )
    results = engine.sensitivity_analysis(profile, req.service_levels)
    return {
        str(sl): ForecastItemResponse(**fr.__dict__)
        for sl, fr in results.items()
    }


@app.get("/api/engine/health")
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "engines": ["scheduler", "inventory"]}
