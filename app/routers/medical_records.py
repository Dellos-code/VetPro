from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MedicalRecord, Role
from app.schemas import MedicalRecordCreate, MedicalRecordResponse
from app.security import require_role

router = APIRouter(prefix="/api/medical-records", tags=["medical-records"])


@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def create_medical_record(
    payload: MedicalRecordCreate,
    db: Annotated[Session, Depends(get_db)],
) -> MedicalRecord:
    record = MedicalRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MedicalRecord:
    record = db.get(MedicalRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record


@router.get("/pet/{pet_id}", response_model=list[MedicalRecordResponse])
def get_records_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicalRecord]:
    return db.query(MedicalRecord).filter(MedicalRecord.pet_id == pet_id).all()


@router.get("/vet/{vet_id}", response_model=list[MedicalRecordResponse])
def get_records_by_vet(
    vet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicalRecord]:
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.veterinarian_id == vet_id)
        .all()
    )
