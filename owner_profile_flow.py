from dataclasses import dataclass, field
from typing import Optional, List

from models.user import Owner
from models.animal import Animal
from models.medical_record import MedicalRecord
from models.pet_document import PetDocument
from data_store import DataStore
from uc7_owner_profile.owner_data_retriever import OwnerDataRetriever
from uc7_owner_profile.pet_checker import PetChecker
from uc7_owner_profile.access_checker import AccessChecker
from uc7_owner_profile.pet_data_retriever import PetDataRetriever


@dataclass
class ProfileSummaryResult:
    """Returned by select_profile() – mirrors the OwnerProfileScreen display."""
    success: bool
    owner_data: Optional[dict] = None
    pet_list: List[Animal] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class PetProfileResult:
    """Returned by select_pet() – mirrors the PetProfileScreen display."""
    success: bool
    pet_data: Optional[Animal] = None
    medical_data: List[MedicalRecord] = field(default_factory=list)
    documents: List[PetDocument] = field(default_factory=list)
    error_message: Optional[str] = None


class OwnerProfileFlow:
    """
    UC7 – Προβολή Προφίλ Ιδιοκτήτη (v0.2).

    Orchestrates the full sequence diagram:
      select_profile()  → Basic Flow steps 1-3 plus Alt Flows 1 & 3
      select_pet()      → Basic Flow steps 4-7 plus Alt Flow 2
    """

    def __init__(self):
        self._data_retriever = OwnerDataRetriever()
        self._pet_checker = PetChecker()
        self._access_checker = AccessChecker()
        self._pet_data_retriever = PetDataRetriever()

    # ── Step 1: Owner selects profile ────────────────────────────────────────

    def select_profile(self, owner_id: str) -> ProfileSummaryResult:
        """
        Basic Flow 1-3:
          fetchOwnerData → getOwnerDetails → checkPets → displayProfileSummary

        Alt Flow 3 (Αποτυχία φόρτωσης στοιχείων):
          fetchOwnerData returns None → ErrorMessage

        Alt Flow 1 (Δεν υπάρχουν καταχωρημένα ζώα):
          getPetList returns [] → EmptyListMessage + suggest receptionist
        """
        owner = self._data_retriever.fetch_owner_data(owner_id)
        if owner is None:
            return ProfileSummaryResult(
                success=False,
                error_message="Η φόρτωση απέτυχε. Προσπαθήστε ξανά."
            )

        owner_data = self._data_retriever.get_owner_details(owner)
        pet_list = self._pet_checker.get_pet_list(owner_id)

        if not pet_list:
            return ProfileSummaryResult(
                success=False,
                owner_data=owner_data,
                error_message="Δεν υπάρχουν καταχωρημένα ζώα. "
                              "Επικοινωνήστε με τη ρεσεψιόν."
            )

        return ProfileSummaryResult(success=True, owner_data=owner_data,
                                    pet_list=pet_list)

    # ── Step 4: Owner selects a pet ──────────────────────────────────────────

    def select_pet(self, owner_id: str, animal_id: str) -> PetProfileResult:
        """
        Basic Flow 4-7:
          checkAccess → fetchPetData (getMedicalHistory + getDocuments)
          → displayPetProfile

        Alt Flow 2 (Ανεπαρκή δικαιώματα):
          checkAccess returns False → AccessDeniedMessage
        """
        if not self._access_checker.check_access(owner_id, animal_id):
            return PetProfileResult(
                success=False,
                error_message="Δεν έχετε πρόσβαση."
            )

        store = DataStore()
        animal = store.get_animal(animal_id)

        medical_records, all_docs = self._pet_data_retriever.fetch_pet_data(animal_id)
        approved_docs = [d for d in all_docs
                         if self._access_checker.can_view_document(d)]

        return PetProfileResult(
            success=True,
            pet_data=animal,
            medical_data=medical_records,
            documents=approved_docs,
        )

    # ── Step 8-9: Owner exits ────────────────────────────────────────────────

    def exit_profile(self) -> None:
        """Owner closes profile → system returns to HomeScreen."""
        pass
