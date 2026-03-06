from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Appointment, Hospitalization, Invoice, Medication


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_appointments(self, start: datetime, end: datetime) -> int:
        result = self.db.exec(
            select(func.count(Appointment.id)).where(
                Appointment.date_time >= start,
                Appointment.date_time <= end,
            )
        ).one_or_none()
        return result or 0

    def get_revenue(self, start: datetime, end: datetime) -> Decimal:
        result = self.db.exec(
            select(func.sum(Invoice.total_amount)).where(
                Invoice.paid == True,  # noqa: E712
                Invoice.date_issued >= start,
                Invoice.date_issued <= end,
            )
        ).one_or_none()
        return result or Decimal(0)

    def get_low_stock_medications(self) -> list[Medication]:
        return list(
            self.db.exec(
                select(Medication).where(
                    Medication.stock_quantity <= Medication.reorder_level
                )
            ).all()
        )

    def get_currently_hospitalized(self) -> list[Hospitalization]:
        return list(
            self.db.exec(
                select(Hospitalization).where(
                    Hospitalization.status == "ADMITTED"
                )
            ).all()
        )
