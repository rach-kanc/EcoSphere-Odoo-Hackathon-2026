"""Data access helpers for CSR employee participations."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.csr_activity import EmployeeParticipation


class EmployeeParticipationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, participation_id: int) -> Optional[EmployeeParticipation]:
        return self.db.get(EmployeeParticipation, participation_id)

    def get_by_employee_and_activity(
        self, employee_id: int, activity_id: int
    ) -> Optional[EmployeeParticipation]:
        return (
            self.db.query(EmployeeParticipation)
            .filter(
                EmployeeParticipation.employee_id == employee_id,
                EmployeeParticipation.activity_id == activity_id,
            )
            .one_or_none()
        )

    def create(
        self, participation: EmployeeParticipation
    ) -> EmployeeParticipation:
        self.db.add(participation)
        self.db.flush()
        return participation
