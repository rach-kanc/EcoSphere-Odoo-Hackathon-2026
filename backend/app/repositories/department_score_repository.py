"""Data access helpers for DepartmentScore records."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.department_score import DepartmentScore


class DepartmentScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, department_id: int, period: date) -> Optional[DepartmentScore]:
        return (
            self.db.query(DepartmentScore)
            .filter(
                DepartmentScore.department_id == department_id,
                DepartmentScore.period == period,
            )
            .one_or_none()
        )

    def upsert_environmental_score(
        self,
        *,
        department_id: int,
        period: date,
        environmental_score: float,
        environmental_weight: float,
    ) -> DepartmentScore:
        """Store the environmental component and recompute total_score.

        Social/Governance scores are not yet implemented elsewhere; they default
        to 0 until their own scoring engines land, and each is provisionally
        given half of the weight not claimed by the Environmental pillar.
        """
        row = self.get(department_id, period)
        if row is None:
            row = DepartmentScore(
                department_id=department_id,
                period=period,
                social_score=0.0,
                governance_score=0.0,
            )
            self.db.add(row)

        row.environmental_score = environmental_score
        remaining_weight = max(0.0, 1.0 - environmental_weight)
        other_weight = remaining_weight / 2
        row.total_score = round(
            environmental_score * environmental_weight
            + row.social_score * other_weight
            + row.governance_score * other_weight,
            1,
        )
        self.db.flush()
        return row
