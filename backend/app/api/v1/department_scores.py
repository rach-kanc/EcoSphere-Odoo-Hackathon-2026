"""Department Score / Environmental Score API routes (issue #10)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.department_score import DepartmentScoreRead, EnvironmentalScoreBreakdown
from app.services.environmental_score_service import (
    EnvironmentalScoreService,
    EnvironmentalScoreValidationError,
)

router = APIRouter(prefix="/department-scores", tags=["department-scores"])


def get_environmental_score_service(db: Session = Depends(get_db)) -> EnvironmentalScoreService:
    return EnvironmentalScoreService(db)


@router.get("/{department_id}/environmental", response_model=EnvironmentalScoreBreakdown)
def get_environmental_score(
    department_id: int,
    period: date,
    service: EnvironmentalScoreService = Depends(get_environmental_score_service),
):
    """Preview the environmental score for a department/period without persisting it."""
    try:
        return service.calculate(department_id, period)
    except EnvironmentalScoreValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{department_id}/calculate", response_model=DepartmentScoreRead)
def calculate_and_store_department_score(
    department_id: int,
    period: date,
    service: EnvironmentalScoreService = Depends(get_environmental_score_service),
):
    """Calculate the environmental score and persist it into DepartmentScore."""
    try:
        row = service.calculate_and_store(department_id, period)
        service.db.commit()
        return row
    except EnvironmentalScoreValidationError as exc:
        service.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
