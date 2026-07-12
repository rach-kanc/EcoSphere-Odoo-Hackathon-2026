"""create departments and csr_activities tables

Revision ID: 0003_csr_activity
Revises: 0002_category
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_csr_activity"
down_revision: Union[str, None] = "0002_category"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "csr_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("max_participants", sa.Integer(), nullable=True),
        sa.Column("points_per_participation", sa.Integer(), nullable=False),
        sa.Column("evidence_required", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("Draft", "Active", "Completed", "Archived", name="csr_activity_status"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_csr_activity_valid_date_range",
        ),
        sa.CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name="ck_csr_activity_max_participants_positive",
        ),
        sa.CheckConstraint(
            "points_per_participation >= 0",
            name="ck_csr_activity_points_non_negative",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_csr_activities_category_id", "csr_activities", ["category_id"]
    )
    op.create_index(
        "ix_csr_activities_department_id", "csr_activities", ["department_id"]
    )
    op.create_index("ix_csr_activities_status", "csr_activities", ["status"])
    op.create_index(
        "ix_csr_activities_status_dates",
        "csr_activities",
        ["status", "start_date", "end_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_csr_activities_status_dates", table_name="csr_activities")
    op.drop_index("ix_csr_activities_status", table_name="csr_activities")
    op.drop_index("ix_csr_activities_department_id", table_name="csr_activities")
    op.drop_index("ix_csr_activities_category_id", table_name="csr_activities")
    op.drop_table("csr_activities")
    op.drop_table("departments")
    sa.Enum(name="csr_activity_status").drop(op.get_bind(), checkfirst=True)
