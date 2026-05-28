import random
from typing import Dict
from pydantic import BaseModel

# --- Μοντέλα Δεδομένων (Data Models) ---
class PrescriptionRequest(BaseModel):
    medication_id: int
    veterinarian_id: int
    quantity: int

class MedicationStock(BaseModel):
    medication_id: int
    name: str
    current_stock: int
    safety_threshold: int = 10

# --- Μηχανή Διαχείρισης Αποθέματος (Inventory Engine) ---
class InventoryEngine:
    """
    Μηχανή ελέγχου αποθεμάτων και πρόβλεψης ελλείψεων (Use Case 10).
    Υλοποιεί το 'Negative Stock Lock' και τον στοχαστικό έλεγχο.
    """
    
    def __init__(self, db_session):
        self.db = db_session # Mock DB session

    def get_current_stock(self, medication_id: int) -> int:
        """Ανακτά το τρέχον απόθεμα από τη βάση (Entity: MedicationDatabase)."""
        # Προσομοίωση: Ας πούμε ότι το φάρμακο έχει 15 τεμάχια
        return 15

    def verify_stock(self, medication_id: int, requested_qty: int) -> bool:
        """
        Ο πυρήνας του Negative Stock Lock. 
        Διασφαλίζει ότι το απόθεμα δεν θα πέσει ποτέ κάτω από το 0.
        """
        current_stock = self.get_current_stock(medication_id)
        if (current_stock - requested_qty) >= 0:
            return True
        return False

    def trigger_forecast(self, medication_id: int, new_stock: int) -> Dict:
        """
        Ελεγκτής Πρόβλεψης (Monte Carlo Simulation).
        Αναλύει αν το νέο απόθεμα είναι επίφοβο για μελλοντική έλλειψη.
        """
        # Απλοποιημένη λογική στοχαστικής πρόβλεψης για το παράδειγμα
        risk_score = random.uniform(0.1, 1.0)
        
        if new_stock < 10 or risk_score > 0.8:
            # Ενεργοποίηση Ελεγκτή Ειδοποιήσεων
            return {"forecast_alert": True, "message": "Υψηλός κίνδυνος έλλειψης. Απαιτείται αναπλήρωση!"}
        return {"forecast_alert": False, "message": "Απόθεμα ασφαλές."}

    def execute_consume_stock(self, request: PrescriptionRequest) -> Dict:
        """
        Η κύρια ροή συνταγογράφησης και αφαίρεσης αποθέματος.
        """
        # 1. Έλεγχος Επάρκειας (Negative Stock Lock)
        is_sufficient = self.verify_stock(request.medication_id, request.quantity)
        
        if not is_sufficient:
            # Ελεγκτής Σφαλμάτων - Βίαιη διακοπή
            raise ValueError("Σφάλμα: Αρνητικό Απόθεμα! Η ζητούμενη ποσότητα υπερβαίνει το διαθέσιμο.")

        # 2. Ελεγκτής Ενημέρωσης (consume_stock)
        current_stock = self.get_current_stock(request.medication_id)
        new_stock = current_stock - request.quantity
        self._update_db_stock(request.medication_id, new_stock)

        # 3. Ελεγκτής Πρόβλεψης (Αυτοματοποίηση μετά την αφαίρεση)
        forecast_result = self.trigger_forecast(request.medication_id, new_stock)

        return {
            "status": "success", 
            "message": "Επιτυχής Αφαίρεση Φαρμάκου",
            "new_stock": new_stock,
            "forecast": forecast_result
        }

    def _update_db_stock(self, med_id: int, new_qty: int):
        """Εσωτερική συνάρτηση για το UPDATE στη βάση."""
        pass # Προσομοίωση DB commit

# Παράδειγμα χρήσης:
# inventory = InventoryEngine(db_session=db)
# try:
#     result = inventory.execute_consume_stock(prescription_req)
# except ValueError as e:
#     print(e)
