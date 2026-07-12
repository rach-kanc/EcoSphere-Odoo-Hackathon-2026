"""ProductESGProfile ORM model — ESG metadata attached to a product.

Links a :class:`~app.models.product.Product` to the emission factor(s) used to
calculate its footprint and to a set of sustainability attributes. When a
Manufacturing or Purchase operation involves a product, its profile supplies the
emission factor for automated carbon accounting via
:meth:`ProductESGProfile.emission_factor_for_calculation`, which the existing
``CarbonTransaction.record_auto(emission_factor=...)`` consumes.

A product may be associated with several emission factors (e.g. one for raw
material, one for transport); ``primary_emission_factor`` marks the default used
for auto-calculation.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.emission_factor import EmissionFactor

# Many-to-many: a profile can reference several emission factors, and a factor
# can apply to many products.
product_esg_emission_factors = Table(
    "product_esg_emission_factors",
    Base.metadata,
    Column(
        "product_esg_profile_id",
        Integer,
        ForeignKey("product_esg_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "emission_factor_id",
        Integer,
        ForeignKey("emission_factors.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ProductESGProfile(Base):
    __tablename__ = "product_esg_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # One profile per product.
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    product: Mapped["Product"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Product", back_populates="esg_profile"
    )

    # Associated emission factor(s) and the default one for auto-calculation.
    emission_factors: Mapped[list[EmissionFactor]] = relationship(
        "EmissionFactor",
        secondary=product_esg_emission_factors,
        order_by="EmissionFactor.id",  # deterministic fallback ordering
    )
    primary_emission_factor_id: Mapped[int | None] = mapped_column(
        ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True
    )
    primary_emission_factor: Mapped[EmissionFactor | None] = relationship(
        "EmissionFactor", foreign_keys=[primary_emission_factor_id]
    )

    # ── Sustainability attributes ─────────────────────────────────────────
    is_recyclable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_biodegradable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_carbon_neutral: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recycled_content_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    certification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ecolabel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Free-form extension point for attributes not modelled above.
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def emission_factor_for_calculation(self) -> EmissionFactor | None:
        """Return the emission factor to use for auto carbon accounting.

        Prefers the explicitly-marked ``primary_emission_factor``; otherwise
        falls back to the first associated factor. The result is passed to
        ``CarbonTransaction.record_auto(emission_factor=...)``.
        """
        if self.primary_emission_factor is not None:
            return self.primary_emission_factor
        return self.emission_factors[0] if self.emission_factors else None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductESGProfile product_id={self.product_id}>"
