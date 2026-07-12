"""Pydantic v2 schemas for the EnvironmentalGoal resource."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.environmental_goal import GoalStatus, TargetMetric


class EnvironmentalGoalBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    department_id: int | None = Field(None, description="None = organisation-wide scope")
    target_metric: TargetMetric = TargetMetric.TOTAL_CO2E
    baseline_value: float | None = None
    target_value: float
    unit: str = Field(..., max_length=32)
    start_date: date | None = None
    deadline: date


class EnvironmentalGoalCreate(EnvironmentalGoalBase):
    current_value: float = 0.0


class EnvironmentalGoalUpdateProgress(BaseModel):
    """Update measured progress; status is re-derived server-side."""

    current_value: float


class EnvironmentalGoalRead(EnvironmentalGoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    current_value: float
    # Derived, read-only fields.
    status: GoalStatus
    progress_pct: float
