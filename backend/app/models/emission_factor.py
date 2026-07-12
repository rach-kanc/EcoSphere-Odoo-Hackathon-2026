"""EmissionFactor ORM model — carbon conversion master data.

An emission factor converts an operational quantity (litres of fuel, kWh of
electricity, km travelled, ...) into kg CO2e. Factors change over time as
methodologies and energy mixes are updated, so this model is **versioned**:

* Every version that describes the same logical factor shares a ``factor_code``.
* Each version carries an ``effective_start`` (and optional ``effective_end``).
* Introducing a new value creates a *new row* and closes the previous version's
  ``effective_end`` — the old row is never overwritten, so historical carbon
  transactions can always look up the factor that was in force on their date.

Use :meth:`EmissionFactor.new_version` to add a version and :meth:`resolve` to
find the factor active for a code on a given date.
"""
from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    Float,
    Index,
    Integer,
    String,
    and_,
    or_,
)
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.database import Base


class ActivityType(str, enum.Enum):
    """Category of operational activity an emission factor applies to."""

    FUEL = "fuel"
    ELECTRICITY = "electricity"
    TRAVEL = "travel"
    PURCHASE = "purchase"
    WASTE = "waste"
    WATER = "water"
    OTHER = "other"


class FactorStatus(str, enum.Enum):
    """Lifecycle status of an emission factor version."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class EmissionFactor(Base):
    """A single, immutable version of an emission factor."""

    __tablename__ = "emission_factors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Logical identity shared across all versions of the same factor.
    factor_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="activity_type"), nullable=False
    )
    # Unit of the operational quantity this factor is expressed per, e.g.
    # "litre", "kWh", "km", "kg".
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    # kg CO2e emitted per one ``unit`` of activity.
    co2e_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str | None] = mapped_column(String(512), nullable=True)

    effective_start: Mapped[date] = mapped_column(Date, nullable=False)
    # ``None`` means the version is open-ended (current).
    effective_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[FactorStatus] = mapped_column(
        Enum(FactorStatus, name="factor_status"),
        nullable=False,
        default=FactorStatus.ACTIVE,
    )

    __table_args__ = (
        CheckConstraint("co2e_per_unit >= 0", name="ck_emission_factor_co2e_non_negative"),
        CheckConstraint(
            "effective_end IS NULL OR effective_end >= effective_start",
            name="ck_emission_factor_valid_period",
        ),
        # Fast lookup of "which version is in force" by code + date.
        Index("ix_emission_factor_code_period", "factor_code", "effective_start"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<EmissionFactor {self.factor_code} v(start={self.effective_start}, "
            f"end={self.effective_end}) {self.co2e_per_unit} kgCO2e/{self.unit}>"
        )

    def is_effective_on(self, on_date: date) -> bool:
        """Return True if this version is active and covers ``on_date``."""
        if self.status is not FactorStatus.ACTIVE:
            return False
        if on_date < self.effective_start:
            return False
        return self.effective_end is None or on_date <= self.effective_end

    @classmethod
    def resolve(
        cls, db: Session, factor_code: str, on_date: date | None = None
    ) -> "EmissionFactor | None":
        """Return the active factor version for ``factor_code`` on ``on_date``.

        Defaults to today. Only ACTIVE versions whose effective period contains
        the date are considered; the latest-starting match wins.
        """
        on_date = on_date or date.today()
        return (
            db.query(cls)
            .filter(
                cls.factor_code == factor_code,
                cls.status == FactorStatus.ACTIVE,
                cls.effective_start <= on_date,
                or_(cls.effective_end.is_(None), cls.effective_end >= on_date),
            )
            .order_by(cls.effective_start.desc())
            .first()
        )

    @classmethod
    def history(cls, db: Session, factor_code: str) -> list["EmissionFactor"]:
        """Return every version of ``factor_code``, oldest first."""
        return (
            db.query(cls)
            .filter(cls.factor_code == factor_code)
            .order_by(cls.effective_start.asc())
            .all()
        )

    @classmethod
    def new_version(
        cls,
        db: Session,
        *,
        factor_code: str,
        name: str,
        activity_type: ActivityType,
        unit: str,
        co2e_per_unit: float,
        effective_start: date,
        source: str | None = None,
    ) -> "EmissionFactor":
        """Add a new version of a factor without overwriting existing history.

        Any currently-open version of ``factor_code`` (``effective_end is None``)
        that starts before ``effective_start`` is closed on the day before the
        new version takes effect. The old row is preserved so historical
        transactions still resolve to the value that was in force at their date.

        The caller is responsible for committing the session.
        """
        from datetime import timedelta

        open_versions = (
            db.query(cls)
            .filter(
                cls.factor_code == factor_code,
                cls.effective_end.is_(None),
                cls.effective_start < effective_start,
            )
            .all()
        )
        for prior in open_versions:
            prior.effective_end = effective_start - timedelta(days=1)

        version = cls(
            factor_code=factor_code,
            name=name,
            activity_type=activity_type,
            unit=unit,
            co2e_per_unit=co2e_per_unit,
            effective_start=effective_start,
            source=source,
            status=FactorStatus.ACTIVE,
        )
        db.add(version)
        db.flush()
        return version
