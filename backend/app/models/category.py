"""Category ORM model for reusable Social and Gamification master data."""
from __future__ import annotations

import enum

from sqlalchemy import Enum, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CategoryType(str, enum.Enum):
    CSR_ACTIVITY = "CSR_ACTIVITY"
    CHALLENGE = "CHALLENGE"


class CategoryStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, name="category_type"), nullable=False, index=True
    )
    status: Mapped[CategoryStatus] = mapped_column(
        Enum(CategoryStatus, name="category_status"),
        nullable=False,
        default=CategoryStatus.ACTIVE,
        index=True,
    )

    __table_args__ = (Index("ix_categories_type_status", "type", "status"),)
