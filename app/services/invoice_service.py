from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session, select

from app.models import Invoice, User
from app.schemas import InvoiceCreate


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: InvoiceCreate) -> Invoice:
        invoice = Invoice(**payload.model_dump())
        # UC2 — Αρχικοποίηση υπολοίπου
        if not invoice.paid:
            invoice.remaining_amount = invoice.total_amount
        else:
            invoice.remaining_amount = Decimal("0.00")
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        # UC2 — Ενημέρωση χρέους ιδιοκτήτη
        if not invoice.paid:
            owner = self.db.get(User, invoice.owner_id)
            if owner is not None:
                unpaid = self.db.exec(
                    select(Invoice).where(
                        Invoice.owner_id == owner.id,
                        Invoice.paid == False,  # noqa: E712
                    )
                ).all()
                owner.debt_balance = sum(
                    (inv.remaining_amount or inv.total_amount)
                    for inv in unpaid
                )
                self.db.commit()
                self.db.refresh(owner)
        return invoice

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)

    def get_by_owner(self, owner_id: int) -> list[Invoice]:
        return list(
            self.db.exec(
                select(Invoice).where(Invoice.owner_id == owner_id)
            ).all()
        )

    def get_unpaid(self) -> list[Invoice]:
        return list(
            self.db.exec(
                select(Invoice).where(Invoice.paid == False)  # noqa: E712
            ).all()
        )

    def mark_paid(self, invoice: Invoice) -> Invoice:
        invoice.paid = True
        invoice.remaining_amount = Decimal("0.00")
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
