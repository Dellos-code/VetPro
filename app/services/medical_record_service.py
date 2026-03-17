from __future__ import annotations

from sqlmodel import Session, select

from app.models import MedicalRecord
from app.schemas import MedicalRecordCreate


class MedicalRecordService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: MedicalRecordCreate) -> MedicalRecord:
        record = MedicalRecord(**payload.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: int) -> MedicalRecord | None:
        return self.db.get(MedicalRecord, record_id)

    def get_by_pet(self, pet_id: int) -> list[MedicalRecord]:
        return list(
            self.db.exec(
                select(MedicalRecord).where(MedicalRecord.pet_id == pet_id)
            ).all()
        )

    def get_by_vet(self, vet_id: int) -> list[MedicalRecord]:
        return list(
            self.db.exec(
                select(MedicalRecord).where(
                    MedicalRecord.veterinarian_id == vet_id
                )
            ).all()
        )
