"""Tests for Category CRUD and CSR-only validation."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.category import CategoryType
from app.services.category_service import CategoryService


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


def test_service_seeds_default_categories(db):
    service = CategoryService(db)
    categories = service.seed_default_csr_categories(
        ["Environment", "Education", "Health", "Community"]
    )
    db.commit()

    assert [category.name for category in categories] == [
        "Environment",
        "Education",
        "Health",
        "Community",
    ]
    assert all(category.type is CategoryType.CSR_ACTIVITY for category in categories)


def test_create_list_update_delete_categories_via_api(client):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Environment", "type": "CSR_ACTIVITY", "status": "Active"},
    )
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = client.get("/api/v1/categories?type=CSR_ACTIVITY")
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Environment"]

    response = client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Env & Climate", "status": "Inactive"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Inactive"

    response = client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 204


def test_api_rejects_challenge_category_write(client):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Sprint", "type": "CHALLENGE", "status": "Active"},
    )
    assert response.status_code == 400
