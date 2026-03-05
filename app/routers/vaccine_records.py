from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, VaccineRecord
from app.schemas import VaccineRecordCreate, VaccineRecordResponse
from app.security import require_role

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
    record = VaccineRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/pet/{pet_id}", response_model=list[VaccineRecordResponse])
def get_records_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[VaccineRecord]:
    return db.query(VaccineRecord).filter(VaccineRecord.pet_id == pet_id).all()


@router.get("/overdue", response_model=list[VaccineRecordResponse])
def get_overdue_records(
    db: Annotated[Session, Depends(get_db)],
    as_of: Annotated[Optional[date], Query(alias="date")] = None,
) -> list[VaccineRecord]:
    check_date = as_of if as_of is not None else date.today()
    return (
        db.query(VaccineRecord)
        .filter(
            VaccineRecord.next_due_date.isnot(None),
            VaccineRecord.next_due_date < check_date,
        )
        .all()
    )
