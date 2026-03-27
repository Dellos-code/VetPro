from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Invoice, Payment, User
from app.schemas import PaymentCreate


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: PaymentCreate) -> Payment:
        payment = Payment(**payload.model_dump())
        self.db.add(payment)
        self.db.flush()

        # Auto-mark invoice as paid when total payments cover the invoice amount
        invoice = self.db.get(Invoice, payload.invoice_id)
        if invoice is not None:
            total_paid = self.db.exec(
                select(func.sum(Payment.amount)).where(
                    Payment.invoice_id == invoice.id
                )
            ).one_or_none() or Decimal(0)
            if total_paid >= invoice.total_amount:
                invoice.paid = True
                invoice.remaining_amount = Decimal("0.00")
            else:
                # UC2 — Μερική πληρωμή: υπολογισμός υπολοίπου
                invoice.remaining_amount = invoice.total_amount - total_paid

            # UC2 — Ενημέρωση χρέους ιδιοκτήτη
            owner = self.db.get(User, invoice.owner_id)
            if owner is not None:
                unpaid_invoices = self.db.exec(
                    select(Invoice).where(
                        Invoice.owner_id == owner.id,
                        Invoice.paid == False,  # noqa: E712
                    )
                ).all()
                owner.debt_balance = sum(
                    (inv.remaining_amount or inv.total_amount)
                    for inv in unpaid_invoices
                )

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_invoice(self, invoice_id: int) -> list[Payment]:
        return list(
            self.db.exec(
                select(Payment).where(Payment.invoice_id == invoice_id)
            ).all()
        )
