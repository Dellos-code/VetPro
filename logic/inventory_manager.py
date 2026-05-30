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
