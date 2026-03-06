from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_db
from app.models import Invoice
from app.schemas import InvoiceCreate, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    svc = InvoiceService(db)
    return svc.create(payload)


@router.get("/owner/{owner_id}", response_model=list[InvoiceResponse])
def get_invoices_by_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Invoice]:
    svc = InvoiceService(db)
    return svc.get_by_owner(owner_id)


@router.get("/unpaid", response_model=list[InvoiceResponse])
def get_unpaid_invoices(
    db: Annotated[Session, Depends(get_db)],
) -> list[Invoice]:
    svc = InvoiceService(db)
    return svc.get_unpaid()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    svc = InvoiceService(db)
    invoice = svc.get_by_id(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Invoice:
    svc = InvoiceService(db)
    invoice = svc.get_by_id(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return svc.mark_paid(invoice)
