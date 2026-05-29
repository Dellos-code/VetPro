"""
UC8 – Προβολή Ειδοποιήσεων  |  Test Cases 


ΜΕΘΟΔΟΣ ΕΛΕΓΧΟΥ (Testing Method)
--------------------------------
Χρησιμοποιείται **Black-box Functional Testing** με δύο τεχνικές που
διδαχθήκαμε στο μάθημα:

  1. Κλάσεις Ισοδυναμίας (Equivalence Partitioning)
     Κάθε ροή του use case αντιστοιχεί σε μία κλάση ισοδυναμίας. Επιλέγεται
     ένα αντιπροσωπευτικό δεδομένο εισόδου ανά κλάση:
        - Ενεργές ειδοποιήσεις (κανονική αποστολή)   -> Basic Flow
        - Απενεργοποιημένες ειδοποιήσεις (profile only) -> Alt Flow 1
        - Αποτυχία αποστολής (σφάλμα)                 -> Alt Flow 2
        - Ακύρωση υπενθύμισης                         -> Alt Flow 3
        - Αλλαγή ημερομηνίας υπενθύμισης              -> Alt Flow 4

  2. Ανάλυση Οριακών Τιμών (Boundary Value Analysis)
     Στο Alt Flow 4 ελέγχεται η ακριβής οριακή τιμή του υπολογισμού της
     ημερομηνίας αποστολής: send_date == ημερομηνία_ενέργειας - 7 ημέρες.

ΠΙΝΑΚΑΣ ΔΕΔΟΜΕΝΩΝ ΕΛΕΓΧΟΥ (Test Data)
-------------------------------------
| Test                                | Είσοδος (Input)              | Αναμενόμενο Αποτέλεσμα           |
|-------------------------------------|------------------------------|---------------------------------|
| test_basic_flow                     | ραντεβού AP1 (εμβολ. +10 ημ.)| status "sent" -> "delivered"    |
| test_alt_flow_1_notifications_disab.| owner με email & sms = False | status "profile_only"           |
| test_alt_flow_2_send_failure        | προσομοίωση σφάλματος email  | status "failed" + εγγραφή στο   |
|                                     |                              | error_log                       |
| test_alt_flow_3_cancel_reminder     | ακύρωση notification         | status "cancelled"              |
| test_alt_flow_4_update_reminder_date| νέα ημ/νία ενέργειας +20 ημ. | send_date == νέα_ημ/νία - 7 ημ. |

ΑΠΟΤΕΛΕΣΜΑΤΑ (Results): 5/5 PASSED
=============================================================================
"""
from datetime import date, timedelta

from data_store import DataStore
from models.user import Owner
from models.animal import Animal
from models.appointment import Appointment
from models.notification import NotificationPreference
from services.notification_service import NotificationService


def _seed():
    store = DataStore()

    store.save_owner(Owner(
        id="O3", username="petowner", email="petowner@example.com",
        phone_number="6911111111", address="Πάτρα"
    ))
    store.save_animal(Animal(
        id="A2", name="Luna", species="Γάτα", breed="Siamese",
        age=2, weight=4.5, owner_id="O3"
    ))
    store.save_appointment(Appointment(
        id="AP1",
        appt_date=date.today() + timedelta(days=10),
        time="10:00",
        reason="Εμβολιασμός",
        status="scheduled",
        animal_id="A2",
        owner_id="O3",
    ))


def test_basic_flow():
    """
    Basic Flow: vet action → reminder created → notification sent → delivered.

    Κλάση Ισοδυναμίας : Ενεργές ειδοποιήσεις (κανονική αποστολή).
    Δεδομένα Εισόδου  : ραντεβού AP1 (Εμβολιασμός σε 10 ημέρες), owner O3.
    Αναμενόμενο       : δημιουργία notification, status "sent" (ή
                        "profile_only"), και μετά το mark_delivered -> "delivered".
    """
    DataStore.reset()
    _seed()
    svc = NotificationService()

    notification = svc.process_vet_action("AP1")
    assert notification is not None
    assert notification.owner_id == "O3"
    assert notification.status in ("sent", "profile_only")

    delivered = svc.mark_notification_delivered(notification.id)
    assert delivered
    stored = DataStore().get_notification(notification.id)
    assert stored.status == "delivered"

    print("UC8 Basic Flow: PASSED")


def test_alt_flow_1_notifications_disabled():
    """
    Alt Flow 1: owner disabled email/SMS → notification shown in profile only.

    Κλάση Ισοδυναμίας : Απενεργοποιημένες ειδοποιήσεις (email & sms = False).
    Δεδομένα Εισόδου  : owner O3 με NotificationPreference(email=False, sms=False).
    Αναμενόμενο       : status "profile_only" (εμφάνιση μόνο στο προφίλ, χωρίς
                        αποστολή email/SMS).
    """
    DataStore.reset()
    _seed()
    DataStore().save_notification_preference(
        NotificationPreference(owner_id="O3",
                               email_enabled=False,
                               sms_enabled=False)
    )

    notification = NotificationService().process_vet_action("AP1")
    assert notification is not None
    assert notification.status == "profile_only"

    print("UC8 Alt Flow 1 (Notifications Disabled): PASSED")


def test_alt_flow_2_send_failure():
    """
    Alt Flow 2: simulated send failure → notification marked failed, error logged.

    Κλάση Ισοδυναμίας : Αποτυχία αποστολής ειδοποίησης (σφάλμα).
    Δεδομένα Εισόδου  : notification σε κατάσταση "pending", κλήση
                        ErrorHandler.handle_error με μήνυμα "Λάθος email".
    Αναμενόμενο       : status "failed" και καταχώρηση του σφάλματος στο
                        error_log του DataStore.
    """
    DataStore.reset()
    _seed()

    from uc8_notifications.notification_dispatcher import NotificationDispatcher
    from uc8_notifications.error_handler import ErrorHandler
    from models.notification import Notification
    import uuid

    store = DataStore()
    notification = Notification(
        id=str(uuid.uuid4()),
        message="Test failure",
        send_date=date.today(),
        notification_type="test",
        status="pending",
        owner_id="O3",
    )
    store.save_notification(notification)

    # Manually invoke error path
    handler = ErrorHandler()
    handler.handle_error(notification, "Λάθος email")

    stored = store.get_notification(notification.id)
    assert stored.status == "failed"
    log = store.get_error_log()
    assert any(e["notification_id"] == notification.id for e in log)

    print("UC8 Alt Flow 2 (Send Failure): PASSED")


def test_alt_flow_3_cancel_reminder():
    """
    Alt Flow 3: appointment cancelled → linked reminder cancelled.

    Κλάση Ισοδυναμίας : Ακύρωση υπενθύμισης (το ραντεβού ακυρώνεται).
    Δεδομένα Εισόδου  : notification που δημιουργήθηκε από το ραντεβού AP1,
                        κλήση cancel_reminder_for_appointment.
    Αναμενόμενο       : status "cancelled".
    """
    DataStore.reset()
    _seed()
    svc = NotificationService()

    notification = svc.process_vet_action("AP1")
    assert notification is not None

    cancelled = svc.cancel_reminder_for_appointment(notification.id)
    assert cancelled
    assert DataStore().get_notification(notification.id).status == "cancelled"

    print("UC8 Alt Flow 3 (Cancel Reminder): PASSED")


def test_alt_flow_4_update_reminder_date():
    """
    Alt Flow 4: vet changes action date → reminder send-date shifts accordingly.

    Τεχνική: Ανάλυση Οριακών Τιμών (Boundary Value Analysis).
    Δεδομένα Εισόδου  : notification από AP1· νέα ημερομηνία ενέργειας =
                        σήμερα + 20 ημέρες.
    Αναμενόμενο       : η send_date αλλάζει και ισούται ΑΚΡΙΒΩΣ με
                        (νέα_ημερομηνία_ενέργειας - 7 ημέρες) — οριακή τιμή.
    """
    DataStore.reset()
    _seed()
    svc = NotificationService()

    notification = svc.process_vet_action("AP1")
    assert notification is not None
    original_send_date = DataStore().get_notification(notification.id).send_date

    new_action_date = date.today() + timedelta(days=20)
    updated = svc.update_reminder_date(notification.id, new_action_date)
    assert updated

    stored = DataStore().get_notification(notification.id)
    assert stored.send_date != original_send_date
    assert stored.send_date == new_action_date - timedelta(days=7)

    print("UC8 Alt Flow 4 (Update Reminder Date): PASSED")


if __name__ == "__main__":
    test_basic_flow()
    test_alt_flow_1_notifications_disabled()
    test_alt_flow_2_send_failure()
    test_alt_flow_3_cancel_reminder()
    test_alt_flow_4_update_reminder_date()
    print("\nAll UC8 tests PASSED")
