"""Data access helpers for PendingAutoCalculation records."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.carbon_transaction import SourceType
from app.models.pending_auto_calculation import PendingAutoCalculation, PendingStatus


class PendingAutoCalculationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self, *, status: Optional[PendingStatus] = None
    ) -> list[PendingAutoCalculation]:
        query = self.db.query(PendingAutoCalculation)
        if status is not None:
            query = query.filter(PendingAutoCalculation.status == status)
        return query.order_by(PendingAutoCalculation.created_at.desc()).all()

    def get(self, pending_id: int) -> Optional[PendingAutoCalculation]:
        return self.db.get(PendingAutoCalculation, pending_id)

    def find_by_source(
        self, source_type: SourceType, source_record_id: int
    ) -> Optional[PendingAutoCalculation]:
        return (
            self.db.query(PendingAutoCalculation)
            .filter(
                PendingAutoCalculation.source_type == source_type,
                PendingAutoCalculation.source_record_id == source_record_id,
            )
            .one_or_none()
        )

    def create(self, pending: PendingAutoCalculation) -> PendingAutoCalculation:
        self.db.add(pending)
        self.db.flush()
        return pending
