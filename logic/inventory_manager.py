from database.db_setup import get_connection

# 1. Μηχανή Ασφάλειας (UC10 - Negative Lock)
class NegativeLockEngine:
    def verifyStock(self, item_name, qty):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT stock_level FROM medications WHERE name = ?", (item_name,))
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
        conn = get_connection()
        try:
            # Επιστρέφει πραγματική λίστα για να μην σκάει η len() στο UI
            low = conn.execute(
                "SELECT name, stock_level, min_threshold FROM medications WHERE stock_level <= min_threshold"
            ).fetchall()
            return [dict(m) for m in low]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            conn.close()

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
                "UPDATE medications SET stock_level = stock_level - ? WHERE name = ?",
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

    def submitReplenishRequest(self, item_name, qty):
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE medications SET stock_level = stock_level + ? WHERE name = ?", (qty, item_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()
