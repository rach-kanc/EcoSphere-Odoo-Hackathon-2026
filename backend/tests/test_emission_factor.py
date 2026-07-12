"""Tests for EmissionFactor versioning (issue #1 acceptance criteria)."""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.emission_factor import ActivityType, EmissionFactor, FactorStatus


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)()
    try:
        yield session
    finally:
        session.close()


def test_new_version_closes_previous_and_keeps_history(db):
    v1 = EmissionFactor.new_version(
        db,
        factor_code="grid.electricity.in",
        name="India grid electricity",
        activity_type=ActivityType.ELECTRICITY,
        unit="kWh",
        co2e_per_unit=0.82,
        effective_start=date(2024, 1, 1),
        source="CEA 2024",
    )
    v2 = EmissionFactor.new_version(
        db,
        factor_code="grid.electricity.in",
        name="India grid electricity",
        activity_type=ActivityType.ELECTRICITY,
        unit="kWh",
        co2e_per_unit=0.71,
        effective_start=date(2025, 1, 1),
        source="CEA 2025",
    )
    db.commit()

    # Old version is closed the day before the new one, never overwritten.
    assert v1.effective_end == date(2024, 12, 31)
    assert v1.co2e_per_unit == 0.82
    assert v2.effective_end is None

    # Both versions remain queryable for historical accuracy.
    history = EmissionFactor.history(db, "grid.electricity.in")
    assert [f.co2e_per_unit for f in history] == [0.82, 0.71]


def test_resolve_returns_factor_in_force_on_date(db):
    EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.68, effective_start=date(2024, 1, 1),
    )
    EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.51, effective_start=date(2025, 1, 1),
    )
    db.commit()

    # A 2024 transaction resolves to the 2024 value; a 2025 one to the new value.
    assert EmissionFactor.resolve(db, "fuel.diesel", date(2024, 6, 1)).co2e_per_unit == 2.68
    assert EmissionFactor.resolve(db, "fuel.diesel", date(2025, 6, 1)).co2e_per_unit == 2.51
    # Before any version exists -> nothing.
    assert EmissionFactor.resolve(db, "fuel.diesel", date(2023, 1, 1)) is None


def test_inactive_version_is_not_resolved(db):
    v = EmissionFactor.new_version(
        db, factor_code="travel.air", name="Air travel", activity_type=ActivityType.TRAVEL,
        unit="km", co2e_per_unit=0.15, effective_start=date(2024, 1, 1),
    )
    db.commit()
    assert EmissionFactor.resolve(db, "travel.air", date(2024, 6, 1)) is not None

    v.status = FactorStatus.INACTIVE
    db.commit()
    assert EmissionFactor.resolve(db, "travel.air", date(2024, 6, 1)) is None
