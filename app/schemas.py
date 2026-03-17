from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import SQLModel

from app.models import AppointmentStatus, PaymentMethod, ReminderType, Role


# ── User ─────────────────────────────────────────────────────────────

class UserCreate(SQLModel):
    username: str
    password: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: Role
    enabled: bool = True


class UserResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: Role
    enabled: bool


# ── Pet ──────────────────────────────────────────────────────────────

class PetCreate(SQLModel):
    name: str
    species: str
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    microchip_number: Optional[str] = None
    owner_id: Optional[int] = None


class PetResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    species: str
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    microchip_number: Optional[str] = None
    owner_id: Optional[int] = None


# ── Appointment ──────────────────────────────────────────────────────

class AppointmentCreate(SQLModel):
    pet_id: int
    veterinarian_id: int
    date_time: datetime
    reason: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None


class AppointmentResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    veterinarian_id: int
    date_time: datetime
    reason: Optional[str] = None
    status: AppointmentStatus
    notes: Optional[str] = None


# ── Medical Record ───────────────────────────────────────────────────

class MedicalRecordCreate(SQLModel):
    pet_id: int
    veterinarian_id: int
    date: datetime
    diagnosis: str
    treatment: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    veterinarian_id: int
    date: datetime
    diagnosis: str
    treatment: Optional[str] = None
    notes: Optional[str] = None


# ── Vaccine ──────────────────────────────────────────────────────────

class VaccineCreate(SQLModel):
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None


class VaccineResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None


# ── Vaccine Record ───────────────────────────────────────────────────

class VaccineRecordCreate(SQLModel):
    pet_id: int
    vaccine_id: int
    administered_by_id: int
    date_administered: date
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None


class VaccineRecordResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    vaccine_id: int
    administered_by_id: int
    date_administered: date
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None


# ── Medication ───────────────────────────────────────────────────────

class MedicationCreate(SQLModel):
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int = 10


class MedicationResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int


# ── Prescription ─────────────────────────────────────────────────────

class PrescriptionCreate(SQLModel):
    medical_record_id: int
    medication_id: int
    dosage: str
    frequency: str
    duration_days: Optional[int] = None
    instructions: Optional[str] = None


class PrescriptionResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    medical_record_id: int
    medication_id: int
    dosage: str
    frequency: str
    duration_days: Optional[int] = None
    instructions: Optional[str] = None


# ── Invoice ──────────────────────────────────────────────────────────

class InvoiceCreate(SQLModel):
    owner_id: int
    appointment_id: Optional[int] = None
    date_issued: datetime
    total_amount: Decimal
    paid: bool = False
    description: Optional[str] = None


class InvoiceResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    owner_id: int
    appointment_id: Optional[int] = None
    date_issued: datetime
    total_amount: Decimal
    paid: bool
    description: Optional[str] = None


# ── Payment ──────────────────────────────────────────────────────────

class PaymentCreate(SQLModel):
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod


class PaymentResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod


# ── Hospitalization ──────────────────────────────────────────────────

class HospitalizationCreate(SQLModel):
    pet_id: int
    veterinarian_id: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    reason: str
    status: Optional[str] = None
    daily_notes: Optional[str] = None


class HospitalizationResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    veterinarian_id: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    reason: str
    status: Optional[str] = None
    daily_notes: Optional[str] = None


# ── Reminder ─────────────────────────────────────────────────────────

class ReminderCreate(SQLModel):
    user_id: int
    message: str
    reminder_date: datetime
    sent: bool = False
    type: ReminderType


class ReminderResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    message: str
    reminder_date: datetime
    sent: bool
    type: ReminderType
