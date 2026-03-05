from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    pets: Mapped[list[Pet]] = relationship("Pet", back_populates="owner")
    reminders: Mapped[list[Reminder]] = relationship("Reminder", back_populates="user")


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    species: Mapped[str] = mapped_column(String, nullable=False)
    breed: Mapped[str | None] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    microchip_number: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True,
    )
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True,
    )

    owner: Mapped[User | None] = relationship("User", back_populates="pets")
    medical_records: Mapped[list[MedicalRecord]] = relationship(
        "MedicalRecord", back_populates="pet", cascade="all, delete-orphan",
    )
    vaccine_records: Mapped[list[VaccineRecord]] = relationship(
        "VaccineRecord", back_populates="pet", cascade="all, delete-orphan",
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pets.id"), nullable=False,
    )
    veterinarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    pet: Mapped[Pet] = relationship("Pet")
    veterinarian: Mapped[User] = relationship("User")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pets.id"), nullable=False,
    )
    veterinarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    diagnosis: Mapped[str] = mapped_column(String, nullable=False)
    treatment: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    pet: Mapped[Pet] = relationship("Pet", back_populates="medical_records")
    veterinarian: Mapped[User] = relationship("User")
    prescriptions: Mapped[list[Prescription]] = relationship(
        "Prescription", back_populates="medical_record",
    )


class Vaccine(Base):
    __tablename__ = "vaccines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
    target_species: Mapped[str | None] = mapped_column(String, nullable=True)


class VaccineRecord(Base):
    __tablename__ = "vaccine_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pets.id"), nullable=False,
    )
    vaccine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vaccines.id"), nullable=False,
    )
    administered_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    date_administered: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String, nullable=True)

    pet: Mapped[Pet] = relationship("Pet", back_populates="vaccine_records")
    vaccine: Mapped[Vaccine] = relationship("Vaccine")
    administered_by: Mapped[User] = relationship("User")


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    medical_record_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medical_records.id"), nullable=False,
    )
    medication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medications.id"), nullable=False,
    )
    dosage: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instructions: Mapped[str | None] = mapped_column(String, nullable=True)

    medical_record: Mapped[MedicalRecord] = relationship(
        "MedicalRecord", back_populates="prescriptions",
    )
    medication: Mapped[Medication] = relationship("Medication")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    appointment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("appointments.id"), nullable=True,
    )
    date_issued: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    owner: Mapped[User] = relationship("User")
    appointment: Mapped[Appointment | None] = relationship("Appointment")
    payments: Mapped[list[Payment]] = relationship(
        "Payment", back_populates="invoice",
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id"), nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False,
    )

    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="payments")


class Hospitalization(Base):
    __tablename__ = "hospitalizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pets.id"), nullable=False,
    )
    veterinarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    admission_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    discharge_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    daily_notes: Mapped[str | None] = mapped_column(String, nullable=True)

    pet: Mapped[Pet] = relationship("Pet")
    veterinarian: Mapped[User] = relationship("User")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    message: Mapped[str] = mapped_column(String, nullable=False)
    reminder_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[ReminderType] = mapped_column(Enum(ReminderType), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="reminders")
