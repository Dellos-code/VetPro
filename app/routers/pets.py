from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Pet
from app.schemas import PetCreate, PetResponse
from app.services.pet_service import PetService

router = APIRouter(prefix="/api/pets", tags=["pets"])


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    payload: PetCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    svc = PetService(db)
    return svc.create(payload)


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    svc = PetService(db)
    pet = svc.get_by_id(pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Το κατοικίδιο δεν βρέθηκε")
    return pet


@router.get("/owner/{owner_id}", response_model=list[PetResponse])
def get_pets_by_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Pet]:
    svc = PetService(db)
    return svc.get_by_owner(owner_id)


@router.get("/microchip/{number}", response_model=PetResponse)
def get_pet_by_microchip(
    number: str,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    svc = PetService(db)
    pet = svc.get_by_microchip(number)
    if pet is None:
        raise HTTPException(status_code=404, detail="Το κατοικίδιο δεν βρέθηκε")
    return pet


@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: int,
    payload: PetCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    svc = PetService(db)
    pet = svc.get_by_id(pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Το κατοικίδιο δεν βρέθηκε")
    return svc.update(pet, payload)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    svc = PetService(db)
    pet = svc.get_by_id(pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Το κατοικίδιο δεν βρέθηκε")
    svc.delete(pet)
