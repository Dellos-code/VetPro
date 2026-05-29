"""
Class Diagram - Business Logic & Engines:

ReportGenerator: +retrieveData(from: Date, to: Date): Object / +generatePDF(data: Object): void
MedHistory: +retrieveData(from: Date, to: Date): Object
DrugCatalog: +findDrug(name: String): Object
TempList: +add(drug: Object, quantity: Integer, dosage: String): void / +clearData(): void / +getData(): Object
ResultsAnalyzer: +notifyResults(records: Object): void / +detectMultipleMatches(): void / +commandDisplay(): void
"""
from database.db_setup import get_connection

class MedHistory:
    """MedHistory (Class Diagram) +retrieveData(from: Date, to: Date): Object"""
    def retrieveData(self, animal_id: str, from_date: str, to_date: str):
        if from_date > to_date:
            raise ValueError("Η αρχική ημερομηνία πρέπει να είναι προγενέστερη της τελικής.")
        conn = get_connection()
        rows = conn.execute("""
            SELECT mr.record_date, mr.record_type, mr.notes,
                   e.diagnosis, v.vaccine_name, v.next_due_date
            FROM medical_records mr
            LEFT JOIN examinations e ON e.record_id = mr.id
            LEFT JOIN vaccinations v ON v.record_id = mr.id
            WHERE mr.animal_id=? AND mr.record_date BETWEEN ? AND ?
            ORDER BY mr.record_date DESC
        """, (animal_id, from_date, to_date)).fetchall()
        conn.close()
        return [dict(r) for r in rows] if rows else None

class ReportGenerator:
    """ReportGenerator (Class Diagram) +retrieveData() / +generatePDF()"""
    def __init__(self):
        self.med_history = MedHistory()

    def retrieveData(self, animal_id: str, from_date: str, to_date: str):
        return self.med_history.retrieveData(animal_id, from_date, to_date)

    def generatePDF(self, data: list, title: str = "Ιατρική Αναφορά") -> str:
        lines = [f"VetPro - {title}", "=" * 40]
        for r in data:
            detail = r.get("diagnosis") or r.get("vaccine_name") or r.get("notes") or ""
            lines.append(f"[{r['record_date']}] {r['record_type']}: {detail}")
        return "\n".join(lines)

class DrugCatalog:
    """DrugCatalog (Class Diagram) +findDrug(name: String): Object"""
    def findDrug(self, name: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM medications WHERE LOWER(name)=LOWER(?)", (name,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

class TempList:
    """TempList (Class Diagram) +add() / +clearData() / +getData()"""
    def __init__(self):
        self._items = []

    def add(self, drug: dict, quantity: int, dosage: str) -> str:
        self._items.append({"drug": drug, "quantity": quantity, "dosage": dosage})
        return "addConfirmation"

    def clearData(self):
        self._items.clear()
        return "OK"

    def getData(self):
        return list(self._items)

class ResultsAnalyzer:
    """ResultsAnalyzer (Class Diagram) +notifyResults() / +detectMultipleMatches() / +commandDisplay()"""
    def notifyResults(self, records: list) -> dict:
        return {
            "count": len(records),
            "has_multiple": len(records) > 1,
            "is_empty": len(records) == 0,
            "records": records
        }

    def detectMultipleMatches(self, records: list) -> bool:
        return len(records) > 1

    def commandDisplay(self, records: list):
        return [dict(r) for r in records]
