"""Data access helpers for ESGPolicy and PolicyAcknowledgement records."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.policy import ESGPolicy, PolicyAcknowledgement, PolicyStatus, PolicyType


class PolicyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        policy_type: Optional[PolicyType] = None,
        status: Optional[PolicyStatus] = None,
    ) -> list[ESGPolicy]:
        query = self.db.query(ESGPolicy)
        if policy_type is not None:
            query = query.filter(ESGPolicy.type == policy_type)
        if status is not None:
            query = query.filter(ESGPolicy.status == status)
        return query.order_by(ESGPolicy.effective_date.desc(), ESGPolicy.id.desc()).all()

    def get(self, policy_id: int) -> Optional[ESGPolicy]:
        return self.db.get(ESGPolicy, policy_id)

    def create(self, policy: ESGPolicy) -> ESGPolicy:
        self.db.add(policy)
        self.db.flush()
        return policy

    def delete(self, policy: ESGPolicy) -> None:
        self.db.delete(policy)

    def get_acknowledgement(self, employee_id: int, policy_id: int) -> Optional[PolicyAcknowledgement]:
        return (
            self.db.query(PolicyAcknowledgement)
            .filter(
                PolicyAcknowledgement.employee_id == employee_id,
                PolicyAcknowledgement.policy_id == policy_id,
            )
            .one_or_none()
        )

    def create_acknowledgement(self, ack: PolicyAcknowledgement) -> PolicyAcknowledgement:
        self.db.add(ack)
        self.db.flush()
        return ack

    def list_pending_for_user(self, user_id: int) -> list[ESGPolicy]:
        signed_subquery = (
            self.db.query(PolicyAcknowledgement.policy_id)
            .filter(PolicyAcknowledgement.employee_id == user_id)
            .subquery()
        )
        return (
            self.db.query(ESGPolicy)
            .filter(ESGPolicy.status == PolicyStatus.ACTIVE)
            .filter(ESGPolicy.id.not_in(signed_subquery))
            .order_by(ESGPolicy.effective_date.desc(), ESGPolicy.id.desc())
            .all()
        )
