"""create categories table

Revision ID: 0002_category
Revises: 0001_emission_factor
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_category"
down_revision: Union[str, None] = "0001_emission_factor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sa.Enum("CSR_ACTIVITY", "CHALLENGE", name="category_type"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("Active", "Inactive", name="category_status"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_type", "categories", ["type"])
    op.create_index("ix_categories_status", "categories", ["status"])
    op.create_index("ix_categories_type_status", "categories", ["type", "status"])


def downgrade() -> None:
    op.drop_index("ix_categories_type_status", table_name="categories")
    op.drop_index("ix_categories_status", table_name="categories")
    op.drop_index("ix_categories_type", table_name="categories")
    op.drop_table("categories")
    sa.Enum(name="category_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="category_status").drop(op.get_bind(), checkfirst=True)
