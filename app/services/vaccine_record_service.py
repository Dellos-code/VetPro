from __future__ import annotations

from datetime import date

from sqlmodel import Session, select

from app.models import VaccineRecord
from app.schemas import VaccineRecordCreate


class VaccineRecordService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: VaccineRecordCreate) -> VaccineRecord:
        record = VaccineRecord(**payload.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_pet(self, pet_id: int) -> list[VaccineRecord]:
        return list(
            self.db.exec(
                select(VaccineRecord).where(VaccineRecord.pet_id == pet_id)
            ).all()
        )

    def get_overdue(self, check_date: date) -> list[VaccineRecord]:
        return list(
            self.db.exec(
                select(VaccineRecord).where(
                    VaccineRecord.next_due_date.isnot(None),  # type: ignore[union-attr]
                    VaccineRecord.next_due_date < check_date,  # type: ignore[operator]
                )
            ).all()
        )
