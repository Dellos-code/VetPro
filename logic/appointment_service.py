import sqlite3
from database.db_setup import get_connection

# 1. Μηχανή Βελτιστοποίησης
class OptimizationEngine:
    def checkAvailability(self, date, time):
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM appointments WHERE date = ? AND time = ?", (date, time))
            conflict = cursor.fetchone()
            return conflict is None  # True αν είναι ελεύθερο
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()

# 2. Ελεγκτής Εγγραφής
class SaveController:
    def initiateSave(self, data):
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO appointments (owner_id, pet_id, date, time, reason) VALUES (?, ?, ?, ?, ?)",
                (data['owner_id'], data['pet_id'], data['date'], data['time'], data['reason'])
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()

# 3. Λήψη Αιτήματος (Κεντρικός Ελεγκτής)
class AppointmentRequestController:
    def __init__(self):
        self.engine = OptimizationEngine()
        self.save_ctrl = SaveController()

    def submitAppointment(self, owner_id, pet_id, date, time, reason):
        data = {'owner_id': owner_id, 'pet_id': pet_id, 'date': date, 'time': time, 'reason': reason}
        
        is_available = self.engine.checkAvailability(date, time)
        if is_available:
            return self.save_ctrl.initiateSave(data)
        return False
