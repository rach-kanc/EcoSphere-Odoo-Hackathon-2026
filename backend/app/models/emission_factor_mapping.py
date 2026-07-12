"""EmissionFactorMapping ORM model — mapping configuration for auto calculation.

The auto emission engine (issue #7) needs to turn an incoming source record
(a purchase line, a fleet trip, an expense, ...) into the right emission
factor. A mapping row says: "for this ``source_type`` and this ``match_key``,
use the factor identified by ``factor_code``." The engine then resolves the
active :class:`~app.models.emission_factor.EmissionFactor` version for that code
on the transaction's date.

``match_key`` is an opaque business key supplied by the source record — e.g. a
product SKU for purchases/manufacturing, a fuel type for fleet, or an expense
category. ``(source_type, match_key)`` is unique so each source maps to exactly
one factor code.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.carbon_transaction import SourceType


class EmissionFactorMapping(Base):
    __tablename__ = "emission_factor_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type"), nullable=False
    )
    # Business key from the source record used to pick a factor, e.g. a product
    # SKU, fuel type, or expense category.
    match_key: Mapped[str] = mapped_column(String(128), nullable=False)
    # Logical emission factor code (resolved to an active version by date).
    factor_code: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("source_type", "match_key", name="uq_emission_factor_mapping_source_key"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<EmissionFactorMapping {self.source_type}/{self.match_key} "
            f"-> {self.factor_code}>"
        )
