"""Tests for ESGPolicy CRUD and user signature acknowledgements."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.policy import ESGPolicy, PolicyStatus, PolicyType
from app.models.user import User


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
    
    # Seed a test user
    test_user = User(
        email="test.user@ecosphere.com",
        full_name="Test User",
        role="employee",
        is_active=True,
        xp_points=0,
        level=1,
    )
    session.add(test_user)
    session.commit()
    
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


def test_create_list_update_delete_policies_via_api(client):
    # 1. Create Policy
    response = client.post(
        "/api/v1/policies",
        json={
            "title": "Sustainable Travel Guidelines",
            "type": "environmental",
            "content": "Trains should be used instead of flights for short trips.",
            "version": "1.0",
            "effective_date": "2026-07-12",
            "status": "active",
        },
    )
    assert response.status_code == 201
    policy_id = response.json()["id"]

    # 2. Get Policy
    response = client.get(f"/api/v1/policies/{policy_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Sustainable Travel Guidelines"

    # 3. List Policies
    response = client.get("/api/v1/policies?status=active")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["version"] == "1.0"

    # 4. Update Policy
    response = client.put(
        f"/api/v1/policies/{policy_id}",
        json={"title": "Updated Travel Guidelines", "version": "1.1"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Travel Guidelines"
    assert response.json()["version"] == "1.1"


def test_policy_pending_and_acknowledgement_flow(client, db):
    # Retrieve our test user id
    user = db.query(User).filter(User.email == "test.user@ecosphere.com").one()
    user_id = user.id

    # Create an active policy
    response = client.post(
        "/api/v1/policies",
        json={
            "title": "Data Protection Standard",
            "type": "data_privacy",
            "content": "Always lock your computer when leaving your desk.",
            "version": "1.0",
            "effective_date": "2026-07-12",
            "status": "active",
        },
    )
    assert response.status_code == 201
    policy_id = response.json()["id"]

    # Check pending policies for user
    response = client.get(f"/api/v1/policies/pending?user_id={user_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == policy_id

    # Acknowledge the policy
    response = client.post(
        f"/api/v1/policies/{policy_id}/acknowledge?user_id={user_id}",
        json={"signature_text": "Test User"},
    )
    assert response.status_code == 201
    assert response.json()["signature_text"] == "Test User"

    # Verify policy is no longer pending
    response = client.get(f"/api/v1/policies/pending?user_id={user_id}")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # Verify XP was awarded (user should have 100 XP now)
    db.refresh(user)
    assert user.xp_points == 100
    assert user.level == 1  # 100 XP / 1000 + 1 = 1


def test_cannot_acknowledge_inactive_policy(client, db):
    user = db.query(User).filter(User.email == "test.user@ecosphere.com").one()
    user_id = user.id

    # Create draft policy
    response = client.post(
        "/api/v1/policies",
        json={
            "title": "Draft Safety Policy",
            "type": "health_safety",
            "content": "Placeholder.",
            "version": "1.0",
            "effective_date": "2026-07-12",
            "status": "draft",
        },
    )
    assert response.status_code == 201
    policy_id = response.json()["id"]

    # Try acknowledging
    response = client.post(
        f"/api/v1/policies/{policy_id}/acknowledge?user_id={user_id}",
        json={"signature_text": "Test User"},
    )
    assert response.status_code == 400
