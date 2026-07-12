"""ORM models package.

Importing every model module here ensures they are registered on
``Base.metadata`` so ``Base.metadata.create_all`` and Alembic autogenerate
can discover every table in one import.
"""
# ── Teammate-owned models (do not modify these) ────────────────────────────
from app.models.emission_factor import (  # noqa: F401
    ActivityType,
    EmissionFactor,
    FactorStatus,
)
from app.models.category import Category, CategoryStatus, CategoryType  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.csr_activity import CSRActivity, CSRActivityStatus, EmployeeParticipation, ParticipationStatus  # noqa: F401

# ── Feature models (Governance, Environmental, Gamification, Dashboard) ────
from app.models.user import User, UserRole  # noqa: F401
from app.models.carbon_transaction import CarbonTransaction, TransactionSource  # noqa: F401
from app.models.environmental_goal import EnvironmentalGoal, GoalStatus, TargetMetric  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_esg_profile import ProductESGProfile  # noqa: F401
from app.models.policy import ESGPolicy, PolicyType, PolicyStatus, PolicyAcknowledgement  # noqa: F401
from app.models.audit import Audit, AuditStatus, ComplianceIssue, IssueSeverity, IssueStatus  # noqa: F401
from app.models.challenge import Challenge, ChallengeDifficulty, ChallengeStatus, ChallengeParticipation  # noqa: F401
from app.models.badge import Badge, BadgeRarity, UserBadge  # noqa: F401
from app.models.reward import Reward, RewardStatus, RewardRedemption, RedemptionStatus  # noqa: F401
from app.models.department_score import DepartmentScore  # noqa: F401
from app.models.notification import Notification, NotificationType  # noqa: F401
from app.models.app_setting import AppSetting  # noqa: F401
from app.models.emission_factor_mapping import EmissionFactorMapping  # noqa: F401
from app.models.pending_auto_calculation import (  # noqa: F401
    PendingAutoCalculation,
    PendingStatus,
)

__all__ = [
    "ActivityType",
    "EmissionFactor",
    "FactorStatus",
    "Category",
    "CategoryStatus",
    "CategoryType",
    "Department",
    "CSRActivity",
    "CSRActivityStatus",
    "EmployeeParticipation",
    "ParticipationStatus",
    "User",
    "UserRole",
    "CarbonTransaction",
    "TransactionSource",
    "EnvironmentalGoal",
    "GoalStatus",
    "TargetMetric",
    "Product",
    "ProductESGProfile",
    "ESGPolicy",
    "PolicyType",
    "PolicyStatus",
    "PolicyAcknowledgement",
    "Audit",
    "AuditStatus",
    "ComplianceIssue",
    "IssueSeverity",
    "IssueStatus",
    "Challenge",
    "ChallengeDifficulty",
    "ChallengeStatus",
    "ChallengeParticipation",
    "Badge",
    "BadgeRarity",
    "UserBadge",
    "Reward",
    "RewardStatus",
    "RewardRedemption",
    "RedemptionStatus",
    "DepartmentScore",
    "Notification",
    "NotificationType",
    "AppSetting",
    "EmissionFactorMapping",
    "PendingAutoCalculation",
    "PendingStatus",
]
