"""Pydantic v2 schemas for the CarbonTransaction resource."""
from __future__ import annotations
from typing import Optional

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.carbon_transaction import CreatedBy, SourceType, TransactionStatus


class CarbonTransactionCreateAuto(BaseModel):
    """Payload to auto-calculate and record a transaction.

    CO2e is derived server-side from the resolved emission factor, so it is not
    accepted here. Supply either ``emission_factor_id`` or ``factor_code``.
    """

    department_id: Optional[int] = None
    source_type: SourceType
    source_record_id: Optional[int] = None
    source_reference: Optional[str] = Field(None, max_length=255)
    emission_factor_id: Optional[int] = None
    factor_code: Optional[str] = Field(None, max_length=64)
    quantity: float = Field(..., ge=0)
    transaction_date: date


class CarbonTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: Optional[int]
    source_type: SourceType
    source_record_id: Optional[int]
    source_reference: Optional[str]
    emission_factor_id: int
    quantity: float
    co2e: float
    transaction_date: date
    created_by: CreatedBy
    status: TransactionStatus
