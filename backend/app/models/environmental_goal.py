"""Environmental Goal ORM model — sustainability targets with progress tracking."""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GoalStatus(str, enum.Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    ACHIEVED = "achieved"
    MISSED = "missed"


class EnvironmentalGoal(Base):
    """A time-bound sustainability target for an organisation or department.

    Examples: 'Reduce emissions by 20%', 'Achieve Net Zero by 2030'.
    Progress is tracked via ``current_value`` vs ``target_value``.
    """

    __tablename__ = "environmental_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    # Numeric target — e.g. 500 (kgCO2e), 20 (%), 1000 (kWh)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "kgCO2e", "%", "kWh"
    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status"), nullable=False, default=GoalStatus.ON_TRACK
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department | None"] = relationship("Department")  # type: ignore[name-defined]

    @property
    def progress_pct(self) -> float:
        """Percentage progress toward the target (capped at 100)."""
        if self.target_value == 0:
            return 0.0
        return min(round((self.current_value / self.target_value) * 100, 1), 100.0)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EnvironmentalGoal '{self.title}' {self.progress_pct}% — {self.status}>"
