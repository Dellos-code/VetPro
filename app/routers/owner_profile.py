from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_db
from app.models import Invoice, Pet, Role, User
from app.schemas import OwnerProfileResponse, PetResponse, InvoiceResponse, UserResponse
from app.security import require_role

router = APIRouter(prefix="/api/owner-profile", tags=["owner-profile"])


@router.get(
    "/{owner_id}",
    response_model=OwnerProfileResponse,
)
def get_owner_profile(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> OwnerProfileResponse:
    """UC7 — Προφίλ ιδιοκτήτη: κατοικίδια, χρέη, ανεξόφλητα τιμολόγια."""
    owner = db.get(User, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Ο ιδιοκτήτης δεν βρέθηκε")
    if owner.role != Role.OWNER:
        raise HTTPException(
            status_code=400,
            detail="Ο χρήστης δεν είναι ιδιοκτήτης",
        )

    pets = list(
        db.exec(select(Pet).where(Pet.owner_id == owner_id)).all()
    )
    unpaid = list(
        db.exec(
            select(Invoice).where(
                Invoice.owner_id == owner_id,
                Invoice.paid == False,  # noqa: E712
            )
        ).all()
    )
    total_debt = sum(
        (inv.remaining_amount or inv.total_amount) for inv in unpaid
    )

    return OwnerProfileResponse(
        user=UserResponse.model_validate(owner),
        pets=[PetResponse.model_validate(p) for p in pets],
        unpaid_invoices=[InvoiceResponse.model_validate(i) for i in unpaid],
        total_debt=total_debt,
    )
