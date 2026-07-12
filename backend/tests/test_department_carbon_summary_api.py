"""Tests for the department carbon tracking summary endpoint (issue #8)."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.carbon_transaction import CarbonTransaction, SourceType
from app.models.department import Department
from app.models.emission_factor import ActivityType, EmissionFactor


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def seeded(db):
    eng = Department(name="Engineering", code="ENG", employee_count=5)
    ops = Department(name="Operations", code="OPS", employee_count=5)
    factor = EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.0, effective_start=date(2026, 1, 1),
    )
    db.add_all([eng, ops])
    db.commit()

    t1 = CarbonTransaction.record_auto(
        db, source_type=SourceType.FLEET, quantity=100, transaction_date=date(2026, 6, 1),
        emission_factor=factor,
    )
    t1.department_id = eng.id
    t2 = CarbonTransaction.record_auto(
        db, source_type=SourceType.EXPENSE, quantity=50, transaction_date=date(2026, 6, 10),
        emission_factor=factor,
    )
    t2.department_id = eng.id
    t3 = CarbonTransaction.record_auto(
        db, source_type=SourceType.FLEET, quantity=25, transaction_date=date(2026, 7, 1),
        emission_factor=factor,
    )
    t3.department_id = ops.id
    db.commit()
    return {"eng": eng, "ops": ops}


def test_summary_aggregates_totals_per_department(client, seeded):
    eng, ops = seeded["eng"], seeded["ops"]
    response = client.get("/api/v1/carbon-transactions/summary/by-department")
    assert response.status_code == 200
    by_id = {row["department_id"]: row for row in response.json()}

    assert by_id[eng.id]["transaction_count"] == 2
    assert by_id[eng.id]["total_co2e"] == pytest.approx(300.0)
    assert by_id[eng.id]["department_name"] == "Engineering"

    assert by_id[ops.id]["transaction_count"] == 1
    assert by_id[ops.id]["total_co2e"] == pytest.approx(50.0)


def test_summary_filters_by_date_range_and_source_type(client, seeded):
    eng = seeded["eng"]
    response = client.get(
        "/api/v1/carbon-transactions/summary/by-department",
        params={"source_type": "fleet", "date_from": "2026-06-01", "date_to": "2026-06-30"},
    )
    rows = {row["department_id"]: row for row in response.json()}
    assert rows[eng.id]["transaction_count"] == 1
    assert rows[eng.id]["total_co2e"] == pytest.approx(200.0)


def test_drill_down_to_department_transactions(client, seeded):
    eng = seeded["eng"]
    response = client.get("/api/v1/carbon-transactions", params={"department_id": eng.id})
    assert response.status_code == 200
    assert len(response.json()) == 2
