from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Hospitalization, HospitalizationLog, Role
from app.schemas import (
    HospitalizationCreate,
    HospitalizationLogCreate,
    HospitalizationLogResponse,
    HospitalizationResponse,
)
from app.security import require_role
from app.services.hospitalization_log_service import HospitalizationLogService
from app.services.hospitalization_service import HospitalizationService

router = APIRouter(prefix="/api/hospitalizations", tags=["hospitalizations"])


@router.post(
    "/",
    response_model=HospitalizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def admit_pet(
    payload: HospitalizationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    svc = HospitalizationService(db)
    return svc.admit(payload)


@router.get("/pet/{pet_id}", response_model=list[HospitalizationResponse])
def get_hospitalizations_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    svc = HospitalizationService(db)
    return svc.get_by_pet(pet_id)


@router.get("/current", response_model=list[HospitalizationResponse])
def get_current_hospitalizations(
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    svc = HospitalizationService(db)
    return svc.get_current()


@router.get("/{hospitalization_id}", response_model=HospitalizationResponse)
def get_hospitalization(
    hospitalization_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    svc = HospitalizationService(db)
    hosp = svc.get_by_id(hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Η νοσηλεία δεν βρέθηκε")
    return hosp


@router.put(
    "/{hospitalization_id}/discharge",
    response_model=HospitalizationResponse,
    dependencies=[Depends(require_role(Role.VET))],
)
def discharge_pet(
    hospitalization_id: int,
    db: Annotated[Session, Depends(get_db)],
    discharge_instructions: Annotated[Optional[str], Body()] = None,
) -> Hospitalization:
    """UC4 — Εξιτήριο νοσηλείας με οδηγίες."""
    svc = HospitalizationService(db)
    hosp = svc.get_by_id(hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Η νοσηλεία δεν βρέθηκε")
    return svc.discharge(hosp, discharge_instructions)


@router.put("/{hospitalization_id}/notes", response_model=HospitalizationResponse)
def update_daily_notes(
    hospitalization_id: int,
    notes: Annotated[str, Body()],
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    svc = HospitalizationService(db)
    hosp = svc.get_by_id(hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Η νοσηλεία δεν βρέθηκε")
    return svc.update_notes(hosp, notes)


# ── UC4: Ημερήσιο αρχείο νοσηλείας (Daily Logs) ──

@router.post(
    "/{hospitalization_id}/logs",
    response_model=HospitalizationLogResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def add_daily_log(
    hospitalization_id: int,
    payload: HospitalizationLogCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HospitalizationLog:
    """UC4 — Καταχώρηση ημερήσιας καταγραφής (θερμοκρασία, διατροφή, φαρμακευτική αγωγή)."""
    svc = HospitalizationService(db)
    hosp = svc.get_by_id(hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Η νοσηλεία δεν βρέθηκε")
    payload.hospitalization_id = hospitalization_id
    log_svc = HospitalizationLogService(db)
    return log_svc.create(payload)


@router.get(
    "/{hospitalization_id}/logs",
    response_model=list[HospitalizationLogResponse],
)
def get_daily_logs(
    hospitalization_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[HospitalizationLog]:
    """UC4 — Λίστα ημερήσιων καταγραφών νοσηλείας."""
    log_svc = HospitalizationLogService(db)
    return log_svc.get_by_hospitalization(hospitalization_id)
