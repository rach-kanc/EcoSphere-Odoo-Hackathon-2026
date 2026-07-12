"""Environmental Score calculation engine (issue #10).

Formula (hybrid — Business Workflow Section 5)
================================================
The Environmental Score for a department in a given month is a weighted blend
of two components, each on a 0-100 scale:

1. **Goal attainment** (default weight 0.6) — the average ``progress_pct``
   across the department's :class:`EnvironmentalGoal` rows. This is inherently
   emissions/energy/water/waste aware, since goals track those metrics
   directly against a target and timeline.

2. **Emissions trend** (default weight 0.4) — an objective month-over-month
   check independent of whether any goals are configured: the department's
   confirmed CO2e this period vs the prior period. A flat trend scores 50
   (neutral); every 1% reduction adds a point (up to 100), every 1% increase
   subtracts a point (down to 0).

If a department has no goals, 100% of the weight shifts to the emissions
trend (and vice versa if there's no prior-period data to compare). If neither
signal is available, the score is 0.0 (nothing to reward yet).

The resulting ``environmental_score`` feeds into ``DepartmentScore.total_score``
alongside Social and Governance scores (not yet implemented — they default to
0 until their own scoring engines land). The Environmental pillar's weight in
that roll-up is configurable via ``SettingsService`` (default 40%, per
Section 5); Social and Governance provisionally split whatever weight
remains.
"""
from __future__ import annotations

from calendar import monthrange
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.carbon_transaction import CarbonTransaction, TransactionStatus
from app.models.department import Department
from app.models.department_score import DepartmentScore
from app.models.environmental_goal import EnvironmentalGoal
from app.repositories.department_score_repository import DepartmentScoreRepository
from app.schemas.department_score import EnvironmentalScoreBreakdown
from app.services.settings_service import SettingsService

# Sub-weights between the two components of the environmental score itself
# (distinct from the environmental-vs-social-vs-governance pillar weight).
_GOAL_WEIGHT = 0.6
_EMISSIONS_WEIGHT = 0.4


class EnvironmentalScoreError(Exception):
    pass


class EnvironmentalScoreValidationError(EnvironmentalScoreError):
    pass


def _month_bounds(period: date) -> tuple[date, date]:
    start = period.replace(day=1)
    end = start.replace(day=monthrange(start.year, start.month)[1])
    return start, end


def _previous_month_bounds(period_start: date) -> tuple[date, date]:
    if period_start.month == 1:
        prev_start = period_start.replace(year=period_start.year - 1, month=12, day=1)
    else:
        prev_start = period_start.replace(month=period_start.month - 1, day=1)
    prev_end = prev_start.replace(day=monthrange(prev_start.year, prev_start.month)[1])
    return prev_start, prev_end


class EnvironmentalScoreService:
    def __init__(self, db: Session):
        self.db = db
        self.scores = DepartmentScoreRepository(db)
        self.settings = SettingsService(db)

    def calculate(self, department_id: int, period: date) -> EnvironmentalScoreBreakdown:
        if self.db.get(Department, department_id) is None:
            raise EnvironmentalScoreValidationError(f"Department {department_id} not found")

        period_start, period_end = _month_bounds(period)

        goal_score = self._goal_attainment_score(department_id)
        emissions_score = self._emissions_trend_score(department_id, period_start, period_end)

        goal_weight, emissions_weight = _GOAL_WEIGHT, _EMISSIONS_WEIGHT
        if goal_score is None and emissions_score is None:
            environmental_score = 0.0
        elif goal_score is None:
            environmental_score = emissions_score
        elif emissions_score is None:
            environmental_score = goal_score
        else:
            environmental_score = goal_score * goal_weight + emissions_score * emissions_weight

        return EnvironmentalScoreBreakdown(
            goal_attainment_score=goal_score,
            emissions_trend_score=emissions_score,
            goal_weight=goal_weight,
            emissions_weight=emissions_weight,
            environmental_score=round(environmental_score, 1),
        )

    def calculate_and_store(self, department_id: int, period: date) -> DepartmentScore:
        breakdown = self.calculate(department_id, period)
        pillar_weight = self.settings.get_environmental_score_weight()
        return self.scores.upsert_environmental_score(
            department_id=department_id,
            period=period.replace(day=1),
            environmental_score=breakdown.environmental_score,
            environmental_weight=pillar_weight,
        )

    def _goal_attainment_score(self, department_id: int) -> float | None:
        goals = (
            self.db.query(EnvironmentalGoal)
            .filter(EnvironmentalGoal.department_id == department_id)
            .all()
        )
        if not goals:
            return None
        return round(sum(g.progress_pct for g in goals) / len(goals), 1)

    def _sum_confirmed_co2e(self, department_id: int, date_from: date, date_to: date) -> float:
        total = (
            self.db.query(func.coalesce(func.sum(CarbonTransaction.co2e), 0.0))
            .filter(
                CarbonTransaction.department_id == department_id,
                CarbonTransaction.status == TransactionStatus.CONFIRMED,
                CarbonTransaction.transaction_date >= date_from,
                CarbonTransaction.transaction_date <= date_to,
            )
            .scalar()
        )
        return float(total or 0.0)

    def _emissions_trend_score(
        self, department_id: int, period_start: date, period_end: date
    ) -> float | None:
        previous_start, previous_end = _previous_month_bounds(period_start)
        previous_co2e = self._sum_confirmed_co2e(department_id, previous_start, previous_end)
        if previous_co2e <= 0:
            return None

        current_co2e = self._sum_confirmed_co2e(department_id, period_start, period_end)
        reduction_pct = (previous_co2e - current_co2e) / previous_co2e
        return round(max(0.0, min(50 + reduction_pct * 100, 100.0)), 1)
