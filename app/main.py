from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import (
    appointments,
    hospitalizations,
    invoices,
    medical_records,
    medications,
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
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="VetPro", version="1.0.0", lifespan=lifespan)

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

# Engine routes from the existing micro-service
app.mount("/engines", engine_app)
