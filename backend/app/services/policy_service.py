"""Business logic for ESGPolicy CRUD and acknowledgements."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.policy import ESGPolicy, PolicyAcknowledgement, PolicyStatus, PolicyType
from app.models.user import User
from app.repositories.policy_repository import PolicyRepository
from app.schemas.policy import PolicyCreate, PolicyUpdate


class PolicyError(Exception):
    pass


class PolicyNotFoundError(PolicyError):
    pass


class PolicyValidationError(PolicyError):
    pass


class PolicyAlreadyAcknowledgedError(PolicyError):
    pass


class PolicyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PolicyRepository(db)

    def list_policies(
        self,
        *,
        policy_type: Optional[PolicyType] = None,
        status: Optional[PolicyStatus] = None,
    ) -> list[ESGPolicy]:
        return self.repo.list(policy_type=policy_type, status=status)

    def get_policy(self, policy_id: int) -> ESGPolicy:
        policy = self.repo.get(policy_id)
        if not policy:
            raise PolicyNotFoundError(f"Policy with ID {policy_id} not found")
        return policy

    def create_policy(self, policy_in: PolicyCreate) -> ESGPolicy:
        policy = ESGPolicy(
            title=policy_in.title,
            type=policy_in.type,
            content=policy_in.content,
            version=policy_in.version,
            effective_date=policy_in.effective_date,
            status=policy_in.status,
        )
        return self.repo.create(policy)

    def update_policy(self, policy_id: int, policy_in: PolicyUpdate) -> ESGPolicy:
        policy = self.get_policy(policy_id)
        
        update_data = policy_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
            
        self.db.flush()
        return policy

    def list_pending_policies(self, user_id: int) -> list[ESGPolicy]:
        return self.repo.list_pending_for_user(user_id)

    def acknowledge_policy(
        self, user_id: int, policy_id: int, signature_text: str
    ) -> PolicyAcknowledgement:
        policy = self.get_policy(policy_id)
        if policy.status != PolicyStatus.ACTIVE:
            raise PolicyValidationError(f"Cannot acknowledge a policy that is in status {policy.status.value}")

        existing = self.repo.get_acknowledgement(user_id, policy_id)
        if existing:
            raise PolicyAlreadyAcknowledgedError("User has already acknowledged this policy")

        # Create acknowledgement record
        ack = PolicyAcknowledgement(
            policy_id=policy_id,
            employee_id=user_id,
            signature_text=signature_text,
        )
        ack = self.repo.create_acknowledgement(ack)

        # Award XP to user
        user = self.db.get(User, user_id)
        if user:
            user.xp_points += 100
            user.level = (user.xp_points // 1000) + 1
            self.db.flush()

        return ack
