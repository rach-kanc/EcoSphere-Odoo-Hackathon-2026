"""Carbon Transaction ORM model — calculated emissions from ERP operations."""
from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.emission_factor import EmissionFactor


class SourceType(str, enum.Enum):
    PURCHASE = "purchase"
    MANUFACTURING = "manufacturing"
    EXPENSE = "expense"
    FLEET = "fleet"


class CreatedBy(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"


class TransactionStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# Compatibility Enum for seed.py
class TransactionSource(str, enum.Enum):
    PURCHASE = "purchase"
    MANUFACTURING = "manufacturing"
    FLEET = "fleet"
    EXPENSE = "expense"
    MANUAL = "manual"


class CarbonTransaction(Base):
    """A single emission event tied to a department and an emission factor.

    ``co2e`` = ``quantity`` × ``factor_value``.
    """

    __tablename__ = "carbon_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    emission_factor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emission_factors.id", ondelete="RESTRICT"), nullable=False
    )
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type"),
        nullable=False,
    )
    source_record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    co2e: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[CreatedBy] = mapped_column(
        Enum(CreatedBy, name="created_by"),
        nullable=False,
        default=CreatedBy.MANUAL,
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"),
        nullable=False,
        default=TransactionStatus.CONFIRMED,
    )
    notes: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Mapped private attributes for property synchronization
    _quantity: Mapped[float] = mapped_column("quantity", Float, nullable=False)
    _factor_value: Mapped[float] = mapped_column("factor_value", Float, nullable=False)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="carbon_transactions")
    emission_factor: Mapped["EmissionFactor"] = relationship("EmissionFactor")

    # Property mappings for property synchronization
    @property
    def quantity(self) -> float:
        return self._quantity

    @quantity.setter
    def quantity(self, val: float) -> None:
        self._quantity = val
        if getattr(self, "factor_value", None) is not None:
            self.co2e = val * self.factor_value

    @property
    def factor_value(self) -> float:
        return self._factor_value

    @factor_value.setter
    def factor_value(self, val: float) -> None:
        self._factor_value = val
        if getattr(self, "_quantity", None) is not None:
            self.co2e = self._quantity * val

    # Properties for seed.py compatibility
    @property
    def calculated_emission(self) -> float:
        return self.co2e

    @calculated_emission.setter
    def calculated_emission(self, val: float) -> None:
        self.co2e = val

    @property
    def date(self) -> date:
        return self.transaction_date

    @date.setter
    def date(self, val: date) -> None:
        self.transaction_date = val

    @property
    def source(self) -> TransactionSource:
        if self.created_by == CreatedBy.MANUAL:
            return TransactionSource.MANUAL
        if self.source_type:
            return TransactionSource(self.source_type.value)
        return TransactionSource.MANUAL

    @source.setter
    def source(self, val: TransactionSource | SourceType | str) -> None:
        val_str = val.value if isinstance(val, enum.Enum) else val
        if val_str == "manual":
            self.created_by = CreatedBy.MANUAL
            self.source_type = SourceType.EXPENSE  # Database fallback
        else:
            self.created_by = CreatedBy.AUTO
            self.source_type = SourceType(val_str)

    @classmethod
    def record_auto(
        cls,
        db: Session,
        *,
        source_type: SourceType,
        quantity: float,
        transaction_date: date,
        emission_factor: Optional[EmissionFactor] = None,
        source_record_id: Optional[int] = None,
        source_reference: Optional[str] = None,
        factor_code: Optional[str] = None,
    ) -> "CarbonTransaction":
        if emission_factor is None:
            if factor_code is None:
                raise ValueError("Either emission_factor or factor_code must be provided")
             # Resolve emission factor via versioning
            from app.models.emission_factor import EmissionFactor
            emission_factor = EmissionFactor.resolve(db, factor_code, transaction_date)
            if emission_factor is None:
                raise ValueError(f"No emission factor found for code {factor_code} on date {transaction_date}")

        co2e = quantity * emission_factor.co2e_per_unit

        txn = cls(
            source_type=source_type,
            transaction_date=transaction_date,
            emission_factor_id=emission_factor.id,
            emission_factor=emission_factor,
            notes=source_reference,
            source_record_id=source_record_id,
            source_reference=source_reference,
            created_by=CreatedBy.AUTO,
            status=TransactionStatus.CONFIRMED,
        )
        # Set mapped quantity and factor_value which will trigger correct co2e calculation
        txn.factor_value = emission_factor.co2e_per_unit
        txn.quantity = quantity
        txn.co2e = co2e

        db.add(txn)
        db.flush()
        return txn

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<CarbonTransaction dept={self.department_id} "
            f"co2e={self.co2e:.2f} kgCO2e on {self.transaction_date}>"
        )
