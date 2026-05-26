"""
Προσομοίωση του Sequence Diagram για τη δημιουργία Αναφοράς (Report).
Περιλαμβάνει τις κλάσεις: PetCard, FilterForm, ReportScreen, Message, MedHistory, ReportFile, 
όπως ορίζονται στο Class Diagram και αλληλεπιδρούν στο Sequence Diagram.
"""

class Message:
    def __init__(self):
        self.filter_form = None # Αναφορά για το redirect
        
    def set_filter_form(self, filter_form):
        self.filter_form = filter_form

    def display(self, text):
        print(f"[Message] Εμφάνιση μηνύματος: '{text}'")
        
    def close(self):
        print("[Actor: Κτηνίατρος -> Message] close() - Το μήνυμα έκλεισε.")
        if self.filter_form:
            self.filter_form.redirect()

    def OK(self):
        print("[Actor: Κτηνίατρος -> Message] OK - Ο χρήστης πάτησε OK.")


class ReportFile:
    def __init__(self, filename="pdf_file"):
        self.filename = filename
        print(f"[ReportFile] «create» ({self.filename}) - Δημιουργία αρχείου αναφοράς")


class MedHistory:
    def retrieveData(self, from_date, to_date):
        print(f"[FilterForm -> MedHistory] retrieveData('{from_date}', '{to_date}')")
        # Προσομοίωση: αν η ημερομηνία υποδηλώνει απουσία εγγραφών
        if from_date == "empty":
            return None
        return ["Visit: Εμβολιασμός", "Visit: Αιματολογικές εξετάσεις"]


class ReportScreen:
    def __init__(self, message_system):
        self.message_system = message_system

    def composeAndDisplay(self, visitData):
        print(f"[FilterForm -> ReportScreen] composeAndDisplay(visitData: {visitData})")
        print("[ReportScreen] Η αναφορά συντέθηκε και εμφανίζεται στην οθόνη.")

    def saveReport(self):
        print("[Actor: Κτηνίατρος -> ReportScreen] saveReport()")
        # Δημιουργία αρχείου αναφοράς (PDF)
        ReportFile("report_pdf_file.pdf")
        # Εμφάνιση μηνύματος επιτυχίας
        self.message_system.display("Successfully saved")


class FilterForm:
    def __init__(self, pet_card, med_history, report_screen, message_system):
        self.pet_card = pet_card
        self.med_history = med_history
        self.report_screen = report_screen
        self.message_system = message_system
        self.from_date = None
        self.to_date = None

    def display(self):
        print("[PetCard -> FilterForm] display() - Εμφάνιση Φόρμας Φίλτρων")

    def cancel(self):
        print("[Actor: Κτηνίατρος -> FilterForm] cancel()")
        self.pet_card.redirectHome()

    def enterFilters(self, from_date, to_date):
        print(f"[Actor: Κτηνίατρος -> FilterForm] enterFilters('{from_date}', '{to_date}')")
        self.from_date = from_date
        self.to_date = to_date

    def requestReportCreation(self):
        print("[Actor: Κτηνίατρος -> FilterForm] requestReportCreation()")
        visitData = self.med_history.retrieveData(self.from_date, self.to_date)
        
        if visitData is None:
            # Εναλλακτική Ροή 1: Απουσία Εγγραφών
            print("[MedHistory -> FilterForm] null - Δεν βρέθηκαν δεδομένα")
            self.message_system.display("No records found")
            return False # Επιστρέφει False για να ελέγξει το loop του κτηνιάτρου
        else:
            # Βασική Ροή: Δεδομένα Βρέθηκαν
            print(f"[MedHistory -> FilterForm] Επιστροφή visitData")
            self.report_screen.composeAndDisplay(visitData)
            return True # Επιστρέφει True 

    def redirect(self):
         print("[Message -> FilterForm] redirect() - Επιστροφή στη φόρμα φίλτρων")


class PetCard:
    def __init__(self):
        self.filter_form = None

    def set_filter_form(self, filter_form):
        self.filter_form = filter_form

    def selectCreateReport(self):
        print("[Actor: Κτηνίατρος -> PetCard] selectCreateReport()")
        self.filter_form.display()

    def redirectHome(self):
        print("[FilterForm -> PetCard] redirectHome() - Ανακατεύθυνση στην Αρχική")


# ==========================================
# Προσομοίωση Αλληλεπίδρασης Actor (Κτηνίατρος)
# ==========================================
class Veterinarian:
    def __init__(self, pet_card, filter_form, report_screen, message_system):
        self.pet_card = pet_card
        self.filter_form = filter_form
        self.report_screen = report_screen
        self.message_system = message_system
        self.tried_empty = False

    def run_scenario_cancel(self):
        print("\n--- alt [Ακύρωση Διαδικασίας (Εναλλακτική Ροή 2)] ---")
        self.pet_card.selectCreateReport()
        self.filter_form.cancel()

    def run_scenario_create_report(self):
        print("\n--- [Συνέχιση Διαδικασίας] & loop [Επανάληψη μέχρι να βρεθούν δεδομένα] ---")
        self.pet_card.selectCreateReport()
        
        while True:
            # Προσομοίωση: την 1η φορά ο χρήστης βάζει ημερομηνίες που δεν έχουν δεδομένα
            if not self.tried_empty:
                print("\n>>> Δοκιμή αναζήτησης με απουσία δεδομένων:")
                self.filter_form.enterFilters("empty", "2023-12-31")
                self.tried_empty = True
            # την 2η φορά ο χρήστης βάζει σωστές ημερομηνίες
            else:
                print("\n>>> Δοκιμή αναζήτησης με σωστές ημερομηνίες:")
                self.filter_form.enterFilters("2023-01-01", "2023-12-31")
                
            success = self.filter_form.requestReportCreation()
            
            if not success:
                # Εναλλακτική Ροή 1: Απουσία Εγγραφών
                print("--- alt [Απουσία Εγγραφών (Εναλλακτική Ροή 1)] ---")
                self.message_system.close() # Αυτό καλεί και το redirect() της φόρμας
            else:
                # Βασική Ροή: Δεδομένα Βρέθηκαν
                print("--- [Δεδομένα Βρέθηκαν (Βασική Ροή)] ---")
                self.report_screen.saveReport()
                self.message_system.OK()
                break # Έξοδος από το loop


if __name__ == "__main__":
    # Αρχικοποίηση Συστήματος - Δημιουργία αντικειμένων
    msg = Message()
    history = MedHistory()
    rep_screen = ReportScreen(msg)
    pet_card = PetCard()
    
    # Το FilterForm εξαρτάται από τα υπόλοιπα components
    filter_form = FilterForm(pet_card, history, rep_screen, msg)
    
    # Σύνδεση references
    pet_card.set_filter_form(filter_form)
    msg.set_filter_form(filter_form)
    
    # Αρχικοποίηση Actor
    vet = Veterinarian(pet_card, filter_form, rep_screen, msg)
    
    # 1ο Σενάριο: Ο χρήστης ακυρώνει
    vet.run_scenario_cancel()
    
    # 2ο Σενάριο: Ο χρήστης προχωράει σε δημιουργία (με 1 αποτυχία αναζήτησης και μετά επιτυχία)
    vet.run_scenario_create_report()
