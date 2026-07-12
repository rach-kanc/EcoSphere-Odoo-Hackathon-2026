"""AppSetting ORM model — a small key/value store for platform settings.

Used for feature flags and other global configuration that does not warrant a
dedicated table. Values are stored as strings; typed accessors live in
``app.services.settings_service``. The auto emission calculation toggle
(issue #7) is the first consumer.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Well-known setting keys.
AUTO_CALCULATION_ENABLED = "auto_calculation_enabled"
# Weight (0.0-1.0) the Environmental pillar contributes to Department Total
# Score, per Business Workflow Section 5. Default 0.40 (issue #10).
ENVIRONMENTAL_SCORE_WEIGHT = "environmental_score_weight"


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    value: Mapped[str] = mapped_column(String(512), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AppSetting {self.key}={self.value!r}>"
