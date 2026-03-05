from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBasic()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not user.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return user


def require_role(*roles: Role):
    """Return a dependency that checks the authenticated user has one of the given roles."""

    def _check(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check
