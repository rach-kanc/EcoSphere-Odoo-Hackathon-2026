"""Pydantic v2 schemas for Product and ProductESGProfile."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str | None


class ProductESGProfileBase(BaseModel):
    product_id: int
    primary_emission_factor_id: int | None = None
    emission_factor_ids: list[int] = Field(default_factory=list)
    is_recyclable: bool = False
    is_biodegradable: bool = False
    is_carbon_neutral: bool = False
    recycled_content_pct: float | None = Field(None, ge=0, le=100)
    certification: str | None = Field(None, max_length=255)
    ecolabel: str | None = Field(None, max_length=255)
    attributes: dict | None = None


class ProductESGProfileCreate(ProductESGProfileBase):
    pass


class ProductESGProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    primary_emission_factor_id: int | None
    is_recyclable: bool
    is_biodegradable: bool
    is_carbon_neutral: bool
    recycled_content_pct: float | None
    certification: str | None
    ecolabel: str | None
    attributes: dict | None
