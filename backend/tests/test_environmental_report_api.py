"""Tests for Environmental Report generation (issue #13)."""
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
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool, future=True
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
    dept = Department(name="Engineering", code="ENG", employee_count=5)
    factor = EmissionFactor.new_version(
        db, factor_code="fuel.diesel", name="Diesel", activity_type=ActivityType.FUEL,
        unit="litre", co2e_per_unit=2.0, effective_start=date(2026, 1, 1),
    )
    db.add(dept)
    db.commit()
    txn = CarbonTransaction.record_auto(
        db, source_type=SourceType.FLEET, quantity=10, transaction_date=date(2026, 6, 1),
        emission_factor=factor,
    )
    txn.department_id = dept.id
    db.commit()
    return dept


@pytest.mark.parametrize(
    "fmt,content_type",
    [
        ("csv", "text/csv"),
        ("excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("pdf", "application/pdf"),
    ],
)
def test_report_export_formats(client, seeded, fmt, content_type):
    response = client.get(
        "/api/v1/reports/environmental",
        params={"format": fmt, "department_id": seeded.id, "date_from": "2026-06-01", "date_to": "2026-06-30"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type)
    assert len(response.content) > 0


def test_report_rejects_unknown_format(client):
    response = client.get("/api/v1/reports/environmental", params={"format": "word"})
    assert response.status_code == 422


def test_csv_report_contains_row_data(client, seeded):
    response = client.get(
        "/api/v1/reports/environmental", params={"format": "csv", "department_id": seeded.id}
    )
    text = response.content.decode("utf-8")
    assert "Engineering" in text
    assert "fleet" in text
