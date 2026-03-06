from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_db
from app.models import Role, VaccineRecord
from app.schemas import VaccineRecordCreate, VaccineRecordResponse
from app.security import require_role
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
