"""
Class Diagram - Business Logic & Engines:

CostCalculation: +calculateAndDisplayTotal(): void
PaymentProcessor: processPayment + calculateRemaining
ChargeCheck: +detectMissingCharges(): void / +terminateTemporarily(): void / +approveContinuation(): void
PartialManagement: +calculateBalance(): void / +forwardAsPartial(): void
DebtRegistration: +recordBalanceAsDebt(): void / +confirm(): void
POSCommunication: +sendCardData(): void / +rejectTransaction(errorMsg: String): void
StatusUpdate: +updateStatus(status: String): void
"""
import uuid
from datetime import date
from database.db_setup import get_connection

class ChargeCheck:
    """UC2: ελέγχει αν υπάρχουν καταχωρημένες χρεώσεις"""
    def detectMissingCharges(self, appointment_id: str) -> bool:
        """Returns True if charges are MISSING (error case)"""
        conn = get_connection()
        apt = conn.execute("SELECT id FROM appointments WHERE id=?", (appointment_id,)).fetchone()
        conn.close()
        return apt is None

    def terminateTemporarily(self):
        raise ValueError("Σφάλμα: Δεν υπάρχουν καταχωρημένες χρεώσεις για τη συγκεκριμένη επίσκεψη.")

    def approveContinuation(self):
        return True

class CostCalculation:
    """CostCalculation (Class Diagram) +calculateAndDisplayTotal(): void"""
    def calculateAndDisplayTotal(self, appointment_id: str, default: float = 50.0) -> float:
        conn = get_connection()
        pay = conn.execute("SELECT amount FROM payments WHERE appointment_id=?", (appointment_id,)).fetchone()
        conn.close()
        return pay["amount"] if pay else default

class POSCommunication:
    """POSCommunication (Class Diagram) +sendCardData(): void / +rejectTransaction(): void"""
    def sendCardData(self, amount: float) -> bool:
        # Simulated POS communication
        return True

    def rejectTransaction(self, error_msg: str):
        raise ValueError(f"POS: {error_msg}")

class PartialManagement:
    """PartialManagement (Class Diagram) +calculateBalance(): void / +forwardAsPartial(): void"""
    def calculateBalance(self, total: float, paid: float) -> float:
        return max(0.0, total - paid)

    def forwardAsPartial(self, owner_id: str, balance: float):
        DebtRegistration().recordBalanceAsDebt(owner_id, balance)

class DebtRegistration:
    """DebtRegistration (Class Diagram) +recordBalanceAsDebt(): void / +confirm(): void"""
    def recordBalanceAsDebt(self, owner_id: str, amount: float):
        conn = get_connection()
        conn.execute("UPDATE owners SET debt_amount = debt_amount + ? WHERE user_id=?", (amount, owner_id))
        conn.commit()
        conn.close()

    def confirm(self):
        return True

class StatusUpdate:
    """StatusUpdate (Class Diagram) +updateStatus(status: String): void"""
    def updateStatus(self, appointment_id: str, status: str):
        conn = get_connection()
        conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appointment_id))
        conn.commit()
        conn.close()

class PaymentProcessor:
    """Orchestrates UC2 payment flow using all above classes"""
    def __init__(self):
        self.charge_check = ChargeCheck()
        self.cost_calc = CostCalculation()
        self.partial_mgmt = PartialManagement()
        self.debt_reg = DebtRegistration()
        self.status_update = StatusUpdate()
        self.pos = POSCommunication()

    def calculateCost(self, appointment_id: str) -> float:
        """Payment.calculateCost(appointmentId: String): Double"""
        return self.cost_calc.calculateAndDisplayTotal(appointment_id)

    def processPayment(self, appointment_id: str, owner_id: str,
                       amount: float, method: str, total: float) -> dict:
        """Payment.processPayment(): Boolean"""
        # UC2 Alt Flow 3: check charges
        if self.charge_check.detectMissingCharges(appointment_id):
            self.charge_check.terminateTemporarily()

        if method == "Κάρτα":
            try:
                self.pos.sendCardData(amount)
            except Exception as e:
                self.pos.rejectTransaction(str(e))
                raise ValueError("Η συναλλαγή με κάρτα απορρίφθηκε.")

        remaining = self.calculateRemaining(amount, total)
        status = "Paid" if remaining <= 0 else "Partial"

        conn = get_connection()
        conn.execute(
            "INSERT INTO payments (id,amount,method,pay_date,status,appointment_id,owner_id) VALUES (?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), amount, method, date.today().isoformat(), status, appointment_id, owner_id)
        )
        conn.commit()
        conn.close()

        if remaining > 0:
            self.partial_mgmt.forwardAsPartial(owner_id, remaining)

        self.status_update.updateStatus(appointment_id, "Completed")
        return {"status": status, "paid": amount, "remaining": remaining}

    def calculateRemaining(self, paid_amount: float, total: float) -> float:
        """Payment.calculateRemaining(paidAmount: Double): Double"""
        return max(0.0, total - paid_amount)
