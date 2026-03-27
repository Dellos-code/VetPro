from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_db
from app.models import Report, Role
from app.schemas import ReportResponse
from app.security import require_role
from app.services.report_entity_service import ReportEntityService

router = APIRouter(prefix="/api/generated-reports", tags=["generated-reports"])


@router.post(
    "/medical-history/{pet_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET, Role.ADMIN))],
)
def generate_medical_history_report(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
    generated_by_id: Annotated[Optional[int], Query()] = None,
) -> Report:
    """UC6 — Δημιουργία αναφοράς ιατρικού ιστορικού με φίλτρα ημερομηνιών."""
    svc = ReportEntityService(db)
    try:
        return svc.generate_medical_history_report(
            pet_id=pet_id,
            generated_by_id=generated_by_id or 0,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Report:
    svc = ReportEntityService(db)
    report = svc.get_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Η αναφορά δεν βρέθηκε")
    return report


@router.get("/pet/{pet_id}", response_model=list[ReportResponse])
def get_reports_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Report]:
    svc = ReportEntityService(db)
    return svc.get_by_pet(pet_id)
