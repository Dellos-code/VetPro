from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Reminder
from app.schemas import ReminderCreate, ReminderResponse

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Reminder:
    reminder = Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/user/{user_id}", response_model=list[ReminderResponse])
def get_reminders_by_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Reminder]:
    return db.query(Reminder).filter(Reminder.user_id == user_id).all()


@router.get("/pending", response_model=list[ReminderResponse])
def get_pending_reminders(
    db: Annotated[Session, Depends(get_db)],
) -> list[Reminder]:
    return (
        db.query(Reminder)
        .filter(Reminder.sent == False, Reminder.reminder_date < datetime.now())  # noqa: E712
        .all()
    )


@router.put("/{reminder_id}/sent", response_model=ReminderResponse)
def mark_as_sent(
    reminder_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Reminder:
    reminder = db.get(Reminder, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.sent = True
    db.commit()
    db.refresh(reminder)
    return reminder
