"""Business logic for CSR employee participation submission and review."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.csr_activity import ActivityStatus, CSRActivity, EmployeeParticipation, ParticipationStatus
from app.models.user import User
from app.repositories.employee_participation_repository import (
    EmployeeParticipationRepository,
)
from app.schemas.employee_participation import (
    EmployeeParticipationCreate,
    EmployeeParticipationReview,
)
from app.services.gamification_service import GamificationService
from app.services.notification_service import NotificationService


class EmployeeParticipationError(Exception):
    pass


class EmployeeParticipationNotFoundError(EmployeeParticipationError):
    pass


class EmployeeParticipationValidationError(EmployeeParticipationError):
    pass


class EmployeeParticipationDuplicateError(EmployeeParticipationError):
    pass


class EmployeeParticipationService:
    def __init__(self, db: Session):
        self.repo = EmployeeParticipationRepository(db)
        self.gamification_service = GamificationService(db)
        self.notification_service = NotificationService(db)

    def create_participation(
        self, payload: EmployeeParticipationCreate
    ) -> EmployeeParticipation:
        employee = self._get_active_employee(payload.employee_id)
        activity = self._get_activity(payload.activity_id)
        self._ensure_activity_accepts_participation(activity)

        existing = self.repo.get_by_employee_and_activity(
            payload.employee_id, payload.activity_id
        )
        if existing is not None:
            raise EmployeeParticipationDuplicateError(
                "Employee has already submitted participation for this activity"
            )

        participation = EmployeeParticipation(
            employee_id=employee.id,
            activity_id=activity.id,
            proof=payload.proof,
            approval_status=ParticipationStatus.PENDING,
            points_earned=0,
            completion_date=payload.completion_date,
        )
        return self.repo.create(participation)

    def approve_participation(
        self,
        participation_id: int,
        payload: Optional[EmployeeParticipationReview] = None,
    ) -> EmployeeParticipation:
        participation = self.get_participation(participation_id)
        self._ensure_pending(participation)
        if payload is not None and payload.approved_by_id is not None:
            self._get_reviewer(payload.approved_by_id)
            participation.approved_by_id = payload.approved_by_id

        if self._is_evidence_required(participation.activity) and not self._has_proof(participation):
            raise EmployeeParticipationValidationError(
                "Proof is required before this participation can be approved"
            )

        points = participation.activity.xp_reward
        participation.approval_status = ParticipationStatus.APPROVED
        participation.points_earned = points
        participation.completion_date = participation.completion_date or date.today()
        self.gamification_service.credit_xp(participation.employee, points)
        self.notification_service.notify_csr_participation_approved(
            recipient_id=participation.employee_id,
            participation_id=participation.id,
            points_earned=points,
        )
        self.repo.db.flush()
        return participation

    def reject_participation(
        self,
        participation_id: int,
        payload: Optional[EmployeeParticipationReview] = None,
    ) -> EmployeeParticipation:
        participation = self.get_participation(participation_id)
        self._ensure_pending(participation)
        if payload is not None and payload.approved_by_id is not None:
            self._get_reviewer(payload.approved_by_id)
            participation.approved_by_id = payload.approved_by_id

        participation.approval_status = ParticipationStatus.REJECTED
        participation.points_earned = 0
        self.notification_service.notify_csr_participation_rejected(
            recipient_id=participation.employee_id,
            participation_id=participation.id,
        )
        self.repo.db.flush()
        return participation

    def get_participation(self, participation_id: int) -> EmployeeParticipation:
        participation = self.repo.get(participation_id)
        if participation is None:
            raise EmployeeParticipationNotFoundError(
                f"Employee participation {participation_id} not found"
            )
        return participation

    def _get_active_employee(self, employee_id: int) -> User:
        employee = self.repo.db.get(User, employee_id)
        if employee is None:
            raise EmployeeParticipationValidationError(f"Employee {employee_id} not found")
        if not employee.is_active:
            raise EmployeeParticipationValidationError("Employee is inactive")
        return employee

    def _get_reviewer(self, reviewer_id: int) -> User:
        reviewer = self.repo.db.get(User, reviewer_id)
        if reviewer is None:
            raise EmployeeParticipationValidationError(f"Reviewer {reviewer_id} not found")
        if not reviewer.is_active:
            raise EmployeeParticipationValidationError("Reviewer is inactive")
        return reviewer

    def _get_activity(self, activity_id: int) -> CSRActivity:
        activity = self.repo.db.get(CSRActivity, activity_id)
        if activity is None:
            raise EmployeeParticipationValidationError(f"CSR activity {activity_id} not found")
        return activity

    @staticmethod
    def _ensure_activity_accepts_participation(activity: CSRActivity) -> None:
        if activity.status in {ActivityStatus.COMPLETED, ActivityStatus.CANCELLED}:
            raise EmployeeParticipationValidationError(
                "CSR activity is not open for participation"
            )

    @staticmethod
    def _ensure_pending(participation: EmployeeParticipation) -> None:
        if participation.approval_status is not ParticipationStatus.PENDING:
            raise EmployeeParticipationValidationError(
                "Only pending participations can be reviewed"
            )

    @staticmethod
    def _is_evidence_required(activity: CSRActivity) -> bool:
        return activity.evidence_required

    @staticmethod
    def _has_proof(participation: EmployeeParticipation) -> bool:
        return participation.proof is not None and participation.proof.strip() != ""
