from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Vaccine
from app.schemas import VaccineCreate, VaccineResponse
from app.services.vaccine_service import VaccineService

router = APIRouter(prefix="/api/vaccines", tags=["vaccines"])


@router.post("/", response_model=VaccineResponse, status_code=status.HTTP_201_CREATED)
def create_vaccine(
    payload: VaccineCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Vaccine:
    svc = VaccineService(db)
    return svc.create(payload)


@router.get("/", response_model=list[VaccineResponse])
def list_vaccines(
    db: Annotated[Session, Depends(get_db)],
) -> list[Vaccine]:
    svc = VaccineService(db)
    return svc.get_all()


@router.get("/{vaccine_id}", response_model=VaccineResponse)
def get_vaccine(
    vaccine_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Vaccine:
    svc = VaccineService(db)
    vaccine = svc.get_by_id(vaccine_id)
    if vaccine is None:
        raise HTTPException(status_code=404, detail="Το εμβόλιο δεν βρέθηκε")
    return vaccine
