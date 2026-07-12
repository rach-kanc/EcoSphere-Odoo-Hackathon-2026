"""Audit & Compliance Issue ORM models."""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class IssueSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    OVERDUE = "overdue"


class Audit(Base):
    """A governance audit conducted against a department."""

    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    auditor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus, name="audit_status"), nullable=False, default=AuditStatus.PLANNED
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    auditor: Mapped["User"] = relationship("User", foreign_keys=[auditor_id])  # type: ignore[name-defined]
    department: Mapped["Department | None"] = relationship("Department")  # type: ignore[name-defined]
    compliance_issues: Mapped[list["ComplianceIssue"]] = relationship(
        "ComplianceIssue", back_populates="audit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Audit '{self.title}' on {self.date} [{self.status}]>"


class ComplianceIssue(Base):
    """A specific violation or finding raised within an audit."""

    __tablename__ = "compliance_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    audit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[IssueSeverity] = mapped_column(
        Enum(IssueSeverity, name="issue_severity"), nullable=False, default=IssueSeverity.MEDIUM
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status"), nullable=False, default=IssueStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    audit: Mapped["Audit"] = relationship("Audit", back_populates="compliance_issues")
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])  # type: ignore[name-defined]

    @property
    def is_overdue(self) -> bool:
        return self.status not in (IssueStatus.RESOLVED,) and self.due_date < date.today()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ComplianceIssue '{self.title}' [{self.severity}/{self.status}]>"
