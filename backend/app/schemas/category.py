"""Pydantic v2 schemas for the Category resource."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryStatus, CategoryType


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: CategoryType
    status: CategoryStatus = CategoryStatus.ACTIVE


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    type: CategoryType | None = None
    status: CategoryStatus | None = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
