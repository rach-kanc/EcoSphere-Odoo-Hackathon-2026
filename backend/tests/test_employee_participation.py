"""Tests for CSR employee participation submission and review."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.csr_activity import ActivityStatus, CSRActivity, ParticipationStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole


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
def participation_data(db):
    employee = User(
        email="employee@example.com",
        hashed_password="hashed",
        full_name="Employee One",
        role=UserRole.EMPLOYEE,
    )
    reviewer = User(
        email="manager@example.com",
        hashed_password="hashed",
        full_name="Manager One",
        role=UserRole.DEPT_MANAGER,
    )
    activity = CSRActivity(
        title="Tree planting",
        date=date(2026, 8, 12),
        xp_reward=75,
        evidence_required=True,
        status=ActivityStatus.ONGOING,
    )
    db.add_all([employee, reviewer, activity])
    db.commit()
    return {"employee": employee, "reviewer": reviewer, "activity": activity}


def test_employee_can_submit_participation_once(client, participation_data):
    response = client.post(
        "/api/v1/employee-participations",
        json={
            "employee_id": participation_data["employee"].id,
            "activity_id": participation_data["activity"].id,
            "proof": "https://files.example.com/proof.jpg",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["approval_status"] == ParticipationStatus.PENDING.value
    assert payload["points_earned"] == 0

    duplicate = client.post(
        "/api/v1/employee-participations",
        json={
            "employee_id": participation_data["employee"].id,
            "activity_id": participation_data["activity"].id,
        },
    )
    assert duplicate.status_code == 409


def test_approval_requires_proof_when_activity_requires_evidence(
    client, db, participation_data
):
    response = client.post(
        "/api/v1/employee-participations",
        json={
            "employee_id": participation_data["employee"].id,
            "activity_id": participation_data["activity"].id,
        },
    )
    assert response.status_code == 201

    participation_id = response.json()["id"]
    response = client.patch(
        f"/api/v1/employee-participations/{participation_id}/approve",
        json={"approved_by_id": participation_data["reviewer"].id},
    )
    assert response.status_code == 400
    db.refresh(participation_data["employee"])
    assert participation_data["employee"].xp_points == 0
    assert db.query(Notification).count() == 0


def test_approval_credits_xp_and_sends_notification(client, db, participation_data):
    response = client.post(
        "/api/v1/employee-participations",
        json={
            "employee_id": participation_data["employee"].id,
            "activity_id": participation_data["activity"].id,
            "proof": "s3://bucket/proof.pdf",
            "completion_date": "2026-08-12",
        },
    )
    assert response.status_code == 201
    participation_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/employee-participations/{participation_id}/approve",
        json={"approved_by_id": participation_data["reviewer"].id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["approval_status"] == ParticipationStatus.APPROVED.value
    assert payload["points_earned"] == 75

    db.refresh(participation_data["employee"])
    assert participation_data["employee"].xp_points == 75
    notification = db.query(Notification).one()
    assert notification.type is NotificationType.CSR_APPROVED
    assert notification.recipient_id == participation_data["employee"].id


def test_rejection_sends_notification_without_xp(client, db, participation_data):
    response = client.post(
        "/api/v1/employee-participations",
        json={
            "employee_id": participation_data["employee"].id,
            "activity_id": participation_data["activity"].id,
        },
    )
    participation_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/employee-participations/{participation_id}/reject",
        json={"approved_by_id": participation_data["reviewer"].id},
    )
    assert response.status_code == 200
    assert response.json()["approval_status"] == ParticipationStatus.REJECTED.value

    db.refresh(participation_data["employee"])
    assert participation_data["employee"].xp_points == 0
    notification = db.query(Notification).one()
    assert notification.type is NotificationType.CSR_REJECTED
