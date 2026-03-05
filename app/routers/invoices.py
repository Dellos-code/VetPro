from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Invoice
from app.schemas import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    invoice = Invoice(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/owner/{owner_id}", response_model=list[InvoiceResponse])
def get_invoices_by_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Invoice]:
    return db.query(Invoice).filter(Invoice.owner_id == owner_id).all()


@router.get("/unpaid", response_model=list[InvoiceResponse])
def get_unpaid_invoices(
    db: Annotated[Session, Depends(get_db)],
) -> list[Invoice]:
    return db.query(Invoice).filter(Invoice.paid == False).all()  # noqa: E712


@router.put("/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.paid = True
    db.commit()
    db.refresh(invoice)
    return invoice
