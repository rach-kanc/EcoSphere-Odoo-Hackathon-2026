"""Business logic for CSRActivity CRUD and lifecycle handling."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.category import Category, CategoryStatus, CategoryType
from app.models.csr_activity import CSRActivity, CSRActivityStatus
from app.models.department import Department
from app.repositories.csr_activity_repository import CSRActivityRepository
from app.schemas.csr_activity import CSRActivityCreate, CSRActivityUpdate


class CSRActivityError(Exception):
    pass


class CSRActivityNotFoundError(CSRActivityError):
    pass


class CSRActivityValidationError(CSRActivityError):
    pass


class CSRActivityInvalidTransitionError(CSRActivityError):
    pass


class CSRActivityService:
    _ALLOWED_STATUS_TRANSITIONS = {
        CSRActivityStatus.DRAFT: {
            CSRActivityStatus.DRAFT,
            CSRActivityStatus.ACTIVE,
            CSRActivityStatus.ARCHIVED,
        },
        CSRActivityStatus.ACTIVE: {
            CSRActivityStatus.ACTIVE,
            CSRActivityStatus.COMPLETED,
            CSRActivityStatus.ARCHIVED,
        },
        CSRActivityStatus.COMPLETED: {
            CSRActivityStatus.COMPLETED,
            CSRActivityStatus.ARCHIVED,
        },
        CSRActivityStatus.ARCHIVED: {CSRActivityStatus.ARCHIVED},
    }

    def __init__(self, db: Session):
        self.repo = CSRActivityRepository(db)

    def list_activities(
        self,
        *,
        department_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[CSRActivityStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[CSRActivity]:
        if date_from is not None and date_to is not None and date_to < date_from:
            raise CSRActivityValidationError("date_to must be greater than or equal to date_from")
        return self.repo.list(
            department_id=department_id,
            category_id=category_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    def get_activity(self, activity_id: int) -> CSRActivity:
        activity = self.repo.get(activity_id)
        if activity is None:
            raise CSRActivityNotFoundError(f"CSR activity {activity_id} not found")
        return activity

    def create_activity(self, payload: CSRActivityCreate) -> CSRActivity:
        if payload.status is not CSRActivityStatus.DRAFT:
            raise CSRActivityValidationError("CSR activities must be created in Draft")
        self._ensure_category(payload.category_id)
        self._ensure_department(payload.department_id)
        activity = CSRActivity(
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            department_id=payload.department_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            location=payload.location,
            max_participants=payload.max_participants,
            points_per_participation=payload.points_per_participation,
            evidence_required=payload.evidence_required,
            status=payload.status,
        )
        return self.repo.create(activity)

    def update_activity(
        self, activity_id: int, payload: CSRActivityUpdate
    ) -> CSRActivity:
        activity = self.get_activity(activity_id)
        update_data = payload.model_dump(exclude_unset=True)
        self._ensure_required_fields_not_null(update_data)

        if "category_id" in update_data:
            self._ensure_category(payload.category_id)
            activity.category_id = payload.category_id
        if "department_id" in update_data:
            self._ensure_department(payload.department_id)
            activity.department_id = payload.department_id
        if "status" in update_data:
            self._ensure_status_transition(activity.status, payload.status)
            activity.status = payload.status

        for field in (
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "max_participants",
            "points_per_participation",
            "evidence_required",
        ):
            if field in update_data:
                setattr(activity, field, update_data[field])

        self._ensure_activity_date_range(activity.start_date, activity.end_date)
        self.repo.db.flush()
        return activity

    def delete_activity(self, activity_id: int) -> None:
        activity = self.get_activity(activity_id)
        self.repo.delete(activity)

    def _ensure_category(self, category_id: Optional[int]) -> Category:
        if category_id is None:
            raise CSRActivityValidationError("category_id is required")
        category = self.repo.db.get(Category, category_id)
        if category is None:
            raise CSRActivityValidationError(f"Category {category_id} not found")
        if category.type is not CategoryType.CSR_ACTIVITY:
            raise CSRActivityValidationError(
                "CSR activities can only use categories with type CSR_ACTIVITY"
            )
        if category.status is not CategoryStatus.ACTIVE:
            raise CSRActivityValidationError("CSR activity category must be Active")
        return category

    def _ensure_department(self, department_id: Optional[int]) -> Optional[Department]:
        if department_id is None:
            return None
        department = self.repo.db.get(Department, department_id)
        if department is None:
            raise CSRActivityValidationError(f"Department {department_id} not found")
        return department

    def _ensure_status_transition(
        self,
        current_status: CSRActivityStatus,
        next_status: Optional[CSRActivityStatus],
    ) -> None:
        if next_status is None:
            return
        allowed = self._ALLOWED_STATUS_TRANSITIONS[current_status]
        if next_status not in allowed:
            raise CSRActivityInvalidTransitionError(
                f"Cannot move CSR activity from {current_status.value} to {next_status.value}"
            )

    @staticmethod
    def _ensure_activity_date_range(
        start_date: Optional[date], end_date: Optional[date]
    ) -> None:
        if start_date is not None and end_date is not None and end_date < start_date:
            raise CSRActivityValidationError(
                "end_date must be greater than or equal to start_date"
            )

    @staticmethod
    def _ensure_required_fields_not_null(update_data: dict[str, object]) -> None:
        required_fields = {
            "title",
            "category_id",
            "points_per_participation",
            "evidence_required",
            "status",
        }
        null_fields = sorted(
            field for field in required_fields if field in update_data and update_data[field] is None
        )
        if null_fields:
            raise CSRActivityValidationError(
                f"{', '.join(null_fields)} cannot be null"
            )
