from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import AppointmentStatus, PaymentMethod, ReminderType, Role


# ── User ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: Role
    enabled: bool = True


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: Role
    enabled: bool


# ── Pet ──────────────────────────────────────────────────────────────

class PetCreate(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    microchip_number: Optional[str] = None
    owner_id: Optional[int] = None


class PetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    species: str
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    microchip_number: Optional[str] = None
    owner_id: Optional[int] = None


# ── Appointment ──────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    pet_id: int
    veterinarian_id: int
    date_time: datetime
    reason: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    veterinarian_id: int
    date_time: datetime
    reason: Optional[str] = None
    status: AppointmentStatus
    notes: Optional[str] = None


# ── Medical Record ───────────────────────────────────────────────────

class MedicalRecordCreate(BaseModel):
    pet_id: int
    veterinarian_id: int
    date: datetime
    diagnosis: str
    treatment: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    veterinarian_id: int
    date: datetime
    diagnosis: str
    treatment: Optional[str] = None
    notes: Optional[str] = None


# ── Vaccine ──────────────────────────────────────────────────────────

class VaccineCreate(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None


class VaccineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None


# ── Vaccine Record ───────────────────────────────────────────────────

class VaccineRecordCreate(BaseModel):
    pet_id: int
    vaccine_id: int
    administered_by_id: int
    date_administered: date
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None


class VaccineRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    vaccine_id: int
    administered_by_id: int
    date_administered: date
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None


# ── Medication ───────────────────────────────────────────────────────

class MedicationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int = 10


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int


# ── Prescription ─────────────────────────────────────────────────────

class PrescriptionCreate(BaseModel):
    medical_record_id: int
    medication_id: int
    dosage: str
    frequency: str
    duration_days: Optional[int] = None
    instructions: Optional[str] = None


class PrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medical_record_id: int
    medication_id: int
    dosage: str
    frequency: str
    duration_days: Optional[int] = None
    instructions: Optional[str] = None


# ── Invoice ──────────────────────────────────────────────────────────

class InvoiceCreate(BaseModel):
    owner_id: int
    appointment_id: Optional[int] = None
    date_issued: datetime
    total_amount: Decimal
    paid: bool = False
    description: Optional[str] = None


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    appointment_id: Optional[int] = None
    date_issued: datetime
    total_amount: Decimal
    paid: bool
    description: Optional[str] = None


# ── Payment ──────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod


# ── Hospitalization ──────────────────────────────────────────────────

class HospitalizationCreate(BaseModel):
    pet_id: int
    veterinarian_id: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    reason: str
    status: Optional[str] = None
    daily_notes: Optional[str] = None


class HospitalizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    veterinarian_id: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    reason: str
    status: Optional[str] = None
    daily_notes: Optional[str] = None


# ── Reminder ─────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    user_id: int
    message: str
    reminder_date: datetime
    sent: bool = False
    type: ReminderType


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message: str
    reminder_date: datetime
    sent: bool
    type: ReminderType
