from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Hospitalization, Role
from app.schemas import HospitalizationCreate, HospitalizationResponse
from app.security import require_role

router = APIRouter(prefix="/api/hospitalizations", tags=["hospitalizations"])


@router.post(
    "/",
    response_model=HospitalizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def admit_pet(
    payload: HospitalizationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    hospitalization = Hospitalization(**payload.model_dump())
    hospitalization.status = "ADMITTED"
    db.add(hospitalization)
    db.commit()
    db.refresh(hospitalization)
    return hospitalization


@router.get("/pet/{pet_id}", response_model=list[HospitalizationResponse])
def get_hospitalizations_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    return (
        db.query(Hospitalization)
        .filter(Hospitalization.pet_id == pet_id)
        .all()
    )


@router.get("/current", response_model=list[HospitalizationResponse])
def get_current_hospitalizations(
    db: Annotated[Session, Depends(get_db)],
) -> list[Hospitalization]:
    return (
        db.query(Hospitalization)
        .filter(Hospitalization.status == "ADMITTED")
        .all()
    )


@router.get("/{hospitalization_id}", response_model=HospitalizationResponse)
def get_hospitalization(
    hospitalization_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    hosp = db.get(Hospitalization, hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Hospitalization not found")
    return hosp


@router.put(
    "/{hospitalization_id}/discharge",
    response_model=HospitalizationResponse,
    dependencies=[Depends(require_role(Role.VET))],
)
def discharge_pet(
    hospitalization_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    hosp = db.get(Hospitalization, hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Hospitalization not found")
    hosp.discharge_date = datetime.now()
    hosp.status = "DISCHARGED"
    db.commit()
    db.refresh(hosp)
    return hosp


@router.put("/{hospitalization_id}/notes", response_model=HospitalizationResponse)
def update_daily_notes(
    hospitalization_id: int,
    notes: Annotated[str, Body()],
    db: Annotated[Session, Depends(get_db)],
) -> Hospitalization:
    hosp = db.get(Hospitalization, hospitalization_id)
    if hosp is None:
        raise HTTPException(status_code=404, detail="Hospitalization not found")
    hosp.daily_notes = notes
    db.commit()
    db.refresh(hosp)
    return hosp
