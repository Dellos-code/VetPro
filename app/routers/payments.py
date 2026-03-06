from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_db
from app.models import Payment
from app.schemas import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Payment:
    svc = PaymentService(db)
    return svc.create(payload)


@router.get("/invoice/{invoice_id}", response_model=list[PaymentResponse])
def get_payments_by_invoice(
    invoice_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[Payment]:
    svc = PaymentService(db)
    return svc.get_by_invoice(invoice_id)
