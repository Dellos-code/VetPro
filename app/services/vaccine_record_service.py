from __future__ import annotations

from datetime import date, timedelta

from sqlmodel import Session, select

from app.models import SideEffect, Vaccine, VaccineRecord
from app.schemas import VaccineRecordCreate


class VaccineRecordService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def check_allergy(self, pet_id: int, vaccine_id: int) -> list[SideEffect]:
        """UC3 — Έλεγχος αλλεργικής αντίδρασης πριν τον εμβολιασμό."""
        stmt = (
            select(SideEffect)
            .join(VaccineRecord)
            .where(
                VaccineRecord.pet_id == pet_id,
                VaccineRecord.vaccine_id == vaccine_id,
            )
        )
        return list(self.db.exec(stmt).all())

    def create(self, payload: VaccineRecordCreate) -> VaccineRecord:
        record = VaccineRecord(**payload.model_dump())

        # UC3 — Αυτόματος υπολογισμός επόμενης δόσης
        if record.next_due_date is None and record.date_administered is not None:
            vaccine = self.db.get(Vaccine, record.vaccine_id)
            if vaccine is not None:
                record.next_due_date = (
                    record.date_administered
                    + timedelta(days=vaccine.default_interval_days)
                )

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
