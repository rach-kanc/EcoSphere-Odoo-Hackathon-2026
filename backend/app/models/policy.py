"""ESG Policy & Policy Acknowledgement ORM models."""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PolicyType(str, enum.Enum):
    ANTI_BRIBERY = "anti_bribery"
    DATA_PRIVACY = "data_privacy"
    ENVIRONMENTAL = "environmental"
    CODE_OF_CONDUCT = "code_of_conduct"
    HEALTH_SAFETY = "health_safety"
    OTHER = "other"


class PolicyStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ESGPolicy(Base):
    """A governance policy employees must acknowledge."""

    __tablename__ = "esg_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType, name="policy_type"), nullable=False, default=PolicyType.OTHER
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="policy_status"), nullable=False, default=PolicyStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    acknowledgements: Mapped[list["PolicyAcknowledgement"]] = relationship(
        "PolicyAcknowledgement", back_populates="policy", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ESGPolicy '{self.title}' v{self.version} [{self.status}]>"


class PolicyAcknowledgement(Base):
    """Records that an employee has read and accepted a policy version."""

    __tablename__ = "policy_acknowledgements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("esg_policies.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    signature_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    policy: Mapped["ESGPolicy"] = relationship("ESGPolicy", back_populates="acknowledgements")
    employee: Mapped["User"] = relationship("User")  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PolicyAcknowledgement policy={self.policy_id} user={self.employee_id}>"
