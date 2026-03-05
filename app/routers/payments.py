from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Invoice, Payment
from app.schemas import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Payment:
    payment = Payment(**payload.model_dump())
    db.add(payment)
    db.flush()

    # Auto-mark invoice as paid when total payments cover the invoice amount
    invoice = db.get(Invoice, payload.invoice_id)
    if invoice is not None:
        total_paid = (
            db.query(func.sum(Payment.amount))
            .filter(Payment.invoice_id == invoice.id)
            .scalar()
        ) or Decimal(0)
        if total_paid >= invoice.total_amount:
            invoice.paid = True

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/invoice/{invoice_id}", response_model=list[PaymentResponse])
def get_payments_by_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Payment]:
    return db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
