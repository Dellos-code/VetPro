from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, AppointmentStatus, Role
from app.schemas import AppointmentCreate, AppointmentResponse
from app.security import require_role

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_role(Role.OWNER, Role.RECEPTIONIST, Role.VET, Role.ADMIN)),
    ],
)
def create_appointment(
    payload: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.get("/pet/{pet_id}", response_model=list[AppointmentResponse])
def get_appointments_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    return db.query(Appointment).filter(Appointment.pet_id == pet_id).all()


@router.get("/vet/{vet_id}", response_model=list[AppointmentResponse])
def get_appointments_by_vet(
    vet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.veterinarian_id == vet_id)
        .all()
    )


@router.get("/range", response_model=list[AppointmentResponse])
def get_appointments_by_range(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.date_time >= start, Appointment.date_time <= end)
        .all()
    )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for key, value in payload.model_dump().items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.put("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment


@router.put("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = AppointmentStatus.COMPLETED
    db.commit()
    db.refresh(appointment)
    return appointment
