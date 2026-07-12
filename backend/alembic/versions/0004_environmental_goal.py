"""create environmental_goals table

Revision ID: 0004_environmental_goal
Revises: 0003_carbon_transaction
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_environmental_goal"
down_revision: Union[str, None] = "0003_csr_activity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "environmental_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column(
            "target_metric",
            sa.Enum(
                "total_co2e",
                "reduction_pct",
                "energy",
                "water",
                "waste",
                "renewable_pct",
                "other",
                name="target_metric",
            ),
            nullable=False,
        ),
        sa.Column("baseline_value", sa.Float(), nullable=True),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("on_track", "at_risk", "achieved", "missed", name="goal_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_environmental_goals_department_id", "environmental_goals", ["department_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_environmental_goals_department_id", table_name="environmental_goals")
    op.drop_table("environmental_goals")
    sa.Enum(name="target_metric").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="goal_status").drop(op.get_bind(), checkfirst=True)
