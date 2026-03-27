"""Comprehensive tests for the VetPro FastAPI backend."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx import BasicAuth

from app.main import app
from app.models import Role
from app.security import get_password_hash

# ---------------------------------------------------------------------------
# Test client (DB setup handled by conftest.py)
# ---------------------------------------------------------------------------

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_user_in_db(
    username: str,
    password: str,
    role: Role,
    *,
    full_name: str = "Test User",
    email: str | None = None,
    enabled: bool = True,
) -> dict:
    """Insert a user with a hashed password directly via the API and return the response body."""
    email = email or f"{username}@vetpro.test"
    resp = client.post(
        "/api/users/",
        json={
            "username": username,
            "password": password,
            "full_name": full_name,
            "email": email,
            "role": role.value,
            "enabled": enabled,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _admin_auth() -> BasicAuth:
    """Create an admin user and return BasicAuth credentials."""
    _create_user_in_db("admin_user", "adminpass", Role.ADMIN, email="admin@vetpro.test")
    return BasicAuth("admin_user", "adminpass")


def _vet_auth(suffix: str = "") -> tuple[BasicAuth, dict]:
    """Create a vet user and return (BasicAuth, user_data)."""
    uname = f"vet_user{suffix}"
    data = _create_user_in_db(uname, "vetpass", Role.VET, email=f"{uname}@vetpro.test")
    return BasicAuth(uname, "vetpass"), data


def _owner_auth(suffix: str = "") -> tuple[BasicAuth, dict]:
    """Create an owner user and return (BasicAuth, user_data)."""
    uname = f"owner_user{suffix}"
    data = _create_user_in_db(uname, "ownerpass", Role.OWNER, email=f"{uname}@vetpro.test")
    return BasicAuth(uname, "ownerpass"), data


def _create_pet(owner_id: int | None = None, **overrides) -> dict:
    defaults = {
        "name": "Buddy",
        "species": "Dog",
        "breed": "Labrador",
        "date_of_birth": "2020-01-15",
        "gender": "Male",
        "microchip_number": None,
        "owner_id": owner_id,
    }
    defaults.update(overrides)
    resp = client.post("/api/pets/", json=defaults)
    assert resp.status_code == 201
    return resp.json()


def _create_appointment(pet_id: int, vet_id: int, auth: BasicAuth, **overrides) -> dict:
    defaults = {
        "pet_id": pet_id,
        "veterinarian_id": vet_id,
        "date_time": datetime.now().isoformat(),
        "reason": "Checkup",
        "status": "SCHEDULED",
    }
    defaults.update(overrides)
    resp = client.post("/api/appointments/", json=defaults, auth=auth)
    assert resp.status_code == 201
    return resp.json()


def _create_medical_record(pet_id: int, vet_id: int, auth: BasicAuth, **overrides) -> dict:
    defaults = {
        "pet_id": pet_id,
        "veterinarian_id": vet_id,
        "date": datetime.now().isoformat(),
        "diagnosis": "Healthy",
        "treatment": "None needed",
    }
    defaults.update(overrides)
    resp = client.post("/api/medical-records/", json=defaults, auth=auth)
    assert resp.status_code == 201
    return resp.json()


def _create_vaccine(**overrides) -> dict:
    defaults = {"name": "Rabies", "manufacturer": "PetVax", "target_species": "Dog"}
    defaults.update(overrides)
    resp = client.post("/api/vaccines/", json=defaults)
    assert resp.status_code == 201
    return resp.json()


def _create_medication(auth: BasicAuth, **overrides) -> dict:
    defaults = {
        "name": "Amoxicillin",
        "description": "Antibiotic",
        "stock_quantity": 100,
        "unit_price": "12.50",
        "reorder_level": 10,
    }
    defaults.update(overrides)
    resp = client.post("/api/medications/", json=defaults, auth=auth)
    assert resp.status_code == 201
    return resp.json()


def _create_invoice(owner_id: int, **overrides) -> dict:
    defaults = {
        "owner_id": owner_id,
        "date_issued": datetime.now().isoformat(),
        "total_amount": "150.00",
        "paid": False,
        "description": "Consultation fee",
    }
    defaults.update(overrides)
    resp = client.post("/api/invoices/", json=defaults)
    assert resp.status_code == 201
    return resp.json()


# ===================================================================
# Test classes
# ===================================================================


class TestUsers:
    """User CRUD endpoints."""

    def test_create_user(self):
        resp = client.post(
            "/api/users/",
            json={
                "username": "john",
                "password": "secret",
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "555-0100",
                "role": "OWNER",
                "enabled": True,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "john"
        assert data["full_name"] == "John Doe"
        assert data["role"] == "OWNER"
        assert data["enabled"] is True
        assert "password" not in data

    def test_get_user(self):
        user = _create_user_in_db("alice", "pass", Role.VET)
        resp = client.get(f"/api/users/{user['id']}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "alice"

    def test_get_user_not_found(self):
        resp = client.get("/api/users/9999")
        assert resp.status_code == 404

    def test_get_users_by_role(self):
        _create_user_in_db("v1", "p", Role.VET, email="v1@test.com")
        _create_user_in_db("v2", "p", Role.VET, email="v2@test.com")
        _create_user_in_db("o1", "p", Role.OWNER, email="o1@test.com")
        resp = client.get("/api/users/role/VET")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_update_user(self):
        user = _create_user_in_db("bob", "pass", Role.OWNER)
        resp = client.put(
            f"/api/users/{user['id']}",
            json={
                "username": "bob_updated",
                "password": "newpass",
                "full_name": "Bob Updated",
                "email": "bob_updated@test.com",
                "role": "OWNER",
                "enabled": True,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == "bob_updated"
        assert resp.json()["full_name"] == "Bob Updated"

    def test_delete_user_requires_admin(self):
        auth = _admin_auth()
        target = _create_user_in_db("target", "p", Role.OWNER, email="target@test.com")
        resp = client.delete(f"/api/users/{target['id']}", auth=auth)
        assert resp.status_code == 204

        # Confirm deleted
        resp = client.get(f"/api/users/{target['id']}")
        assert resp.status_code == 404

    def test_delete_user_forbidden_for_non_admin(self):
        owner_auth, _ = _owner_auth()
        target = _create_user_in_db("target2", "p", Role.OWNER, email="target2@test.com")
        resp = client.delete(f"/api/users/{target['id']}", auth=owner_auth)
        assert resp.status_code == 403


class TestPets:
    """Pet CRUD endpoints."""

    def test_create_pet(self):
        owner = _create_user_in_db("pet_owner", "p", Role.OWNER)
        resp = client.post(
            "/api/pets/",
            json={
                "name": "Max",
                "species": "Dog",
                "breed": "Golden Retriever",
                "date_of_birth": "2019-06-01",
                "gender": "Male",
                "microchip_number": "MC-12345",
                "owner_id": owner["id"],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Max"
        assert data["owner_id"] == owner["id"]
        assert data["microchip_number"] == "MC-12345"

    def test_get_pet(self):
        pet = _create_pet()
        resp = client.get(f"/api/pets/{pet['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Buddy"

    def test_get_pet_not_found(self):
        resp = client.get("/api/pets/9999")
        assert resp.status_code == 404

    def test_get_pets_by_owner(self):
        owner = _create_user_in_db("multi_pet_owner", "p", Role.OWNER)
        _create_pet(owner["id"], name="Pet1", microchip_number="MC-001")
        _create_pet(owner["id"], name="Pet2", microchip_number="MC-002")
        resp = client.get(f"/api/pets/owner/{owner['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_microchip_lookup(self):
        _create_pet(microchip_number="CHIP-999")
        resp = client.get("/api/pets/microchip/CHIP-999")
        assert resp.status_code == 200
        assert resp.json()["microchip_number"] == "CHIP-999"

    def test_microchip_not_found(self):
        resp = client.get("/api/pets/microchip/NONEXISTENT")
        assert resp.status_code == 404

    def test_update_pet(self):
        pet = _create_pet()
        resp = client.put(
            f"/api/pets/{pet['id']}",
            json={
                "name": "Buddy Updated",
                "species": "Dog",
                "breed": "Poodle",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Buddy Updated"
        assert resp.json()["breed"] == "Poodle"

    def test_delete_pet(self):
        pet = _create_pet()
        resp = client.delete(f"/api/pets/{pet['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/api/pets/{pet['id']}")
        assert resp.status_code == 404


class TestAppointments:
    """Appointment endpoints."""

    def test_create_appointment(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        appt = _create_appointment(pet["id"], vet["id"], vet_auth)
        assert appt["status"] == "SCHEDULED"
        assert appt["pet_id"] == pet["id"]

    def test_create_appointment_unauthorized(self):
        """Unauthenticated request must fail."""
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date_time": datetime.now().isoformat(),
                "reason": "Checkup",
            },
        )
        assert resp.status_code == 401

    def test_get_appointment(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        appt = _create_appointment(pet["id"], vet["id"], vet_auth)
        resp = client.get(f"/api/appointments/{appt['id']}")
        assert resp.status_code == 200

    def test_get_appointments_by_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        _create_appointment(pet["id"], vet["id"], vet_auth)
        _create_appointment(pet["id"], vet["id"], vet_auth)
        resp = client.get(f"/api/appointments/pet/{pet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_appointments_by_vet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        _create_appointment(pet["id"], vet["id"], vet_auth)
        resp = client.get(f"/api/appointments/vet/{vet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_appointments_by_date_range(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        now = datetime.now()
        _create_appointment(
            pet["id"], vet["id"], vet_auth,
            date_time=(now - timedelta(days=1)).isoformat(),
        )
        _create_appointment(
            pet["id"], vet["id"], vet_auth,
            date_time=(now + timedelta(days=5)).isoformat(),
        )
        start = (now - timedelta(days=2)).isoformat()
        end = now.isoformat()
        resp = client.get(f"/api/appointments/range?start={start}&end={end}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_cancel_appointment(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        appt = _create_appointment(pet["id"], vet["id"], vet_auth)
        resp = client.put(f"/api/appointments/{appt['id']}/cancel")
        assert resp.status_code == 200
        assert resp.json()["status"] == "CANCELLED"

    def test_complete_appointment(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        appt = _create_appointment(pet["id"], vet["id"], vet_auth)
        resp = client.put(f"/api/appointments/{appt['id']}/complete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "COMPLETED"


class TestMedicalRecords:
    """Medical record endpoints."""

    def test_create_medical_record(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)
        assert record["diagnosis"] == "Healthy"
        assert record["pet_id"] == pet["id"]

    def test_create_medical_record_requires_vet(self):
        owner_auth, owner = _owner_auth()
        pet = _create_pet(owner["id"])
        resp = client.post(
            "/api/medical-records/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": owner["id"],
                "date": datetime.now().isoformat(),
                "diagnosis": "Sick",
            },
            auth=owner_auth,
        )
        assert resp.status_code == 403

    def test_get_medical_record(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)
        resp = client.get(f"/api/medical-records/{record['id']}")
        assert resp.status_code == 200

    def test_get_records_by_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        _create_medical_record(pet["id"], vet["id"], vet_auth)
        _create_medical_record(
            pet["id"], vet["id"], vet_auth,
            diagnosis="Ear infection", treatment="Antibiotics",
        )
        resp = client.get(f"/api/medical-records/pet/{pet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_records_by_vet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        _create_medical_record(pet["id"], vet["id"], vet_auth)
        resp = client.get(f"/api/medical-records/vet/{vet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestVaccines:
    """Vaccine endpoints."""

    def test_create_vaccine(self):
        vax = _create_vaccine()
        assert vax["name"] == "Rabies"
        assert vax["manufacturer"] == "PetVax"

    def test_list_vaccines(self):
        _create_vaccine(name="Rabies")
        _create_vaccine(name="Distemper", manufacturer="VaxCo", target_species="Dog")
        resp = client.get("/api/vaccines/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_vaccine_by_id(self):
        vax = _create_vaccine()
        resp = client.get(f"/api/vaccines/{vax['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Rabies"

    def test_get_vaccine_not_found(self):
        resp = client.get("/api/vaccines/9999")
        assert resp.status_code == 404


class TestVaccineRecords:
    """Vaccine record endpoints."""

    def test_create_vaccine_record(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        vax = _create_vaccine()
        today = date.today()
        resp = client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": pet["id"],
                "vaccine_id": vax["id"],
                "administered_by_id": vet["id"],
                "date_administered": today.isoformat(),
                "next_due_date": (today + timedelta(days=365)).isoformat(),
                "batch_number": "BATCH-001",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["pet_id"] == pet["id"]
        assert data["batch_number"] == "BATCH-001"

    def test_create_vaccine_record_requires_vet(self):
        owner_auth, owner = _owner_auth()
        resp = client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": 1,
                "vaccine_id": 1,
                "administered_by_id": owner["id"],
                "date_administered": date.today().isoformat(),
            },
            auth=owner_auth,
        )
        assert resp.status_code == 403

    def test_get_vaccine_records_by_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        vax = _create_vaccine()
        client.post(
            "/api/vaccine-records/",
            json={
                "pet_id": pet["id"],
                "vaccine_id": vax["id"],
                "administered_by_id": vet["id"],
                "date_administered": date.today().isoformat(),
            },
            auth=vet_auth,
        )
        resp = client.get(f"/api/vaccine-records/pet/{pet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestMedications:
    """Medication endpoints."""

    def test_create_medication(self):
        auth = _admin_auth()
        med = _create_medication(auth)
        assert med["name"] == "Amoxicillin"
        assert med["stock_quantity"] == 100

    def test_create_medication_requires_admin(self):
        vet_auth, _ = _vet_auth()
        resp = client.post(
            "/api/medications/",
            json={
                "name": "Ibuprofen",
                "stock_quantity": 50,
                "reorder_level": 10,
            },
            auth=vet_auth,
        )
        assert resp.status_code == 403

    def test_list_medications(self):
        auth = _admin_auth()
        _create_medication(auth, name="Med1")
        _create_medication(auth, name="Med2")
        resp = client.get("/api/medications/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_low_stock(self):
        auth = _admin_auth()
        _create_medication(auth, name="LowMed", stock_quantity=5, reorder_level=10)
        _create_medication(auth, name="OkMed", stock_quantity=50, reorder_level=10)
        resp = client.get("/api/medications/low-stock")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["name"] == "LowMed"

    def test_update_stock(self):
        auth = _admin_auth()
        med = _create_medication(auth)
        resp = client.put(
            f"/api/medications/{med['id']}/stock?quantity=200", auth=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["stock_quantity"] == 200

    def test_update_medication(self):
        auth = _admin_auth()
        med = _create_medication(auth)
        resp = client.put(
            f"/api/medications/{med['id']}",
            json={
                "name": "Amoxicillin Updated",
                "stock_quantity": 80,
                "reorder_level": 15,
            },
            auth=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Amoxicillin Updated"
        assert resp.json()["reorder_level"] == 15


class TestPrescriptions:
    """Prescription endpoints and stock decrement logic."""

    def test_create_prescription_decrements_stock(self):
        admin_auth = _admin_auth()
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        med = _create_medication(admin_auth, stock_quantity=10)
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)

        resp = client.post(
            "/api/prescriptions/",
            json={
                "medical_record_id": record["id"],
                "medication_id": med["id"],
                "dosage": "500mg",
                "frequency": "Twice daily",
                "duration_days": 7,
                "instructions": "Take with food",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201

        # Verify stock decremented
        med_resp = client.get(f"/api/medications/{med['id']}")
        assert med_resp.json()["stock_quantity"] == 9

    def test_prescription_out_of_stock(self):
        admin_auth = _admin_auth()
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        med = _create_medication(admin_auth, name="EmptyMed", stock_quantity=0)
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)

        resp = client.post(
            "/api/prescriptions/",
            json={
                "medical_record_id": record["id"],
                "medication_id": med["id"],
                "dosage": "500mg",
                "frequency": "Once daily",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 400

    def test_get_prescription(self):
        admin_auth = _admin_auth()
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        med = _create_medication(admin_auth, stock_quantity=10)
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)
        presc = client.post(
            "/api/prescriptions/",
            json={
                "medical_record_id": record["id"],
                "medication_id": med["id"],
                "dosage": "250mg",
                "frequency": "Once daily",
            },
            auth=vet_auth,
        ).json()

        resp = client.get(f"/api/prescriptions/{presc['id']}")
        assert resp.status_code == 200
        assert resp.json()["dosage"] == "250mg"

    def test_get_prescriptions_by_record(self):
        admin_auth = _admin_auth()
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        med = _create_medication(admin_auth, stock_quantity=50)
        record = _create_medical_record(pet["id"], vet["id"], vet_auth)
        for _ in range(3):
            client.post(
                "/api/prescriptions/",
                json={
                    "medical_record_id": record["id"],
                    "medication_id": med["id"],
                    "dosage": "100mg",
                    "frequency": "Daily",
                },
                auth=vet_auth,
            )
        resp = client.get(f"/api/prescriptions/record/{record['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_create_prescription_requires_vet(self):
        owner_auth, _ = _owner_auth()
        resp = client.post(
            "/api/prescriptions/",
            json={
                "medical_record_id": 1,
                "medication_id": 1,
                "dosage": "100mg",
                "frequency": "Daily",
            },
            auth=owner_auth,
        )
        assert resp.status_code == 403


class TestInvoicesAndPayments:
    """Invoice and payment endpoints with auto-paid logic."""

    def test_create_invoice(self):
        owner = _create_user_in_db("inv_owner", "p", Role.OWNER)
        inv = _create_invoice(owner["id"])
        assert inv["paid"] is False
        assert inv["owner_id"] == owner["id"]

    def test_get_invoice(self):
        owner = _create_user_in_db("inv_owner2", "p", Role.OWNER)
        inv = _create_invoice(owner["id"])
        resp = client.get(f"/api/invoices/{inv['id']}")
        assert resp.status_code == 200

    def test_get_invoices_by_owner(self):
        owner = _create_user_in_db("inv_owner3", "p", Role.OWNER)
        _create_invoice(owner["id"])
        _create_invoice(owner["id"], description="Second invoice")
        resp = client.get(f"/api/invoices/owner/{owner['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_unpaid_invoices(self):
        owner = _create_user_in_db("inv_owner4", "p", Role.OWNER)
        _create_invoice(owner["id"])
        _create_invoice(owner["id"], paid=True, description="Paid one")
        resp = client.get("/api/invoices/unpaid")
        assert resp.status_code == 200
        unpaid = resp.json()
        assert all(inv["paid"] is False for inv in unpaid)

    def test_mark_invoice_paid(self):
        owner = _create_user_in_db("inv_owner5", "p", Role.OWNER)
        inv = _create_invoice(owner["id"])
        resp = client.put(f"/api/invoices/{inv['id']}/pay")
        assert resp.status_code == 200
        assert resp.json()["paid"] is True

    def test_create_payment(self):
        owner = _create_user_in_db("pay_owner", "p", Role.OWNER)
        inv = _create_invoice(owner["id"], total_amount="200.00")
        resp = client.post(
            "/api/payments/",
            json={
                "invoice_id": inv["id"],
                "amount": "100.00",
                "payment_date": datetime.now().isoformat(),
                "method": "CASH",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["invoice_id"] == inv["id"]

    def test_payment_auto_marks_invoice_paid(self):
        owner = _create_user_in_db("pay_owner2", "p", Role.OWNER)
        inv = _create_invoice(owner["id"], total_amount="100.00")

        # Partial payment — not yet paid
        client.post(
            "/api/payments/",
            json={
                "invoice_id": inv["id"],
                "amount": "60.00",
                "payment_date": datetime.now().isoformat(),
                "method": "CARD",
            },
        )
        inv_resp = client.get(f"/api/invoices/{inv['id']}")
        assert inv_resp.json()["paid"] is False

        # Remaining payment covers total
        client.post(
            "/api/payments/",
            json={
                "invoice_id": inv["id"],
                "amount": "40.00",
                "payment_date": datetime.now().isoformat(),
                "method": "BANK_TRANSFER",
            },
        )
        inv_resp = client.get(f"/api/invoices/{inv['id']}")
        assert inv_resp.json()["paid"] is True

    def test_get_payments_by_invoice(self):
        owner = _create_user_in_db("pay_owner3", "p", Role.OWNER)
        inv = _create_invoice(owner["id"])
        for _ in range(2):
            client.post(
                "/api/payments/",
                json={
                    "invoice_id": inv["id"],
                    "amount": "50.00",
                    "payment_date": datetime.now().isoformat(),
                    "method": "CASH",
                },
            )
        resp = client.get(f"/api/payments/invoice/{inv['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestHospitalizations:
    """Hospitalization admit / discharge / current endpoints."""

    def test_admit_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        resp = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Surgery",
            },
            auth=vet_auth,
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "ADMITTED"

    def test_admit_requires_vet(self):
        owner_auth, owner = _owner_auth()
        resp = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": 1,
                "veterinarian_id": owner["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Observation",
            },
            auth=owner_auth,
        )
        assert resp.status_code == 403

    def test_discharge_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        hosp = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Surgery",
            },
            auth=vet_auth,
        ).json()

        resp = client.put(
            f"/api/hospitalizations/{hosp['id']}/discharge", auth=vet_auth,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "DISCHARGED"
        assert data["discharge_date"] is not None

    def test_get_current_hospitalizations(self):
        vet_auth, vet = _vet_auth()
        pet1 = _create_pet(name="Pet1", microchip_number="H-001")
        pet2 = _create_pet(name="Pet2", microchip_number="H-002")

        hosp1 = client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet1["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Reason A",
            },
            auth=vet_auth,
        ).json()
        client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet2["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Reason B",
            },
            auth=vet_auth,
        )
        # Discharge one
        client.put(
            f"/api/hospitalizations/{hosp1['id']}/discharge", auth=vet_auth,
        )

        resp = client.get("/api/hospitalizations/current")
        assert resp.status_code == 200
        current = resp.json()
        assert len(current) == 1
        assert current[0]["status"] == "ADMITTED"

    def test_get_hospitalizations_by_pet(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Check",
            },
            auth=vet_auth,
        )
        resp = client.get(f"/api/hospitalizations/pet/{pet['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_update_daily_notes(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
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

        resp = client.put(
            f"/api/hospitalizations/{hosp['id']}/notes",
            content='"Day 1: Stable condition"',
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        assert resp.json()["daily_notes"] == "Day 1: Stable condition"


class TestReminders:
    """Reminder endpoints."""

    def test_create_reminder(self):
        user = _create_user_in_db("rem_user", "p", Role.OWNER)
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        resp = client.post(
            "/api/reminders/",
            json={
                "user_id": user["id"],
                "message": "Vaccination due",
                "reminder_date": past,
                "sent": False,
                "type": "VACCINE",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["message"] == "Vaccination due"

    def test_get_reminders_by_user(self):
        user = _create_user_in_db("rem_user2", "p", Role.OWNER)
        for i in range(3):
            client.post(
                "/api/reminders/",
                json={
                    "user_id": user["id"],
                    "message": f"Reminder {i}",
                    "reminder_date": datetime.now().isoformat(),
                    "type": "GENERAL",
                },
            )
        resp = client.get(f"/api/reminders/user/{user['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_get_pending_reminders(self):
        user = _create_user_in_db("rem_user3", "p", Role.OWNER)
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        future = (datetime.now() + timedelta(days=5)).isoformat()

        # Past unsent — should appear as pending
        client.post(
            "/api/reminders/",
            json={
                "user_id": user["id"],
                "message": "Past reminder",
                "reminder_date": past,
                "type": "FOLLOWUP",
            },
        )
        # Future unsent — should not appear
        client.post(
            "/api/reminders/",
            json={
                "user_id": user["id"],
                "message": "Future reminder",
                "reminder_date": future,
                "type": "GENERAL",
            },
        )

        resp = client.get("/api/reminders/pending")
        assert resp.status_code == 200
        pending = resp.json()
        assert len(pending) == 1
        assert pending[0]["message"] == "Past reminder"

    def test_mark_reminder_as_sent(self):
        user = _create_user_in_db("rem_user4", "p", Role.OWNER)
        rem = client.post(
            "/api/reminders/",
            json={
                "user_id": user["id"],
                "message": "Send me",
                "reminder_date": datetime.now().isoformat(),
                "type": "APPOINTMENT",
            },
        ).json()

        resp = client.put(f"/api/reminders/{rem['id']}/sent")
        assert resp.status_code == 200
        assert resp.json()["sent"] is True


class TestReports:
    """Report endpoints (require ADMIN or VET role)."""

    def test_count_appointments(self):
        vet_auth, vet = _vet_auth()
        pet = _create_pet()
        now = datetime.now()
        _create_appointment(
            pet["id"], vet["id"], vet_auth,
            date_time=now.isoformat(),
        )
        _create_appointment(
            pet["id"], vet["id"], vet_auth,
            date_time=(now - timedelta(days=10)).isoformat(),
        )

        start = (now - timedelta(days=1)).isoformat()
        end = (now + timedelta(days=1)).isoformat()
        resp = client.get(
            f"/api/reports/appointments/count?start={start}&end={end}",
            auth=vet_auth,
        )
        assert resp.status_code == 200
        assert resp.json() == 1

    def test_revenue(self):
        auth = _admin_auth()
        owner = _create_user_in_db("rev_owner", "p", Role.OWNER, email="rev@test.com")
        now = datetime.now()
        _create_invoice(owner["id"], total_amount="200.00", paid=True,
                        date_issued=now.isoformat())
        _create_invoice(owner["id"], total_amount="300.00", paid=False,
                        date_issued=now.isoformat(), description="Unpaid")

        start = (now - timedelta(days=1)).isoformat()
        end = (now + timedelta(days=1)).isoformat()
        resp = client.get(
            f"/api/reports/revenue?start={start}&end={end}", auth=auth,
        )
        assert resp.status_code == 200
        # Only paid invoices count
        assert float(resp.json()) == pytest.approx(200.0)

    def test_low_stock_report(self):
        auth = _admin_auth()
        _create_medication(auth, name="Low1", stock_quantity=3, reorder_level=10)
        _create_medication(auth, name="Ok1", stock_quantity=100, reorder_level=10)
        resp = client.get("/api/reports/low-stock", auth=auth)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_hospitalized_report(self):
        vet_auth, vet = _vet_auth()
        # Also need the vet_auth to access the report endpoint (VET role)
        pet = _create_pet()
        client.post(
            "/api/hospitalizations/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "admission_date": datetime.now().isoformat(),
                "reason": "Surgery",
            },
            auth=vet_auth,
        )
        resp = client.get("/api/reports/hospitalized", auth=vet_auth)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_reports_require_admin_or_vet(self):
        owner_auth, _ = _owner_auth()
        now = datetime.now()
        start = (now - timedelta(days=1)).isoformat()
        end = (now + timedelta(days=1)).isoformat()
        resp = client.get(
            f"/api/reports/appointments/count?start={start}&end={end}",
            auth=owner_auth,
        )
        assert resp.status_code == 403

    def test_reports_require_auth(self):
        now = datetime.now()
        start = (now - timedelta(days=1)).isoformat()
        end = (now + timedelta(days=1)).isoformat()
        resp = client.get(
            f"/api/reports/appointments/count?start={start}&end={end}",
        )
        assert resp.status_code == 401


class TestSecurity:
    """Authentication and authorization edge cases."""

    def test_unauthenticated_access_to_protected_endpoint(self):
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date_time": datetime.now().isoformat(),
                "reason": "Test",
            },
        )
        assert resp.status_code == 401

    def test_wrong_password(self):
        _create_user_in_db("secuser", "correct", Role.VET)
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date_time": datetime.now().isoformat(),
                "reason": "Test",
            },
            auth=BasicAuth("secuser", "wrong"),
        )
        assert resp.status_code == 401

    def test_nonexistent_user(self):
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date_time": datetime.now().isoformat(),
                "reason": "Test",
            },
            auth=BasicAuth("ghost", "password"),
        )
        assert resp.status_code == 401

    def test_disabled_user_rejected(self):
        _create_user_in_db("disabled_vet", "pass", Role.VET, enabled=False)
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date_time": datetime.now().isoformat(),
                "reason": "Test",
            },
            auth=BasicAuth("disabled_vet", "pass"),
        )
        assert resp.status_code == 403

    def test_wrong_role_rejected(self):
        """Receptionist cannot create medical records (VET only)."""
        _create_user_in_db("recep", "pass", Role.RECEPTIONIST)
        resp = client.post(
            "/api/medical-records/",
            json={
                "pet_id": 1,
                "veterinarian_id": 1,
                "date": datetime.now().isoformat(),
                "diagnosis": "Test",
            },
            auth=BasicAuth("recep", "pass"),
        )
        assert resp.status_code == 403

    def test_admin_can_delete_user(self):
        auth = _admin_auth()
        target = _create_user_in_db("del_me", "p", Role.OWNER, email="del@test.com")
        resp = client.delete(f"/api/users/{target['id']}", auth=auth)
        assert resp.status_code == 204

    def test_owner_cannot_create_medication(self):
        owner_auth, _ = _owner_auth()
        resp = client.post(
            "/api/medications/",
            json={"name": "Aspirin", "stock_quantity": 50, "reorder_level": 10},
            auth=owner_auth,
        )
        assert resp.status_code == 403

    def test_receptionist_can_create_appointment(self):
        _create_user_in_db("recep2", "pass", Role.RECEPTIONIST, email="recep2@test.com")
        vet = _create_user_in_db("vet_for_recep", "p", Role.VET, email="vr@test.com")
        pet = _create_pet()
        resp = client.post(
            "/api/appointments/",
            json={
                "pet_id": pet["id"],
                "veterinarian_id": vet["id"],
                "date_time": datetime.now().isoformat(),
                "reason": "Routine",
            },
            auth=BasicAuth("recep2", "pass"),
        )
        assert resp.status_code == 201
