from __future__ import annotations

from sqlmodel import Session, select

from app.models import HospitalizationLog
from app.schemas import HospitalizationLogCreate


class HospitalizationLogService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: HospitalizationLogCreate) -> HospitalizationLog:
        log = HospitalizationLog.model_validate(data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_id(self, log_id: int) -> HospitalizationLog | None:
        return self.db.get(HospitalizationLog, log_id)

    def get_by_hospitalization(
        self, hospitalization_id: int
    ) -> list[HospitalizationLog]:
        return list(
            self.db.exec(
                select(HospitalizationLog).where(
                    HospitalizationLog.hospitalization_id == hospitalization_id
                )
            ).all()
        )
