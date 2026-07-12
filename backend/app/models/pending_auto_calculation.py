"""PendingAutoCalculation ORM model — review queue for unmatched source records.

When the auto emission engine (issue #7) ingests a source record but cannot find
an active emission factor for it (no mapping configured, or the mapped factor has
no version effective on the transaction date), it does not silently drop the
record — it parks it here for a human to review. Once a mapping/factor is added,
the pending row can be retried and, on success, is marked ``resolved``.

``(source_type, source_record_id)`` is unique so repeated edits to the same
source record update the existing pending row rather than piling up duplicates.
"""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.carbon_transaction import SourceType


class PendingStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class PendingAutoCalculation(Base):
    __tablename__ = "pending_auto_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type"), nullable=False
    )
    source_record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    match_key: Mapped[str] = mapped_column(String(128), nullable=False)
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[PendingStatus] = mapped_column(
        Enum(PendingStatus, name="pending_status"),
        nullable=False,
        default=PendingStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "source_type",
            "source_record_id",
            name="uq_pending_auto_calc_source",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PendingAutoCalculation {self.source_type}/{self.source_record_id} "
            f"[{self.status}]>"
        )
