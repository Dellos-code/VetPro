from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import SQLModel

from app.models import (
    AppointmentStatus,
    HospitalizationStatus,
    NotificationType,
    PaymentMethod,
    ReminderType,
    Role,
    SideEffectSeverity,
)


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
    debt_balance: Decimal = Decimal("0.00")


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
    priority: int = 1
    duration_minutes: int = 30


class AppointmentResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    veterinarian_id: int
    date_time: datetime
    reason: Optional[str] = None
    status: AppointmentStatus
    notes: Optional[str] = None
    priority: int = 1
    duration_minutes: int = 30


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


# ── Examination ──────────────────────────────────────────────────────

class ExaminationCreate(SQLModel):
    pet_id: int
    veterinarian_id: int
    date: datetime
    exam_type: str
    findings: Optional[str] = None
    recommendations: Optional[str] = None


class ExaminationResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: int
    veterinarian_id: int
    date: datetime
    exam_type: str
    findings: Optional[str] = None
    recommendations: Optional[str] = None


# ── Vaccine ──────────────────────────────────────────────────────────

class VaccineCreate(SQLModel):
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None
    default_interval_days: int = 365


class VaccineResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    manufacturer: Optional[str] = None
    target_species: Optional[str] = None
    default_interval_days: int = 365


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


# ── Side Effect ──────────────────────────────────────────────────────

class SideEffectCreate(SQLModel):
    vaccine_record_id: int
    description: str
    severity: SideEffectSeverity
    date_observed: date
    notes: Optional[str] = None


class SideEffectResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    vaccine_record_id: int
    description: str
    severity: SideEffectSeverity
    date_observed: date
    notes: Optional[str] = None


# ── Medication ───────────────────────────────────────────────────────

class MedicationCreate(SQLModel):
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int = 10
    avg_daily_demand: Optional[float] = None
    lead_time_mean: Optional[float] = None
    lead_time_std: Optional[float] = None


class MedicationResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: Optional[str] = None
    stock_quantity: int
    unit_price: Optional[Decimal] = None
    reorder_level: int
    avg_daily_demand: Optional[float] = None
    lead_time_mean: Optional[float] = None
    lead_time_std: Optional[float] = None


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
    remaining_amount: Decimal = Decimal("0.00")


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
    discharge_instructions: Optional[str] = None


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
    discharge_instructions: Optional[str] = None


# ── Hospitalization Log ──────────────────────────────────────────────

class HospitalizationLogCreate(SQLModel):
    hospitalization_id: int
    date: datetime
    temperature: Optional[float] = None
    diet: Optional[str] = None
    medications_given: Optional[str] = None
    observations: Optional[str] = None


class HospitalizationLogResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    hospitalization_id: int
    date: datetime
    temperature: Optional[float] = None
    diet: Optional[str] = None
    medications_given: Optional[str] = None
    observations: Optional[str] = None


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


# ── Notification ─────────────────────────────────────────────────────

class NotificationCreate(SQLModel):
    user_id: int
    message: str
    notification_type: NotificationType
    scheduled_date: datetime
    sent: bool = False
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None


class NotificationResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    message: str
    notification_type: NotificationType
    scheduled_date: datetime
    sent: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None


# ── Report ───────────────────────────────────────────────────────────

class ReportCreate(SQLModel):
    pet_id: Optional[int] = None
    generated_by_id: int
    report_type: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    generated_at: datetime
    content: Optional[str] = None


class ReportResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    pet_id: Optional[int] = None
    generated_by_id: int
    report_type: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    generated_at: datetime
    content: Optional[str] = None


# ── Composite / UC-specific schemas ─────────────────────────────────

class AnimalHistoryResponse(SQLModel):
    """UC1 — Πλήρες ιστορικό ζώου."""
    pet: PetResponse
    medical_records: List[MedicalRecordResponse] = []
    vaccine_records: List[VaccineRecordResponse] = []
    examinations: List[ExaminationResponse] = []
    # UC1 alt flow — Μήνυμα εάν το ιστορικό είναι κενό
    message: Optional[str] = None


class AnimalSearchResponse(SQLModel):
    """UC1 — Αποτελέσματα αναζήτησης ζώων (πολλαπλά αποτελέσματα / συνώνυμα)."""
    results: List[PetResponse] = []
    count: int = 0
    # UC1 alt flow — Μήνυμα πολλαπλών αποτελεσμάτων
    message: Optional[str] = None


class OwnerProfileResponse(SQLModel):
    """UC7 — Προφίλ ιδιοκτήτη με κατοικίδια και χρέη."""
    user: UserResponse
    pets: List[PetResponse] = []
    unpaid_invoices: List[InvoiceResponse] = []
    total_debt: Decimal = Decimal("0.00")


class AllergyCheckResult(SQLModel):
    """UC3 — Αποτέλεσμα ελέγχου αλλεργίας εμβολιασμού."""
    has_previous_reaction: bool = False
    previous_side_effects: List[SideEffectResponse] = []
    warning_message: Optional[str] = None


# ── Σχήματα ρόλων — Role-specific entity schemas ────────────────────


class VeterinarianCreate(SQLModel):
    user_id: int
    specialization: Optional[str] = None
    license_number: Optional[str] = None


class VeterinarianResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    specialization: Optional[str] = None
    license_number: Optional[str] = None


class AdministratorCreate(SQLModel):
    user_id: int
    department: Optional[str] = None


class AdministratorResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    department: Optional[str] = None


class OwnerCreate(SQLModel):
    user_id: int
    address: Optional[str] = None


class OwnerResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    address: Optional[str] = None


class ReceptionistCreate(SQLModel):
    user_id: int
    desk_number: Optional[str] = None


class ReceptionistResponse(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    desk_number: Optional[str] = None
