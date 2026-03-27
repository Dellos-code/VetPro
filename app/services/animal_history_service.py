from __future__ import annotations

from sqlmodel import Session, select

from app.models import Examination, MedicalRecord, Pet, VaccineRecord
from app.schemas import (
    AnimalHistoryResponse,
    AnimalSearchResponse,
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
        - Κενό ιστορικό → returns response with empty lists + message
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

        # UC1 alt flow — Κενό ιστορικό
        message = None
        if not records and not vaccines and not exams:
            message = "Δεν βρέθηκε ιατρικό ιστορικό για αυτό το ζώο."

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
            message=message,
        )

    def search_by_name(self, name: str) -> AnimalSearchResponse:
        """UC1 alt flow — Αναζήτηση με βάση όνομα (συνώνυμα / πολλαπλά αποτελέσματα)."""
        results = list(
            self.db.exec(
                select(Pet).where(Pet.name.contains(name))  # type: ignore[attr-defined]
            ).all()
        )

        # UC1 alt flow — Πολλαπλά αποτελέσματα / συνώνυμα
        message = None
        if not results:
            message = "Δεν βρέθηκε ζώο με αυτό το όνομα."
        elif len(results) > 1:
            message = (
                f"Βρέθηκαν {len(results)} ζώα με παρόμοιο όνομα. "
                "Παρακαλώ επιλέξτε το σωστό."
            )

        return AnimalSearchResponse(
            results=[PetResponse.model_validate(p) for p in results],
            count=len(results),
            message=message,
        )
