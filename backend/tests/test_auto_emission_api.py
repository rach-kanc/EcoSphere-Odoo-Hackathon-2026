"""Tests for the Auto Emission Calculation engine (issue #7)."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.carbon_transaction import CarbonTransaction, CreatedBy
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
def diesel_factor(db):
    factor = EmissionFactor.new_version(
        db,
        factor_code="fuel.diesel",
        name="Diesel",
        activity_type=ActivityType.FUEL,
        unit="litre",
        co2e_per_unit=2.68,
        effective_start=date(2026, 1, 1),
    )
    db.commit()
    return factor


def _enable_auto(client):
    response = client.put("/api/v1/settings/auto-calculation", json={"enabled": True})
    assert response.status_code == 200
    assert response.json()["enabled"] is True


def _add_mapping(client, match_key="TRUCK-01", factor_code="fuel.diesel"):
    response = client.post(
        "/api/v1/emission-factor-mappings",
        json={
            "source_type": "fleet",
            "match_key": match_key,
            "factor_code": factor_code,
        },
    )
    assert response.status_code == 201
    return response.json()


def _ingest(client, *, source_record_id=1, match_key="TRUCK-01", quantity=100, txn_date="2026-06-01"):
    return client.post(
        "/api/v1/auto-calculation/ingest",
        json={
            "source_type": "fleet",
            "source_record_id": source_record_id,
            "match_key": match_key,
            "quantity": quantity,
            "transaction_date": txn_date,
        },
    )


# ── settings toggle ─────────────────────────────────────────────────────────
def test_auto_calculation_defaults_to_disabled(client):
    response = client.get("/api/v1/settings/auto-calculation")
    assert response.status_code == 200
    assert response.json()["enabled"] is False


def test_ingest_is_noop_when_disabled(client, db, diesel_factor):
    _add_mapping(client)
    response = _ingest(client)
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"
    assert db.query(CarbonTransaction).count() == 0


# ── happy path ──────────────────────────────────────────────────────────────
def test_ingest_creates_auto_transaction(client, db, diesel_factor):
    _enable_auto(client)
    _add_mapping(client)

    response = _ingest(client, quantity=100)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "created"
    txn_id = body["carbon_transaction_id"]

    txn = db.get(CarbonTransaction, txn_id)
    assert txn.created_by is CreatedBy.AUTO
    assert txn.co2e == pytest.approx(268.0)
    assert txn.source_record_id == 1


# ── dedup / edit ────────────────────────────────────────────────────────────
def test_reingesting_edited_record_updates_not_duplicates(client, db, diesel_factor):
    _enable_auto(client)
    _add_mapping(client)

    first = _ingest(client, source_record_id=7, quantity=100).json()
    second = _ingest(client, source_record_id=7, quantity=250).json()

    assert first["carbon_transaction_id"] == second["carbon_transaction_id"]
    assert second["status"] == "updated"
    assert db.query(CarbonTransaction).count() == 1

    txn = db.get(CarbonTransaction, second["carbon_transaction_id"])
    assert txn.quantity == 250
    assert txn.co2e == pytest.approx(670.0)


# ── flag for review ─────────────────────────────────────────────────────────
def test_ingest_without_mapping_flags_for_review(client, db, diesel_factor):
    _enable_auto(client)
    # No mapping configured for this match_key.
    response = _ingest(client, match_key="UNKNOWN")
    assert response.status_code == 200
    assert response.json()["status"] == "flagged"
    assert db.query(CarbonTransaction).count() == 0

    pending = client.get("/api/v1/auto-calculation/pending").json()
    assert len(pending) == 1
    assert pending[0]["match_key"] == "UNKNOWN"


def test_ingest_with_mapping_but_no_active_factor_flags(client, db):
    _enable_auto(client)
    # Mapping points at a factor code that has no versions at all.
    _add_mapping(client, factor_code="does.not.exist")
    response = _ingest(client)
    assert response.json()["status"] == "flagged"
    assert "no active emission factor" in response.json()["detail"].lower()


def test_reingesting_flagged_record_updates_same_pending_row(client, db):
    _enable_auto(client)
    _ingest(client, source_record_id=3, match_key="UNKNOWN", quantity=10)
    _ingest(client, source_record_id=3, match_key="UNKNOWN", quantity=20)

    pending = client.get("/api/v1/auto-calculation/pending").json()
    assert len(pending) == 1
    assert pending[0]["quantity"] == 20


# ── retry after fixing configuration ────────────────────────────────────────
def test_retry_pending_creates_transaction_after_mapping_added(client, db, diesel_factor):
    _enable_auto(client)
    flagged = _ingest(client, source_record_id=9, match_key="TRUCK-09").json()
    pending_id = flagged["pending_id"]
    assert pending_id is not None

    # Operator adds the missing mapping, then retries.
    _add_mapping(client, match_key="TRUCK-09")
    retry = client.post(f"/api/v1/auto-calculation/pending/{pending_id}/retry")
    assert retry.status_code == 200
    assert retry.json()["status"] == "created"

    # Pending row is now resolved and no longer in the default pending list.
    assert client.get("/api/v1/auto-calculation/pending").json() == []
    assert db.query(CarbonTransaction).count() == 1


# ── mapping CRUD ────────────────────────────────────────────────────────────
def test_mapping_duplicate_source_key_conflicts(client):
    _add_mapping(client, match_key="DUP")
    response = client.post(
        "/api/v1/emission-factor-mappings",
        json={"source_type": "fleet", "match_key": "DUP", "factor_code": "fuel.diesel"},
    )
    assert response.status_code == 409


def test_mapping_update_and_delete(client):
    mapping = _add_mapping(client, match_key="EDIT")
    mapping_id = mapping["id"]

    response = client.put(
        f"/api/v1/emission-factor-mappings/{mapping_id}",
        json={"factor_code": "fuel.petrol", "is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["factor_code"] == "fuel.petrol"
    assert response.json()["is_active"] is False

    response = client.delete(f"/api/v1/emission-factor-mappings/{mapping_id}")
    assert response.status_code == 204
    assert client.get("/api/v1/emission-factor-mappings").json() == []


def test_inactive_mapping_flags_for_review(client, db, diesel_factor):
    _enable_auto(client)
    mapping = _add_mapping(client, match_key="OFF")
    client.put(
        f"/api/v1/emission-factor-mappings/{mapping['id']}",
        json={"is_active": False},
    )
    response = _ingest(client, match_key="OFF")
    assert response.json()["status"] == "flagged"
