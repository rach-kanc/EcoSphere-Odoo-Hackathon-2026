"""Carbon Transaction ORM model — calculated emissions from ERP operations."""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransactionSource(str, enum.Enum):
    PURCHASE = "purchase"
    MANUFACTURING = "manufacturing"
    FLEET = "fleet"
    EXPENSE = "expense"
    MANUAL = "manual"


class CarbonTransaction(Base):
    """A single emission event tied to a department and an emission factor.

    ``calculated_emission`` = ``quantity`` × ``emission_factor.co2e_per_unit``.
    This is computed by the carbon service and stored for audit purposes.
    """

    __tablename__ = "carbon_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )
    emission_factor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emission_factors.id", ondelete="RESTRICT"), nullable=False
    )
    source: Mapped[TransactionSource] = mapped_column(
        Enum(TransactionSource, name="transaction_source"),
        nullable=False,
        default=TransactionSource.MANUAL,
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    calculated_emission: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="carbon_transactions")  # type: ignore[name-defined]
    emission_factor: Mapped["EmissionFactor"] = relationship("EmissionFactor")  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<CarbonTransaction dept={self.department_id} "
            f"emission={self.calculated_emission:.2f} kgCO2e on {self.date}>"
        )
