"""Gamification side effects shared by social and challenge workflows."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User


class GamificationService:
    def __init__(self, db: Session):
        self.db = db

    def credit_xp(self, user: User, points: int) -> User:
        if points < 0:
            raise ValueError("points must be non-negative")
        user.xp_points += points
        user.level = max(user.level, (user.xp_points // 100) + 1)
        self.db.flush()
        return user
