from __future__ import annotations

import json
from datetime import date, datetime

from sqlmodel import Session, select

from app.models import (
    Examination,
    MedicalRecord,
    Pet,
    Report,
    VaccineRecord,
)
from app.schemas import ReportCreate


class ReportEntityService:
    """UC6 — Δημιουργία αναφορών ιατρικού ιστορικού."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_medical_history_report(
        self,
        pet_id: int,
        generated_by_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Report:
        """Δημιουργία αναφοράς ιστορικού — generates a report with filtered medical data."""
        pet = self.db.get(Pet, pet_id)
        if pet is None:
            raise ValueError("Το ζώο δεν βρέθηκε")

        # Φίλτρα ημερομηνιών
        records_q = select(MedicalRecord).where(MedicalRecord.pet_id == pet_id)
        vaccines_q = select(VaccineRecord).where(VaccineRecord.pet_id == pet_id)
        exams_q = select(Examination).where(Examination.pet_id == pet_id)

        if date_from:
            dt_from = datetime.combine(date_from, datetime.min.time())
            records_q = records_q.where(MedicalRecord.date >= dt_from)
            exams_q = exams_q.where(Examination.date >= dt_from)
            vaccines_q = vaccines_q.where(
                VaccineRecord.date_administered >= date_from
            )
        if date_to:
            dt_to = datetime.combine(date_to, datetime.max.time())
            records_q = records_q.where(MedicalRecord.date <= dt_to)
            exams_q = exams_q.where(Examination.date <= dt_to)
            vaccines_q = vaccines_q.where(
                VaccineRecord.date_administered <= date_to
            )

        records = list(self.db.exec(records_q).all())
        vaccines = list(self.db.exec(vaccines_q).all())
        exams = list(self.db.exec(exams_q).all())

        content = json.dumps(
            {
                "pet_name": pet.name,
                "species": pet.species,
                "medical_records_count": len(records),
                "vaccine_records_count": len(vaccines),
                "examinations_count": len(exams),
                "medical_records": [
                    {
                        "date": r.date.isoformat(),
                        "diagnosis": r.diagnosis,
                        "treatment": r.treatment,
                    }
                    for r in records
                ],
                "vaccine_records": [
                    {
                        "date": v.date_administered.isoformat(),
                        "vaccine_id": v.vaccine_id,
                    }
                    for v in vaccines
                ],
                "examinations": [
                    {
                        "date": e.date.isoformat(),
                        "type": e.exam_type,
                        "findings": e.findings,
                    }
                    for e in exams
                ],
            },
            ensure_ascii=False,
        )

        report = Report(
            pet_id=pet_id,
            generated_by_id=generated_by_id,
            report_type="medical_history",
            date_from=date_from,
            date_to=date_to,
            generated_at=datetime.now(),
            content=content,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_id(self, report_id: int) -> Report | None:
        return self.db.get(Report, report_id)

    def get_by_pet(self, pet_id: int) -> list[Report]:
        return list(
            self.db.exec(
                select(Report).where(Report.pet_id == pet_id)
            ).all()
        )
