from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Reminder
from app.schemas import ReminderCreate, ReminderResponse
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Reminder:
    svc = ReminderService(db)
    return svc.create(payload)


@router.get("/user/{user_id}", response_model=list[ReminderResponse])
def get_reminders_by_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Reminder]:
    svc = ReminderService(db)
    return svc.get_by_user(user_id)


@router.get("/pending", response_model=list[ReminderResponse])
def get_pending_reminders(
    db: Annotated[Session, Depends(get_db)],
) -> list[Reminder]:
    svc = ReminderService(db)
    return svc.get_pending()


@router.put("/{reminder_id}/sent", response_model=ReminderResponse)
def mark_as_sent(
    reminder_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Reminder:
    svc = ReminderService(db)
    reminder = svc.get_by_id(reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Η υπενθύμιση δεν βρέθηκε")
    return svc.mark_sent(reminder)
