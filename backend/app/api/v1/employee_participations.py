"""Employee participation API routes for CSR activities."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.employee_participation import (
    EmployeeParticipationCreate,
    EmployeeParticipationRead,
    EmployeeParticipationReview,
)
from app.services.employee_participation_service import (
    EmployeeParticipationDuplicateError,
    EmployeeParticipationNotFoundError,
    EmployeeParticipationService,
    EmployeeParticipationValidationError,
)

router = APIRouter(prefix="/employee-participations", tags=["employee-participations"])


def get_employee_participation_service(
    db: Session = Depends(get_db),
) -> EmployeeParticipationService:
    return EmployeeParticipationService(db)


@router.post("", response_model=EmployeeParticipationRead, status_code=status.HTTP_201_CREATED)
def create_employee_participation(
    payload: EmployeeParticipationCreate,
    service: EmployeeParticipationService = Depends(get_employee_participation_service),
):
    try:
        participation = service.create_participation(payload)
        service.repo.db.commit()
        return participation
    except EmployeeParticipationDuplicateError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EmployeeParticipationValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{participation_id}/approve", response_model=EmployeeParticipationRead)
def approve_employee_participation(
    participation_id: int,
    payload: Optional[EmployeeParticipationReview] = None,
    service: EmployeeParticipationService = Depends(get_employee_participation_service),
):
    try:
        participation = service.approve_participation(participation_id, payload)
        service.repo.db.commit()
        return participation
    except EmployeeParticipationNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmployeeParticipationValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{participation_id}/reject", response_model=EmployeeParticipationRead)
def reject_employee_participation(
    participation_id: int,
    payload: Optional[EmployeeParticipationReview] = None,
    service: EmployeeParticipationService = Depends(get_employee_participation_service),
):
    try:
        participation = service.reject_participation(participation_id, payload)
        service.repo.db.commit()
        return participation
    except EmployeeParticipationNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmployeeParticipationValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
