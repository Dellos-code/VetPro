from __future__ import annotations

from sqlmodel import Session, select

from app.models import Examination
from app.schemas import ExaminationCreate


class ExaminationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: ExaminationCreate) -> Examination:
        exam = Examination.model_validate(data)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_by_id(self, exam_id: int) -> Examination | None:
        return self.db.get(Examination, exam_id)

    def get_by_pet(self, pet_id: int) -> list[Examination]:
        return list(
            self.db.exec(
                select(Examination).where(Examination.pet_id == pet_id)
            ).all()
        )

    def get_by_vet(self, vet_id: int) -> list[Examination]:
        return list(
            self.db.exec(
                select(Examination).where(
                    Examination.veterinarian_id == vet_id
                )
            ).all()
        )
