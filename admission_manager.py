"""
Class Diagram - Business Logic & Engines:

AdmissionManager: +createAdmission(): void / +saveRecord(): void / +setCriticalStatus(): void
                  +notifyOwner(details: String): void
DailyLogManager: +recordProgress(): void / +modifyMedication(newMeds: String, reason: String): void
                 +setCriticalStatus(): void / +sendUrgentAlert(): void
                 +addDailyLog(): void / +sendSummary(): void
DischargeManager: +process(discharge): void / +updateStatus(): void / +notifyOwner(instructions): void
StatusManager: +updateStatus(status: String): void
NotificationManager: +notifyOwner(details: String): void / +create(): void
"""
import uuid
from datetime import date
from database.db_setup import get_connection

class StatusManager:
    """StatusManager (Class Diagram) +updateStatus(status: String): void"""
    def updateStatus(self, hospitalization_id: str, status: str):
        conn = get_connection()
        conn.execute("UPDATE hospitalizations SET status=? WHERE id=?", (status, hospitalization_id))
        conn.commit()
        conn.close()

class NotificationManager:
    """NotificationManager (Class Diagram) +notifyOwner() / +create()"""
    def notifyOwner(self, owner_id: str, animal_id: str, details: str, notif_type: str = "Νοσηλεία"):
        conn = get_connection()
        conn.execute(
            "INSERT INTO reminders (id,send_date,reminder_type,message,status,owner_id,animal_id) VALUES (?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), date.today().isoformat(), notif_type, details, "Sent", owner_id, animal_id)
        )
        conn.commit()
        conn.close()

    def create(self, owner_id: str, message: str):
        self.notifyOwner(owner_id, None, message)

class AdmissionManager:
    """AdmissionManager (Class Diagram) +createAdmission() / +saveRecord() / +notifyOwner()"""
    def __init__(self):
        self.status_manager = StatusManager()
        self.notif_manager  = NotificationManager()

    def createAdmission(self, animal_id: str, vet_id: str,
                         reason: str, initial_meds: str = "") -> str:
        hosp_id = str(uuid.uuid4())
        self.saveRecord(hosp_id, animal_id, vet_id, reason)
        return hosp_id

    def saveRecord(self, hosp_id: str, animal_id: str, vet_id: str, reason: str):
        conn = get_connection()
        conn.execute(
            "INSERT INTO hospitalizations (id,admission_date,reason,status,animal_id,vet_id) VALUES (?,?,?,?,?,?)",
            (hosp_id, date.today().isoformat(), reason, "Active", animal_id, vet_id)
        )
        conn.commit()
        conn.close()

    def setCriticalStatus(self, hosp_id: str):
        self.status_manager.updateStatus(hosp_id, "Critical")

    def notifyOwner(self, owner_id: str, animal_id: str, details: str):
        self.notif_manager.notifyOwner(owner_id, animal_id, details, "Νοσηλεία")

class DailyLogManager:
    """DailyLogManager (Class Diagram) - daily hospitalization records"""
    def __init__(self):
        self.notif_manager = NotificationManager()

    def recordProgress(self, hosp_id: str, temp: float, weight: float,
                        medication: str, notes: str):
        self.addDailyLog(hosp_id, temp, weight, medication, notes)

    def addDailyLog(self, hosp_id: str, temp: float, weight: float,
                     medication: str, notes: str):
        conn = get_connection()
        conn.execute("""
            INSERT INTO daily_logs (id,log_date,temperature,weight,medication,notes,hospitalization_id)
            VALUES (?,?,?,?,?,?,?)
        """, (str(uuid.uuid4()), date.today().isoformat(), temp, weight, medication, notes, hosp_id))
        conn.commit()
        conn.close()

    def modifyMedication(self, hosp_id: str, new_meds: str, reason: str):
        conn = get_connection()
        # Add a note about medication change
        conn.execute("""
            INSERT INTO daily_logs (id,log_date,medication,notes,hospitalization_id)
            VALUES (?,?,?,?,?)
        """, (str(uuid.uuid4()), date.today().isoformat(), new_meds,
              f"Αλλαγή αγωγής: {reason}", hosp_id))
        conn.commit()
        conn.close()

    def setCriticalStatus(self, hosp_id: str):
        StatusManager().updateStatus(hosp_id, "Critical")

    def sendUrgentAlert(self, owner_id: str, animal_id: str):
        self.notif_manager.notifyOwner(owner_id, animal_id,
                                        "⚠️ Κρίσιμη κατάσταση ζώου - επικοινωνήστε αμέσως",
                                        "Επείγον")

    def sendSummary(self, owner_id: str, animal_id: str, summary: str):
        self.notif_manager.notifyOwner(owner_id, animal_id, summary, "Ενημέρωση Νοσηλείας")

class DischargeManager:
    """DischargeManager (Class Diagram) +process() / +updateStatus() / +notifyOwner()"""
    def __init__(self):
        self.status_manager = StatusManager()
        self.notif_manager  = NotificationManager()

    def process(self, hosp_id: str, instructions: str):
        self.updateStatus(hosp_id)
        return hosp_id

    def updateStatus(self, hosp_id: str):
        conn = get_connection()
        conn.execute(
            "UPDATE hospitalizations SET status='Discharged', discharge_date=? WHERE id=?",
            (date.today().isoformat(), hosp_id)
        )
        conn.commit()
        conn.close()

    def notifyOwner(self, owner_id: str, animal_id: str, instructions: str):
        self.notif_manager.notifyOwner(owner_id, animal_id,
                                        f"Εξιτήριο: {instructions}", "Εξιτήριο")
