from __future__ import annotations

from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models import (
    Notification,
    NotificationType,
    VaccineRecord,
    Appointment,
    AppointmentStatus,
    User,
    Pet,
)
from app.schemas import NotificationCreate


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: NotificationCreate) -> Notification:
        notification = Notification.model_validate(data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: int) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def get_by_user(self, user_id: int) -> list[Notification]:
        return list(
            self.db.exec(
                select(Notification).where(Notification.user_id == user_id)
            ).all()
        )

    def get_pending(self) -> list[Notification]:
        """Εκκρεμείς ειδοποιήσεις — unsent notifications whose scheduled date has passed."""
        now = datetime.utcnow()
        return list(
            self.db.exec(
                select(Notification).where(
                    Notification.sent == False,  # noqa: E712
                    Notification.scheduled_date <= now,
                )
            ).all()
        )

    def mark_sent(self, notification_id: int) -> Notification | None:
        notification = self.db.get(Notification, notification_id)
        if notification:
            notification.sent = True
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def generate_vaccine_reminders(self) -> list[Notification]:
        """UC8 — Δημιουργία ειδοποιήσεων εμβολιασμού 7 ημέρες και 1 ημέρα πριν."""
        today = datetime.utcnow().date()
        seven_days = today + timedelta(days=7)
        one_day = today + timedelta(days=1)

        records = self.db.exec(
            select(VaccineRecord).where(
                VaccineRecord.next_due_date != None,  # noqa: E711
            )
        ).all()

        created = []
        for record in records:
            if record.next_due_date is None:
                continue

            pet = self.db.get(Pet, record.pet_id)
            if pet is None or pet.owner_id is None:
                continue

            for target_date, label in [
                (seven_days, "7 ημέρες πριν"),
                (one_day, "1 ημέρα πριν"),
            ]:
                if record.next_due_date == target_date:
                    # Έλεγχος αν υπάρχει ήδη
                    existing = self.db.exec(
                        select(Notification).where(
                            Notification.related_entity_type == "vaccine_record",
                            Notification.related_entity_id == record.id,
                            Notification.scheduled_date == datetime.combine(
                                target_date, datetime.min.time()
                            ),
                        )
                    ).first()
                    if existing:
                        continue

                    notif = Notification(
                        user_id=pet.owner_id,
                        message=(
                            f"Υπενθύμιση εμβολιασμού ({label}): "
                            f"Το ζώο {pet.name} έχει προγραμματισμένο "
                            f"εμβολιασμό στις {record.next_due_date}"
                        ),
                        notification_type=NotificationType.VACCINE_REMINDER,
                        scheduled_date=datetime.combine(
                            today, datetime.min.time()
                        ),
                        related_entity_type="vaccine_record",
                        related_entity_id=record.id,
                    )
                    self.db.add(notif)
                    created.append(notif)

        if created:
            self.db.commit()
            for n in created:
                self.db.refresh(n)
        return created

    def generate_appointment_reminders(self) -> list[Notification]:
        """UC8 — Δημιουργία ειδοποιήσεων ραντεβού 7 ημέρες και 1 ημέρα πριν."""
        today = datetime.utcnow().date()
        seven_days = today + timedelta(days=7)
        one_day = today + timedelta(days=1)

        appointments = self.db.exec(
            select(Appointment).where(
                Appointment.status == AppointmentStatus.SCHEDULED,
            )
        ).all()

        created = []
        for appt in appointments:
            appt_date = appt.date_time.date()
            pet = self.db.get(Pet, appt.pet_id)
            if pet is None or pet.owner_id is None:
                continue

            for target_date, label in [
                (seven_days, "7 ημέρες πριν"),
                (one_day, "1 ημέρα πριν"),
            ]:
                if appt_date == target_date:
                    existing = self.db.exec(
                        select(Notification).where(
                            Notification.related_entity_type == "appointment",
                            Notification.related_entity_id == appt.id,
                            Notification.scheduled_date == datetime.combine(
                                today, datetime.min.time()
                            ),
                        )
                    ).first()
                    if existing:
                        continue

                    notif = Notification(
                        user_id=pet.owner_id,
                        message=(
                            f"Υπενθύμιση ραντεβού ({label}): "
                            f"Το ζώο {pet.name} έχει ραντεβού "
                            f"στις {appt.date_time}"
                        ),
                        notification_type=NotificationType.APPOINTMENT_REMINDER,
                        scheduled_date=datetime.combine(
                            today, datetime.min.time()
                        ),
                        related_entity_type="appointment",
                        related_entity_id=appt.id,
                    )
                    self.db.add(notif)
                    created.append(notif)

        if created:
            self.db.commit()
            for n in created:
                self.db.refresh(n)
        return created
