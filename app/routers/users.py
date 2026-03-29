from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Role, User
from app.schemas import UserCreate, UserResponse
from app.security import require_role
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    svc = UserService(db)
    return svc.create(payload)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    svc = UserService(db)
    user = svc.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε")
    return user


@router.get("/role/{role}", response_model=list[UserResponse])
def get_users_by_role(
    role: Role,
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    svc = UserService(db)
    return svc.get_by_role(role)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    svc = UserService(db)
    user = svc.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε")
    return svc.update(user, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    svc = UserService(db)
    user = svc.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε")
    svc.delete(user)
