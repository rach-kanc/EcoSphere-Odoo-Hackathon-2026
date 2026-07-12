"""create governance tables

Revision ID: 0002_governance_models
Revises: 0001_emission_factor
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_governance_models"
down_revision: Union[str, None] = "0001_emission_factor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. departments table
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_departments_code", "departments", ["code"], unique=True)
    op.create_index("ix_departments_id", "departments", ["id"], unique=False)

    # 2. users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("points_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    # 3. esg_policies table
    op.create_table(
        "esg_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Draft"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_esg_policies_id", "esg_policies", ["id"], unique=False)

    # 4. policy_acknowledgements table
    op.create_table(
        "policy_acknowledgements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("policy_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Pending"),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["policy_id"], ["esg_policies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("policy_id", "employee_id", name="uq_policy_employee"),
    )
    op.create_index("ix_policy_acknowledgements_id", "policy_acknowledgements", ["id"], unique=False)

    # 5. audits table
    op.create_table(
        "audits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("auditor", sa.String(length=255), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("findings_summary", sa.Text(), nullable=True, server_default=""),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Scheduled"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audits_id", "audits", ["id"], unique=False)

    # 6. compliance_issues table
    op.create_table(
        "compliance_issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audit_id", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Open"),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_issues_id", "compliance_issues", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_compliance_issues_id", table_name="compliance_issues")
    op.drop_table("compliance_issues")
    op.drop_index("ix_audits_id", table_name="audits")
    op.drop_table("audits")
    op.drop_index("ix_policy_acknowledgements_id", table_name="policy_acknowledgements")
    op.drop_table("policy_acknowledgements")
    op.drop_index("ix_esg_policies_id", table_name="esg_policies")
    op.drop_table("esg_policies")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_departments_id", table_name="departments")
    op.drop_index("ix_departments_code", table_name="departments")
    op.drop_table("departments")
