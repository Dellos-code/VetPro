from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User
from app.schemas import UserCreate, UserResponse
from app.security import get_password_hash, require_role

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = User(
        username=payload.username,
        password=get_password_hash(payload.password),
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        enabled=payload.enabled,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/role/{role}", response_model=list[UserResponse])
def get_users_by_role(
    role: Role,
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    return db.query(User).filter(User.role == role).all()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = payload.username
    user.password = get_password_hash(payload.password)
    user.full_name = payload.full_name
    user.email = payload.email
    user.phone = payload.phone
    user.role = payload.role
    user.enabled = payload.enabled
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
