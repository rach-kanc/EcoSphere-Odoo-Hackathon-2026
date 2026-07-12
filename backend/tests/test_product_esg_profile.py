"""Tests for ProductESGProfile (issue #4 acceptance criteria)."""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
import app.models  # noqa: F401  (register all models on metadata)
from app.models.carbon_transaction import CarbonTransaction, SourceType
from app.models.emission_factor import ActivityType, EmissionFactor
from app.models.product import Product
from app.models.product_esg_profile import ProductESGProfile


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def steel_factor(db):
    f = EmissionFactor.new_version(
        db, factor_code="material.steel", name="Steel", activity_type=ActivityType.PURCHASE,
        unit="kg", co2e_per_unit=1.9, effective_start=date(2024, 1, 1),
    )
    db.commit()
    return f


def test_profile_links_product_and_factors(db, steel_factor):
    product = Product(name="Steel Widget", sku="SW-001")
    db.add(product)
    db.flush()

    profile = ProductESGProfile(
        product_id=product.id,
        emission_factors=[steel_factor],
        primary_emission_factor=steel_factor,
        is_recyclable=True,
        recycled_content_pct=40.0,
        certification="ISO 14001",
        attributes={"origin": "recycled_scrap"},
    )
    db.add(profile)
    db.commit()

    # Linked to the product (one-to-one both directions).
    assert product.esg_profile is profile
    assert profile.product.sku == "SW-001"
    # Associated emission factor(s) + sustainability attributes persisted.
    assert steel_factor in profile.emission_factors
    assert profile.is_recyclable is True
    assert profile.attributes["origin"] == "recycled_scrap"


def test_one_profile_per_product_enforced(db):
    product = Product(name="Gadget", sku="G-1")
    db.add(product)
    db.flush()
    db.add(ProductESGProfile(product_id=product.id))
    db.commit()

    from sqlalchemy.exc import IntegrityError

    db.add(ProductESGProfile(product_id=product.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_emission_factor_for_calculation_prefers_primary(db, steel_factor):
    transport = EmissionFactor.new_version(
        db, factor_code="transport.truck", name="Truck", activity_type=ActivityType.FUEL,
        unit="km", co2e_per_unit=0.12, effective_start=date(2024, 1, 1),
    )
    db.commit()

    # Profile with a primary set (plus other associated factors) -> primary wins.
    p1 = Product(name="Beam", sku="B-1")
    db.add(p1)
    db.flush()
    with_primary = ProductESGProfile(
        product_id=p1.id,
        emission_factors=[transport, steel_factor],
        primary_emission_factor=steel_factor,
    )
    db.add(with_primary)
    db.commit()
    assert with_primary.emission_factor_for_calculation() is steel_factor

    # Profile with no primary -> falls back to its (only) associated factor.
    p2 = Product(name="Panel", sku="P-1")
    db.add(p2)
    db.flush()
    no_primary = ProductESGProfile(product_id=p2.id, emission_factors=[transport])
    db.add(no_primary)
    db.commit()
    assert no_primary.emission_factor_for_calculation() is transport


def test_profile_feeds_auto_carbon_calculation(db, steel_factor):
    """A Manufacturing/Purchase record can auto-calculate CO2e via the profile."""
    product = Product(name="Steel Widget", sku="SW-9")
    db.add(product)
    db.flush()
    profile = ProductESGProfile(
        product_id=product.id, primary_emission_factor=steel_factor,
    )
    db.add(profile)
    db.commit()

    factor = profile.emission_factor_for_calculation()
    txn = CarbonTransaction.record_auto(
        db,
        source_type=SourceType.PURCHASE,
        quantity=100.0,  # 100 kg of steel
        transaction_date=date(2024, 6, 1),
        emission_factor=factor,
        source_reference=f"product:{product.id}",
    )
    db.commit()
    assert txn.co2e == pytest.approx(190.0)  # 100 kg x 1.9 kgCO2e/kg
