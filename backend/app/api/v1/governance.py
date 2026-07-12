from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.department import Department
from app.models.esg_policy import ESGPolicy
from app.models.policy_acknowledgement import PolicyAcknowledgement
from app.models.audit import Audit
from app.models.compliance_issue import ComplianceIssue

from app.schemas.user import UserCreate, UserRead
from app.schemas.department import DepartmentCreate, DepartmentRead
from app.schemas.esg_policy import ESGPolicyCreate, ESGPolicyUpdate, ESGPolicyRead
from app.schemas.policy_acknowledgement import (
    PolicyAcknowledgementCreate,
    PolicyAcknowledgementUpdate,
    PolicyAcknowledgementRead,
)
from app.schemas.audit import AuditCreate, AuditUpdate, AuditRead
from app.schemas.compliance_issue import (
    ComplianceIssueCreate,
    ComplianceIssueUpdate,
    ComplianceIssueRead,
)

from app.services.governance import GovernanceService

router = APIRouter(prefix="/governance", tags=["Governance"])

# --- Departments ---
@router.post("/departments/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(dep: DepartmentCreate, db: Session = Depends(get_db)):
    db_dep = db.query(Department).filter(Department.code == dep.code).first()
    if db_dep:
        raise HTTPException(status_code=400, detail="Department code already exists")
    db_dep = Department(name=dep.name, code=dep.code)
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)
    return db_dep

@router.get("/departments/", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

# --- Users ---
@router.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User email already exists")
    if user.department_id:
        dep = db.query(Department).filter(Department.id == user.department_id).first()
        if not dep:
            raise HTTPException(status_code=404, detail="Department not found")
    
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        department_id=user.department_id,
        points_balance=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# --- ESG Policies ---
@router.post("/policies/", response_model=ESGPolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(policy: ESGPolicyCreate, db: Session = Depends(get_db)):
    db_policy = ESGPolicy(
        title=policy.title,
        category=policy.category,
        content=policy.content,
        version=policy.version,
        status=policy.status,
        published_at=datetime.utcnow() if policy.status == "Published" else None
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.get("/policies/", response_model=list[ESGPolicyRead])
def list_policies(db: Session = Depends(get_db)):
    return db.query(ESGPolicy).all()

@router.get("/policies/{policy_id}", response_model=ESGPolicyRead)
def read_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(ESGPolicy).filter(ESGPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.patch("/policies/{policy_id}", response_model=ESGPolicyRead)
def update_policy(policy_id: int, policy_update: ESGPolicyUpdate, db: Session = Depends(get_db)):
    policy = db.query(ESGPolicy).filter(ESGPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    update_data = policy_update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "Published" and policy.status != "Published":
        update_data["published_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(policy, key, value)
    
    db.commit()
    db.refresh(policy)
    return policy

# --- Policy Acknowledgements ---
@router.post("/acknowledgements/", response_model=PolicyAcknowledgementRead, status_code=status.HTTP_201_CREATED)
def log_acknowledgement(ack: PolicyAcknowledgementCreate, db: Session = Depends(get_db)):
    policy = db.query(ESGPolicy).filter(ESGPolicy.id == ack.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    employee = db.query(User).filter(User.id == ack.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    existing = db.query(PolicyAcknowledgement).filter(
        PolicyAcknowledgement.policy_id == ack.policy_id,
        PolicyAcknowledgement.employee_id == ack.employee_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Acknowledgement record already exists for this policy and employee")
    
    db_ack = PolicyAcknowledgement(
        policy_id=ack.policy_id,
        employee_id=ack.employee_id,
        status="Pending",
        acknowledged_at=None
    )
    db.add(db_ack)
    db.commit()
    db.refresh(db_ack)
    return db_ack

@router.patch("/acknowledgements/{ack_id}", response_model=PolicyAcknowledgementRead)
def acknowledge_policy(ack_id: int, ack_update: PolicyAcknowledgementUpdate, db: Session = Depends(get_db)):
    if ack_update.status == "Acknowledged":
        db_ack = GovernanceService.acknowledge_policy(db, ack_id)
        if not db_ack:
            raise HTTPException(status_code=404, detail="Acknowledgement not found")
        db.commit()
        db.refresh(db_ack)
        return db_ack
    else:
        db_ack = db.query(PolicyAcknowledgement).filter(PolicyAcknowledgement.id == ack_id).first()
        if not db_ack:
            raise HTTPException(status_code=404, detail="Acknowledgement not found")
        db_ack.status = ack_update.status
        if ack_update.status == "Pending":
            db_ack.acknowledged_at = None
        db.commit()
        db.refresh(db_ack)
        return db_ack

@router.get("/acknowledgements/", response_model=list[PolicyAcknowledgementRead])
def list_acknowledgements(
    employee_id: int | None = None,
    policy_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(PolicyAcknowledgement)
    if employee_id:
        query = query.filter(PolicyAcknowledgement.employee_id == employee_id)
    if policy_id:
        query = query.filter(PolicyAcknowledgement.policy_id == policy_id)
    if status:
        query = query.filter(PolicyAcknowledgement.status == status)
    return query.all()

# --- Audits ---
@router.post("/audits/", response_model=AuditRead, status_code=status.HTTP_201_CREATED)
def create_audit(audit: AuditCreate, db: Session = Depends(get_db)):
    dep = db.query(Department).filter(Department.id == audit.department_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_audit = Audit(
        title=audit.title,
        department_id=audit.department_id,
        auditor=audit.auditor,
        date=audit.date,
        findings_summary=audit.findings_summary,
        status=audit.status
    )
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

@router.get("/audits/", response_model=list[AuditRead])
def list_audits(db: Session = Depends(get_db)):
    return db.query(Audit).all()

@router.patch("/audits/{audit_id}", response_model=AuditRead)
def update_audit(audit_id: int, audit_update: AuditUpdate, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    update_data = audit_update.model_dump(exclude_unset=True)
    if "department_id" in update_data:
        dep = db.query(Department).filter(Department.id == update_data["department_id"]).first()
        if not dep:
            raise HTTPException(status_code=404, detail="Department not found")
    
    for key, value in update_data.items():
        setattr(audit, key, value)
    
    db.commit()
    db.refresh(audit)
    return audit

# --- Compliance Issues ---
@router.get("/compliance-issues/overdue", response_model=list[ComplianceIssueRead])
def list_overdue_compliance_issues(db: Session = Depends(get_db)):
    return GovernanceService.get_overdue_issues(db)

@router.post("/compliance-issues/", response_model=ComplianceIssueRead, status_code=status.HTTP_201_CREATED)
def create_compliance_issue(issue: ComplianceIssueCreate, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == issue.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    
    if issue.audit_id:
        audit = db.query(Audit).filter(Audit.id == issue.audit_id).first()
        if not audit:
            raise HTTPException(status_code=404, detail="Audit not found")
            
    db_issue = ComplianceIssue(
        audit_id=issue.audit_id,
        severity=issue.severity,
        description=issue.description,
        owner_id=issue.owner_id,
        due_date=issue.due_date,
        status="Open"
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.get("/compliance-issues/", response_model=list[ComplianceIssueRead])
def list_compliance_issues(db: Session = Depends(get_db)):
    return db.query(ComplianceIssue).all()

@router.patch("/compliance-issues/{issue_id}", response_model=ComplianceIssueRead)
def update_compliance_issue(issue_id: int, issue_update: ComplianceIssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(ComplianceIssue).filter(ComplianceIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Compliance issue not found")
    
    update_data = issue_update.model_dump(exclude_unset=True)
    if "owner_id" in update_data:
        owner = db.query(User).filter(User.id == update_data["owner_id"]).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")
    
    if "audit_id" in update_data and update_data["audit_id"] is not None:
        audit = db.query(Audit).filter(Audit.id == update_data["audit_id"]).first()
        if not audit:
            raise HTTPException(status_code=404, detail="Audit not found")
            
    for key, value in update_data.items():
        setattr(issue, key, value)
    
    db.commit()
    db.refresh(issue)
    return issue
