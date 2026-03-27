from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_db
from app.models import Role, SideEffect, VaccineRecord
from app.schemas import (
    AllergyCheckResult,
    SideEffectCreate,
    SideEffectResponse,
    VaccineRecordCreate,
    VaccineRecordResponse,
)
from app.security import require_role
from app.services.side_effect_service import SideEffectService
from app.services.vaccine_record_service import VaccineRecordService

router = APIRouter(prefix="/api/vaccine-records", tags=["vaccine-records"])


@router.post(
    "/",
    response_model=VaccineRecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def administer_vaccine(
    payload: VaccineRecordCreate,
    db: Annotated[Session, Depends(get_db)],
) -> VaccineRecord:
    """UC3 — Χορήγηση εμβολίου (αυτόματος υπολογισμός επόμενης δόσης)."""
    svc = VaccineRecordService(db)
    return svc.create(payload)


@router.get("/pet/{pet_id}", response_model=list[VaccineRecordResponse])
def get_records_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[VaccineRecord]:
    svc = VaccineRecordService(db)
    return svc.get_by_pet(pet_id)


@router.get("/overdue", response_model=list[VaccineRecordResponse])
def get_overdue_records(
    db: Annotated[Session, Depends(get_db)],
    as_of: Annotated[Optional[date], Query(alias="date")] = None,
) -> list[VaccineRecord]:
    svc = VaccineRecordService(db)
    check_date = as_of if as_of is not None else date.today()
    return svc.get_overdue(check_date)


# ── UC3: Έλεγχος αλλεργίας ──

@router.get(
    "/allergy-check/{pet_id}/{vaccine_id}",
    response_model=AllergyCheckResult,
)
def check_allergy(
    pet_id: int,
    vaccine_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AllergyCheckResult:
    """UC3 — Έλεγχος αλλεργικών αντιδράσεων πριν τον εμβολιασμό."""
    svc = VaccineRecordService(db)
    side_effects = svc.check_allergy(pet_id, vaccine_id)
    has_reaction = len(side_effects) > 0
    warning = None
    if has_reaction:
        warning = (
            "Προσοχή: Το ζώο έχει εμφανίσει παρενέργειες σε προηγούμενο "
            "εμβολιασμό με αυτό το εμβόλιο."
        )
    return AllergyCheckResult(
        has_previous_reaction=has_reaction,
        previous_side_effects=[
            SideEffectResponse.model_validate(se) for se in side_effects
        ],
        warning_message=warning,
    )


# ── UC3: Καταγραφή παρενεργειών ──

@router.post(
    "/{vaccine_record_id}/side-effects",
    response_model=SideEffectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def record_side_effect(
    vaccine_record_id: int,
    payload: SideEffectCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SideEffect:
    """UC3 — Καταγραφή παρενέργειας μετά τον εμβολιασμό."""
    payload.vaccine_record_id = vaccine_record_id
    se_svc = SideEffectService(db)
    return se_svc.create(payload)


@router.get(
    "/{vaccine_record_id}/side-effects",
    response_model=list[SideEffectResponse],
)
def get_side_effects(
    vaccine_record_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[SideEffect]:
    """UC3 — Λίστα παρενεργειών εμβολιασμού."""
    se_svc = SideEffectService(db)
    return se_svc.get_by_vaccine_record(vaccine_record_id)
