from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.compliance_issue import ComplianceIssue
from app.models.policy_acknowledgement import PolicyAcknowledgement
from app.models.user import User

class GovernanceService:
    @staticmethod
    def get_overdue_issues(db: Session) -> list[ComplianceIssue]:
        """Retrieve all compliance issues that are open/in progress and past their due date."""
        now = datetime.utcnow()
        return (
            db.query(ComplianceIssue)
            .filter(
                and_(
                    ComplianceIssue.status != "Resolved",
                    ComplianceIssue.due_date < now
                )
            )
            .all()
        )

    @staticmethod
    def acknowledge_policy(db: Session, acknowledgement_id: int) -> PolicyAcknowledgement | None:
        """Mark a policy as acknowledged, set timestamp, and award gamification points to the employee."""
        ack = db.query(PolicyAcknowledgement).filter(PolicyAcknowledgement.id == acknowledgement_id).first()
        if not ack:
            return None
        
        if ack.status != "Acknowledged":
            ack.status = "Acknowledged"
            ack.acknowledged_at = datetime.utcnow()
            
            # Award gamification points (e.g., 10 points for completing ESG acknowledgement)
            employee = db.query(User).filter(User.id == ack.employee_id).first()
            if employee:
                employee.points_balance += 10
            
            db.flush()
        
        return ack
