"""Platform settings API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auto_emission import (
    AutoCalculationSettingRead,
    AutoCalculationSettingUpdate,
)
from app.schemas.department_score import (
    EnvironmentalScoreWeightRead,
    EnvironmentalScoreWeightUpdate,
)
from app.services.settings_service import SettingsService, SettingsValidationError

router = APIRouter(prefix="/settings", tags=["settings"])


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    return SettingsService(db)


@router.get("/auto-calculation", response_model=AutoCalculationSettingRead)
def get_auto_calculation_setting(
    service: SettingsService = Depends(get_settings_service),
):
    return AutoCalculationSettingRead(enabled=service.is_auto_calculation_enabled())


@router.put("/auto-calculation", response_model=AutoCalculationSettingRead)
def update_auto_calculation_setting(
    payload: AutoCalculationSettingUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    enabled = service.set_auto_calculation_enabled(payload.enabled)
    service.repo.db.commit()
    return AutoCalculationSettingRead(enabled=enabled)


@router.get("/environmental-score-weight", response_model=EnvironmentalScoreWeightRead)
def get_environmental_score_weight(
    service: SettingsService = Depends(get_settings_service),
):
    return EnvironmentalScoreWeightRead(weight=service.get_environmental_score_weight())


@router.put("/environmental-score-weight", response_model=EnvironmentalScoreWeightRead)
def update_environmental_score_weight(
    payload: EnvironmentalScoreWeightUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    try:
        weight = service.set_environmental_score_weight(payload.weight)
        service.repo.db.commit()
        return EnvironmentalScoreWeightRead(weight=weight)
    except SettingsValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
