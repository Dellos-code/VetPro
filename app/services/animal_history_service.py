from __future__ import annotations

from sqlmodel import Session, select

from app.models import Examination, MedicalRecord, Pet, VaccineRecord
from app.schemas import (
    AnimalHistoryResponse,
    ExaminationResponse,
    MedicalRecordResponse,
    PetResponse,
    VaccineRecordResponse,
)


class AnimalHistoryService:
    """UC1 — Προβολή ιστορικού ζώου."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_history(self, pet_id: int) -> AnimalHistoryResponse | None:
        """Ανάκτηση πλήρους ιστορικού ζώου.

        Alt flows:
        - Ζώο δεν βρέθηκε → returns None
        - Κενό ιστορικό → returns response with empty lists
        """
        pet = self.db.get(Pet, pet_id)
        if pet is None:
            return None

        records = list(
            self.db.exec(
                select(MedicalRecord).where(MedicalRecord.pet_id == pet_id)
            ).all()
        )
        vaccines = list(
            self.db.exec(
                select(VaccineRecord).where(VaccineRecord.pet_id == pet_id)
            ).all()
        )
        exams = list(
            self.db.exec(
                select(Examination).where(Examination.pet_id == pet_id)
            ).all()
        )

        return AnimalHistoryResponse(
            pet=PetResponse.model_validate(pet),
            medical_records=[
                MedicalRecordResponse.model_validate(r) for r in records
            ],
            vaccine_records=[
                VaccineRecordResponse.model_validate(v) for v in vaccines
            ],
            examinations=[
                ExaminationResponse.model_validate(e) for e in exams
            ],
        )

    def search_by_name(self, name: str) -> list[Pet]:
        """UC1 alt flow — Αναζήτηση με βάση όνομα (συνώνυμα / πολλαπλά αποτελέσματα)."""
        return list(
            self.db.exec(
                select(Pet).where(Pet.name.contains(name))  # type: ignore[attr-defined]
            ).all()
        )
