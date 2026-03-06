from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import Reminder
from app.schemas import ReminderCreate


class ReminderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ReminderCreate) -> Reminder:
        reminder = Reminder(**payload.model_dump())
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def get_by_user(self, user_id: int) -> list[Reminder]:
        return list(
            self.db.exec(
                select(Reminder).where(Reminder.user_id == user_id)
            ).all()
        )

    def get_pending(self) -> list[Reminder]:
        return list(
            self.db.exec(
                select(Reminder).where(
                    Reminder.sent == False,  # noqa: E712
                    Reminder.reminder_date < datetime.now(),
                )
            ).all()
        )

    def mark_sent(self, reminder: Reminder) -> Reminder:
        reminder.sent = True
        self.db.commit()
        self.db.refresh(reminder)
        return reminder
