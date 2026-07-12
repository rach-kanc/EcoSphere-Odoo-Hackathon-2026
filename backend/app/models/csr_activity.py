"""CSRActivity ORM model for company-organized social initiatives."""
from __future__ import annotations

import enum
from datetime import date
from typing import Optional, TYPE_CHECKING

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

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.department import Department
    from app.models.user import User


class CSRActivityStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


# Alias for seed compatibility
ActivityStatus = CSRActivityStatus


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
    participations: Mapped[list["EmployeeParticipation"]] = relationship(
        "EmployeeParticipation", back_populates="activity", cascade="all, delete-orphan"
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

    # Seed compatibility properties
    @property
    def date(self) -> Optional[date]:
        return self.start_date

    @date.setter
    def date(self, val: Optional[date]) -> None:
        self.start_date = val
        self.end_date = val

    @property
    def xp_reward(self) -> int:
        return self.points_per_participation

    @xp_reward.setter
    def xp_reward(self, val: int) -> None:
        self.points_per_participation = val


class ParticipationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmployeeParticipation(Base):
    __tablename__ = "employee_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("csr_activities.id", ondelete="CASCADE"), nullable=False
    )
    proof_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus, name="participation_status"),
        nullable=False,
        default=ParticipationStatus.PENDING,
    )
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    employee: Mapped["User"] = relationship("User", foreign_keys=[employee_id])  # type: ignore[name-defined]
    activity: Mapped["CSRActivity"] = relationship("CSRActivity", back_populates="participations")
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])  # type: ignore[name-defined]
