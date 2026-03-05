from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Medication, Prescription, Role
from app.schemas import PrescriptionCreate, PrescriptionResponse
from app.security import require_role

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
    medication = db.get(Medication, payload.medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    if medication.stock_quantity < 1:
        raise HTTPException(status_code=400, detail="Medication out of stock")
    medication.stock_quantity -= 1

    prescription = Prescription(**payload.model_dump())
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Prescription:
    prescription = db.get(Prescription, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@router.get("/record/{record_id}", response_model=list[PrescriptionResponse])
def get_prescriptions_by_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Prescription]:
    return (
        db.query(Prescription)
        .filter(Prescription.medical_record_id == record_id)
        .all()
    )
