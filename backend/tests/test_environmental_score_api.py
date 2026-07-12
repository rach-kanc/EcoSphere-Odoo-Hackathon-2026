"""Tests for the Environmental Score calculation engine (issue #10)."""
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
def department(db):
    dept = Department(name="Engineering", code="ENG", employee_count=10)
    db.add(dept)
    db.commit()
    return dept


def test_no_signal_scores_zero(client, department):
    response = client.get(
        "/api/v1/department-scores/{}/environmental".format(department.id),
        params={"period": "2026-06-01"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["goal_attainment_score"] is None
    assert body["emissions_trend_score"] is None
    assert body["environmental_score"] == 0.0


def test_goal_only_score_uses_average_progress(client, db, department):
    db.add(
        EnvironmentalGoal(
            title="Cut emissions",
            department_id=department.id,
            target_metric=TargetMetric.TOTAL_CO2E,
            baseline_value=1000,
            target_value=500,
            current_value=750,  # 50% progress toward target
            unit="kgCO2e",
            start_date=date(2026, 1, 1),
            deadline=date(2026, 12, 31),
        )
    )
    db.commit()

    response = client.get(
        f"/api/v1/department-scores/{department.id}/environmental",
        params={"period": "2026-06-01"},
    )
    body = response.json()
    assert body["goal_attainment_score"] == pytest.approx(50.0)
    assert body["emissions_trend_score"] is None
    # No emissions data => 100% weight on goal component.
    assert body["environmental_score"] == pytest.approx(50.0)


def test_emissions_trend_reduction_scores_above_neutral(client, db, department):
    factor = EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=1.0, effective_start=date(2026, 1, 1),
    )
    db.commit()
    prev = CarbonTransaction.record_auto(
        db, source_type=SourceType.FLEET, quantity=100, transaction_date=date(2026, 5, 15),
        emission_factor=factor,
    )
    prev.department_id = department.id
    curr = CarbonTransaction.record_auto(
        db, source_type=SourceType.FLEET, quantity=50, transaction_date=date(2026, 6, 15),
        emission_factor=factor,
    )
    curr.department_id = department.id
    db.commit()

    response = client.get(
        f"/api/v1/department-scores/{department.id}/environmental",
        params={"period": "2026-06-01"},
    )
    body = response.json()
    # 50% reduction => 50 + 50 = 100, capped at 100.
    assert body["emissions_trend_score"] == pytest.approx(100.0)
    assert body["goal_attainment_score"] is None
    assert body["environmental_score"] == pytest.approx(100.0)


def test_calculate_and_store_applies_configurable_weight(client, db, department):
    db.add(
        EnvironmentalGoal(
            title="Cut emissions",
            department_id=department.id,
            target_metric=TargetMetric.TOTAL_CO2E,
            baseline_value=1000,
            target_value=500,
            current_value=500,  # 100% progress
            unit="kgCO2e",
            start_date=date(2026, 1, 1),
            deadline=date(2026, 12, 31),
        )
    )
    db.commit()

    weight_resp = client.put(
        "/api/v1/settings/environmental-score-weight", json={"weight": 0.5}
    )
    assert weight_resp.status_code == 200
    assert weight_resp.json()["weight"] == 0.5

    response = client.post(
        f"/api/v1/department-scores/{department.id}/calculate",
        params={"period": "2026-06-01"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["environmental_score"] == pytest.approx(100.0)
    # social/governance default to 0, so total = 100 * 0.5 = 50.
    assert body["total_score"] == pytest.approx(50.0)

    # Re-calculating for the same period upserts rather than duplicating.
    response2 = client.post(
        f"/api/v1/department-scores/{department.id}/calculate",
        params={"period": "2026-06-15"},  # same month, different day
    )
    assert response2.json()["id"] == body["id"]


def test_environmental_score_weight_rejects_out_of_range(client):
    response = client.put("/api/v1/settings/environmental-score-weight", json={"weight": 1.5})
    assert response.status_code == 422


def test_unknown_department_rejected(client):
    response = client.get(
        "/api/v1/department-scores/9999/environmental", params={"period": "2026-06-01"}
    )
    assert response.status_code == 400
