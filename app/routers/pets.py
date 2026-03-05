from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pet
from app.schemas import PetCreate, PetResponse

router = APIRouter(prefix="/api/pets", tags=["pets"])


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    payload: PetCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    pet = Pet(**payload.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    pet = db.get(Pet, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.get("/owner/{owner_id}", response_model=list[PetResponse])
def get_pets_by_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Pet]:
    return db.query(Pet).filter(Pet.owner_id == owner_id).all()


@router.get("/microchip/{number}", response_model=PetResponse)
def get_pet_by_microchip(
    number: str,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    pet = db.query(Pet).filter(Pet.microchip_number == number).first()
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: int,
    payload: PetCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Pet:
    pet = db.get(Pet, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    for key, value in payload.model_dump().items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    pet = db.get(Pet, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    db.delete(pet)
    db.commit()
