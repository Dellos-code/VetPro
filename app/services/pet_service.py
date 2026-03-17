from __future__ import annotations

from sqlmodel import Session, select

from app.models import Pet
from app.schemas import PetCreate


class PetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: PetCreate) -> Pet:
        pet = Pet(**payload.model_dump())
        self.db.add(pet)
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def get_by_id(self, pet_id: int) -> Pet | None:
        return self.db.get(Pet, pet_id)

    def get_by_owner(self, owner_id: int) -> list[Pet]:
        return list(
            self.db.exec(select(Pet).where(Pet.owner_id == owner_id)).all()
        )

    def get_by_microchip(self, number: str) -> Pet | None:
        return self.db.exec(
            select(Pet).where(Pet.microchip_number == number)
        ).first()

    def update(self, pet: Pet, payload: PetCreate) -> Pet:
        for key, value in payload.model_dump().items():
            setattr(pet, key, value)
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def delete(self, pet: Pet) -> None:
        self.db.delete(pet)
        self.db.commit()
