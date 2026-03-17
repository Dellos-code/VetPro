from __future__ import annotations

from sqlmodel import Session, select

from app.models import Invoice
from app.schemas import InvoiceCreate


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: InvoiceCreate) -> Invoice:
        invoice = Invoice(**payload.model_dump())
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
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
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
