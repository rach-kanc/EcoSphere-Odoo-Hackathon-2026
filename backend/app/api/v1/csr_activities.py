"""CSRActivity API routes."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.csr_activity import CSRActivityStatus
from app.schemas.csr_activity import (
    CSRActivityCreate,
    CSRActivityRead,
    CSRActivityUpdate,
)
from app.services.csr_activity_service import (
    CSRActivityInvalidTransitionError,
    CSRActivityNotFoundError,
    CSRActivityService,
    CSRActivityValidationError,
)

router = APIRouter(prefix="/csr-activities", tags=["csr-activities"])


def get_csr_activity_service(db: Session = Depends(get_db)) -> CSRActivityService:
    return CSRActivityService(db)


@router.get("", response_model=list[CSRActivityRead])
def list_csr_activities(
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status_filter: Optional[CSRActivityStatus] = Query(default=None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    service: CSRActivityService = Depends(get_csr_activity_service),
):
    try:
        return service.list_activities(
            department_id=department_id,
            category_id=category_id,
            status=status_filter,
            date_from=date_from,
            date_to=date_to,
        )
    except CSRActivityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{activity_id}", response_model=CSRActivityRead)
def get_csr_activity(
    activity_id: int,
    service: CSRActivityService = Depends(get_csr_activity_service),
):
    try:
        return service.get_activity(activity_id)
    except CSRActivityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=CSRActivityRead, status_code=status.HTTP_201_CREATED)
def create_csr_activity(
    payload: CSRActivityCreate,
    service: CSRActivityService = Depends(get_csr_activity_service),
):
    try:
        activity = service.create_activity(payload)
        service.repo.db.commit()
        return activity
    except CSRActivityValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{activity_id}", response_model=CSRActivityRead)
def update_csr_activity(
    activity_id: int,
    payload: CSRActivityUpdate,
    service: CSRActivityService = Depends(get_csr_activity_service),
):
    try:
        activity = service.update_activity(activity_id, payload)
        service.repo.db.commit()
        return activity
    except CSRActivityNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CSRActivityValidationError, CSRActivityInvalidTransitionError) as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_csr_activity(
    activity_id: int,
    service: CSRActivityService = Depends(get_csr_activity_service),
):
    try:
        service.delete_activity(activity_id)
        service.repo.db.commit()
    except CSRActivityNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
