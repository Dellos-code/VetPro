import enum
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, Enum as SAEnum, Numeric, Text
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


class NotificationType(str, enum.Enum):
    VACCINE_REMINDER = "VACCINE_REMINDER"
    APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER"
    FOLLOWUP = "FOLLOWUP"
    GENERAL = "GENERAL"


class SideEffectSeverity(str, enum.Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"


class HospitalizationStatus(str, enum.Enum):
    ADMITTED = "ADMITTED"
    DISCHARGED = "DISCHARGED"


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
    # Χρέος ιδιοκτήτη - debt balance for owners (UC2 partial payment)
    debt_balance: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=0),
    )

    pets: List["Pet"] = Relationship(back_populates="owner")
    reminders: List["Reminder"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")


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

    owner: Optional["User"] = Relationship(back_populates="pets")
    medical_records: List["MedicalRecord"] = Relationship(
        back_populates="pet",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    vaccine_records: List["VaccineRecord"] = Relationship(
        back_populates="pet",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    examinations: List["Examination"] = Relationship(
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
    # Προτεραιότητα ραντεβού (1-5, 5=EMERGENCY) — used by UC9 heuristic scheduler
    priority: int = Field(default=1, nullable=False)
    duration_minutes: int = Field(default=30, nullable=False)

    pet: Optional["Pet"] = Relationship()
    veterinarian: Optional["User"] = Relationship()


class MedicalRecord(SQLModel, table=True):
    __tablename__ = "medical_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    veterinarian_id: int = Field(foreign_key="users.id", nullable=False)
    date: datetime = Field(nullable=False)
    diagnosis: str = Field(nullable=False)
    treatment: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    pet: Optional["Pet"] = Relationship(back_populates="medical_records")
    veterinarian: Optional["User"] = Relationship()
    prescriptions: List["Prescription"] = Relationship(
        back_populates="medical_record",
    )


class Examination(SQLModel, table=True):
    """Εξέταση — clinical examination entity (UC1)."""
    __tablename__ = "examinations"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    veterinarian_id: int = Field(foreign_key="users.id", nullable=False)
    date: datetime = Field(nullable=False)
    exam_type: str = Field(nullable=False)
    findings: Optional[str] = Field(default=None)
    recommendations: Optional[str] = Field(default=None)

    pet: Optional["Pet"] = Relationship(back_populates="examinations")
    veterinarian: Optional["User"] = Relationship()


class Vaccine(SQLModel, table=True):
    __tablename__ = "vaccines"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    manufacturer: Optional[str] = Field(default=None)
    target_species: Optional[str] = Field(default=None)
    # Ημέρες μέχρι επόμενη δόση — default interval for auto-calculating next dose
    default_interval_days: int = Field(default=365, nullable=False)


class VaccineRecord(SQLModel, table=True):
    __tablename__ = "vaccine_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: int = Field(foreign_key="pets.id", nullable=False)
    vaccine_id: int = Field(foreign_key="vaccines.id", nullable=False)
    administered_by_id: int = Field(foreign_key="users.id", nullable=False)
    date_administered: date = Field(nullable=False)
    next_due_date: Optional[date] = Field(default=None)
    batch_number: Optional[str] = Field(default=None)

    pet: Optional["Pet"] = Relationship(back_populates="vaccine_records")
    vaccine: Optional["Vaccine"] = Relationship()
    administered_by: Optional["User"] = Relationship()
    side_effects: List["SideEffect"] = Relationship(
        back_populates="vaccine_record",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class SideEffect(SQLModel, table=True):
    """Παρενέργεια — records post-vaccination side effects (UC3)."""
    __tablename__ = "side_effects"

    id: Optional[int] = Field(default=None, primary_key=True)
    vaccine_record_id: int = Field(
        foreign_key="vaccine_records.id", nullable=False,
    )
    description: str = Field(nullable=False)
    severity: SideEffectSeverity = Field(
        sa_column=Column(SAEnum(SideEffectSeverity), nullable=False),
    )
    date_observed: date = Field(nullable=False)
    notes: Optional[str] = Field(default=None)

    vaccine_record: Optional["VaccineRecord"] = Relationship(
        back_populates="side_effects",
    )


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
    # Μέση ημερήσια κατανάλωση — average daily demand for UC10 forecasting
    avg_daily_demand: Optional[float] = Field(default=None)
    # Μέσος χρόνος παράδοσης — mean lead time in days
    lead_time_mean: Optional[float] = Field(default=None)
    # Τυπική απόκλιση χρόνου παράδοσης
    lead_time_std: Optional[float] = Field(default=None)


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

    medical_record: Optional["MedicalRecord"] = Relationship(
        back_populates="prescriptions",
    )
    medication: Optional["Medication"] = Relationship()


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
    # Χρέος — remaining unpaid amount for partial payments (UC2)
    remaining_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=0),
    )

    owner: Optional["User"] = Relationship()
    appointment: Optional["Appointment"] = Relationship()
    payments: List["Payment"] = Relationship(back_populates="invoice")


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

    invoice: Optional["Invoice"] = Relationship(back_populates="payments")


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
    # Οδηγίες εξιτηρίου — discharge instructions (UC4)
    discharge_instructions: Optional[str] = Field(default=None)

    pet: Optional["Pet"] = Relationship()
    veterinarian: Optional["User"] = Relationship()
    daily_logs: List["HospitalizationLog"] = Relationship(
        back_populates="hospitalization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class HospitalizationLog(SQLModel, table=True):
    """Ημερήσιο αρχείο νοσηλείας — daily clinical log during hospitalization (UC4)."""
    __tablename__ = "hospitalization_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    hospitalization_id: int = Field(
        foreign_key="hospitalizations.id", nullable=False,
    )
    date: datetime = Field(nullable=False)
    temperature: Optional[float] = Field(default=None)
    diet: Optional[str] = Field(default=None)
    medications_given: Optional[str] = Field(default=None)
    observations: Optional[str] = Field(default=None)

    hospitalization: Optional["Hospitalization"] = Relationship(
        back_populates="daily_logs",
    )


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

    user: Optional["User"] = Relationship(back_populates="reminders")


class Notification(SQLModel, table=True):
    """Ειδοποίηση — scheduled notification entity (UC8)."""
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    message: str = Field(nullable=False)
    notification_type: NotificationType = Field(
        sa_column=Column(SAEnum(NotificationType), nullable=False),
    )
    scheduled_date: datetime = Field(nullable=False)
    sent: bool = Field(default=False)
    related_entity_type: Optional[str] = Field(default=None)
    related_entity_id: Optional[int] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="notifications")


class Report(SQLModel, table=True):
    """Αναφορά — generated report entity (UC6)."""
    __tablename__ = "reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    pet_id: Optional[int] = Field(default=None, foreign_key="pets.id")
    generated_by_id: int = Field(foreign_key="users.id", nullable=False)
    report_type: str = Field(nullable=False)
    date_from: Optional[date] = Field(default=None)
    date_to: Optional[date] = Field(default=None)
    generated_at: datetime = Field(nullable=False)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))

    pet: Optional["Pet"] = Relationship()
    generated_by: Optional["User"] = Relationship()
