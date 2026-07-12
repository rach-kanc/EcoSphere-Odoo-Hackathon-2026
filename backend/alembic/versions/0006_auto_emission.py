"""create auto emission engine tables

Adds the settings store, emission-factor mapping configuration, and the
pending-review queue used by the auto emission calculation engine (issue #7).

Revision ID: 0006_auto_emission
Revises: 0005_product_esg_profile
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_auto_emission"
down_revision: Union[str, None] = "0005_product_esg_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _source_type_enum(bind):
    """Reference the existing ``source_type`` enum without re-creating it."""
    values = ("purchase", "manufacturing", "expense", "fleet")
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*values, name="source_type", create_type=False)
    return sa.Enum(*values, name="source_type")


def upgrade() -> None:
    bind = op.get_bind()
    source_type = _source_type_enum(bind)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.String(length=512), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_app_settings_key"),
    )
    op.create_index("ix_app_settings_key", "app_settings", ["key"])

    op.create_table(
        "emission_factor_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("match_key", sa.String(length=128), nullable=False),
        sa.Column("factor_code", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_type", "match_key", name="uq_emission_factor_mapping_source_key"
        ),
    )

    op.create_table(
        "pending_auto_calculations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("source_record_id", sa.Integer(), nullable=False),
        sa.Column("source_reference", sa.String(length=255), nullable=True),
        sa.Column("match_key", sa.String(length=128), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(length=512), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "resolved", "dismissed", name="pending_status"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_type", "source_record_id", name="uq_pending_auto_calc_source"
        ),
    )


def downgrade() -> None:
    op.drop_table("pending_auto_calculations")
    op.drop_table("emission_factor_mappings")
    op.drop_index("ix_app_settings_key", table_name="app_settings")
    op.drop_table("app_settings")
    sa.Enum(name="pending_status").drop(op.get_bind(), checkfirst=True)
