from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Hospitalization, Invoice, Medication, Role
from app.schemas import HospitalizationResponse, MedicationResponse
from app.security import require_role

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
    dependencies=[Depends(require_role(Role.ADMIN, Role.VET))],
)


@router.get("/appointments/count")
def count_appointments(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> int:
    return (
        db.query(func.count(Appointment.id))
        .filter(Appointment.date_time >= start, Appointment.date_time <= end)
        .scalar()
    ) or 0


@router.get("/revenue")
def get_revenue(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> Decimal:
    result = (
        db.query(func.sum(Invoice.total_amount))
        .filter(
            Invoice.paid == True,  # noqa: E712
            Invoice.date_issued >= start,
            Invoice.date_issued <= end,
        )
        .scalar()
    )
    return result or Decimal(0)


@router.get("/low-stock", response_model=list[MedicationResponse])
def get_low_stock_medications(
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.stock_quantity <= Medication.reorder_level)
        .all()
    )


@router.get("/hospitalized", response_model=list[HospitalizationResponse])
def get_currently_hospitalized(
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    return (
        db.query(Hospitalization)
        .filter(Hospitalization.status == "ADMITTED")
        .all()
    )
