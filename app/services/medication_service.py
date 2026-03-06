from __future__ import annotations

from sqlmodel import Session, select

from app.models import Medication
from app.schemas import MedicationCreate


class MedicationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: MedicationCreate) -> Medication:
        medication = Medication(**payload.model_dump())
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def get_all(self) -> list[Medication]:
        return list(self.db.exec(select(Medication)).all())

    def get_by_id(self, medication_id: int) -> Medication | None:
        return self.db.get(Medication, medication_id)

    def get_low_stock(self) -> list[Medication]:
        return list(
            self.db.exec(
                select(Medication).where(
                    Medication.stock_quantity <= Medication.reorder_level
                )
            ).all()
        )

    def update(self, medication: Medication, payload: MedicationCreate) -> Medication:
        for key, value in payload.model_dump().items():
            setattr(medication, key, value)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def update_stock(self, medication: Medication, quantity: int) -> Medication:
        medication.stock_quantity = quantity
        self.db.commit()
        self.db.refresh(medication)
        return medication
