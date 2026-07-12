"""Gamification repositories for DB operations."""
from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.badge import Badge, UserBadge
from app.models.challenge import Challenge, ChallengeParticipation, ChallengeStatus
from app.models.department import Department
from app.models.reward import Reward, RewardRedemption, RewardStatus
from app.models.user import User


class GamificationRepository:
    """Repository handling all Gamification ORM operations."""

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------------------------------------
    # Challenges
    # -----------------------------------------------------------------------
    def get_challenge(self, challenge_id: int) -> Challenge | None:
        return self.db.execute(
            select(Challenge).where(Challenge.id == challenge_id)
        ).scalar_one_or_none()

    def list_active_challenges(self) -> Sequence[Challenge]:
        return self.db.scalars(
            select(Challenge)
            .where(Challenge.status == ChallengeStatus.ACTIVE)
            .order_by(Challenge.deadline.asc())
        ).all()

    def get_participation(
        self, challenge_id: int, employee_id: int
    ) -> ChallengeParticipation | None:
        return self.db.execute(
            select(ChallengeParticipation)
            .where(
                ChallengeParticipation.challenge_id == challenge_id,
                ChallengeParticipation.employee_id == employee_id,
            )
        ).scalar_one_or_none()

    def get_participation_by_id(self, participation_id: int) -> ChallengeParticipation | None:
        return self.db.execute(
            select(ChallengeParticipation).where(ChallengeParticipation.id == participation_id)
        ).scalar_one_or_none()

    # -----------------------------------------------------------------------
    # Badges
    # -----------------------------------------------------------------------
    def list_badges(self) -> Sequence[Badge]:
        return self.db.scalars(select(Badge).order_by(Badge.id)).all()

    def list_user_badges(self, user_id: int) -> Sequence[UserBadge]:
        return self.db.scalars(
            select(UserBadge)
            .options(joinedload(UserBadge.badge))
            .where(UserBadge.user_id == user_id)
            .order_by(UserBadge.earned_at.desc())
        ).all()

    def get_user_badge(self, user_id: int, badge_id: int) -> UserBadge | None:
        return self.db.execute(
            select(UserBadge)
            .where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        ).scalar_one_or_none()

    # -----------------------------------------------------------------------
    # Rewards
    # -----------------------------------------------------------------------
    def list_rewards(self, only_available: bool = True) -> Sequence[Reward]:
        stmt = select(Reward).order_by(Reward.points_required.asc())
        if only_available:
            stmt = stmt.where(Reward.status == RewardStatus.AVAILABLE, Reward.stock > 0)
        return self.db.scalars(stmt).all()

    def get_reward(self, reward_id: int) -> Reward | None:
        # with_for_update can be used for stock decrement, handled in service
        return self.db.execute(
            select(Reward).where(Reward.id == reward_id)
        ).scalar_one_or_none()

    def list_user_redemptions(self, user_id: int) -> Sequence[RewardRedemption]:
        return self.db.scalars(
            select(RewardRedemption)
            .options(joinedload(RewardRedemption.reward))
            .where(RewardRedemption.employee_id == user_id)
            .order_by(RewardRedemption.redeemed_at.desc())
        ).all()

    # -----------------------------------------------------------------------
    # Leaderboard
    # -----------------------------------------------------------------------
    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """Returns leaderboard rows combining User and Department data."""
        stmt = (
            select(User, Department.name.label("department_name"))
            .outerjoin(Department, User.department_id == Department.id)
            .where(User.is_active == True)  # noqa: E712
            .order_by(User.xp_points.desc(), User.id.asc())
            .limit(limit)
        )
        results = self.db.execute(stmt).all()
        
        leaderboard = []
        for rank, row in enumerate(results, start=1):
            user = cast(User, row[0])
            leaderboard.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "department_name": row[1],
                "level": user.level,
                "xp_points": user.xp_points,
                "rank": rank,
            })
        return leaderboard

    # -----------------------------------------------------------------------
    # General User operations for Gamification
    # -----------------------------------------------------------------------
    def get_user(self, user_id: int) -> User | None:
        return self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    def get_user_stats(self, user_id: int) -> tuple[int, int, int]:
        """Returns (completed_challenges, csr_participations, policies_acknowledged)."""
        # Note: CSR and Policies would normally be in their own modules, 
        # but we count them here for badge unlocking.
        from app.models.challenge import ParticipationStatus
        from app.models.csr_activity import EmployeeParticipation as CSRPart
        from app.models.policy import PolicyAcknowledgement

        # Challenges completed
        challenges_count = self.db.execute(
            select(func.count(ChallengeParticipation.id)).where(
                ChallengeParticipation.employee_id == user_id,
                ChallengeParticipation.status == ParticipationStatus.APPROVED,
            )
        ).scalar() or 0

        # CSR completed
        csr_count = self.db.execute(
            select(func.count(CSRPart.id)).where(
                CSRPart.employee_id == user_id,
                CSRPart.status == "approved", # CSR ParticipationStatus is local to that model
            )
        ).scalar() or 0

        # Policies acknowledged
        policies_count = self.db.execute(
            select(func.count(PolicyAcknowledgement.id)).where(
                PolicyAcknowledgement.employee_id == user_id
            )
        ).scalar() or 0

        return challenges_count, csr_count, policies_count
