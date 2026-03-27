from __future__ import annotations

from sqlmodel import Session, select

from app.models import SideEffect, VaccineRecord
from app.schemas import SideEffectCreate


class SideEffectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: SideEffectCreate) -> SideEffect:
        effect = SideEffect.model_validate(data)
        self.db.add(effect)
        self.db.commit()
        self.db.refresh(effect)
        return effect

    def get_by_id(self, effect_id: int) -> SideEffect | None:
        return self.db.get(SideEffect, effect_id)

    def get_by_vaccine_record(self, vaccine_record_id: int) -> list[SideEffect]:
        return list(
            self.db.exec(
                select(SideEffect).where(
                    SideEffect.vaccine_record_id == vaccine_record_id
                )
            ).all()
        )

    def get_by_pet_and_vaccine(
        self, pet_id: int, vaccine_id: int
    ) -> list[SideEffect]:
        """Έλεγχος αλλεργίας — check if pet has had previous side effects for a vaccine (UC3)."""
        stmt = (
            select(SideEffect)
            .join(VaccineRecord)
            .where(
                VaccineRecord.pet_id == pet_id,
                VaccineRecord.vaccine_id == vaccine_id,
            )
        )
        return list(self.db.exec(stmt).all())
