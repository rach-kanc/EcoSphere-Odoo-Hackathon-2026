"""Business logic for platform settings (typed access over the key/value store)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.app_setting import AUTO_CALCULATION_ENABLED, ENVIRONMENTAL_SCORE_WEIGHT
from app.repositories.app_setting_repository import AppSettingRepository

_TRUE = "true"
_FALSE = "false"
DEFAULT_ENVIRONMENTAL_SCORE_WEIGHT = 0.40


class SettingsError(Exception):
    pass


class SettingsValidationError(SettingsError):
    pass


class SettingsService:
    def __init__(self, db: Session):
        self.repo = AppSettingRepository(db)

    def is_auto_calculation_enabled(self) -> bool:
        setting = self.repo.get(AUTO_CALCULATION_ENABLED)
        # Auto-calculation is opt-in: defaults to off until explicitly enabled.
        return setting is not None and setting.value == _TRUE

    def set_auto_calculation_enabled(self, enabled: bool) -> bool:
        self.repo.set(AUTO_CALCULATION_ENABLED, _TRUE if enabled else _FALSE)
        return enabled

    def get_environmental_score_weight(self) -> float:
        setting = self.repo.get(ENVIRONMENTAL_SCORE_WEIGHT)
        if setting is None:
            return DEFAULT_ENVIRONMENTAL_SCORE_WEIGHT
        return float(setting.value)

    def set_environmental_score_weight(self, weight: float) -> float:
        if not 0.0 <= weight <= 1.0:
            raise SettingsValidationError("environmental_score_weight must be between 0 and 1")
        self.repo.set(ENVIRONMENTAL_SCORE_WEIGHT, str(weight))
        return weight
