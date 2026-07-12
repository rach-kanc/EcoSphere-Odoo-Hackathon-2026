"""Data access helpers for CarbonTransaction records."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.carbon_transaction import (
    CarbonTransaction,
    CreatedBy,
    SourceType,
    TransactionStatus,
)
from app.models.department import Department


class CarbonTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        department_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        status: Optional[TransactionStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[CarbonTransaction]:
        query = self.db.query(CarbonTransaction)
        if department_id is not None:
            query = query.filter(CarbonTransaction.department_id == department_id)
        if source_type is not None:
            query = query.filter(CarbonTransaction.source_type == source_type)
        if status is not None:
            query = query.filter(CarbonTransaction.status == status)
        if date_from is not None:
            query = query.filter(CarbonTransaction.transaction_date >= date_from)
        if date_to is not None:
            query = query.filter(CarbonTransaction.transaction_date <= date_to)
        return query.order_by(
            CarbonTransaction.transaction_date.desc(), CarbonTransaction.id.desc()
        ).all()

    def get(self, transaction_id: int) -> Optional[CarbonTransaction]:
        return self.db.get(CarbonTransaction, transaction_id)

    def find_auto_by_source(
        self, source_type: SourceType, source_record_id: int
    ) -> Optional[CarbonTransaction]:
        """Return the auto-created transaction for a source record, if any.

        Used by the auto emission engine to avoid creating duplicate
        transactions when a source record is re-ingested after an edit.
        """
        return (
            self.db.query(CarbonTransaction)
            .filter(
                CarbonTransaction.created_by == CreatedBy.AUTO,
                CarbonTransaction.source_type == source_type,
                CarbonTransaction.source_record_id == source_record_id,
            )
            .one_or_none()
        )

    def create(self, transaction: CarbonTransaction) -> CarbonTransaction:
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def aggregate_by_department(
        self,
        *,
        source_type: Optional[SourceType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list:
        """Return (department_id, department_name, count, total_co2e) rows."""
        query = (
            self.db.query(
                CarbonTransaction.department_id,
                Department.name,
                func.count(CarbonTransaction.id),
                func.coalesce(func.sum(CarbonTransaction.co2e), 0.0),
            )
            .outerjoin(Department, Department.id == CarbonTransaction.department_id)
        )
        if source_type is not None:
            query = query.filter(CarbonTransaction.source_type == source_type)
        if date_from is not None:
            query = query.filter(CarbonTransaction.transaction_date >= date_from)
        if date_to is not None:
            query = query.filter(CarbonTransaction.transaction_date <= date_to)
        return (
            query.group_by(CarbonTransaction.department_id, Department.name)
            .order_by(func.coalesce(func.sum(CarbonTransaction.co2e), 0.0).desc())
            .all()
        )
