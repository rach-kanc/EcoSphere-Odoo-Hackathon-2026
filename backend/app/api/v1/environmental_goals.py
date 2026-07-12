"""EnvironmentalGoal API routes."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.environmental_goal import (
    EnvironmentalGoalCreate,
    EnvironmentalGoalRead,
    EnvironmentalGoalUpdateProgress,
)
from app.services.environmental_goal_service import (
    EnvironmentalGoalNotFoundError,
    EnvironmentalGoalService,
    EnvironmentalGoalValidationError,
)

router = APIRouter(prefix="/environmental-goals", tags=["environmental-goals"])


def get_environmental_goal_service(db: Session = Depends(get_db)) -> EnvironmentalGoalService:
    return EnvironmentalGoalService(db)


@router.get("", response_model=list[EnvironmentalGoalRead])
def list_environmental_goals(
    department_id: Optional[int] = None,
    refresh_actuals: bool = True,
    as_of: Optional[date] = None,
    service: EnvironmentalGoalService = Depends(get_environmental_goal_service),
):
    return service.list_goals(
        department_id=department_id,
        refresh_actuals=refresh_actuals,
        as_of=as_of,
    )


@router.get("/{goal_id}", response_model=EnvironmentalGoalRead)
def get_environmental_goal(
    goal_id: int,
    refresh_actuals: bool = True,
    as_of: Optional[date] = None,
    service: EnvironmentalGoalService = Depends(get_environmental_goal_service),
):
    try:
        return service.get_goal(goal_id, refresh_actuals=refresh_actuals, as_of=as_of)
    except EnvironmentalGoalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=EnvironmentalGoalRead, status_code=status.HTTP_201_CREATED)
def create_environmental_goal(
    payload: EnvironmentalGoalCreate,
    service: EnvironmentalGoalService = Depends(get_environmental_goal_service),
):
    try:
        goal = service.create_goal(payload)
        service.repo.db.commit()
        return goal
    except EnvironmentalGoalValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{goal_id}/progress", response_model=EnvironmentalGoalRead)
def update_environmental_goal_progress(
    goal_id: int,
    payload: EnvironmentalGoalUpdateProgress,
    service: EnvironmentalGoalService = Depends(get_environmental_goal_service),
):
    try:
        goal = service.update_progress(goal_id, payload)
        service.repo.db.commit()
        return goal
    except EnvironmentalGoalNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{goal_id}/refresh", response_model=EnvironmentalGoalRead)
def refresh_environmental_goal_from_actuals(
    goal_id: int,
    as_of: Optional[date] = None,
    service: EnvironmentalGoalService = Depends(get_environmental_goal_service),
):
    try:
        goal = service.refresh_goal_from_actuals(goal_id, as_of=as_of)
        service.repo.db.commit()
        return goal
    except EnvironmentalGoalNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
