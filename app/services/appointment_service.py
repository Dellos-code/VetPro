from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import Appointment, AppointmentStatus
from app.schemas import AppointmentCreate


class AppointmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: AppointmentCreate) -> Appointment:
        appointment = Appointment(**payload.model_dump())
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_by_id(self, appointment_id: int) -> Appointment | None:
        return self.db.get(Appointment, appointment_id)

    def get_by_pet(self, pet_id: int) -> list[Appointment]:
        return list(
            self.db.exec(
                select(Appointment).where(Appointment.pet_id == pet_id)
            ).all()
        )

    def get_by_vet(self, vet_id: int) -> list[Appointment]:
        return list(
            self.db.exec(
                select(Appointment).where(Appointment.veterinarian_id == vet_id)
            ).all()
        )

    def get_by_range(self, start: datetime, end: datetime) -> list[Appointment]:
        return list(
            self.db.exec(
                select(Appointment).where(
                    Appointment.date_time >= start,
                    Appointment.date_time <= end,
                )
            ).all()
        )

    def update(self, appointment: Appointment, payload: AppointmentCreate) -> Appointment:
        for key, value in payload.model_dump().items():
            setattr(appointment, key, value)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def cancel(self, appointment: Appointment) -> Appointment:
        appointment.status = AppointmentStatus.CANCELLED
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def complete(self, appointment: Appointment) -> Appointment:
        appointment.status = AppointmentStatus.COMPLETED
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
