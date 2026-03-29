from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_db
from app.models import Appointment, Role
from app.schemas import AppointmentCreate, AppointmentResponse
from app.security import require_role
from app.services.appointment_service import AppointmentService

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
    svc = AppointmentService(db)
    return svc.create(payload)


@router.get("/pet/{pet_id}", response_model=list[AppointmentResponse])
def get_appointments_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    svc = AppointmentService(db)
    return svc.get_by_pet(pet_id)


@router.get("/vet/{vet_id}", response_model=list[AppointmentResponse])
def get_appointments_by_vet(
    vet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    svc = AppointmentService(db)
    return svc.get_by_vet(vet_id)


@router.get("/range", response_model=list[AppointmentResponse])
def get_appointments_by_range(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> list[Appointment]:
    svc = AppointmentService(db)
    return svc.get_by_range(start, end)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    svc = AppointmentService(db)
    appointment = svc.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Το ραντεβού δεν βρέθηκε")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    svc = AppointmentService(db)
    appointment = svc.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Το ραντεβού δεν βρέθηκε")
    return svc.update(appointment, payload)


@router.put("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    svc = AppointmentService(db)
    appointment = svc.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Το ραντεβού δεν βρέθηκε")
    return svc.cancel(appointment)


@router.put("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Appointment:
    svc = AppointmentService(db)
    appointment = svc.get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Το ραντεβού δεν βρέθηκε")
    return svc.complete(appointment)
