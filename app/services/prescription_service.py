from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Medication, Prescription
from app.schemas import PrescriptionCreate
from app.services.medication_service import MedicationService


class PrescriptionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: PrescriptionCreate) -> Prescription:
        medication = self.db.get(Medication, payload.medication_id)
        # UC5 alt flow — Φάρμακο δεν βρέθηκε στον κατάλογο
        if medication is None:
            raise HTTPException(
                status_code=404,
                detail="Το φάρμακο δεν βρέθηκε στον κατάλογο",
            )
        MedicationService(self.db).consume_stock(medication, quantity=1)

        prescription = Prescription(**payload.model_dump())
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def get_by_id(self, prescription_id: int) -> Prescription | None:
        return self.db.get(Prescription, prescription_id)

    def get_by_record(self, record_id: int) -> list[Prescription]:
        return list(
            self.db.exec(
                select(Prescription).where(
                    Prescription.medical_record_id == record_id
                )
            ).all()
        )
