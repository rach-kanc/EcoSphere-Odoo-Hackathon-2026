"""Department ESG Score ORM model — monthly weighted score snapshots."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DepartmentScore(Base):
    """Monthly ESG score snapshot for a department.

    ``total_score`` = (environmental_score × 0.40)
                    + (social_score × 0.30)
                    + (governance_score × 0.30)

    Weights are configurable at the application level; this table stores the
    *computed* result so historical scores are never recalculated.
    """

    __tablename__ = "department_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    # ISO 8601 first day of month: 2025-01-01, 2025-02-01, …
    period: Mapped[date] = mapped_column(Date, nullable=False)

    # Pillar scores (0.0 – 100.0)
    environmental_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    social_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    governance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("environmental_score >= 0 AND environmental_score <= 100", name="ck_env_score_range"),
        CheckConstraint("social_score >= 0 AND social_score <= 100", name="ck_soc_score_range"),
        CheckConstraint("governance_score >= 0 AND governance_score <= 100", name="ck_gov_score_range"),
        CheckConstraint("total_score >= 0 AND total_score <= 100", name="ck_total_score_range"),
    )

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="scores")  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<DepartmentScore dept={self.department_id} period={self.period} "
            f"total={self.total_score:.1f}>"
        )
