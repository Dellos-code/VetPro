from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.config import settings
from app.database import engine
from app.routers import (
    animal_history,
    appointments,
    examinations,
    generated_reports,
    hospitalizations,
    invoices,
    medical_records,
    medications,
    notifications,
    owner_profile,
    payments,
    pets,
    prescriptions,
    reminders,
    reports,
    users,
    vaccine_records,
    vaccines,
)
from engines.api import app as engine_app


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CRUD routers
app.include_router(users.router)
app.include_router(pets.router)
app.include_router(appointments.router)
app.include_router(medical_records.router)
app.include_router(vaccines.router)
app.include_router(vaccine_records.router)
app.include_router(prescriptions.router)
app.include_router(medications.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(hospitalizations.router)
app.include_router(reminders.router)
app.include_router(reports.router)

# UC-specific routers
app.include_router(examinations.router)
app.include_router(notifications.router)
app.include_router(animal_history.router)
app.include_router(owner_profile.router)
app.include_router(generated_reports.router)

# Engine routes from the existing micro-service
app.mount("/engines", engine_app)
