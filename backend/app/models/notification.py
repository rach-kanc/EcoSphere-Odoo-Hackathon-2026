"""Notification ORM model — in-app alerts for key platform events."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationType(str, enum.Enum):
    CHALLENGE_APPROVED = "challenge_approved"
    CHALLENGE_REJECTED = "challenge_rejected"
    BADGE_UNLOCKED = "badge_unlocked"
    REWARD_REDEEMED = "reward_redeemed"
    CSR_APPROVED = "csr_approved"
    CSR_REJECTED = "csr_rejected"
    COMPLIANCE_ISSUE_CREATED = "compliance_issue_created"
    COMPLIANCE_ISSUE_OVERDUE = "compliance_issue_overdue"
    POLICY_REMINDER = "policy_reminder"
    GENERAL = "general"


class Notification(Base):
    """An in-app notification delivered to a specific user."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"),
        nullable=False,
        default=NotificationType.GENERAL,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Polymorphic reference to the related object (e.g. challenge id, badge id)
    related_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    recipient: Mapped["User"] = relationship("User", back_populates="notifications", foreign_keys=[recipient_id])  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notification [{self.type}] → user={self.recipient_id} read={self.is_read}>"
