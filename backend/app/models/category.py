"""Category ORM model for reusable Social and Gamification master data."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.csr_activity import CSRActivity
    from app.models.challenge import Challenge


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

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_categories_type_status", "type", "status"),)

    csr_activities: Mapped[list["CSRActivity"]] = relationship(
        "CSRActivity", back_populates="category"
    )
    challenges: Mapped[list["Challenge"]] = relationship(
        "Challenge", back_populates="category"
    )
