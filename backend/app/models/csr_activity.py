"""CSRActivity ORM model for company-organized social initiatives."""
from __future__ import annotations

import enum
from datetime import date
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CSRActivityStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class CSRActivity(Base):
    __tablename__ = "csr_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    points_per_participation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[CSRActivityStatus] = mapped_column(
        Enum(CSRActivityStatus, name="csr_activity_status"),
        nullable=False,
        default=CSRActivityStatus.DRAFT,
        index=True,
    )

    category: Mapped["Category"] = relationship("Category", back_populates="csr_activities")
    department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="csr_activities"
    )

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_csr_activity_valid_date_range",
        ),
        CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name="ck_csr_activity_max_participants_positive",
        ),
        CheckConstraint(
            "points_per_participation >= 0",
            name="ck_csr_activity_points_non_negative",
        ),
        Index("ix_csr_activities_status_dates", "status", "start_date", "end_date"),
    )

    @property
    def is_open_for_participation(self) -> bool:
        return self.status is CSRActivityStatus.ACTIVE
