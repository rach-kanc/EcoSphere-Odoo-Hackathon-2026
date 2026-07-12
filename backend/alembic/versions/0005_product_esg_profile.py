"""create products and product_esg_profiles tables

Revision ID: 0005_product_esg_profile
Revises: 0004_environmental_goal
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_product_esg_profile"
down_revision: Union[str, None] = "0004_environmental_goal"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
    )
    op.create_index("ix_products_sku", "products", ["sku"])

    op.create_table(
        "product_esg_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("primary_emission_factor_id", sa.Integer(), nullable=True),
        sa.Column("is_recyclable", sa.Boolean(), nullable=False),
        sa.Column("is_biodegradable", sa.Boolean(), nullable=False),
        sa.Column("is_carbon_neutral", sa.Boolean(), nullable=False),
        sa.Column("recycled_content_pct", sa.Float(), nullable=True),
        sa.Column("certification", sa.String(length=255), nullable=True),
        sa.Column("ecolabel", sa.String(length=255), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["primary_emission_factor_id"], ["emission_factors.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", name="uq_product_esg_profiles_product_id"),
    )
    op.create_index(
        "ix_product_esg_profiles_product_id", "product_esg_profiles", ["product_id"]
    )

    op.create_table(
        "product_esg_emission_factors",
        sa.Column("product_esg_profile_id", sa.Integer(), nullable=False),
        sa.Column("emission_factor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_esg_profile_id"], ["product_esg_profiles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["emission_factor_id"], ["emission_factors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("product_esg_profile_id", "emission_factor_id"),
    )


def downgrade() -> None:
    op.drop_table("product_esg_emission_factors")
    op.drop_index("ix_product_esg_profiles_product_id", table_name="product_esg_profiles")
    op.drop_table("product_esg_profiles")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_table("products")
