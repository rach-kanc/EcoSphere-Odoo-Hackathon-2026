"""create emission_factors table

Revision ID: 0001_emission_factor
Revises:
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_emission_factor"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emission_factors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("factor_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "activity_type",
            sa.Enum(
                "fuel",
                "electricity",
                "travel",
                "purchase",
                "waste",
                "water",
                "other",
                name="activity_type",
            ),
            nullable=False,
        ),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("co2e_per_unit", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=512), nullable=True),
        sa.Column("effective_start", sa.Date(), nullable=False),
        sa.Column("effective_end", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", name="factor_status"),
            nullable=False,
        ),
        sa.CheckConstraint("co2e_per_unit >= 0", name="ck_emission_factor_co2e_non_negative"),
        sa.CheckConstraint(
            "effective_end IS NULL OR effective_end >= effective_start",
            name="ck_emission_factor_valid_period",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_emission_factors_factor_code", "emission_factors", ["factor_code"]
    )
    op.create_index(
        "ix_emission_factor_code_period",
        "emission_factors",
        ["factor_code", "effective_start"],
    )


def downgrade() -> None:
    op.drop_index("ix_emission_factor_code_period", table_name="emission_factors")
    op.drop_index("ix_emission_factors_factor_code", table_name="emission_factors")
    op.drop_table("emission_factors")
    sa.Enum(name="activity_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="factor_status").drop(op.get_bind(), checkfirst=True)
