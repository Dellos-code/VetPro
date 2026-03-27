from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Examination, Role
from app.schemas import ExaminationCreate, ExaminationResponse
from app.security import require_role
from app.services.examination_service import ExaminationService

router = APIRouter(prefix="/api/examinations", tags=["examinations"])


@router.post(
    "/",
    response_model=ExaminationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.VET))],
)
def create_examination(
    payload: ExaminationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Examination:
    """Δημιουργία εξέτασης."""
    svc = ExaminationService(db)
    return svc.create(payload)


@router.get("/{exam_id}", response_model=ExaminationResponse)
def get_examination(
    exam_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Examination:
    svc = ExaminationService(db)
    exam = svc.get_by_id(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Η εξέταση δεν βρέθηκε")
    return exam


@router.get("/pet/{pet_id}", response_model=list[ExaminationResponse])
def get_examinations_by_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Examination]:
    svc = ExaminationService(db)
    return svc.get_by_pet(pet_id)
