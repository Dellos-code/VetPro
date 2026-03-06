from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Invoice, Payment
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

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_invoice(self, invoice_id: int) -> list[Payment]:
        return list(
            self.db.exec(
                select(Payment).where(Payment.invoice_id == invoice_id)
            ).all()
        )
