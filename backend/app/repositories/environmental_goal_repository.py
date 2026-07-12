"""Data access helpers for EnvironmentalGoal records."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.carbon_transaction import CarbonTransaction, TransactionStatus
from app.models.environmental_goal import EnvironmentalGoal


class EnvironmentalGoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, *, department_id: Optional[int] = None) -> list[EnvironmentalGoal]:
        query = self.db.query(EnvironmentalGoal)
        if department_id is not None:
            query = query.filter(EnvironmentalGoal.department_id == department_id)
        return query.order_by(EnvironmentalGoal.deadline.asc(), EnvironmentalGoal.id.asc()).all()

    def get(self, goal_id: int) -> Optional[EnvironmentalGoal]:
        return self.db.get(EnvironmentalGoal, goal_id)

    def create(self, goal: EnvironmentalGoal) -> EnvironmentalGoal:
        self.db.add(goal)
        self.db.flush()
        return goal

    def sum_confirmed_co2e(
        self,
        *,
        department_id: Optional[int],
        date_from: Optional[date],
        date_to: date,
    ) -> float:
        query = self.db.query(func.coalesce(func.sum(CarbonTransaction.co2e), 0.0)).filter(
            CarbonTransaction.status == TransactionStatus.CONFIRMED,
            CarbonTransaction.transaction_date <= date_to,
        )
        if department_id is not None:
            query = query.filter(CarbonTransaction.department_id == department_id)
        if date_from is not None:
            query = query.filter(CarbonTransaction.transaction_date >= date_from)
        return float(query.scalar() or 0.0)
