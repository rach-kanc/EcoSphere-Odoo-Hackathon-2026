"""Notification side effects for user-facing workflow events."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def notify_csr_participation_approved(
        self, *, recipient_id: int, participation_id: int, points_earned: int
    ) -> Notification:
        notification = Notification(
            recipient_id=recipient_id,
            type=NotificationType.CSR_APPROVED,
            title="CSR participation approved",
            message=f"You earned {points_earned} XP for your CSR participation.",
            related_id=participation_id,
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def notify_csr_participation_rejected(
        self, *, recipient_id: int, participation_id: int
    ) -> Notification:
        notification = Notification(
            recipient_id=recipient_id,
            type=NotificationType.CSR_REJECTED,
            title="CSR participation rejected",
            message="Your CSR participation submission was rejected.",
            related_id=participation_id,
        )
        self.db.add(notification)
        self.db.flush()
        return notification
