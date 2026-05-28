"""
Class Diagram - Business Logic & Engines:

VaccineSaver: +proceed(): void / +create(): void / +saveVaccination(): void / +decreaseStock(type: String): void
AllergyChecker: +checkPreviousAllergy(type: String): Boolean / +getPastAllergies(type: String): Object
DoseCalculator: +calculateNextDose(): void / +createReminder(): void
HistoryManager: +retrieveHistory(): void / +getVaccinationHistory(): Object / +displayHistory(): void
"""
import uuid
from datetime import date, timedelta
from database.db_setup import get_connection

class AllergyChecker:
    """AllergyChecker (Class Diagram) - checks allergy history"""
    def checkPreviousAllergy(self, animal_id: str, vaccine_type: str) -> bool:
        conn = get_connection()
        result = conn.execute("""
            SELECT COUNT(*) as cnt FROM vaccinations v
            JOIN medical_records mr ON v.record_id = mr.id
            WHERE mr.animal_id=? AND v.vaccine_name=? AND v.allergy_reaction=1
        """, (animal_id, vaccine_type)).fetchone()
        conn.close()
        return result["cnt"] > 0

    def getPastAllergies(self, animal_id: str, vaccine_type: str):
        conn = get_connection()
        rows = conn.execute("""
            SELECT mr.record_date, v.vaccine_name FROM vaccinations v
            JOIN medical_records mr ON v.record_id = mr.id
            WHERE mr.animal_id=? AND v.vaccine_name=? AND v.allergy_reaction=1
        """, (animal_id, vaccine_type)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

class DoseCalculator:
    """DoseCalculator (Class Diagram) +calculateNextDose() / +createReminder()"""
    INTERVALS = {"default": 365}

    def calculateNextDose(self, vaccine_name: str) -> str:
        days = self.INTERVALS.get(vaccine_name, self.INTERVALS["default"])
        return (date.today() + timedelta(days=days)).isoformat()

    def createReminder(self, owner_id: str, animal_id: str,
                        vaccine_name: str, next_date: str):
        conn = get_connection()
        conn.execute(
            "INSERT INTO reminders (id,send_date,reminder_type,message,status,owner_id,animal_id) VALUES (?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), next_date, "Εμβόλιο",
             f"Υπενθύμιση εμβολιασμού {vaccine_name}", "Pending", owner_id, animal_id)
        )
        conn.commit()
        conn.close()

class HistoryManager:
    """HistoryManager (Class Diagram) +retrieveHistory() / +getVaccinationHistory() / +displayHistory()"""
    def retrieveHistory(self, animal_id: str):
        conn = get_connection()
        rows = conn.execute("""
            SELECT mr.record_date, mr.record_type, mr.notes,
                   e.diagnosis, v.vaccine_name, v.next_due_date, v.allergy_reaction
            FROM medical_records mr
            LEFT JOIN examinations e ON e.record_id = mr.id
            LEFT JOIN vaccinations v ON v.record_id = mr.id
            WHERE mr.animal_id=?
            ORDER BY mr.record_date DESC
        """, (animal_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def getVaccinationHistory(self, animal_id: str):
        conn = get_connection()
        rows = conn.execute("""
            SELECT mr.record_date, v.vaccine_name, v.batch_number,
                   v.next_due_date, v.allergy_reaction
            FROM vaccinations v
            JOIN medical_records mr ON v.record_id = mr.id
            WHERE mr.animal_id=?
            ORDER BY mr.record_date DESC
        """, (animal_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def displayHistory(self, animal_id: str) -> str:
        records = self.retrieveHistory(animal_id)
        if not records:
            return "Δεν υπάρχουν εγγραφές."
        return "\n".join(
            f"[{r['record_date']}] {r['record_type']}: {r.get('diagnosis') or r.get('vaccine_name') or r.get('notes') or ''}"
            for r in records
        )

class VaccineSaver:
    """VaccineSaver (Class Diagram) - orchestrates UC3"""
    def __init__(self):
        self.allergy_checker = AllergyChecker()
        self.dose_calculator = DoseCalculator()

    def proceed(self):
        pass  # UC3 basic flow continues

    def create(self, animal_id: str, vet_id: str, vaccine_name: str, batch: str, next_due: str):
        conn = get_connection()
        rid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO medical_records (id,record_date,notes,record_type,animal_id,vet_id) VALUES (?,?,?,?,?,?)",
            (rid, date.today().isoformat(), f"Εμβολιασμός {vaccine_name}", "Εμβολιασμός", animal_id, vet_id)
        )
        conn.execute(
            "INSERT INTO vaccinations (record_id,vaccine_name,batch_number,next_due_date) VALUES (?,?,?,?)",
            (rid, vaccine_name, batch, next_due)
        )
        conn.commit()
        conn.close()
        return rid

    def saveVaccination(self, animal_id: str, vet_id: str, owner_id: str,
                        vaccine_name: str, batch: str,
                        allergy_override: bool = False) -> dict:
        # AllergyChecker.checkPreviousAllergy
        has_allergy = self.allergy_checker.checkPreviousAllergy(animal_id, vaccine_name)
        if has_allergy and not allergy_override:
            past = self.allergy_checker.getPastAllergies(animal_id, vaccine_name)
            return {"status": "ALLERGY_WARNING", "past_allergies": past}

        # DoseCalculator.calculateNextDose
        next_due = self.dose_calculator.calculateNextDose(vaccine_name)

        # VaccineSaver.create
        self.create(animal_id, vet_id, vaccine_name, batch, next_due)

        # InventoryManager.decreaseStock
        from logic.inventory_manager import InventoryManager
        try:
            InventoryManager().decreaseStock(vaccine_name, 1)
        except ValueError:
            pass

        # DoseCalculator.createReminder
        self.dose_calculator.createReminder(owner_id, animal_id, vaccine_name, next_due)

        return {"status": "SUCCESS", "next_due_date": next_due}

    def decreaseStock(self, vaccine_type: str):
        from logic.inventory_manager import InventoryManager
        InventoryManager().decreaseStock(vaccine_type, 1)
