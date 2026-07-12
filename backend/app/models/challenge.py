"""Challenge & ChallengeParticipation ORM models — gamification core."""
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


class ChallengeDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ChallengeStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ParticipationStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# Valid lifecycle transitions
VALID_TRANSITIONS: dict[ChallengeStatus, set[ChallengeStatus]] = {
    ChallengeStatus.DRAFT: {ChallengeStatus.ACTIVE, ChallengeStatus.ARCHIVED},
    ChallengeStatus.ACTIVE: {ChallengeStatus.UNDER_REVIEW, ChallengeStatus.ARCHIVED},
    ChallengeStatus.UNDER_REVIEW: {ChallengeStatus.COMPLETED, ChallengeStatus.ACTIVE},
    ChallengeStatus.COMPLETED: {ChallengeStatus.ARCHIVED},
    ChallengeStatus.ARCHIVED: set(),
}


class Challenge(Base):
    """A gamified sustainability challenge employees can join and complete.

    Lifecycle: Draft → Active → Under Review → Completed / Archived
    """

    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        Enum(ChallengeDifficulty, name="challenge_difficulty"),
        nullable=False,
        default=ChallengeDifficulty.MEDIUM,
    )
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[ChallengeStatus] = mapped_column(
        Enum(ChallengeStatus, name="challenge_status"),
        nullable=False,
        default=ChallengeStatus.DRAFT,
    )
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    category: Mapped["Category | None"] = relationship("Category", back_populates="challenges")  # type: ignore[name-defined]
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])  # type: ignore[name-defined]
    participations: Mapped[list["ChallengeParticipation"]] = relationship(
        "ChallengeParticipation",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    def can_transition_to(self, new_status: ChallengeStatus) -> bool:
        """Return True if the status transition is allowed."""
        return new_status in VALID_TRANSITIONS.get(self.status, set())

    @property
    def participation_count(self) -> int:
        return len(self.participations)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Challenge '{self.title}' [{self.status}] {self.xp_reward} XP>"


class ChallengeParticipation(Base):
    """Tracks a single employee's progress through a challenge."""

    __tablename__ = "challenge_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0–100
    proof_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus, name="challenge_participation_status"),
        nullable=False,
        default=ParticipationStatus.IN_PROGRESS,
    )
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="participations")
    employee: Mapped["User"] = relationship("User", foreign_keys=[employee_id], back_populates="challenge_participations")  # type: ignore[name-defined]
    approved_by: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by_id])  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ChallengeParticipation challenge={self.challenge_id} "
            f"user={self.employee_id} [{self.status}]>"
        )
