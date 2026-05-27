"""
Tests for UC7 – Προβολή Προφίλ Ιδιοκτήτη
Covers Basic Flow + Alt Flows 1, 2, 3.
"""
from datetime import date

from data_store import DataStore
from models.user import Owner
from models.animal import Animal
from models.medical_record import MedicalRecord
from models.pet_document import PetDocument
from uc7_owner_profile.owner_profile_flow import OwnerProfileFlow


def _seed():
    """Load a minimal dataset used by the positive-path tests."""
    store = DataStore()

    store.save_owner(Owner(
        id="O1", username="konstantina", email="k@example.com",
        phone_number="6912345678", address="Πάτρα"
    ))

    store.save_animal(Animal(
        id="A1", name="Max", species="Σκύλος", breed="Labrador",
        age=3, weight=25.0, owner_id="O1"
    ))

    store.save_medical_record(MedicalRecord(
        id="MR1", record_date=date(2025, 3, 10),
        notes="Ετήσιος εμβολιασμός", animal_id="A1"
    ))

    store.save_pet_document(PetDocument(
        id="D1", title="Βιβλιάριο Max",
        file_path="/docs/max_passport.pdf",
        upload_date=date(2025, 1, 1), animal_id="A1", is_approved=True
    ))
    # Unapproved doc – must NOT be visible to owner
    store.save_pet_document(PetDocument(
        id="D2", title="Χειρουργείο",
        file_path="/docs/surgery.pdf",
        upload_date=date(2025, 4, 1), animal_id="A1", is_approved=False
    ))


def test_basic_flow():
    """Basic Flow: owner selects profile → picks pet → views full details."""
    DataStore.reset()
    _seed()
    flow = OwnerProfileFlow()

    # Step 1-3: load profile summary
    result = flow.select_profile("O1")
    assert result.success, result.error_message
    assert result.owner_data["username"] == "konstantina"
    assert len(result.pet_list) == 1
    assert result.pet_list[0].name == "Max"

    # Step 4-7: load pet profile
    pet_result = flow.select_pet("O1", "A1")
    assert pet_result.success, pet_result.error_message
    assert pet_result.pet_data.name == "Max"
    assert len(pet_result.medical_data) == 1
    assert pet_result.medical_data[0].notes == "Ετήσιος εμβολιασμός"
    # Only the approved document is returned
    assert len(pet_result.documents) == 1
    assert pet_result.documents[0].id == "D1"

    print("UC7 Basic Flow: PASSED")


def test_alt_flow_1_no_pets():
    """Alt Flow 1: owner has no registered pets."""
    DataStore.reset()
    store = DataStore()
    store.save_owner(Owner(
        id="O2", username="nopets", email="nopets@example.com",
        phone_number="6900000000", address="Αθήνα"
    ))

    result = OwnerProfileFlow().select_profile("O2")
    assert not result.success
    assert "Δεν υπάρχουν καταχωρημένα ζώα" in result.error_message

    print("UC7 Alt Flow 1 (No Pets): PASSED")


def test_alt_flow_2_access_denied():
    """Alt Flow 2: owner tries to view a pet that belongs to someone else."""
    DataStore.reset()
    _seed()
    # Owner O2 has no rights to animal A1 (which belongs to O1)
    result = OwnerProfileFlow().select_pet("O2", "A1")
    assert not result.success
    assert "Δεν έχετε πρόσβαση" in result.error_message

    print("UC7 Alt Flow 2 (Access Denied): PASSED")


def test_alt_flow_3_load_failure():
    """Alt Flow 3: owner record cannot be retrieved (not found)."""
    DataStore.reset()
    result = OwnerProfileFlow().select_profile("NONEXISTENT")
    assert not result.success
    assert "φόρτωση απέτυχε" in result.error_message

    print("UC7 Alt Flow 3 (Load Failure): PASSED")


if __name__ == "__main__":
    test_basic_flow()
    test_alt_flow_1_no_pets()
    test_alt_flow_2_access_denied()
    test_alt_flow_3_load_failure()
    print("\nAll UC7 tests PASSED")
