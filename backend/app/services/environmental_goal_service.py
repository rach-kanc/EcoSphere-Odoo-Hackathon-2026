"""Business logic for EnvironmentalGoal tracking."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.environmental_goal import EnvironmentalGoal, TargetMetric
from app.repositories.environmental_goal_repository import EnvironmentalGoalRepository
from app.schemas.environmental_goal import (
    EnvironmentalGoalCreate,
    EnvironmentalGoalUpdateProgress,
)


class EnvironmentalGoalError(Exception):
    pass


class EnvironmentalGoalNotFoundError(EnvironmentalGoalError):
    pass


class EnvironmentalGoalValidationError(EnvironmentalGoalError):
    pass


class EnvironmentalGoalService:
    def __init__(self, db: Session):
        self.repo = EnvironmentalGoalRepository(db)

    def list_goals(
        self,
        *,
        department_id: Optional[int] = None,
        refresh_actuals: bool = True,
        as_of: Optional[date] = None,
    ) -> list[EnvironmentalGoal]:
        goals = self.repo.list(department_id=department_id)
        if refresh_actuals:
            for goal in goals:
                self.refresh_from_actual_emissions(goal, as_of=as_of)
            self.repo.db.flush()
        return goals

    def get_goal(
        self,
        goal_id: int,
        *,
        refresh_actuals: bool = True,
        as_of: Optional[date] = None,
    ) -> EnvironmentalGoal:
        goal = self.repo.get(goal_id)
        if goal is None:
            raise EnvironmentalGoalNotFoundError(f"Environmental goal {goal_id} not found")
        if refresh_actuals:
            self.refresh_from_actual_emissions(goal, as_of=as_of)
            self.repo.db.flush()
        return goal

    def create_goal(self, payload: EnvironmentalGoalCreate) -> EnvironmentalGoal:
        self._validate_payload(payload)
        self._ensure_department(payload.department_id)

        goal = EnvironmentalGoal(**payload.model_dump())
        goal.refresh_status()
        created = self.repo.create(goal)
        return self.refresh_from_actual_emissions(created)

    def update_progress(
        self,
        goal_id: int,
        payload: EnvironmentalGoalUpdateProgress,
    ) -> EnvironmentalGoal:
        goal = self.get_goal(goal_id, refresh_actuals=False)
        goal.current_value = payload.current_value
        goal.refresh_status()
        self.repo.db.flush()
        return goal

    def refresh_goal_from_actuals(
        self,
        goal_id: int,
        *,
        as_of: Optional[date] = None,
    ) -> EnvironmentalGoal:
        goal = self.get_goal(goal_id, refresh_actuals=False)
        self.refresh_from_actual_emissions(goal, as_of=as_of)
        self.repo.db.flush()
        return goal

    def refresh_from_actual_emissions(
        self,
        goal: EnvironmentalGoal,
        *,
        as_of: Optional[date] = None,
    ) -> EnvironmentalGoal:
        if goal.target_metric != TargetMetric.TOTAL_CO2E:
            goal.refresh_status(as_of=as_of)
            return goal

        effective_date = min(as_of or date.today(), goal.deadline)
        goal.current_value = self.repo.sum_confirmed_co2e(
            department_id=goal.department_id,
            date_from=goal.start_date,
            date_to=effective_date,
        )
        goal.refresh_status(as_of=as_of)
        return goal

    def _ensure_department(self, department_id: Optional[int]) -> Optional[Department]:
        if department_id is None:
            return None
        department = self.repo.db.get(Department, department_id)
        if department is None:
            raise EnvironmentalGoalValidationError(f"Department {department_id} not found")
        return department

    @staticmethod
    def _validate_payload(payload: EnvironmentalGoalCreate) -> None:
        if payload.start_date is not None and payload.deadline < payload.start_date:
            raise EnvironmentalGoalValidationError("deadline must be after start_date")
        if payload.target_value < 0:
            raise EnvironmentalGoalValidationError("target_value must be greater than or equal to 0")
        if payload.baseline_value is not None and payload.baseline_value < 0:
            raise EnvironmentalGoalValidationError("baseline_value must be greater than or equal to 0")
