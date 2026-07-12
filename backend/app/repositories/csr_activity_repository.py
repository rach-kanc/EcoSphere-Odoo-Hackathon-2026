"""Data access helpers for CSRActivity records."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.csr_activity import CSRActivity, CSRActivityStatus


class CSRActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        department_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[CSRActivityStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[CSRActivity]:
        query = self.db.query(CSRActivity)
        if department_id is not None:
            query = query.filter(CSRActivity.department_id == department_id)
        if category_id is not None:
            query = query.filter(CSRActivity.category_id == category_id)
        if status is not None:
            query = query.filter(CSRActivity.status == status)
        if date_from is not None:
            query = query.filter(
                or_(CSRActivity.end_date.is_(None), CSRActivity.end_date >= date_from)
            )
        if date_to is not None:
            query = query.filter(
                or_(CSRActivity.start_date.is_(None), CSRActivity.start_date <= date_to)
            )
        return query.order_by(CSRActivity.start_date.asc(), CSRActivity.id.asc()).all()

    def get(self, activity_id: int) -> Optional[CSRActivity]:
        return self.db.get(CSRActivity, activity_id)

    def create(self, activity: CSRActivity) -> CSRActivity:
        self.db.add(activity)
        self.db.flush()
        return activity

    def delete(self, activity: CSRActivity) -> None:
        self.db.delete(activity)
