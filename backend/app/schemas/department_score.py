"""Pydantic v2 schemas for Department Score / Environmental Score (issue #10)."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EnvironmentalScoreWeightRead(BaseModel):
    weight: float


class EnvironmentalScoreWeightUpdate(BaseModel):
    weight: float = Field(..., ge=0.0, le=1.0)


class EnvironmentalScoreBreakdown(BaseModel):
    """Explains how the environmental score for a department/period was derived."""

    goal_attainment_score: float | None = Field(
        None, description="Average progress_pct across the department's goals, or null if it has none."
    )
    emissions_trend_score: float | None = Field(
        None,
        description="Score derived from this period's CO2e vs the prior period, "
        "or null if there is no prior-period data to compare against.",
    )
    goal_weight: float
    emissions_weight: float
    environmental_score: float


class DepartmentScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    period: date
    environmental_score: float
    social_score: float
    governance_score: float
    total_score: float
    created_at: datetime
