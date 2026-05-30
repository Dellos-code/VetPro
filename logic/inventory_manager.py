from database.db_setup import get_connection

# 1. Μηχανή Ασφάλειας (UC10 - Negative Lock)
class NegativeLockEngine:
    def verifyStock(self, item_name, qty):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
            row = cursor.fetchone()
            if row and row[0] >= qty:
                return True
            return False
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()

# 2. Ελεγκτής Πρόβλεψης
class PredictController:
    def triggerForecast(self):
        pass # Placeholder για μελλοντική AI πρόβλεψη

# 3. Ελεγκτής Ενημέρωσης
class UpdateController:
    def __init__(self):
        self.predict_ctrl = PredictController()

    def executeConsumeStock(self, item_name, qty_to_remove):
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?",
                (qty_to_remove, item_name)
            )
            conn.commit()
            self.predict_ctrl.triggerForecast()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()

# 4. Λήψη Αιτήματος (Κεντρικός Ελεγκτής)
class InventoryRequestController:
    def __init__(self):
        self.lock_ctrl = NegativeLockEngine()
        self.update_ctrl = UpdateController()

    def submitPrescriptionRequest(self, item_name, qty):
        has_enough_stock = self.lock_ctrl.verifyStock(item_name, qty)
        if has_enough_stock:
            return self.update_ctrl.executeConsumeStock(item_name, qty)
        else:
            raise ValueError("Σφάλμα: Αρνητικό Απόθεμα!")
