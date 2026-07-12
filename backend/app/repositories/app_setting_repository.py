"""Data access helpers for the AppSetting key/value store."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting


class AppSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[AppSetting]:
        return self.db.query(AppSetting).filter(AppSetting.key == key).one_or_none()

    def set(self, key: str, value: str) -> AppSetting:
        setting = self.get(key)
        if setting is None:
            setting = AppSetting(key=key, value=value)
            self.db.add(setting)
        else:
            setting.value = value
        self.db.flush()
        return setting
