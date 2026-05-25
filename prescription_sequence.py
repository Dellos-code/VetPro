import datetime
from typing import List

# ==========================================
# 1. ΟΡΙΣΜΟΣ ΚΛΑΣΕΩΝ ΑΠΟ ΤΟ CLASS DIAGRAM
# ==========================================

class Medication:
    """Οντότητα Φαρμάκου (από το πακέτο Entities)"""
    def __init__(self, id: str, name: str, type: str, activeIngredient: str):
        self.id = id
        self.name = name
        self.type = type
        self.activeIngredient = activeIngredient

class Prescription:
    """Οντότητα Συνταγής (από το πακέτο Entities)"""
    def __init__(self, id: str, date: datetime.date, dosage: str, quantity: int, medication: Medication):
        self.id = id
        self.date = date
        self.dosage = dosage
        self.quantity = quantity
        self.medication = medication

    def savePermanently(self) -> None:
        """Μέθοδος μόνιμης αποθήκευσης της συνταγής (όπως αναφέρεται στο 1ο διάγραμμα)"""
        print(f"[MedRecord Entity]: Η συνταγή {self.id} για το φάρμακο '{self.medication.name}' αποθηκεύτηκε μόνιμα.")

class MedicalRecord:
    """Αφηρημένη κλάση Ιατρικού Φακέλου"""
    def __init__(self, id: str, date: datetime.date, notes: str):
        self.id = id
        self.date = date
        self.notes = notes

class Examination(MedicalRecord):
    """Εξέταση που εκδίδει Συνταγές (ως το MedRecord Entity στο Sequence Diagram)"""
    def __init__(self, id: str, date: datetime.date, notes: str, diagnosis: str):
        super().__init__(id, date, notes)
        self.diagnosis = diagnosis
        self.prescriptions: List[Prescription] = []

    def save_prescription(self, prescription: Prescription) -> None:
        """Συνδέει τη συνταγή με την εξέταση και την αποθηκεύει (MedRecordEntity : savePermanently)"""
        self.prescriptions.append(prescription)
        prescription.savePermanently()

class User:
    """Αφηρημένη κλάση Χρήστη"""
    def __init__(self, id: str, username: str, email: str, role: str):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

class Veterinarian(User):
    """Ο Κτηνίατρος (Ο Actor στο Sequence Diagram)"""
    def __init__(self, id: str, username: str, email: str):
        super().__init__(id, username, email, "Veterinarian")
        self.specialty = "Γενική Ιατρική"

    # ==========================================
    # 2. ΥΛΟΠΟΙΗΣΗ ΤΟΥ SEQUENCE DIAGRAM
    # ==========================================
    def createPrescription(self, animalId: str, current_examination: Examination, drug_catalog: List[Medication]) -> None:
        """
        Η κύρια μέθοδος που υλοποιεί τη ροή του Sequence Diagram
        """
        print(f"\n--- Εκκίνηση Συνταγογράφησης (selectCreatePrescription) για ζώο: {animalId} ---")
        print("[Form]: Η φόρμα συνταγογράφησης (PrescriptionForm) εμφανίστηκε.\n")
        
        # Temp List: Προσωρινή λίστα για αποθήκευση των φαρμάκων πριν την τελική υποβολή
        temp_list = []
        
        # loop: Για όσα φάρμακα επιθυμεί ο Κτηνίατρος (Βήματα 4-9)
        while True:
            search_name = input("Εισάγετε όνομα φαρμάκου (ή πατήστε Enter για συνέχεια/έξοδο): ").strip()
            if not search_name:
                break
                
            # Αναζήτηση φαρμάκου (DrugCatalog : findDrug(name))
            found_drug = None
            for drug in drug_catalog:
                if drug.name.lower() == search_name.lower():
                    found_drug = drug
                    break
            
            if found_drug is None:
                # Εναλλακτική Ροή 1: Το φάρμακο δε βρέθηκε
                print("[Message]: Το φάρμακο δε βρέθηκε (Drug not found).")
                print("[Form]: Γίνεται επαναφορά φόρμας (resetForm)...\n")
            else:
                # Βασική Ροή: Το φάρμακο βρέθηκε
                print(f"[Drug Catalog]: Το φάρμακο '{found_drug.name}' βρέθηκε επιτυχώς.")
                print("[Form]: Ανανέωση φόρμας (refreshForm).")
                
                try:
                    # Εισαγωγή λεπτομερειών από τον κτηνίατρο (enterDetails)
                    quantity = int(input("Εισάγετε Ποσότητα (Quantity): "))
                    dosage = input("Εισάγετε Δοσολογία (Dosage): ")
                    
                    # Προσθήκη στην προσωρινή λίστα (TempList : add(drug, quantity, dosage))
                    temp_list.append({
                        "drug": found_drug,
                        "quantity": quantity,
                        "dosage": dosage
                    })
                    print("[Temp List]: Τα δεδομένα προστέθηκαν προσωρινά (addConfirmation).\n")
                except ValueError:
                    print("[Σφάλμα]: Παρακαλώ εισάγετε έγκυρο αριθμό για ποσότητα.\n")

        # Εάν δεν υπάρχουν φάρμακα, τερματίζουμε τη διαδικασία
        if not temp_list:
            print("[Σύστημα]: Δεν προστέθηκαν φάρμακα στη συνταγή. Ακύρωση διαδικασίας.")
            return

        # Επιλογή του Κτηνιάτρου: Ακύρωση ή Υποβολή
        action = input("Επιλέξτε (S)ubmit για Υποβολή Συνταγής, (C)ancel για Ακύρωση: ").strip().upper()
        
        if action == 'C':
            # Εναλλακτική Ροή 2: Ακύρωση Διαδικασίας (cancel)
            confirm = input("[Message]: Είστε σίγουροι; (Are you sure?) (Y/N): ").strip().upper()
            if confirm == 'Y':
                temp_list.clear() # TempList : clearData()
                print("[Temp List]: Διαγραφή δεδομένων προσωρινής λίστας (OK).")
                print("[MedRecordScreen]: Ακύρωση επιτυχής. Ανακατεύθυνση (showMessageAndRedirect).")
            else:
                print("[Σύστημα]: Η ακύρωση διεκόπη.")
                
        elif action == 'S':
            # Βασική Ροή: Καταχώρηση Συνταγής (submitPrescription)
            print("\n[Temp List]: Ανάκτηση δεδομένων συνταγής (getData)...")
            
            # Για κάθε φάρμακο στη λίστα, δημιουργούμε το αντικείμενο Prescription και το σώζουμε
            for idx, item in enumerate(temp_list):
                # Δημιουργία μοναδικού ID
                presc_id = f"PRES-{datetime.datetime.now().strftime('%H%M%S')}-{idx}"
                
                new_prescription = Prescription(
                    id=presc_id,
                    date=datetime.date.today(),
                    dosage=item["dosage"],
                    quantity=item["quantity"],
                    medication=item["drug"]
                )
                
                # MedRecordEntity : savePermanently(prescriptionData)
                current_examination.save_prescription(new_prescription)
                
            print("\n[MedRecordEntity]: Επιτυχής αποθήκευση (saveSuccess).")
            print("[MedRecordScreen]: Η συνταγή καταχωρήθηκε! Ανακατεύθυνση (showSuccessMessageAndRedirect).")
        else:
            print("[Σφάλμα]: Μη έγκυρη ενέργεια.")

# ==========================================
# 3. ΠΑΡΑΔΕΙΓΜΑ ΕΚΤΕΛΕΣΗΣ ΚΩΔΙΚΑ
# ==========================================
if __name__ == "__main__":
    # Δημιουργία υποθετικού καταλόγου φαρμάκων (Drug Catalog)
    catalog = [
        Medication("M01", "Amoxil", "Χάπι", "Αμοξικιλλίνη"),
        Medication("M02", "Rimadyl", "Χάπι", "Καρπροφαίνη"),
        Medication("M03", "Bravecto", "Μασώμενο", "Fluralaner")
    ]
    
    # Δημιουργία Κτηνιάτρου
    vet = Veterinarian("V101", "Dr. Papadopoulos", "vet@clinic.gr")
    
    # Δημιουργία μιας τρέχουσας Εξέτασης (ως το MedRecord Entity που θα δεχθεί τις συνταγές)
    exam = Examination("EX-205", datetime.date.today(), "Ο σκύλος παρουσιάζει λοίμωξη.", "Βακτηριακή Λοίμωξη")
    
    # Κλήση της λειτουργίας
    vet.createPrescription(animalId="DOG-552", current_examination=exam, drug_catalog=catalog)
