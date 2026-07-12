"""Tests for the CarbonTransaction model.

The emission value is calculated by the carbon service and stored on the row;
these tests cover persistence, the department/emission-factor relationships, and
that the stored ``calculated_emission`` matches quantity x the factor value.
"""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
import app.models  # noqa: F401  (register all models on metadata)
from app.models.carbon_transaction import CarbonTransaction, TransactionSource
from app.models.department import Department
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
def dept(db):
    d = Department(name="Operations", code="OPS")
    db.add(d)
    db.commit()
    return d


@pytest.fixture()
def diesel_factor(db):
    f = EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.68, effective_start=date(2024, 1, 1),
    )
    db.commit()
    return f


def test_create_and_persist_transaction(db, dept, diesel_factor):
    emission = 100.0 * diesel_factor.co2e_per_unit
    txn = CarbonTransaction(
        department_id=dept.id,
        emission_factor_id=diesel_factor.id,
        source=TransactionSource.FLEET,
        quantity=100.0,
        calculated_emission=emission,
        date=date(2024, 6, 1),
    )
    db.add(txn)
    db.commit()

    stored = db.get(CarbonTransaction, txn.id)
    assert stored is not None
    assert stored.calculated_emission == pytest.approx(268.0)
    assert stored.source is TransactionSource.FLEET


def test_relationships_resolve(db, dept, diesel_factor):
    txn = CarbonTransaction(
        department_id=dept.id,
        emission_factor_id=diesel_factor.id,
        source=TransactionSource.MANUAL,
        quantity=50.0,
        calculated_emission=50.0 * diesel_factor.co2e_per_unit,
        date=date(2024, 7, 1),
    )
    db.add(txn)
    db.commit()

    assert txn.department.code == "OPS"
    assert txn.emission_factor.factor_code == "fuel.diesel"
    # Back-reference from the department side.
    assert txn in dept.carbon_transactions


def test_source_defaults_to_manual(db, dept, diesel_factor):
    txn = CarbonTransaction(
        department_id=dept.id,
        emission_factor_id=diesel_factor.id,
        quantity=1.0,
        calculated_emission=diesel_factor.co2e_per_unit,
        date=date(2024, 8, 1),
    )
    db.add(txn)
    db.commit()
    assert txn.source is TransactionSource.MANUAL
