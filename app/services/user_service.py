from __future__ import annotations

from sqlmodel import Session, select

from app.models import User
from app.schemas import UserCreate
from app.security import get_password_hash


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: UserCreate) -> User:
        user = User(
            username=payload.username,
            password=get_password_hash(payload.password),
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            role=payload.role,
            enabled=payload.enabled,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_role(self, role: str) -> list[User]:
        return list(self.db.exec(select(User).where(User.role == role)).all())

    def update(self, user: User, payload: UserCreate) -> User:
        user.username = payload.username
        user.password = get_password_hash(payload.password)
        user.full_name = payload.full_name
        user.email = payload.email
        user.phone = payload.phone
        user.role = payload.role
        user.enabled = payload.enabled
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
