"""Pydantic v2 schemas for CSR employee participations."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.csr_activity import ParticipationStatus


class EmployeeParticipationCreate(BaseModel):
    employee_id: int
    activity_id: int
    proof: Optional[str] = Field(None, max_length=512)
    completion_date: Optional[date] = None


class EmployeeParticipationReview(BaseModel):
    approved_by_id: Optional[int] = None


class EmployeeParticipationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    activity_id: int
    proof: Optional[str]
    approval_status: ParticipationStatus
    points_earned: int
    completion_date: Optional[date]
    approved_by_id: Optional[int]
