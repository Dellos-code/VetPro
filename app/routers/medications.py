from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_db
from app.models import Medication, Role
from app.schemas import MedicationCreate, MedicationResponse
from app.security import require_role
from app.services.medication_service import MedicationService

router = APIRouter(prefix="/api/medications", tags=["medications"])


@router.post(
    "/",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def create_medication(
    payload: MedicationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    svc = MedicationService(db)
    return svc.create(payload)


@router.get("/", response_model=list[MedicationResponse])
def list_medications(
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    svc = MedicationService(db)
    return svc.get_all()


@router.get("/low-stock", response_model=list[MedicationResponse])
def get_low_stock(
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    svc = MedicationService(db)
    return svc.get_low_stock()


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(
    medication_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    svc = MedicationService(db)
    medication = svc.get_by_id(medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Το φάρμακο δεν βρέθηκε")
    return medication


@router.put(
    "/{medication_id}",
    response_model=MedicationResponse,
    dependencies=[Depends(require_role(Role.ADMIN, Role.VET))],
)
def update_medication(
    medication_id: int,
    payload: MedicationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    svc = MedicationService(db)
    medication = svc.get_by_id(medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Το φάρμακο δεν βρέθηκε")
    return svc.update(medication, payload)


@router.put(
    "/{medication_id}/stock",
    response_model=MedicationResponse,
    dependencies=[Depends(require_role(Role.ADMIN, Role.VET))],
)
def update_stock(
    medication_id: int,
    quantity: Annotated[int, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    svc = MedicationService(db)
    medication = svc.get_by_id(medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Το φάρμακο δεν βρέθηκε")
    return svc.update_stock(medication, quantity)
