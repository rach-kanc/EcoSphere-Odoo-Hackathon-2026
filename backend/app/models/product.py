"""Product ORM model.

Minimal product master data used as the anchor for ESG metadata
(:class:`~app.models.product_esg_profile.ProductESGProfile`) and, via that
profile, for automated carbon accounting on manufacturing/purchase records.
This is a stub covering only what the ESG profile needs; a fuller Product
(pricing, inventory, vendor, ...) can extend it later.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    esg_profile: Mapped["ProductESGProfile | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "ProductESGProfile", back_populates="product", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product {self.sku or self.id} — {self.name}>"
