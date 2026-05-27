from datetime import date
from typing import Optional

from models.notification import Notification
from data_store import DataStore
from uc8_notifications.process_initiator import ProcessInitiator
from uc8_notifications.reminder_manager import ReminderManager
from uc8_notifications.preference_checker import PreferenceChecker
from uc8_notifications.notification_dispatcher import NotificationDispatcher
from uc8_notifications.status_updater import StatusUpdater
from uc8_notifications.error_handler import ErrorHandler
from uc8_notifications.reminder_canceller import ReminderCanceller


class NotificationService:
    """
    Class Diagram v1.0 – Business Logic & Engines / NotificationService.

    Public API:
        checkPreferences(ownerId: String): Boolean
        sendNotification(notification: Notification): void

    Also exposes higher-level helpers that orchestrate the full UC8 flow.
    """

    def __init__(self):
        self._store = DataStore()
        self._initiator = ProcessInitiator()
        self._reminder_mgr = ReminderManager()
        self._pref_checker = PreferenceChecker()
        self._dispatcher = NotificationDispatcher()
        self._status_updater = StatusUpdater()
        self._error_handler = ErrorHandler()
        self._canceller = ReminderCanceller()

    # ── Class-diagram interface ───────────────────────────────────────────────

    def check_preferences(self, owner_id: str) -> bool:
        """Class Diagram: checkPreferences(ownerId: String): Boolean"""
        return self._pref_checker.get_user_preferences(owner_id).notifications_enabled

    def send_notification(self, notification: Notification) -> None:
        """
        Class Diagram: sendNotification(notification: Notification): void

        Basic Flow steps 3-4:
          - check preferences
          - dispatch via Email/SMS  or  show in profile only (Alt Flow 1)
          - on failure trigger ErrorHandler (Alt Flow 2)
        """
        pref = self._pref_checker.get_user_preferences(notification.owner_id)
        try:
            self._dispatcher.send_notification(notification, pref)
        except RuntimeError as exc:
            self._error_handler.handle_error(notification, str(exc))

    # ── UC8 orchestration helpers ─────────────────────────────────────────────

    def process_vet_action(self, appointment_id: str) -> Optional[Notification]:
        """
        Basic Flow steps 1-4:
          Vet registers action → ProcessInitiator → ReminderManager →
          PreferenceChecker → NotificationDispatcher
        """
        action = self._initiator.init_process(appointment_id)
        if action is None:
            return None

        notification = self._reminder_mgr.create_reminder(
            action_date=action["date"],
            action_type=action["type"],
            owner_id=action["owner_id"],
        )
        self.send_notification(notification)
        return notification

    def mark_notification_delivered(self, notification_id: str) -> bool:
        """Basic Flow steps 5-6: owner views notification → mark delivered."""
        return self._status_updater.mark_as_delivered(notification_id)

    def cancel_reminder_for_appointment(self, notification_id: str) -> bool:
        """Alt Flow 3: appointment cancelled → ReminderCanceller."""
        return self._canceller.cancel_reminder(notification_id)

    def update_reminder_date(self, notification_id: str,
                             new_action_date: date) -> bool:
        """Alt Flow 4: vet changes date → ReminderManager updates reminder."""
        return self._reminder_mgr.update_reminder(notification_id, new_action_date) is not None
