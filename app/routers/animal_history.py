from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.models import Pet
from app.schemas import AnimalHistoryResponse, PetResponse
from app.services.animal_history_service import AnimalHistoryService

router = APIRouter(prefix="/api/animal-history", tags=["animal-history"])


@router.get("/{pet_id}", response_model=AnimalHistoryResponse)
def get_animal_history(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AnimalHistoryResponse:
    """UC1 — Προβολή πλήρους ιστορικού ζώου (εμβόλια, θεραπείες, εξετάσεις)."""
    svc = AnimalHistoryService(db)
    result = svc.get_history(pet_id)
    if result is None:
        # Alt flow: Ζώο δεν βρέθηκε
        raise HTTPException(
            status_code=404, detail="Το ζώο δεν βρέθηκε"
        )
    return result


@router.get("/search/", response_model=list[PetResponse])
def search_animals_by_name(
    name: Annotated[str, Query(min_length=1)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Pet]:
    """UC1 alt flow — Αναζήτηση ζώου (πολλαπλά αποτελέσματα / συνώνυμα)."""
    svc = AnimalHistoryService(db)
    return svc.search_by_name(name)
