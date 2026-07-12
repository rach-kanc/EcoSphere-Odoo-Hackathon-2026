"""Pydantic v2 schemas for the auto emission calculation engine (issue #7)."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.carbon_transaction import SourceType
from app.models.pending_auto_calculation import PendingStatus


# ── Settings ───────────────────────────────────────────────────────────────
class AutoCalculationSettingRead(BaseModel):
    enabled: bool


class AutoCalculationSettingUpdate(BaseModel):
    enabled: bool


# ── Mapping configuration ──────────────────────────────────────────────────
class EmissionFactorMappingBase(BaseModel):
    source_type: SourceType
    match_key: str = Field(..., max_length=128, description="Business key from the source record")
    factor_code: str = Field(..., max_length=64)
    is_active: bool = True


class EmissionFactorMappingCreate(EmissionFactorMappingBase):
    pass


class EmissionFactorMappingUpdate(BaseModel):
    match_key: str | None = Field(None, max_length=128)
    factor_code: str | None = Field(None, max_length=64)
    is_active: bool | None = None


class EmissionFactorMappingRead(EmissionFactorMappingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ── Source-record ingestion ────────────────────────────────────────────────
class SourceRecordIngest(BaseModel):
    """A source record handed to the engine for auto carbon accounting.

    In a real deployment an ERP webhook/cron would post one of these per new or
    edited Purchase / Manufacturing / Expense / Fleet record.
    """

    source_type: SourceType
    source_record_id: int
    match_key: str = Field(..., max_length=128)
    quantity: float = Field(..., gt=0)
    transaction_date: date
    department_id: int | None = None
    source_reference: str | None = Field(None, max_length=255)


class IngestOutcome(BaseModel):
    """Result of ingesting a single source record."""

    status: str  # "created" | "updated" | "flagged" | "disabled"
    detail: str
    carbon_transaction_id: int | None = None
    pending_id: int | None = None


# ── Pending review queue ───────────────────────────────────────────────────
class PendingAutoCalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: SourceType
    source_record_id: int
    source_reference: str | None
    match_key: str
    department_id: int | None
    quantity: float
    transaction_date: date
    reason: str
    status: PendingStatus
    created_at: datetime
