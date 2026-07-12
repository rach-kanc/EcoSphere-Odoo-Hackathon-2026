"""create department_scores table

Adds the monthly ESG score snapshot table consumed by the Environmental
Score calculation engine (issue #10).

Revision ID: 0007_department_score
Revises: 0006_auto_emission
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_department_score"
down_revision: Union[str, None] = "0006_auto_emission"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "department_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("environmental_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("social_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("governance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "environmental_score >= 0 AND environmental_score <= 100", name="ck_env_score_range"
        ),
        sa.CheckConstraint("social_score >= 0 AND social_score <= 100", name="ck_soc_score_range"),
        sa.CheckConstraint(
            "governance_score >= 0 AND governance_score <= 100", name="ck_gov_score_range"
        ),
        sa.CheckConstraint("total_score >= 0 AND total_score <= 100", name="ck_total_score_range"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department_id", "period", name="uq_department_score_dept_period"),
    )


def downgrade() -> None:
    op.drop_table("department_scores")
