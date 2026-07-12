"""Badge & UserBadge ORM models — gamification achievements."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base


class BadgeRarity(str, enum.Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Badge(Base):
    """An achievement badge automatically awarded when an unlock rule is satisfied.

    ``unlock_rule`` is a JSON object. Supported rule types::

        {"type": "xp_threshold",          "value": 500}
        {"type": "challenges_completed",   "value": 10}
        {"type": "csr_count",              "value": 5}
        {"type": "policies_acknowledged",  "value": 3}
    """

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    rarity: Mapped[BadgeRarity] = mapped_column(
        Enum(BadgeRarity, name="badge_rarity"), nullable=False, default=BadgeRarity.COMMON
    )
    # Stored as JSON: {"type": "xp_threshold", "value": 500}
    unlock_rule: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user_badges: Mapped[list["UserBadge"]] = relationship(
        "UserBadge", back_populates="badge", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Badge '{self.name}' [{self.rarity}] rule={self.unlock_rule}>"


class UserBadge(Base):
    """Junction table recording when a user earned a specific badge."""

    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    badge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="badges")  # type: ignore[name-defined]
    badge: Mapped["Badge"] = relationship("Badge", back_populates="user_badges")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserBadge user={self.user_id} badge={self.badge_id} at={self.earned_at}>"
