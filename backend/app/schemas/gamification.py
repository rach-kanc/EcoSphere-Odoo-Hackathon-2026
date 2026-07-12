"""Pydantic schemas for Gamification (Challenges, Badges, Rewards, Leaderboards)."""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.badge import BadgeRarity
from app.models.challenge import ChallengeDifficulty, ChallengeStatus, ParticipationStatus
from app.models.reward import RedemptionStatus, RewardStatus


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------
class BadgeBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    icon_url: str | None = Field(None, max_length=512)
    rarity: BadgeRarity = BadgeRarity.COMMON
    unlock_rule: dict[str, Any]


class BadgeRead(BadgeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserBadgeRead(BaseModel):
    id: int
    user_id: int
    badge_id: int
    earned_at: datetime
    badge: BadgeRead
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
class ChallengeBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    category_id: int | None = None
    xp_reward: int = Field(100, ge=0)
    difficulty: ChallengeDifficulty = ChallengeDifficulty.MEDIUM
    deadline: date | None = None
    evidence_required: bool = False
    status: ChallengeStatus = ChallengeStatus.DRAFT


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    category_id: int | None = None
    xp_reward: int | None = Field(None, ge=0)
    difficulty: ChallengeDifficulty | None = None
    deadline: date | None = None
    evidence_required: bool | None = None
    status: ChallengeStatus | None = None


class ChallengeRead(ChallengeBase):
    id: int
    created_by_id: int | None = None
    created_at: datetime
    updated_at: datetime
    participation_count: int = 0
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Challenge Participation
# ---------------------------------------------------------------------------
class ParticipationBase(BaseModel):
    challenge_id: int
    employee_id: int
    progress: int = Field(0, ge=0, le=100)
    proof_url: str | None = Field(None, max_length=512)
    status: ParticipationStatus = ParticipationStatus.IN_PROGRESS
    xp_awarded: int = 0


class ParticipationUpdate(BaseModel):
    """Payload to update progress on a challenge or submit it."""
    progress: int | None = Field(None, ge=0, le=100)
    proof_url: HttpUrl | str | None = None
    submit_for_review: bool = False


class ParticipationApprove(BaseModel):
    """Payload for a manager to approve a challenge participation."""
    approved: bool


class ParticipationRead(ParticipationBase):
    id: int
    submitted_at: datetime | None = None
    approved_by_id: int | None = None
    created_at: datetime
    challenge: ChallengeRead | None = None
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------
class RewardBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    icon_url: str | None = Field(None, max_length=512)
    points_required: int = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    status: RewardStatus = RewardStatus.AVAILABLE


class RewardCreate(RewardBase):
    pass


class RewardUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    icon_url: str | None = Field(None, max_length=512)
    points_required: int | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    status: RewardStatus | None = None


class RewardRead(RewardBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RedemptionRead(BaseModel):
    id: int
    reward_id: int
    employee_id: int
    xp_spent: int
    status: RedemptionStatus
    redeemed_at: datetime
    reward: RewardRead | None = None
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------
class LeaderboardEntry(BaseModel):
    user_id: int
    full_name: str
    department_name: str | None = None
    level: int
    xp_points: int
    rank: int
    model_config = ConfigDict(from_attributes=True)
