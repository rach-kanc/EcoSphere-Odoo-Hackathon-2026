"""Tests for CarbonTransaction (issue #2 acceptance criteria)."""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
import app.models  # noqa: F401  (register all models on metadata)
from app.models.carbon_transaction import (
    CarbonTransaction,
    CreatedBy,
    SourceType,
    TransactionStatus,
)
from app.models.emission_factor import ActivityType, EmissionFactor


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def diesel_factor(db):
    f = EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.68, effective_start=date(2024, 1, 1),
    )
    db.commit()
    return f


def test_auto_co2e_is_derived(db, diesel_factor):
    txn = CarbonTransaction.record_auto(
        db,
        source_type=SourceType.FLEET,
        quantity=100.0,
        transaction_date=date(2024, 6, 1),
        emission_factor=diesel_factor,
        source_record_id=42,
        source_reference="FLEET/TRIP/42",
    )
    db.commit()

    assert txn.co2e == pytest.approx(268.0)
    assert txn.created_by is CreatedBy.AUTO
    # Polymorphic link back to the originating ERP record.
    assert txn.source_type is SourceType.FLEET
    assert txn.source_record_id == 42
    # Points at the specific factor version used.
    assert txn.emission_factor_id == diesel_factor.id


def test_auto_co2e_recomputes_when_quantity_changes(db, diesel_factor):
    txn = CarbonTransaction.record_auto(
        db, source_type=SourceType.PURCHASE, quantity=10.0,
        transaction_date=date(2024, 6, 1), emission_factor=diesel_factor,
    )
    db.commit()
    assert txn.co2e == pytest.approx(26.8)

    # Changing quantity re-derives CO2e; it is not an independently editable value.
    txn.quantity = 20.0
    assert txn.co2e == pytest.approx(53.6)


def test_record_auto_resolves_factor_by_code_and_date(db):
    EmissionFactor.new_version(
        db, factor_code="grid.elec", name="Grid", activity_type=ActivityType.ELECTRICITY,
        unit="kWh", co2e_per_unit=0.82, effective_start=date(2024, 1, 1),
    )
    EmissionFactor.new_version(
        db, factor_code="grid.elec", name="Grid", activity_type=ActivityType.ELECTRICITY,
        unit="kWh", co2e_per_unit=0.71, effective_start=date(2025, 1, 1),
    )
    db.commit()

    # A 2024-dated transaction uses the 2024 factor value...
    t2024 = CarbonTransaction.record_auto(
        db, source_type=SourceType.EXPENSE, quantity=1000.0,
        transaction_date=date(2024, 6, 1), factor_code="grid.elec",
    )
    # ...a 2025-dated one uses the newer factor.
    t2025 = CarbonTransaction.record_auto(
        db, source_type=SourceType.EXPENSE, quantity=1000.0,
        transaction_date=date(2025, 6, 1), factor_code="grid.elec",
    )
    db.commit()
    assert t2024.co2e == pytest.approx(820.0)
    assert t2025.co2e == pytest.approx(710.0)


def test_record_auto_requires_a_factor(db):
    with pytest.raises(ValueError):
        CarbonTransaction.record_auto(
            db, source_type=SourceType.EXPENSE, quantity=5.0,
            transaction_date=date(2024, 6, 1), factor_code="does.not.exist",
        )
