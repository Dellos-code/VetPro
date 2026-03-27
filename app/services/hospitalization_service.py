from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import Hospitalization
from app.schemas import HospitalizationCreate


class HospitalizationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def admit(self, payload: HospitalizationCreate) -> Hospitalization:
        hospitalization = Hospitalization(**payload.model_dump())
        hospitalization.status = "ADMITTED"
        self.db.add(hospitalization)
        self.db.commit()
        self.db.refresh(hospitalization)
        return hospitalization

    def get_by_id(self, hospitalization_id: int) -> Hospitalization | None:
        return self.db.get(Hospitalization, hospitalization_id)

    def get_by_pet(self, pet_id: int) -> list[Hospitalization]:
        return list(
            self.db.exec(
                select(Hospitalization).where(
                    Hospitalization.pet_id == pet_id
                )
            ).all()
        )

    def get_current(self) -> list[Hospitalization]:
        return list(
            self.db.exec(
                select(Hospitalization).where(
                    Hospitalization.status == "ADMITTED"
                )
            ).all()
        )

    def discharge(
        self,
        hospitalization: Hospitalization,
        discharge_instructions: str | None = None,
    ) -> Hospitalization:
        """UC4 — Εξιτήριο με οδηγίες."""
        hospitalization.discharge_date = datetime.now()
        hospitalization.status = "DISCHARGED"
        if discharge_instructions is not None:
            hospitalization.discharge_instructions = discharge_instructions
        self.db.commit()
        self.db.refresh(hospitalization)
        return hospitalization

    def update_notes(self, hospitalization: Hospitalization, notes: str) -> Hospitalization:
        hospitalization.daily_notes = notes
        self.db.commit()
        self.db.refresh(hospitalization)
        return hospitalization
