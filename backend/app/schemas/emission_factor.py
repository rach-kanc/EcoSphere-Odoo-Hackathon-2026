"""Pydantic v2 schemas for the EmissionFactor resource."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.emission_factor import ActivityType, FactorStatus


class EmissionFactorBase(BaseModel):
    factor_code: str = Field(..., max_length=64, description="Logical id shared across versions")
    name: str = Field(..., max_length=255)
    activity_type: ActivityType
    unit: str = Field(..., max_length=32, description='Unit of activity, e.g. "kWh", "litre", "km"')
    co2e_per_unit: float = Field(..., ge=0, description="kg CO2e per one unit of activity")
    source: str | None = Field(None, max_length=512)


class EmissionFactorCreate(EmissionFactorBase):
    """Payload to create the first version of a factor."""

    effective_start: date


class EmissionFactorNewVersion(BaseModel):
    """Payload to add a new version of an existing factor code."""

    name: str = Field(..., max_length=255)
    activity_type: ActivityType
    unit: str = Field(..., max_length=32)
    co2e_per_unit: float = Field(..., ge=0)
    source: str | None = Field(None, max_length=512)
    effective_start: date


class EmissionFactorRead(EmissionFactorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    effective_start: date
    effective_end: date | None
    status: FactorStatus
