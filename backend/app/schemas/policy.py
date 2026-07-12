"""Pydantic v2 schemas for the ESG Policy and Acknowledgement resources."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.policy import PolicyStatus, PolicyType


class PolicyBase(BaseModel):
    title: str = Field(..., max_length=255)
    type: PolicyType = PolicyType.OTHER
    content: Optional[str] = None
    version: str = Field("1.0", max_length=32)
    effective_date: date
    status: PolicyStatus = PolicyStatus.DRAFT


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    type: Optional[PolicyType] = None
    content: Optional[str] = None
    version: Optional[str] = Field(None, max_length=32)
    effective_date: Optional[date] = None
    status: Optional[PolicyStatus] = None


class PolicyRead(PolicyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PolicyAcknowledgementCreate(BaseModel):
    signature_text: str = Field(..., max_length=255)


class PolicyAcknowledgementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int
    employee_id: int
    acknowledged_at: datetime
    signature_text: Optional[str] = None
