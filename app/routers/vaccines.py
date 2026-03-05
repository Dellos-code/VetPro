from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vaccine
from app.schemas import VaccineCreate, VaccineResponse

router = APIRouter(prefix="/api/vaccines", tags=["vaccines"])


@router.post("/", response_model=VaccineResponse, status_code=status.HTTP_201_CREATED)
def create_vaccine(
    payload: VaccineCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Vaccine:
    vaccine = Vaccine(**payload.model_dump())
    db.add(vaccine)
    db.commit()
    db.refresh(vaccine)
    return vaccine


@router.get("/", response_model=list[VaccineResponse])
def list_vaccines(
    db: Annotated[Session, Depends(get_db)],
) -> list[Vaccine]:
    return db.query(Vaccine).all()


@router.get("/{vaccine_id}", response_model=VaccineResponse)
def get_vaccine(
    vaccine_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Vaccine:
    vaccine = db.get(Vaccine, vaccine_id)
    if vaccine is None:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    return vaccine
