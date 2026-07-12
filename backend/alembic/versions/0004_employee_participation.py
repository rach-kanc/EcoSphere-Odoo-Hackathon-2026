"""create employee participations and social dependencies

Revision ID: 0004_employee_participation
Revises: 0003_carbon_transaction
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_employee_participation"
down_revision: Union[str, None] = "0003_carbon_transaction"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "system_admin",
                "esg_manager",
                "dept_manager",
                "employee",
                "auditor",
                name="user_role",
            ),
            nullable=False,
        ),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("xp_points", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "csr_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("max_participants", sa.Integer(), nullable=True),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.Column("evidence_required", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("upcoming", "ongoing", "completed", "cancelled", name="activity_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_csr_activities_category_id", "csr_activities", ["category_id"])
    op.create_index("ix_csr_activities_status", "csr_activities", ["status"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "challenge_approved",
                "challenge_rejected",
                "badge_unlocked",
                "reward_redeemed",
                "csr_approved",
                "csr_rejected",
                "compliance_issue_created",
                "compliance_issue_overdue",
                "policy_reminder",
                "general",
                name="notification_type",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("related_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])

    op.create_table(
        "employee_participations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("proof", sa.String(length=512), nullable=True),
        sa.Column(
            "approval_status",
            sa.Enum("Pending", "Approved", "Rejected", name="participation_status"),
            nullable=False,
        ),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("completion_date", sa.Date(), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "points_earned >= 0",
            name="ck_employee_participations_points_non_negative",
        ),
        sa.ForeignKeyConstraint(["activity_id"], ["csr_activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "employee_id",
            "activity_id",
            name="uq_employee_participations_employee_activity",
        ),
    )
    op.create_index(
        "ix_employee_participations_activity_id",
        "employee_participations",
        ["activity_id"],
    )
    op.create_index(
        "ix_employee_participations_employee_id",
        "employee_participations",
        ["employee_id"],
    )

    # Add missing departments columns (head_id, parent_id, employee_count, status, created_at)
    with op.batch_alter_table("departments") as batch_op:
        batch_op.add_column(sa.Column("head_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("parent_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("employee_count", sa.Integer(), server_default="0", nullable=False))
        batch_op.add_column(sa.Column("status", sa.Enum("active", "inactive", name="dept_status"), server_default="active", nullable=False))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
        batch_op.create_foreign_key("fk_departments_head_id_users", "users", ["head_id"], ["id"], ondelete="SET NULL")
        batch_op.create_foreign_key("fk_departments_parent_id_departments", "departments", ["parent_id"], ["id"], ondelete="SET NULL")

    # Add missing categories.created_at column
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_column("created_at")

    with op.batch_alter_table("departments") as batch_op:
        batch_op.drop_constraint("fk_departments_parent_id_departments", type_="foreignkey")
        batch_op.drop_constraint("fk_departments_head_id_users", type_="foreignkey")
        batch_op.drop_column("created_at")
        batch_op.drop_column("status")
        batch_op.drop_column("employee_count")
        batch_op.drop_column("parent_id")
        batch_op.drop_column("head_id")

    op.drop_index("ix_employee_participations_employee_id", table_name="employee_participations")
    op.drop_index("ix_employee_participations_activity_id", table_name="employee_participations")
    op.drop_table("employee_participations")
    op.drop_index("ix_notifications_recipient_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_csr_activities_status", table_name="csr_activities")
    op.drop_index("ix_csr_activities_category_id", table_name="csr_activities")
    op.drop_table("csr_activities")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum(name="participation_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="notification_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="activity_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="dept_status").drop(op.get_bind(), checkfirst=True)
