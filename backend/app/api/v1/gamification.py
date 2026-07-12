"""Gamification API Routes."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_manager, get_current_user, get_db
from app.models.user import User
from app.repositories.gamification_repository import GamificationRepository
from app.schemas.gamification import (
    BadgeRead,
    ChallengeRead,
    LeaderboardEntry,
    ParticipationApprove,
    ParticipationRead,
    ParticipationUpdate,
    RedemptionRead,
    RewardRead,
    UserBadgeRead,
)
from app.services.gamification_service import GamificationService


router = APIRouter(prefix="/gamification", tags=["Gamification"])


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
@router.get("/challenges", response_model=list[ChallengeRead])
def list_challenges(db: Session = Depends(get_db)):
    """List all active challenges."""
    repo = GamificationRepository(db)
    return repo.list_active_challenges()


@router.post("/challenges/{challenge_id}/join", response_model=ParticipationRead)
def join_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join an active challenge."""
    service = GamificationService(db)
    return service.join_challenge(challenge_id, current_user.id)


@router.put("/participations/{participation_id}", response_model=ParticipationRead)
def update_participation(
    participation_id: int,
    data: ParticipationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update progress or submit proof for a challenge."""
    service = GamificationService(db)
    return service.update_participation(participation_id, current_user.id, data)


@router.post("/participations/{participation_id}/approve", response_model=ParticipationRead)
def approve_participation(
    participation_id: int,
    data: ParticipationApprove,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager),
):
    """Manager only: Approve a submitted challenge to award XP."""
    service = GamificationService(db)
    if data.approved:
        return service.approve_participation(participation_id, current_manager.id)
    else:
        # Simplistic rejection handling (not full status switch in demo)
        return {"detail": "Participation rejected"}


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------
@router.get("/badges", response_model=list[BadgeRead])
def list_all_badges(db: Session = Depends(get_db)):
    """List all badges available in the system."""
    repo = GamificationRepository(db)
    return repo.list_badges()


@router.get("/badges/me", response_model=list[UserBadgeRead])
def list_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List badges earned by the current user."""
    repo = GamificationRepository(db)
    return repo.list_user_badges(current_user.id)


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------
@router.get("/rewards", response_model=list[RewardRead])
def list_rewards(
    only_available: bool = True,
    db: Session = Depends(get_db)
):
    """List available rewards."""
    repo = GamificationRepository(db)
    return repo.list_rewards(only_available=only_available)


@router.post("/rewards/{reward_id}/redeem", response_model=RedemptionRead)
def redeem_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Redeem a reward using XP points."""
    service = GamificationService(db)
    return service.redeem_reward(reward_id, current_user.id)


@router.get("/rewards/redemptions/me", response_model=list[RedemptionRead])
def my_redemptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's past redemptions."""
    repo = GamificationRepository(db)
    return repo.list_user_redemptions(current_user.id)


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------
@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get the global XP leaderboard."""
    repo = GamificationRepository(db)
    return repo.get_leaderboard(limit=limit)
