"""Tests for new Use Case features: UC1-UC10."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx import BasicAuth

from app.main import app
from app.models import Role

# ---------------------------------------------------------------------------
# Test client (DB setup handled by conftest.py)
# ---------------------------------------------------------------------------

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_user(username: str, password: str, role: Role, **kw) -> dict:
    email = kw.pop("email", f"{username}@vetpro.test")
    resp = client.post(
        "/api/users/",
        json={
            "username": username,
            "password": password,
            "full_name": kw.get("full_name", "Test User"),
            "email": email,
            "role": role.value,
            "enabled": True,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _vet_auth(suffix: str = "") -> tuple[BasicAuth, dict]:
    uname = f"vet{suffix}"
    data = _create_user(uname, "vetpass", Role.VET)
    return BasicAuth(uname, "vetpass"), data


def _admin_auth() -> BasicAuth:
    _create_user("admin", "adminpass", Role.ADMIN)
    return BasicAuth("admin", "adminpass")


def _owner_auth(suffix: str = "") -> tuple[BasicAuth, dict]:
    uname = f"owner{suffix}"
    data = _create_user(uname, "ownerpass", Role.OWNER)
    return BasicAuth(uname, "ownerpass"), data


def _receptionist_auth(suffix: str = "") -> tuple[BasicAuth, dict]:
    uname = f"receptionist{suffix}"
    data = _create_user(uname, "recpass", Role.RECEPTIONIST)
    return BasicAuth(uname, "recpass"), data


def _create_pet(owner_id: int | None = None, **overrides) -> dict:
    defaults = {
        "name": "Buddy",
        "species": "Dog",
        "breed": "Labrador",
        "date_of_birth": "2020-01-15",
        "gender": "Male",
        "owner_id": owner_id,
    }
    defaults.update(overrides)
    resp = client.post("/api/pets/", json=defaults)
    assert resp.status_code == 201
    return resp.json()


def _create_vaccine(auth: BasicAuth | None = None, **overrides) -> dict:
    defaults = {"name": "Rabies", "manufacturer": "PharmaVet", "target_species": "Dog"}
    defaults.update(overrides)
    resp = client.post("/api/vaccines/", json=defaults)
    assert resp.status_code == 201
    return resp.json()


def _create_medication(auth: BasicAuth, **overrides) -> dict:
    defaults = {
        "name": "Amoxicillin",
        "stock_quantity": 100,
        "unit_price": "5.50",
        "reorder_level": 10,
    }
    defaults.update(overrides)
    resp = client.post("/api/medications/", json=defaults, auth=auth)
    assert resp.status_code == 201
    return resp.json()


# ===========================================================================
# UC1: View Animal History
# ===========================================================================


class TestUC1AnimalHistory:
    def test_get_full_history(self):
        """UC1 — Πλήρες ιστορικό ζώου."""
        vet_auth, vet = _vet_auth("uc1")
        pet = _create_pet()

        # Ιατρικό αρχείο
        client.post(
            "/api/medical-records/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": datetime.now().isoformat(),
                "diagnosis": "Healthy",
            },
            auth=vet_auth,
        )

        # Εξέταση
        client.post(
            "/api/examinations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": datetime.now().isoformat(),
                "exam_type": "Blood Test",
                "findings": "Normal",
            },
            auth=vet_auth,
        )

        resp = client.get(f"/api/animal-history/{pet['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pet"]["id"] == pet["id"]
        assert len(data["medical_records"]) == 1
        assert len(data["examinations"]) == 1

    def test_history_not_found(self):
        """UC1 alt flow — Ζώο δεν βρέθηκε."""
        resp = client.get("/api/animal-history/9999")
        assert resp.status_code == 404

    def test_empty_history(self):
        """UC1 alt flow — Κενό ιστορικό."""
        pet = _create_pet(name="Empty", microchip_number="CHIP001")
        resp = client.get(f"/api/animal-history/{pet['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["medical_records"]) == 0
        assert len(data["vaccine_records"]) == 0
        assert len(data["examinations"]) == 0

    def test_search_by_name_multiple_results(self):
        """UC1 alt flow — Πολλαπλά αποτελέσματα / συνώνυμα."""
        _create_pet(name="Max", microchip_number="S1")
        _create_pet(name="Max Jr", microchip_number="S2")
        resp = client.get("/api/animal-history/search/", params={"name": "Max"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 2


# ===========================================================================
# UC2: Payments / Billing
# ===========================================================================


class TestUC2PaymentsBilling:
    def test_partial_payment_creates_debt(self):
        """UC2 — Μερική πληρωμή δημιουργεί χρέος στο προφίλ ιδιοκτήτη."""
        _, owner = _owner_auth("uc2")

        # Τιμολόγιο 100€
        inv_resp = client.post(
            "/api/invoices/",
            json={
                "owner_id": owner["id"],
                "date_issued": datetime.now().isoformat(),
                "total_amount": "100.00",
            },
        )
        assert inv_resp.status_code == 201
        inv = inv_resp.json()
        assert inv["remaining_amount"] == "100.00"

        # Πληρωμή 40€ (μερική)
        pay_resp = client.post(
            "/api/payments/",
            json={
                "invoice_id": inv["id"],
                "amount": "40.00",
                "payment_date": datetime.now().isoformat(),
                "method": "CASH",
            },
        )
        assert pay_resp.status_code == 201

        # Έλεγχος ότι δεν είναι πληρωμένο
        inv_check = client.get(f"/api/invoices/{inv['id']}")
        assert inv_check.json()["paid"] is False

    def test_full_payment_marks_paid(self):
        """UC2 — Πλήρης πληρωμή."""
        _, owner = _owner_auth("uc2b")

        inv = client.post(
            "/api/invoices/",
            json={
                "owner_id": owner["id"],
                "date_issued": datetime.now().isoformat(),
                "total_amount": "50.00",
            },
        ).json()

        client.post(
            "/api/payments/",
            json={
                "invoice_id": inv["id"],
                "amount": "50.00",
                "payment_date": datetime.now().isoformat(),
                "method": "CARD",
            },
        )

        inv_check = client.get(f"/api/invoices/{inv['id']}")
        assert inv_check.json()["paid"] is True


# ===========================================================================
# UC3: Manage Vaccinations
# ===========================================================================


class TestUC3Vaccinations:
    def test_auto_next_due_date(self):
        """UC3 — Αυτόματος υπολογισμός επόμενης δόσης."""
        vet_auth, vet = _vet_auth("uc3")
        pet = _create_pet(microchip_number="VC1")
        vaccine = _create_vaccine(
            name="Rabies UC3",
            default_interval_days=365,
        )

        resp = client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": pet["id"],
                "vaccine_id": vaccine["id"],
                "administered_by_id": vet["id"],
                "date_administered": "2025-01-15",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["next_due_date"] == "2026-01-15"

    def test_allergy_check_no_reaction(self):
        """UC3 — Έλεγχος αλλεργίας χωρίς παρενέργειες."""
        _vet_auth("uc3b")
        pet = _create_pet(name="Safe Pet", microchip_number="VC2")
        vaccine = _create_vaccine(name="Parvo UC3")

        resp = client.get(
            f"/api/vaccine-records/allergy-check/{pet['id']}/{vaccine['id']}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_previous_reaction"] is False
        assert data["warning_message"] is None

    def test_record_side_effect_and_allergy_check(self):
        """UC3 — Καταγραφή παρενέργειας & έλεγχος αλλεργίας."""
        vet_auth, vet = _vet_auth("uc3c")
        pet = _create_pet(name="Allergy Pet", microchip_number="VC3")
        vaccine = _create_vaccine(name="Lepto UC3")

        # Χορήγηση εμβολίου
        vr = client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": pet["id"],
                "vaccine_id": vaccine["id"],
                "administered_by_id": vet["id"],
                "date_administered": "2025-06-01",
            },
            auth=vet_auth,
        ).json()

        # Καταγραφή παρενέργειας
        se_resp = client.post(
            f"/api/vaccine-records/{vr['id']}/side-effects",
            json={
                "vaccine_record_id": vr["id"],
                "description": "Skin rash",
                "severity": "MODERATE",
                "date_observed": "2025-06-02",
            },
            auth=vet_auth,
        )
        assert se_resp.status_code == 201

        # Τώρα ο έλεγχος αλλεργίας πρέπει να επιστρέψει προειδοποίηση
        allergy = client.get(
            f"/api/vaccine-records/allergy-check/{pet['id']}/{vaccine['id']}"
        )
        data = allergy.json()
        assert data["has_previous_reaction"] is True
        assert data["warning_message"] is not None
        assert len(data["previous_side_effects"]) == 1

    def test_get_side_effects_for_record(self):
        """UC3 — Λίστα παρενεργειών εμβολιασμού."""
        vet_auth, vet = _vet_auth("uc3d")
        pet = _create_pet(name="SE Pet", microchip_number="VC4")
        vaccine = _create_vaccine(name="DHPPi UC3")

        vr = client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": pet["id"],
                "vaccine_id": vaccine["id"],
                "administered_by_id": vet["id"],
                "date_administered": "2025-03-01",
            },
            auth=vet_auth,
        ).json()

        client.post(
            f"/api/vaccine-records/{vr['id']}/side-effects",
            json={
                "vaccine_record_id": vr["id"],
                "description": "Lethargy",
                "severity": "MILD",
                "date_observed": "2025-03-02",
            },
            auth=vet_auth,
        )

        resp = client.get(f"/api/vaccine-records/{vr['id']}/side-effects")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ===========================================================================
# UC4: Manage Hospitalization
# ===========================================================================


class TestUC4Hospitalization:
    def test_daily_log(self):
        """UC4 — Ημερήσια καταγραφή (θερμοκρασία, διατροφή, φαρμακευτική αγωγή)."""
        vet_auth, vet = _vet_auth("uc4")
        pet = _create_pet(name="Hosp Pet", microchip_number="H1")

        hosp = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Surgery recovery",
            },
            auth=vet_auth,
        ).json()

        # Προσθήκη ημερήσιας καταγραφής
        log_resp = client.post(
            f"/api/hospitalizations/{hosp['id']}/logs",
            json={
                "hospitalization_id": hosp["id"],
                "date": datetime.now().isoformat(),
                "temperature": 38.5,
                "diet": "Soft food",
                "medications_given": "Amoxicillin 250mg",
                "observations": "Stable condition",
            },
            auth=vet_auth,
        )
        assert log_resp.status_code == 201
        log_data = log_resp.json()
        assert log_data["temperature"] == 38.5
        assert log_data["diet"] == "Soft food"

        # Λίστα καταγραφών
        logs = client.get(f"/api/hospitalizations/{hosp['id']}/logs")
        assert len(logs.json()) == 1

    def test_discharge_with_instructions(self):
        """UC4 — Εξιτήριο με οδηγίες."""
        vet_auth, vet = _vet_auth("uc4b")
        pet = _create_pet(name="Discharge Pet", microchip_number="H2")

        hosp = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Observation",
            },
            auth=vet_auth,
        ).json()

        # Εξιτήριο με οδηγίες
        resp = client.put(
            f"/api/hospitalizations/{hosp['id']}/discharge",
            json="Rest for 3 days, soft diet only.",
            auth=vet_auth,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "DISCHARGED"
        assert data["discharge_instructions"] == "Rest for 3 days, soft diet only."


# ===========================================================================
# UC5: Prescribe Medication
# ===========================================================================


class TestUC5PrescribeMedication:
    def test_medication_not_found(self):
        """UC5 alt flow — Φάρμακο δεν βρέθηκε στον κατάλογο."""
        vet_auth, vet = _vet_auth("uc5")
        pet = _create_pet(name="Rx Pet", microchip_number="P1")

        # Ιατρικό αρχείο
        mr = client.post(
            "/api/medical-records/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": datetime.now().isoformat(),
                "diagnosis": "Infection",
            },
            auth=vet_auth,
        ).json()

        # Συνταγογράφηση ανύπαρκτου φαρμάκου
        resp = client.post(
            "/api/prescriptions/",
            json={
                "medical_record_id": mr["id"],
                "medication_id": 9999,
                "dosage": "250mg",
                "frequency": "Twice daily",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 404
        assert "κατάλογο" in resp.json()["detail"]


# ===========================================================================
# UC6: Generate Reports
# ===========================================================================


class TestUC6Reports:
    def test_generate_medical_history_report(self):
        """UC6 — Δημιουργία αναφοράς ιατρικού ιστορικού."""
        vet_auth, vet = _vet_auth("uc6")
        pet = _create_pet(name="Report Pet", microchip_number="R1")

        # Ιατρικό αρχείο
        client.post(
            "/api/medical-records/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": "2025-06-15T10:00:00",
                "diagnosis": "Healthy",
            },
            auth=vet_auth,
        )

        resp = client.post(
            f"/api/generated-reports/medical-history/{pet['id']}",
            params={"generated_by_id": vet["id"]},
            auth=vet_auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["report_type"] == "medical_history"
        assert data["pet_id"] == pet["id"]
        assert data["content"] is not None

    def test_report_with_date_filter(self):
        """UC6 — Αναφορά με φίλτρα ημερομηνιών."""
        vet_auth, vet = _vet_auth("uc6b")
        pet = _create_pet(name="Filter Pet", microchip_number="R2")

        client.post(
            "/api/medical-records/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": "2025-03-15T10:00:00",
                "diagnosis": "Cold",
            },
            auth=vet_auth,
        )

        resp = client.post(
            f"/api/generated-reports/medical-history/{pet['id']}",
            params={
                "generated_by_id": vet["id"],
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201

    def test_report_pet_not_found(self):
        """UC6 — Ζώο δεν βρέθηκε."""
        vet_auth, _ = _vet_auth("uc6c")
        resp = client.post(
            "/api/generated-reports/medical-history/9999",
            params={"generated_by_id": 1},
            auth=vet_auth,
        )
        assert resp.status_code == 404


# ===========================================================================
# UC7: Owner Profile
# ===========================================================================


class TestUC7OwnerProfile:
    def test_owner_profile_with_pets_and_debts(self):
        """UC7 — Προφίλ ιδιοκτήτη με κατοικίδια και χρέη."""
        _, owner = _owner_auth("uc7")
        pet = _create_pet(owner_id=owner["id"], name="Prof Pet", microchip_number="O1")

        # Τιμολόγιο ανεξόφλητο
        client.post(
            "/api/invoices/",
            json={
                "owner_id": owner["id"],
                "date_issued": datetime.now().isoformat(),
                "total_amount": "75.00",
            },
        )

        resp = client.get(f"/api/owner-profile/{owner['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["id"] == owner["id"]
        assert len(data["pets"]) == 1
        assert len(data["unpaid_invoices"]) == 1
        assert float(data["total_debt"]) > 0

    def test_owner_profile_not_found(self):
        """UC7 — Ιδιοκτήτης δεν βρέθηκε."""
        resp = client.get("/api/owner-profile/9999")
        assert resp.status_code == 404

    def test_non_owner_rejected(self):
        """UC7 — Μη ιδιοκτήτης."""
        vet_auth, vet = _vet_auth("uc7b")
        resp = client.get(f"/api/owner-profile/{vet['id']}")
        assert resp.status_code == 400


# ===========================================================================
# UC8: Notifications
# ===========================================================================


class TestUC8Notifications:
    def test_create_and_list_notifications(self):
        """UC8 — Δημιουργία και λίστα ειδοποιήσεων."""
        _, owner = _owner_auth("uc8")

        resp = client.post(
            "/api/notifications/",
            json={
                "user_id": owner["id"],
                "message": "Υπενθύμιση εμβολιασμού",
                "notification_type": "VACCINE_REMINDER",
                "scheduled_date": datetime.now().isoformat(),
            },
        )
        assert resp.status_code == 201

        notifs = client.get(f"/api/notifications/user/{owner['id']}")
        assert len(notifs.json()) == 1

    def test_mark_notification_sent(self):
        """UC8 — Σήμανση ειδοποίησης ως σταλμένη."""
        _, owner = _owner_auth("uc8b")

        notif = client.post(
            "/api/notifications/",
            json={
                "user_id": owner["id"],
                "message": "Test",
                "notification_type": "GENERAL",
                "scheduled_date": datetime.now().isoformat(),
            },
        ).json()

        resp = client.put(f"/api/notifications/{notif['id']}/sent")
        assert resp.status_code == 200
        assert resp.json()["sent"] is True

    def test_pending_notifications(self):
        """UC8 — Εκκρεμείς ειδοποιήσεις."""
        _, owner = _owner_auth("uc8c")

        # Ειδοποίηση στο παρελθόν
        client.post(
            "/api/notifications/",
            json={
                "user_id": owner["id"],
                "message": "Past notification",
                "notification_type": "GENERAL",
                "scheduled_date": (datetime.now() - timedelta(hours=1)).isoformat(),
            },
        )

        pending = client.get("/api/notifications/pending")
        assert len(pending.json()) >= 1


# ===========================================================================
# UC9: Appointment with priority (Heuristic Scheduler integration)
# ===========================================================================


class TestUC9AppointmentScheduling:
    def test_create_appointment_with_priority(self):
        """UC9 — Ραντεβού με προτεραιότητα."""
        vet_auth, vet = _vet_auth("uc9")
        pet = _create_pet(name="Urgent Pet", microchip_number="A1")

        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "reason": "Emergency",
                "status": "SCHEDULED",
                "priority": 5,
                "duration_minutes": 60,
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["priority"] == 5
        assert data["duration_minutes"] == 60


# ===========================================================================
# UC10: Inventory with forecasting fields
# ===========================================================================


class TestUC10Inventory:
    def test_medication_with_forecasting_fields(self):
        """UC10 — Φάρμακο με πεδία πρόβλεψης αποθέματος."""
        admin_auth = _admin_auth()

        resp = client.post(
            "/api/medications/",
            json={
                "name": "Forecast Med",
                "stock_quantity": 50,
                "unit_price": "10.00",
                "reorder_level": 20,
                "avg_daily_demand": 3.5,
                "lead_time_mean": 7.0,
                "lead_time_std": 2.0,
            },
            auth=admin_auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["avg_daily_demand"] == 3.5
        assert data["lead_time_mean"] == 7.0
        assert data["lead_time_std"] == 2.0


# ===========================================================================
# Examination CRUD
# ===========================================================================


class TestExaminations:
    def test_create_and_get_examination(self):
        vet_auth, vet = _vet_auth("exam1")
        pet = _create_pet(name="Exam Pet", microchip_number="E1")

        resp = client.post(
            "/api/examinations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date": datetime.now().isoformat(),
                "exam_type": "X-Ray",
                "findings": "No fractures",
                "recommendations": "Rest",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201
        exam_id = resp.json()["id"]

        get_resp = client.get(f"/api/examinations/{exam_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["exam_type"] == "X-Ray"

    def test_get_examinations_by_pet(self):
        vet_auth, vet = _vet_auth("exam2")
        pet = _create_pet(name="Multi Exam", microchip_number="E2")

        for t in ["Blood Test", "Ultrasound"]:
            client.post(
                "/api/examinations/",
                json={
                    "pet_id": pet["id"],
                    "veterinarian_id": vet["id"],
                    "date": datetime.now().isoformat(),
                    "exam_type": t,
                },
                auth=vet_auth,
            )

        resp = client.get(f"/api/examinations/pet/{pet['id']}")
        assert len(resp.json()) == 2

    def test_examination_not_found(self):
        resp = client.get("/api/examinations/9999")
        assert resp.status_code == 404
