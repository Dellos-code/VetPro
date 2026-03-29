from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Notification, Role
from app.schemas import NotificationCreate, NotificationResponse
from app.security import require_role
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    payload: NotificationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Notification:
    """Δημιουργία ειδοποίησης."""
    svc = NotificationService(db)
    return svc.create(payload)


@router.get("/user/{user_id}", response_model=list[NotificationResponse])
def get_notifications_by_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    """Ειδοποιήσεις χρήστη."""
    svc = NotificationService(db)
    return svc.get_by_user(user_id)


@router.get("/pending", response_model=list[NotificationResponse])
def get_pending_notifications(
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    """Εκκρεμείς ειδοποιήσεις."""
    svc = NotificationService(db)
    return svc.get_pending()


@router.put("/{notification_id}/sent", response_model=NotificationResponse)
def mark_notification_sent(
    notification_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Notification:
    """Σήμανση ειδοποίησης ως σταλμένη."""
    svc = NotificationService(db)
    notif = svc.mark_sent(notification_id)
    if notif is None:
        raise HTTPException(
            status_code=404, detail="Η ειδοποίηση δεν βρέθηκε"
        )
    return notif


@router.post(
    "/generate/vaccines",
    response_model=list[NotificationResponse],
    dependencies=[Depends(require_role(Role.ADMIN, Role.VET, Role.RECEPTIONIST))],
)
def generate_vaccine_reminders(
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    """UC8 — Δημιουργία ειδοποιήσεων εμβολιασμού (7 ημέρες & 1 ημέρα πριν)."""
    svc = NotificationService(db)
    return svc.generate_vaccine_reminders()


@router.post(
    "/generate/appointments",
    response_model=list[NotificationResponse],
    dependencies=[Depends(require_role(Role.ADMIN, Role.VET, Role.RECEPTIONIST))],
)
def generate_appointment_reminders(
    db: Annotated[Session, Depends(get_db)],
) -> list[Notification]:
    """UC8 — Δημιουργία ειδοποιήσεων ραντεβού (7 ημέρες & 1 ημέρα πριν)."""
    svc = NotificationService(db)
    return svc.generate_appointment_reminders()
