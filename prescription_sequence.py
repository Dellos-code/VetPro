"""
Υλοποίηση της λογικής του Sequence Diagram για τη Συνταγογράφηση,
χρησιμοποιώντας ΜΟΝΟ τις κλάσεις που εμφανίζονται στο διάγραμμα.
"""

class DrugCatalog:
    """Ο κατάλογος φαρμάκων (Entity/Database)"""
    def __init__(self):
        # Εικονικά δεδομένα φαρμάκων για τον κατάλογο
        self.drugs = [
            {"name": "Amoxil", "type": "Χάπι"},
            {"name": "Rimadyl", "type": "Χάπι"},
            {"name": "Bravecto", "type": "Μασώμενο"}
        ]

    def findDrug(self, name: str):
        print(f"  [DrugCatalog] Αναζήτηση φαρμάκου: '{name}'")
        for drug in self.drugs:
            if drug["name"].lower() == name.lower():
                return drug
        return None

class TempList:
    """Η προσωρινή λίστα για τα φάρμακα πριν την τελική αποθήκευση"""
    def __init__(self):
        self.items = []

    def add(self, drug, quantity, dosage):
        print(f"  [TempList] Προσθήκη φαρμάκου '{drug['name']}', ποσότητα: {quantity}, δοσολογία: '{dosage}'")
        self.items.append({"drug": drug, "quantity": quantity, "dosage": dosage})
        return "addConfirmation"

    def clearData(self):
        print("  [TempList] Καθαρισμός προσωρινών δεδομένων")
        self.items.clear()
        return "OK"

    def getData(self):
        print("  [TempList] Ανάκτηση όλων των προσωρινών δεδομένων συνταγής")
        return self.items

class MedRecordEntity:
    """Η οντότητα του Ιατρικού Φακέλου / Εξέτασης που σώζει τη συνταγή"""
    def savePermanently(self, prescriptionData):
        print(f"  [MedRecordEntity] Μόνιμη αποθήκευση συνταγής με {len(prescriptionData)} φάρμακα:")
        for item in prescriptionData:
            print(f"    - Φάρμακο: {item['drug']['name']} | Ποσότητα: {item['quantity']} | Δοσολογία: {item['dosage']}")
        return "saveSuccess"

class MedRecordScreen:
    """Η οθόνη του ιατρικού φακέλου"""
    def __init__(self):
        self.prescription_form = None

    def set_form(self, form):
        self.prescription_form = form

    def selectCreatePrescription(self):
        print("[MedRecordScreen] Ο Κτηνίατρος επέλεξε δημιουργία συνταγής")
        if self.prescription_form:
            self.prescription_form.display()

    def showMessageAndRedirect(self):
        print("[MedRecordScreen] Ακύρωση - Ανακατεύθυνση στην προηγούμενη οθόνη")

    def showSuccessMessageAndRedirect(self):
        print("[MedRecordScreen] Επιτυχία - Η συνταγή καταχωρήθηκε! Ανακατεύθυνση")

class Message:
    """Κλάση για την εμφάνιση μηνυμάτων και παραθύρων επιβεβαίωσης"""
    def __init__(self):
        self.prescription_form = None
        self.temp_list = None
        self.med_record_screen = None

    def set_references(self, form, temp_list, screen):
        self.prescription_form = form
        self.temp_list = temp_list
        self.med_record_screen = screen

    def display(self, text):
        print(f"  [Message] Εμφάνιση μηνύματος: '{text}'")

    def close(self):
        print("  [Message] Κλείσιμο μηνύματος. (Επιστροφή OK στη φόρμα)")
        if self.prescription_form:
            self.prescription_form.resetForm()

    def requestConfirmation(self, text):
        print(f"  [Message] Παράθυρο επιβεβαίωσης: '{text}'")

    def confirm(self):
        print("  [Message] Ο χρήστης πάτησε 'Επιβεβαίωση'")
        if self.temp_list:
            response = self.temp_list.clearData()
            if response == "OK" and self.med_record_screen:
                self.med_record_screen.showMessageAndRedirect()

class PrescriptionForm:
    """Η φόρμα συνταγογράφησης (Boundary/View)"""
    def __init__(self, drug_catalog, temp_list, med_record_entity):
        self.drug_catalog = drug_catalog
        self.temp_list = temp_list
        self.med_record_entity = med_record_entity
        self.message = None
        self.med_record_screen = None
        
        self.current_drug = None
        self.current_quantity = None
        self.current_dosage = None

    def set_references(self, message, screen):
        self.message = message
        self.med_record_screen = screen

    def display(self):
        print("  [PrescriptionForm] Προβολή της φόρμας συνταγογράφησης")

    def searchDrug(self, name):
        print(f"  [PrescriptionForm] Λήψη αιτήματος αναζήτησης φαρμάκου: {name}")
        drugData = self.drug_catalog.findDrug(name)
        
        if drugData is None:
            # Εναλλακτική ροή 1: Φάρμακο δε βρέθηκε
            if self.message:
                self.message.display("Drug not found")
        else:
            # Βασική ροή: Φάρμακο βρέθηκε
            self.current_drug = drugData
            self.refreshForm()

    def resetForm(self):
        print("  [PrescriptionForm] Επαναφορά της φόρμας")
        self.current_drug = None

    def refreshForm(self):
        print("  [PrescriptionForm] Ανανέωση φόρμας με τα δεδομένα του επιλεγμένου φαρμάκου")

    def selectDrug(self):
        print("  [PrescriptionForm] Επιβεβαίωση επιλογής φαρμάκου από τη λίστα")

    def enterDetails(self, quantity, dosage):
        print(f"  [PrescriptionForm] Λήψη λεπτομερειών: ποσότητα={quantity}, δοσολογία='{dosage}'")
        self.current_quantity = quantity
        self.current_dosage = dosage

    def addDrug(self):
        print("  [PrescriptionForm] Αίτημα προσθήκης του φαρμάκου στην προσωρινή λίστα")
        if self.current_drug:
            confirmation = self.temp_list.add(self.current_drug, self.current_quantity, self.current_dosage)
            if confirmation == "addConfirmation":
                print("  [PrescriptionForm] Επιτυχής προσθήκη - Λήψη επιβεβαίωσης 'addConfirmation'")

    def cancel(self):
        print("  [PrescriptionForm] Λήψη αιτήματος ακύρωσης διαδικασίας")
        if self.message:
            self.message.requestConfirmation("Are you sure?")

    def submitPrescription(self):
        print("  [PrescriptionForm] Λήψη αιτήματος υποβολής συνταγής")
        prescriptionData = self.temp_list.getData()
        
        response = self.med_record_entity.savePermanently(prescriptionData)
        if response == "saveSuccess":
            if self.med_record_screen:
                self.med_record_screen.showSuccessMessageAndRedirect()


class Veterinarian:
    """Ο Actor 'Κτηνίατρος' που αλληλεπιδρά με το σύστημα βάσει του Sequence Diagram"""
    def __init__(self, med_record_screen, prescription_form, message):
        self.med_record_screen = med_record_screen
        self.prescription_form = prescription_form
        self.message = message

    # ===============================================
    # Ενέργειες που πυροδοτεί ο Actor στο σύστημα
    # ===============================================
    def action_selectCreatePrescription(self):
        print("\n[ACTOR] Ο Κτηνίατρος πατάει 'Δημιουργία Συνταγής' (selectCreatePrescription)")
        self.med_record_screen.selectCreatePrescription()

    def action_searchDrug(self, name):
        print(f"\n[ACTOR] Ο Κτηνίατρος αναζητά το φάρμακο '{name}' (searchDrug)")
        self.prescription_form.searchDrug(name)

    def action_closeMessage(self):
        print("\n[ACTOR] Ο Κτηνίατρος κλείνει το αναδυόμενο μήνυμα (close)")
        self.message.close()

    def action_selectDrug(self):
        print("\n[ACTOR] Ο Κτηνίατρος επιλέγει το βρεθέν φάρμακο (selectDrug)")
        self.prescription_form.selectDrug()

    def action_enterDetails(self, quantity, dosage):
        print(f"\n[ACTOR] Ο Κτηνίατρος πληκτρολογεί ποσότητα={quantity}, δοσολογία='{dosage}' (enterDetails)")
        self.prescription_form.enterDetails(quantity, dosage)

    def action_addDrug(self):
        print("\n[ACTOR] Ο Κτηνίατρος πατάει το κουμπί 'Προσθήκη' (addDrug)")
        self.prescription_form.addDrug()

    def action_cancel(self):
        print("\n[ACTOR] Ο Κτηνίατρος πατάει το κουμπί 'Ακύρωση' (cancel)")
        self.prescription_form.cancel()

    def action_confirm(self):
        print("\n[ACTOR] Ο Κτηνίατρος επιβεβαιώνει την ακύρωση στο παράθυρο διαλόγου (confirm)")
        self.message.confirm()

    def action_submitPrescription(self):
        print("\n[ACTOR] Ο Κτηνίατρος πατάει το κουμπί 'Καταχώρηση Συνταγής' (submitPrescription)")
        self.prescription_form.submitPrescription()


# ==========================================
# ΣΕΝΑΡΙΑ ΕΚΤΕΛΕΣΗΣ ΓΙΑ ΕΠΙΔΕΙΞΗ
# ==========================================
def main():
    # 1. Αρχικοποίηση όλων των αντικειμένων του διαγράμματος
    drug_catalog = DrugCatalog()
    temp_list = TempList()
    med_record_entity = MedRecordEntity()
    
    med_record_screen = MedRecordScreen()
    message = Message()
    
    prescription_form = PrescriptionForm(drug_catalog, temp_list, med_record_entity)
    
    # 2. Σύνδεση εξαρτήσεων (Dependency Injection)
    med_record_screen.set_form(prescription_form)
    prescription_form.set_references(message, med_record_screen)
    message.set_references(prescription_form, temp_list, med_record_screen)
    
    # Ο Actor
    vet = Veterinarian(med_record_screen, prescription_form, message)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print(" ΣΕΝΑΡΙΟ 1: ΒΑΣΙΚΗ ΡΟΗ & ΕΝΑΛΛΑΚΤΙΚΗ 1 (ΦΑΡΜΑΚΟ ΔΕ ΒΡΕΘΗΚΕ)")
    print("="*60)
    
    # Ξεκινάει η συνταγογράφηση
    vet.action_selectCreatePrescription()
    
    # Εναλλακτική Ροή 1: Φάρμακο που δεν υπάρχει
    vet.action_searchDrug("Panadol")
    vet.action_closeMessage()
    
    # Βασική Ροή: Φάρμακο που υπάρχει
    vet.action_searchDrug("Amoxil")
    vet.action_selectDrug()
    vet.action_enterDetails(quantity=2, dosage="1 χάπι ανά 12 ώρες")
    vet.action_addDrug()

    # Προσθήκη δεύτερου φαρμάκου
    vet.action_searchDrug("Bravecto")
    vet.action_selectDrug()
    vet.action_enterDetails(quantity=1, dosage="1 μασώμενο κάθε 3 μήνες")
    vet.action_addDrug()
    
    # Καταχώρηση (Βασική Ροή - Τέλος)
    vet.action_submitPrescription()

    # ---------------------------------------------------------
    print("\n\n" + "="*60)
    print(" ΣΕΝΑΡΙΟ 2: ΕΝΑΛΛΑΚΤΙΚΗ ΡΟΗ 2 (ΑΚΥΡΩΣΗ ΔΙΑΔΙΚΑΣΙΑΣ)")
    print("="*60)
    
    # Εκκαθάριση της προσωρινής λίστας για τη νέα δοκιμή
    temp_list.clearData()
    
    # Ξεκινάει νέα συνταγογράφηση
    vet.action_selectCreatePrescription()
    
    # Βρίσκει φάρμακο και προσθέτει
    vet.action_searchDrug("Rimadyl")
    vet.action_selectDrug()
    vet.action_enterDetails(quantity=1, dosage="Μισό χάπι την ημέρα")
    vet.action_addDrug()
    
    # Ακύρωση της διαδικασίας από τον Κτηνίατρο
    vet.action_cancel()
    
    # Επιβεβαίωση της ακύρωσης στο αναδυόμενο μήνυμα
    vet.action_confirm()

if __name__ == "__main__":
    main()
