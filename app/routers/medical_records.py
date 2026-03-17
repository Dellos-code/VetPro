from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import MedicalRecord, Role
from app.schemas import MedicalRecordCreate, MedicalRecordResponse
from app.security import require_role
from app.services.medical_record_service import MedicalRecordService

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
    svc = MedicalRecordService(db)
    return svc.create(payload)


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MedicalRecord:
    svc = MedicalRecordService(db)
    record = svc.get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record


@router.get("/pet/{pet_id}", response_model=list[MedicalRecordResponse])
def get_records_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicalRecord]:
    svc = MedicalRecordService(db)
    return svc.get_by_pet(pet_id)


@router.get("/vet/{vet_id}", response_model=list[MedicalRecordResponse])
def get_records_by_vet(
    vet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicalRecord]:
    svc = MedicalRecordService(db)
    return svc.get_by_vet(vet_id)
