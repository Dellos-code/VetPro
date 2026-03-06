from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import Field, Relationship, SQLModel


# ── Enums ────────────────────────────────────────────────────────────

class Role(str, enum.Enum):
    OWNER = "OWNER"
    VET = "VET"
    RECEPTIONIST = "RECEPTIONIST"
    ADMIN = "ADMIN"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"


class ReminderType(str, enum.Enum):
    VACCINE = "VACCINE"
    APPOINTMENT = "APPOINTMENT"
    FOLLOWUP = "FOLLOWUP"
    GENERAL = "GENERAL"


# ── Models ───────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    email: str = Field(unique=True, nullable=False)
    phone: Optional[str] = Field(default=None)
    role: Role = Field(sa_column=Column(SAEnum(Role), nullable=False))
    enabled: bool = Field(default=True)

    pets: list[Pet] = Relationship(back_populates="owner")
    reminders: list[Reminder] = Relationship(back_populates="user")


class Pet(SQLModel, table=True):
    __tablename__ = "pets"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    species: str = Field(nullable=False)
    breed: Optional[str] = Field(default=None)
    date_of_birth: Optional[date] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    microchip_number: Optional[str] = Field(default=None, unique=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")

    owner: Optional[User] = Relationship(back_populates="pets")
    medical_records: list[MedicalRecord] = Relationship(
        back_populates="pet",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    vaccine_records: list[VaccineRecord] = Relationship(
        back_populates="pet",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    veterinarian_id: int = Field(foreign_key="users.id", nullable=False)
    date_time: datetime = Field(nullable=False)
    reason: Optional[str] = Field(default=None)
    status: AppointmentStatus = Field(
        sa_column=Column(SAEnum(AppointmentStatus), nullable=False),
    )
    notes: Optional[str] = Field(default=None)

    pet: Pet = Relationship()
    veterinarian: User = Relationship()


class MedicalRecord(SQLModel, table=True):
    __tablename__ = "medical_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    veterinarian_id: int = Field(foreign_key="users.id", nullable=False)
    date: datetime = Field(nullable=False)
    diagnosis: str = Field(nullable=False)
    treatment: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    pet: Pet = Relationship(back_populates="medical_records")
    veterinarian: User = Relationship()
    prescriptions: list[Prescription] = Relationship(
        back_populates="medical_record",
    )


class Vaccine(SQLModel, table=True):
    __tablename__ = "vaccines"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    manufacturer: Optional[str] = Field(default=None)
    target_species: Optional[str] = Field(default=None)


class VaccineRecord(SQLModel, table=True):
    __tablename__ = "vaccine_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    vaccine_id: int = Field(foreign_key="vaccines.id", nullable=False)
    administered_by_id: int = Field(foreign_key="users.id", nullable=False)
    date_administered: date = Field(nullable=False)
    next_due_date: Optional[date] = Field(default=None)
    batch_number: Optional[str] = Field(default=None)

    pet: Pet = Relationship(back_populates="vaccine_records")
    vaccine: Vaccine = Relationship()
    administered_by: User = Relationship()


class Medication(SQLModel, table=True):
    __tablename__ = "medications"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default=None)
    stock_quantity: int = Field(nullable=False)
    unit_price: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )
    reorder_level: int = Field(default=10, nullable=False)


class Prescription(SQLModel, table=True):
    __tablename__ = "prescriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    medical_record_id: int = Field(
        foreign_key="medical_records.id", nullable=False,
    )
    medication_id: int = Field(foreign_key="medications.id", nullable=False)
    dosage: str = Field(nullable=False)
    frequency: str = Field(nullable=False)
    duration_days: Optional[int] = Field(default=None)
    instructions: Optional[str] = Field(default=None)

    medical_record: MedicalRecord = Relationship(
        back_populates="prescriptions",
    )
    medication: Medication = Relationship()


class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", nullable=False)
    appointment_id: Optional[int] = Field(
        default=None, foreign_key="appointments.id",
    )
    date_issued: datetime = Field(nullable=False)
    total_amount: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    paid: bool = Field(default=False)
    description: Optional[str] = Field(default=None)

    owner: User = Relationship()
    appointment: Optional[Appointment] = Relationship()
    payments: list[Payment] = Relationship(back_populates="invoice")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id", nullable=False)
    amount: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    payment_date: datetime = Field(nullable=False)
    method: PaymentMethod = Field(
        sa_column=Column(SAEnum(PaymentMethod), nullable=False),
    )

    invoice: Invoice = Relationship(back_populates="payments")


class Hospitalization(SQLModel, table=True):
    __tablename__ = "hospitalizations"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    veterinarian_id: int = Field(foreign_key="users.id", nullable=False)
    admission_date: datetime = Field(nullable=False)
    discharge_date: Optional[datetime] = Field(default=None)
    reason: str = Field(nullable=False)
    status: Optional[str] = Field(default=None)
    daily_notes: Optional[str] = Field(default=None)

    pet: Pet = Relationship()
    veterinarian: User = Relationship()


class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    message: str = Field(nullable=False)
    reminder_date: datetime = Field(nullable=False)
    sent: bool = Field(default=False)
    type: ReminderType = Field(
        sa_column=Column(SAEnum(ReminderType), nullable=False),
    )

    user: User = Relationship(back_populates="reminders")
