from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Prescription, Role
from app.schemas import PrescriptionCreate, PrescriptionResponse
from app.security import require_role
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.post(
    "/",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def create_prescription(
    payload: PrescriptionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Prescription:
    svc = PrescriptionService(db)
    return svc.create(payload)


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Prescription:
    svc = PrescriptionService(db)
    prescription = svc.get_by_id(prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@router.get("/record/{record_id}", response_model=list[PrescriptionResponse])
def get_prescriptions_by_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Prescription]:
    svc = PrescriptionService(db)
    return svc.get_by_record(record_id)
