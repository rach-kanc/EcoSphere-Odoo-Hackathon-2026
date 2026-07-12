"""Pydantic v2 schemas for the Category resource."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryStatus, CategoryType


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: CategoryType
    status: CategoryStatus = CategoryStatus.ACTIVE


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[CategoryType] = None
    status: Optional[CategoryStatus] = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
