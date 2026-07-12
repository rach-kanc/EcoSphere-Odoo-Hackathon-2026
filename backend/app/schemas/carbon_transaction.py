"""Pydantic v2 schemas for the CarbonTransaction resource."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.carbon_transaction import CreatedBy, SourceType, TransactionStatus


class CarbonTransactionCreateAuto(BaseModel):
    """Payload to auto-calculate and record a transaction.

    CO2e is derived server-side from the resolved emission factor, so it is not
    accepted here. Supply either ``emission_factor_id`` or ``factor_code``.
    """

    department_id: int | None = None
    source_type: SourceType
    source_record_id: int | None = None
    source_reference: str | None = Field(None, max_length=255)
    emission_factor_id: int | None = None
    factor_code: str | None = Field(None, max_length=64)
    quantity: float = Field(..., ge=0)
    transaction_date: date


class CarbonTransactionCreateManual(BaseModel):
    """Payload for a user manually logging a transaction (issue #6).

    Unlike the auto-calculation flow, the caller picks a specific emission
    factor version directly. CO2e is still derived server-side from
    ``quantity * factor.co2e_per_unit`` — it is never accepted from the client.
    """

    department_id: int | None = None
    source_type: SourceType
    emission_factor_id: int
    quantity: float = Field(..., gt=0)
    transaction_date: date
    source_reference: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=512)


class CarbonTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int | None
    source_type: SourceType
    source_record_id: int | None
    source_reference: str | None
    emission_factor_id: int
    quantity: float
    factor_value: float
    co2e: float
    transaction_date: date
    created_by: CreatedBy
    status: TransactionStatus
    notes: str | None


class DepartmentCarbonSummary(BaseModel):
    """Aggregated CO2e totals for one department (issue #8)."""

    department_id: int | None
    department_name: str | None
    transaction_count: int
    total_co2e: float
