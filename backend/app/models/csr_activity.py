"""CSR Activity & Employee Participation ORM models."""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActivityStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ParticipationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CSRActivity(Base):
    """A company-organised CSR event employees can participate in."""

    __tablename__ = "csr_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus, name="activity_status"),
        nullable=False,
        default=ActivityStatus.UPCOMING,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    category: Mapped["Category | None"] = relationship("Category", back_populates="csr_activities")  # type: ignore[name-defined]
    participations: Mapped[list["EmployeeParticipation"]] = relationship(
        "EmployeeParticipation", back_populates="activity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CSRActivity '{self.title}' on {self.date}>"


class EmployeeParticipation(Base):
    """Tracks an employee's involvement in a CSR activity, including approval."""

    __tablename__ = "employee_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("csr_activities.id", ondelete="CASCADE"), nullable=False
    )
    proof_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus, name="participation_status"),
        nullable=False,
        default=ParticipationStatus.PENDING,
    )
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    employee: Mapped["User"] = relationship("User", foreign_keys=[employee_id])  # type: ignore[name-defined]
    activity: Mapped["CSRActivity"] = relationship("CSRActivity", back_populates="participations")
    approved_by: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by_id])  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EmployeeParticipation user={self.employee_id} activity={self.activity_id} [{self.status}]>"
