from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.department import Department
from app.models.esg_policy import ESGPolicy
from app.models.policy_acknowledgement import PolicyAcknowledgement
from app.models.audit import Audit
from app.models.compliance_issue import ComplianceIssue
from app.services.governance import GovernanceService

# Create test engine and session factory
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to set up/tear down database for unit tests
@pytest.fixture(name="db")
def db_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Fixture for API Client with database override
@pytest.fixture(name="client")
def client_fixture(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==================== UNIT & SERVICE TESTS ====================

def test_model_cascades_and_constraints(db):
    # Setup department & user
    dep = Department(name="Sustainability", code="SUST")
    db.add(dep)
    db.commit()
    
    user = User(name="Alice", email="alice@ecosphere.com", role="Officer", department_id=dep.id)
    db.add(user)
    db.commit()
    
    # Setup policy
    policy = ESGPolicy(title="Carbon Reduction", category="Environmental", content="Reduce carbon emissions.")
    db.add(policy)
    db.commit()
    
    # Setup acknowledgement
    ack = PolicyAcknowledgement(policy_id=policy.id, employee_id=user.id)
    db.add(ack)
    db.commit()
    
    # Check composite unique constraint
    with pytest.raises(Exception):
        duplicate_ack = PolicyAcknowledgement(policy_id=policy.id, employee_id=user.id)
        db.add(duplicate_ack)
        db.commit()
    db.rollback()
    
    # Verify cascade delete of acknowledgement when User is deleted
    db.delete(user)
    db.commit()
    assert db.query(PolicyAcknowledgement).filter(PolicyAcknowledgement.id == ack.id).first() is None


def test_governance_service_acknowledge_policy(db):
    dep = Department(name="S", code="S")
    db.add(dep)
    db.commit()
    user = User(name="Alice", email="alice@ecosphere.com", role="Officer", department_id=dep.id, points_balance=0)
    db.add(user)
    policy = ESGPolicy(title="P", category="E", content="C")
    db.add(policy)
    db.commit()
    
    ack = PolicyAcknowledgement(policy_id=policy.id, employee_id=user.id, status="Pending")
    db.add(ack)
    db.commit()
    
    # Call service
    updated_ack = GovernanceService.acknowledge_policy(db, ack.id)
    db.commit()
    
    assert updated_ack is not None
    assert updated_ack.status == "Acknowledged"
    assert updated_ack.acknowledged_at is not None
    assert user.points_balance == 10  # Gamification point award


def test_governance_service_get_overdue_issues(db):
    dep = Department(name="S", code="S")
    db.add(dep)
    db.commit()
    user = User(name="Alice", email="alice@ecosphere.com", role="Officer", department_id=dep.id)
    db.add(user)
    db.commit()
    
    # Overdue compliance issue
    overdue_issue = ComplianceIssue(
        severity="High",
        description="Expired certificate",
        owner_id=user.id,
        due_date=datetime.utcnow() - timedelta(days=2),
        status="Open"
    )
    # Active compliance issue (not overdue)
    active_issue = ComplianceIssue(
        severity="High",
        description="Pending review",
        owner_id=user.id,
        due_date=datetime.utcnow() + timedelta(days=2),
        status="Open"
    )
    # Resolved compliance issue (should be ignored even if past due_date)
    resolved_issue = ComplianceIssue(
        severity="High",
        description="Resolved leak",
        owner_id=user.id,
        due_date=datetime.utcnow() - timedelta(days=2),
        status="Resolved"
    )
    db.add_all([overdue_issue, active_issue, resolved_issue])
    db.commit()
    
    overdue_list = GovernanceService.get_overdue_issues(db)
    assert len(overdue_list) == 1
    assert overdue_list[0].id == overdue_issue.id


# ==================== API ROUTE TESTS ====================

def test_api_departments(client):
    # Create department
    response = client.post("/governance/departments/", json={"name": "Engineering", "code": "ENG"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering"
    assert data["code"] == "ENG"
    assert "id" in data
    
    # Duplicate code check
    response = client.post("/governance/departments/", json={"name": "Engineering 2", "code": "ENG"})
    assert response.status_code == 400
    
    # List departments
    response = client.get("/governance/departments/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_api_users(client):
    # Setup department
    dep_resp = client.post("/governance/departments/", json={"name": "HR", "code": "HR"})
    dep_id = dep_resp.json()["id"]
    
    # Create user
    response = client.post("/governance/users/", json={
        "name": "Bob",
        "email": "bob@ecosphere.com",
        "role": "Manager",
        "department_id": dep_id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bob"
    assert data["email"] == "bob@ecosphere.com"
    assert data["points_balance"] == 0


def test_api_policies_workflow(client):
    # Create policy
    response = client.post("/governance/policies/", json={
        "title": "Waste Disposal Policy",
        "category": "Environmental",
        "content": "Proper waste separation guidelines...",
        "version": "1.0",
        "status": "Draft"
    })
    assert response.status_code == 201
    policy_id = response.json()["id"]
    assert response.json()["published_at"] is None
    
    # Read policy
    response = client.get(f"/governance/policies/{policy_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Waste Disposal Policy"
    
    # Publish policy
    response = client.patch(f"/governance/policies/{policy_id}", json={"status": "Published"})
    assert response.status_code == 200
    assert response.json()["status"] == "Published"
    assert response.json()["published_at"] is not None


def test_api_acknowledgements_workflow(client):
    # Setup user and policy
    dep_id = client.post("/governance/departments/", json={"name": "HR", "code": "HR"}).json()["id"]
    user_id = client.post("/governance/users/", json={
        "name": "Alice",
        "email": "alice@ecosphere.com",
        "role": "Officer",
        "department_id": dep_id
    }).json()["id"]
    policy_id = client.post("/governance/policies/", json={
        "title": "Safety Policy",
        "category": "Social",
        "content": "Guidelines",
        "version": "1.0",
        "status": "Published"
    }).json()["id"]
    
    # Create acknowledgement record
    response = client.post("/governance/acknowledgements/", json={
        "policy_id": policy_id,
        "employee_id": user_id
    })
    assert response.status_code == 201
    ack_id = response.json()["id"]
    assert response.json()["status"] == "Pending"
    
    # Perform sign-off
    response = client.patch(f"/governance/acknowledgements/{ack_id}", json={"status": "Acknowledged"})
    assert response.status_code == 200
    assert response.json()["status"] == "Acknowledged"
    assert response.json()["acknowledged_at"] is not None
    
    # Verify user points updated
    user_data = client.get("/governance/users/").json()[0]
    assert user_data["points_balance"] == 10


def test_api_audits_and_compliance_issues(client):
    # Setup department & user
    dep_id = client.post("/governance/departments/", json={"name": "HR", "code": "HR"}).json()["id"]
    user_id = client.post("/governance/users/", json={
        "name": "Bob",
        "email": "bob@ecosphere.com",
        "role": "Manager",
        "department_id": dep_id
    }).json()["id"]
    
    # Schedule audit
    audit_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
    response = client.post("/governance/audits/", json={
        "title": "Q3 Sustainability Audit",
        "department_id": dep_id,
        "auditor": "EcoVeritas Corp",
        "date": audit_date,
        "findings_summary": "",
        "status": "Scheduled"
    })
    assert response.status_code == 201
    audit_id = response.json()["id"]
    
    # Log compliance issue
    due_date = (datetime.utcnow() - timedelta(days=1)).isoformat() # overdue
    response = client.post("/governance/compliance-issues/", json={
        "audit_id": audit_id,
        "severity": "Critical",
        "description": "Missing chemical storage manifest",
        "owner_id": user_id,
        "due_date": due_date
    })
    assert response.status_code == 201
    issue_id = response.json()["id"]
    
    # Get overdue issues
    response = client.get("/governance/compliance-issues/overdue")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == issue_id
