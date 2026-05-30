"""
InventoryManager (Class Diagram: Business Logic & Engines)
+decreaseStock(type: String): void
+updateStock(): void
+createLowStockAlert(): void

ForecastEngine (Class Diagram)
+triggerForecast(): void
"""
from database.db_setup import get_connection

class InventoryManager:
    def decreaseStock(self, med_name: str, qty: int = 1):
        conn = get_connection()
        med = conn.execute(
            "SELECT stock_level, min_threshold FROM medications WHERE name=?", (med_name,)
        ).fetchone()
        if not med:
            conn.close()
            raise ValueError(f"Φάρμακο '{med_name}' δεν βρέθηκε στη βάση.")
        # Negative Stock Lock (UC10)
        if med["stock_level"] - qty < 0:
            conn.close()
            raise ValueError(f"Ανεπαρκές απόθεμα {med_name}: {med['stock_level']} διαθέσιμα, ζητήθηκαν {qty}.")
        conn.execute("UPDATE medications SET stock_level = stock_level - ? WHERE name=?", (qty, med_name))
        conn.commit()
        new_stock = conn.execute("SELECT stock_level FROM medications WHERE name=?", (med_name,)).fetchone()["stock_level"]
        conn.close()
        if new_stock <= med["min_threshold"]:
            self.createLowStockAlert(med_name, new_stock)
        return new_stock

    def updateStock(self, med_name: str, qty: int):
        conn = get_connection()
        conn.execute("UPDATE medications SET stock_level = stock_level + ? WHERE name=?", (qty, med_name))
        conn.commit()
        conn.close()

    def createLowStockAlert(self, med_name: str, current: int):
        print(f"[InventoryManager] ⚠️ ALERT: Χαμηλό απόθεμα '{med_name}': {current} τεμάχια")

class ForecastEngine:
    """ForecastEngine (Class Diagram) +triggerForecast(): void"""
    def triggerForecast(self):
        conn = get_connection()
        low = conn.execute(
            "SELECT name, stock_level, min_threshold FROM medications WHERE stock_level <= min_threshold"
        ).fetchall()
        conn.close()
        alerts = [dict(m) for m in low]
        return alerts
=======
import sqlite3
from database.db_setup import get_connection

# 1. Μηχανή Negative Lock
class NegativeLockEngine:
    def verifyStock(self, item_name, qty_requested):
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
            result = cursor.fetchone()
            if result:
                return result[0] >= qty_requested
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

