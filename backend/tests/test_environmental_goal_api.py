"""Tests for EnvironmentalGoal tracking from actual emissions."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.carbon_transaction import CarbonTransaction, SourceType, TransactionStatus
from app.models.department import Department
from app.models.emission_factor import ActivityType, EmissionFactor
from app.models.environmental_goal import EnvironmentalGoal, TargetMetric


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
def master_data(db):
    operations = Department(name="Operations", code="OPS", employee_count=10)
    sales = Department(name="Sales", code="SAL", employee_count=5)
    factor = EmissionFactor.new_version(
        db,
        factor_code="fuel.diesel",
        name="Diesel",
        activity_type=ActivityType.FUEL,
        unit="litre",
        co2e_per_unit=1.0,
        effective_start=date(2026, 1, 1),
    )
    db.add_all([operations, sales])
    db.commit()
    return {"operations": operations, "sales": sales, "factor": factor}


def add_transaction(
    db,
    *,
    department_id: int,
    factor: EmissionFactor,
    co2e: float,
    transaction_date: date,
    status: TransactionStatus = TransactionStatus.CONFIRMED,
) -> CarbonTransaction:
    transaction = CarbonTransaction(
        department_id=department_id,
        source_type=SourceType.FLEET,
        transaction_date=transaction_date,
        emission_factor_id=factor.id,
        emission_factor=factor,
        status=status,
    )
    transaction.factor_value = factor.co2e_per_unit
    transaction.quantity = co2e
    db.add(transaction)
    return transaction


def test_list_goals_refreshes_from_confirmed_carbon_transactions(client, db, master_data):
    operations = master_data["operations"]
    sales = master_data["sales"]
    factor = master_data["factor"]
    goal = EnvironmentalGoal(
        title="Keep operations emissions under budget",
        department_id=operations.id,
        target_metric=TargetMetric.TOTAL_CO2E,
        target_value=1000.0,
        current_value=0.0,
        unit="kgCO2e",
        start_date=date(2026, 1, 1),
        deadline=date(2026, 12, 31),
    )
    db.add(goal)
    add_transaction(
        db,
        department_id=operations.id,
        factor=factor,
        co2e=650.0,
        transaction_date=date(2026, 7, 1),
    )
    add_transaction(
        db,
        department_id=operations.id,
        factor=factor,
        co2e=500.0,
        transaction_date=date(2026, 7, 1),
        status=TransactionStatus.CANCELLED,
    )
    add_transaction(
        db,
        department_id=operations.id,
        factor=factor,
        co2e=50.0,
        transaction_date=date(2025, 12, 31),
    )
    add_transaction(
        db,
        department_id=sales.id,
        factor=factor,
        co2e=300.0,
        transaction_date=date(2026, 7, 1),
    )
    db.commit()

    response = client.get("/api/v1/environmental-goals", params={"as_of": "2026-07-02"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["current_value"] == pytest.approx(650.0)
    assert payload[0]["progress_pct"] == pytest.approx(65.0)
    assert payload[0]["status"] == "at_risk"


def test_refresh_marks_emissions_goal_missed_after_deadline(client, db, master_data):
    operations = master_data["operations"]
    factor = master_data["factor"]
    goal = EnvironmentalGoal(
        title="Keep annual emissions under cap",
        department_id=operations.id,
        target_metric=TargetMetric.TOTAL_CO2E,
        target_value=100.0,
        current_value=0.0,
        unit="kgCO2e",
        start_date=date(2026, 1, 1),
        deadline=date(2026, 12, 31),
    )
    db.add(goal)
    add_transaction(
        db,
        department_id=operations.id,
        factor=factor,
        co2e=125.0,
        transaction_date=date(2026, 12, 30),
    )
    db.commit()

    response = client.post(
        f"/api/v1/environmental-goals/{goal.id}/refresh",
        params={"as_of": "2027-01-01"},
    )

    assert response.status_code == 200
    assert response.json()["current_value"] == pytest.approx(125.0)
    assert response.json()["status"] == "missed"
