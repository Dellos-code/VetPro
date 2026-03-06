from __future__ import annotations

from sqlmodel import Session, select

from app.models import Vaccine
from app.schemas import VaccineCreate


class VaccineService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: VaccineCreate) -> Vaccine:
        vaccine = Vaccine(**payload.model_dump())
        self.db.add(vaccine)
        self.db.commit()
        self.db.refresh(vaccine)
        return vaccine

    def get_all(self) -> list[Vaccine]:
        return list(self.db.exec(select(Vaccine)).all())

    def get_by_id(self, vaccine_id: int) -> Vaccine | None:
        return self.db.get(Vaccine, vaccine_id)
