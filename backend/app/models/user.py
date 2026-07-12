"""User ORM model — authentication, roles, and gamification XP."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    SYSTEM_ADMIN = "system_admin"
    ESG_MANAGER = "esg_manager"
    DEPT_MANAGER = "dept_manager"
    EMPLOYEE = "employee"
    AUDITOR = "auditor"


class User(Base):
    """Platform user — covers all roles from admin to employee."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.EMPLOYEE
    )
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Gamification
    xp_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="users", foreign_keys=[department_id])  # type: ignore[name-defined]
    badges: Mapped[list["UserBadge"]] = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")  # type: ignore[name-defined]
    reward_redemptions: Mapped[list["RewardRedemption"]] = relationship("RewardRedemption", back_populates="employee", foreign_keys="RewardRedemption.employee_id")  # type: ignore[name-defined]
    challenge_participations: Mapped[list["ChallengeParticipation"]] = relationship("ChallengeParticipation", back_populates="employee", foreign_keys="ChallengeParticipation.employee_id")  # type: ignore[name-defined]
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="recipient", foreign_keys="Notification.recipient_id")  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} role={self.role}>"
