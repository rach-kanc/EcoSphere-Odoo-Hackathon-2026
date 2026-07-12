"""Gamification business logic."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.badge import UserBadge
from app.models.challenge import ChallengeParticipation, ParticipationStatus, ChallengeStatus
from app.models.notification import Notification, NotificationType
from app.models.reward import RewardRedemption, RedemptionStatus, RewardStatus
from app.repositories.gamification_repository import GamificationRepository
from app.schemas.gamification import ParticipationUpdate


class GamificationService:
    """Service handling Gamification business logic and XP engine."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GamificationRepository(db)

    # -----------------------------------------------------------------------
    # Challenges
    # -----------------------------------------------------------------------
    def join_challenge(self, challenge_id: int, user_id: int) -> ChallengeParticipation:
        challenge = self.repo.get_challenge(challenge_id)
        if not challenge or challenge.status != ChallengeStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Challenge is not active or not found.")

        existing = self.repo.get_participation(challenge_id, user_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already joined this challenge.")

        participation = ChallengeParticipation(
            challenge_id=challenge_id,
            employee_id=user_id,
            status=ParticipationStatus.IN_PROGRESS,
            progress=0,
        )
        self.db.add(participation)
        self.db.commit()
        self.db.refresh(participation)
        return participation

    def update_participation(
        self, participation_id: int, user_id: int, update_data: ParticipationUpdate
    ) -> ChallengeParticipation:
        participation = self.repo.get_participation_by_id(participation_id)
        if not participation:
            raise HTTPException(status_code=404, detail="Participation not found.")
        if participation.employee_id != user_id:
            raise HTTPException(status_code=403, detail="Not your participation.")
        if participation.status != ParticipationStatus.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Cannot update participation in this status.")

        if update_data.progress is not None:
            participation.progress = update_data.progress
        if update_data.proof_url is not None:
            participation.proof_url = str(update_data.proof_url)

        if update_data.submit_for_review:
            if participation.challenge.evidence_required and not participation.proof_url:
                raise HTTPException(status_code=400, detail="Evidence is required to submit.")
            if participation.progress < 100:
                raise HTTPException(status_code=400, detail="Progress must be 100 to submit.")
            participation.status = ParticipationStatus.SUBMITTED

        self.db.commit()
        self.db.refresh(participation)
        return participation

    def approve_participation(self, participation_id: int, manager_id: int) -> ChallengeParticipation:
        participation = self.repo.get_participation_by_id(participation_id)
        if not participation:
            raise HTTPException(status_code=404, detail="Participation not found.")
        if participation.status != ParticipationStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="Participation must be submitted for approval.")

        # Approve and award XP
        participation.status = ParticipationStatus.APPROVED
        participation.approved_by_id = manager_id
        participation.xp_awarded = participation.challenge.xp_reward

        # Update User XP
        user = participation.employee
        user.xp_points += participation.xp_awarded
        
        # Calculate new level (simple formula: level = xp // 100 + 1)
        new_level = (user.xp_points // 100) + 1
        user.level = max(user.level, new_level)

        # Create Notification
        notif = Notification(
            recipient_id=user.id,
            type=NotificationType.CHALLENGE_APPROVED,
            title="Challenge Approved ✅",
            message=f"Your submission for '{participation.challenge.title}' has been approved. +{participation.xp_awarded} XP!",
            related_id=participation.challenge_id
        )
        self.db.add(notif)

        self.db.commit()
        
        # Evaluate Badge Unlocks
        self._evaluate_badges(user.id)
        
        self.db.refresh(participation)
        return participation

    # -----------------------------------------------------------------------
    # Rewards
    # -----------------------------------------------------------------------
    def redeem_reward(self, reward_id: int, user_id: int) -> RewardRedemption:
        reward = self.repo.get_reward(reward_id)
        if not reward:
            raise HTTPException(status_code=404, detail="Reward not found.")
        if reward.status != RewardStatus.AVAILABLE or reward.stock <= 0:
            raise HTTPException(status_code=400, detail="Reward is out of stock.")

        user = self.repo.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if user.xp_points < reward.points_required:
            raise HTTPException(status_code=400, detail="Not enough XP points.")

        # Perform redemption
        user.xp_points -= reward.points_required
        reward.stock -= 1
        if reward.stock == 0:
            reward.status = RewardStatus.OUT_OF_STOCK

        redemption = RewardRedemption(
            reward_id=reward.id,
            employee_id=user.id,
            xp_spent=reward.points_required,
            status=RedemptionStatus.PENDING
        )
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        return redemption

    # -----------------------------------------------------------------------
    # XP & Badge Engine
    # -----------------------------------------------------------------------
    def _evaluate_badges(self, user_id: int) -> None:
        """Evaluates and awards any newly unlocked badges for the user."""
        user = self.repo.get_user(user_id)
        if not user:
            return

        all_badges = self.repo.list_badges()
        earned_badge_ids = {ub.badge_id for ub in self.repo.list_user_badges(user_id)}
        
        ch_count, csr_count, pol_count = self.repo.get_user_stats(user_id)

        newly_awarded = []
        for badge in all_badges:
            if badge.id in earned_badge_ids:
                continue

            # Check rule
            rule: dict[str, Any] = badge.unlock_rule
            rule_type = rule.get("type")
            target_value = rule.get("value", 0)

            unlocked = False
            if rule_type == "xp_threshold":
                unlocked = user.xp_points >= target_value
            elif rule_type == "challenges_completed":
                unlocked = ch_count >= target_value
            elif rule_type == "csr_count":
                unlocked = csr_count >= target_value
            elif rule_type == "policies_acknowledged":
                unlocked = pol_count >= target_value

            if unlocked:
                # Award it
                ub = UserBadge(user_id=user.id, badge_id=badge.id)
                self.db.add(ub)
                newly_awarded.append(badge)

                # Send notification
                notif = Notification(
                    recipient_id=user.id,
                    type=NotificationType.BADGE_UNLOCKED,
                    title=f"Badge Unlocked: {badge.name} 🏆",
                    message=f"Congratulations! You've unlocked the '{badge.name}' badge.",
                    related_id=badge.id
                )
                self.db.add(notif)

        if newly_awarded:
            self.db.commit()
