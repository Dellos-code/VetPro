"""
AppointmentService (Class Diagram: Business Logic & Engines)
+initiateSave(data: Object): void
+insertAppointment(data: Object): void

SchedulerEngine (implied by UC9 sequence diagram)
- checkAvailability
- conflict detection / preemption for urgent
"""
import uuid
from database.db_setup import get_connection

class AppointmentService:
    def initiateSave(self, data: dict):
        self.insertAppointment(data)

    def insertAppointment(self, data: dict):
        conn = get_connection()
        conflict = conn.execute(
            "SELECT id FROM appointments WHERE vet_id=? AND appt_date=? AND time=? AND status='Scheduled'",
            (data.get("vet_id"), data["appt_date"], data["time"])
        ).fetchone()
        if conflict and data.get("priority", 1) < 5:
            conn.close()
            raise ValueError("CONFLICT: Σύγκρουση ωρών. Επιλέξτε άλλη ώρα.")
        if conflict and data.get("priority", 1) >= 5:
            # Preemption for urgent (UC9 Alt Flow 2)
            conn.execute("UPDATE appointments SET status='Rescheduled' WHERE id=?", (conflict["id"],))
        conn.execute(
            "INSERT INTO appointments (id,appt_date,time,reason,status,priority,animal_id,vet_id) VALUES (?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), data["appt_date"], data["time"], data["reason"],
             "Scheduled", data.get("priority", 1), data["animal_id"], data.get("vet_id"))
        )
        conn.commit()
        conn.close()
