"""create departments and carbon_transactions tables

Revision ID: 0003_carbon_transaction
Revises: 0002_category
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_carbon_transaction"
down_revision: Union[str, None] = "0002_category"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_departments_name"),
        sa.UniqueConstraint("code", name="uq_departments_code"),
    )

    op.create_table(
        "carbon_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column(
            "source_type",
            sa.Enum("purchase", "manufacturing", "expense", "fleet", name="source_type"),
            nullable=False,
        ),
        sa.Column("source_record_id", sa.Integer(), nullable=True),
        sa.Column("source_reference", sa.String(length=255), nullable=True),
        sa.Column("emission_factor_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("co2e", sa.Float(), nullable=False),
        sa.Column("factor_value", sa.Float(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column(
            "created_by",
            sa.Enum("auto", "manual", name="created_by"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("draft", "confirmed", "cancelled", name="transaction_status"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity >= 0", name="ck_carbon_txn_quantity_non_negative"),
        sa.CheckConstraint("co2e >= 0", name="ck_carbon_txn_co2e_non_negative"),
        sa.CheckConstraint(
            "created_by <> 'auto' OR co2e = quantity * factor_value",
            name="ck_carbon_txn_auto_co2e_derived",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["emission_factor_id"], ["emission_factors.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_carbon_transactions_department_id", "carbon_transactions", ["department_id"]
    )
    op.create_index(
        "ix_carbon_transactions_source_record_id",
        "carbon_transactions",
        ["source_record_id"],
    )
    op.create_index(
        "ix_carbon_transactions_emission_factor_id",
        "carbon_transactions",
        ["emission_factor_id"],
    )
    op.create_index(
        "ix_carbon_transactions_transaction_date",
        "carbon_transactions",
        ["transaction_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_carbon_transactions_transaction_date", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_emission_factor_id", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_source_record_id", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_department_id", table_name="carbon_transactions")
    op.drop_table("carbon_transactions")
    op.drop_table("departments")
    sa.Enum(name="source_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="created_by").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="transaction_status").drop(op.get_bind(), checkfirst=True)
