"""Tests for CSRActivity CRUD, filtering, and lifecycle rules."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.category import Category, CategoryStatus, CategoryType
from app.models.department import Department


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
    category = Category(
        name="Environment",
        type=CategoryType.CSR_ACTIVITY,
        status=CategoryStatus.ACTIVE,
    )
    other_category = Category(
        name="Challenge",
        type=CategoryType.CHALLENGE,
        status=CategoryStatus.ACTIVE,
    )
    department = Department(name="People Ops")
    db.add_all([category, other_category, department])
    db.commit()
    return {
        "category": category,
        "other_category": other_category,
        "department": department,
    }


def test_create_list_update_delete_csr_activities_via_api(client, master_data):
    category = master_data["category"]
    department = master_data["department"]
    response = client.post(
        "/api/v1/csr-activities",
        json={
            "title": "Beach cleanup",
            "description": "Company volunteer day",
            "category_id": category.id,
            "department_id": department.id,
            "start_date": "2026-08-01",
            "end_date": "2026-08-01",
            "location": "Mumbai",
            "max_participants": 40,
            "points_per_participation": 25,
            "evidence_required": True,
        },
    )
    assert response.status_code == 201
    payload = response.json()
    activity_id = payload["id"]
    assert payload["status"] == "Draft"
    assert payload["is_open_for_participation"] is False

    response = client.put(
        f"/api/v1/csr-activities/{activity_id}",
        json={"status": "Active"},
    )
    assert response.status_code == 200
    assert response.json()["is_open_for_participation"] is True

    response = client.get(
        "/api/v1/csr-activities",
        params={
            "department_id": department.id,
            "category_id": category.id,
            "status": "Active",
            "date_from": "2026-07-31",
            "date_to": "2026-08-02",
        },
    )
    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Beach cleanup"]

    response = client.put(
        f"/api/v1/csr-activities/{activity_id}",
        json={"status": "Completed"},
    )
    assert response.status_code == 200
    assert response.json()["is_open_for_participation"] is False

    response = client.delete(f"/api/v1/csr-activities/{activity_id}")
    assert response.status_code == 204


def test_rejects_non_csr_category(client, master_data):
    response = client.post(
        "/api/v1/csr-activities",
        json={
            "title": "Wrong category",
            "category_id": master_data["other_category"].id,
        },
    )
    assert response.status_code == 400


def test_rejects_non_draft_creation(client, master_data):
    response = client.post(
        "/api/v1/csr-activities",
        json={
            "title": "Already active",
            "category_id": master_data["category"].id,
            "status": "Active",
        },
    )
    assert response.status_code == 400


def test_rejects_invalid_lifecycle_transition(client, master_data):
    response = client.post(
        "/api/v1/csr-activities",
        json={
            "title": "Mentorship drive",
            "category_id": master_data["category"].id,
            "start_date": date(2026, 9, 1).isoformat(),
        },
    )
    assert response.status_code == 201
    activity_id = response.json()["id"]

    response = client.put(
        f"/api/v1/csr-activities/{activity_id}",
        json={"status": "Completed"},
    )
    assert response.status_code == 400
