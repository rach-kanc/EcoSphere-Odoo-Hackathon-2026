"""Pydantic v2 schemas for the CSRActivity resource."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.csr_activity import CSRActivityStatus


class CSRActivityBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_id: int
    department_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=255)
    max_participants: Optional[int] = Field(None, gt=0)
    points_per_participation: int = Field(0, ge=0)
    evidence_required: bool = True
    status: CSRActivityStatus = CSRActivityStatus.DRAFT

    @model_validator(mode="after")
    def validate_date_range(self) -> "CSRActivityBase":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be greater than or equal to start_date")
        return self


class CSRActivityCreate(CSRActivityBase):
    pass


class CSRActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=255)
    max_participants: Optional[int] = Field(None, gt=0)
    points_per_participation: Optional[int] = Field(None, ge=0)
    evidence_required: Optional[bool] = None
    status: Optional[CSRActivityStatus] = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "CSRActivityUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be greater than or equal to start_date")
        return self


class CSRActivityRead(CSRActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_open_for_participation: bool
