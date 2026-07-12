"""Reward & RewardRedemption ORM models — gamification store."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RewardStatus(str, enum.Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class RedemptionStatus(str, enum.Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class Reward(Base):
    """A redeemable item employees can purchase with XP points.

    When ``stock`` reaches 0 the status should be set to OUT_OF_STOCK.
    Redemption automatically deducts ``points_required`` from the user's XP.
    """

    __tablename__ = "rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    points_required: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[RewardStatus] = mapped_column(
        Enum(RewardStatus, name="reward_status"),
        nullable=False,
        default=RewardStatus.AVAILABLE,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    redemptions: Mapped[list["RewardRedemption"]] = relationship(
        "RewardRedemption", back_populates="reward", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Reward '{self.name}' {self.points_required} XP stock={self.stock}>"


class RewardRedemption(Base):
    """Records a single reward redemption by an employee."""

    __tablename__ = "reward_redemptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reward_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rewards.id", ondelete="RESTRICT"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    xp_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RedemptionStatus] = mapped_column(
        Enum(RedemptionStatus, name="redemption_status"),
        nullable=False,
        default=RedemptionStatus.PENDING,
    )
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    reward: Mapped["Reward"] = relationship("Reward", back_populates="redemptions")
    employee: Mapped["User"] = relationship("User", back_populates="reward_redemptions", foreign_keys=[employee_id])  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RewardRedemption user={self.employee_id} reward={self.reward_id} "
            f"xp={self.xp_spent} [{self.status}]>"
        )
