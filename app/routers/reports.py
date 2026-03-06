from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_db
from app.models import Hospitalization, Medication, Role
from app.schemas import HospitalizationResponse, MedicationResponse
from app.security import require_role
from app.services.report_service import ReportService

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
    svc = ReportService(db)
    return svc.count_appointments(start, end)


@router.get("/revenue")
def get_revenue(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> Decimal:
    svc = ReportService(db)
    return svc.get_revenue(start, end)


@router.get("/low-stock", response_model=list[MedicationResponse])
def get_low_stock_medications(
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    svc = ReportService(db)
    return svc.get_low_stock_medications()


@router.get("/hospitalized", response_model=list[HospitalizationResponse])
def get_currently_hospitalized(
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    svc = ReportService(db)
    return svc.get_currently_hospitalized()
