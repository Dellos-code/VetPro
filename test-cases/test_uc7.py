"""

UC7 – Προβολή Προφίλ Ιδιοκτήτη  |  Test Cases 


ΜΕΘΟΔΟΣ ΕΛΕΓΧΟΥ (Testing Method)
--------------------------------
Χρησιμοποιείται **Black-box Functional Testing** με δύο τεχνικές:

  1. Κλάσεις Ισοδυναμίας (Equivalence Partitioning)
     Κάθε ροή του use case αντιστοιχεί σε μία κλάση ισοδυναμίας. Επιλέγεται
     ένα αντιπροσωπευτικό δεδομένο εισόδου ανά κλάση:
        - Έγκυρος ιδιοκτήτης ΜΕ κατοικίδια         -> Basic Flow
        - Ιδιοκτήτης ΧΩΡΙΣ κατοικίδια              -> Alt Flow 1
        - Μη εξουσιοδοτημένος ιδιοκτήτης            -> Alt Flow 2
        - Ανύπαρκτος ιδιοκτήτης (αποτυχία φόρτωσης) -> Alt Flow 3

  2. Έλεγχος Πρόσβασης / Φιλτράρισμα (Decision logic)
     Στο Basic Flow ελέγχεται ότι εμφανίζεται ΜΟΝΟ το εγκεκριμένο έγγραφο
     (is_approved=True) και αποκλείεται το μη εγκεκριμένο (is_approved=False).

ΠΙΝΑΚΑΣ ΔΕΔΟΜΕΝΩΝ ΕΛΕΓΧΟΥ (Test Data)
-------------------------------------
| Test                          | Είσοδος (Input)               | Αναμενόμενο Αποτέλεσμα            |
|-------------------------------|-------------------------------|----------------------------------|
| test_basic_flow               | owner O1, 1 ζώο, 1 εγκεκρ. +   | success, 1 ζώο, 1 ιατρ. αρχείο,  |
|                               | 1 μη-εγκεκρ. έγγραφο           | μόνο 1 (εγκεκριμένο) έγγραφο      |
| test_alt_flow_1_no_pets       | owner O2 χωρίς ζώα             | fail: "Δεν υπάρχουν καταχωρημένα  |
|                               |                               | ζώα"                             |
| test_alt_flow_2_access_denied | owner O2 ζητά ζώο A1 (του O1)  | fail: "Δεν έχετε πρόσβαση"        |
| test_alt_flow_3_load_failure  | owner ID "NONEXISTENT"        | fail: "Η φόρτωση απέτυχε"         |

ΑΠΟΤΕΛΕΣΜΑΤΑ (Results): 4/4 PASSED
=============================================================================
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
    """
    Basic Flow: owner selects profile → picks pet → views full details.

    Κλάση Ισοδυναμίας : Έγκυρος ιδιοκτήτης ΜΕ καταχωρημένα κατοικίδια.
    Δεδομένα Εισόδου  : owner O1, ζώο A1 (Max), 1 ιατρικό αρχείο,
                        1 εγκεκριμένο (D1) + 1 μη-εγκεκριμένο (D2) έγγραφο.
    Αναμενόμενο       : success· επιστρέφεται 1 ζώο, 1 ιατρικό αρχείο και
                        ΜΟΝΟ το εγκεκριμένο έγγραφο (D1).
    """
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
    """
    Alt Flow 1: owner has no registered pets.

    Κλάση Ισοδυναμίας : Έγκυρος ιδιοκτήτης ΧΩΡΙΣ καταχωρημένα κατοικίδια.
    Δεδομένα Εισόδου  : owner O2, 0 ζώα.
    Αναμενόμενο       : fail με μήνυμα "Δεν υπάρχουν καταχωρημένα ζώα".
    """
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
    """
    Alt Flow 2: owner tries to view a pet that belongs to someone else.

    Κλάση Ισοδυναμίας : Μη εξουσιοδοτημένος ιδιοκτήτης (έλεγχος δικαιωμάτων).
    Δεδομένα Εισόδου  : owner O2 ζητά πρόσβαση στο ζώο A1 που ανήκει στον O1.
    Αναμενόμενο       : fail με μήνυμα "Δεν έχετε πρόσβαση".
    """
    DataStore.reset()
    _seed()
    # Owner O2 has no rights to animal A1 (which belongs to O1)
    result = OwnerProfileFlow().select_pet("O2", "A1")
    assert not result.success
    assert "Δεν έχετε πρόσβαση" in result.error_message

    print("UC7 Alt Flow 2 (Access Denied): PASSED")


def test_alt_flow_3_load_failure():
    """
    Alt Flow 3: owner record cannot be retrieved (not found).

    Κλάση Ισοδυναμίας : Ανύπαρκτος ιδιοκτήτης (αποτυχία φόρτωσης δεδομένων).
    Δεδομένα Εισόδου  : owner ID "NONEXISTENT" που δεν υπάρχει στο store.
    Αναμενόμενο       : fail με μήνυμα "Η φόρτωση απέτυχε".
    """
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
