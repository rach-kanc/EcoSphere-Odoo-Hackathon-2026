"""Tests for the standalone Emission Factor seed script (issue #14)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.emission_factor import ActivityType, EmissionFactor
import seed_emission_factors as seed_mod


@pytest.fixture()
def patched_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, future=True)
    monkeypatch.setattr(seed_mod, "engine", engine)
    monkeypatch.setattr(seed_mod, "SessionLocal", session_local)
    return session_local


def test_seed_covers_every_activity_type_and_is_idempotent(patched_db):
    seed_mod.seed_emission_factors()
    with patched_db() as db:
        factors = db.query(EmissionFactor).all()
        assert len(factors) == len(seed_mod.FACTORS)
        assert {f.activity_type for f in factors} == set(ActivityType)

    # Re-running does not duplicate rows.
    seed_mod.seed_emission_factors()
    with patched_db() as db:
        assert db.query(EmissionFactor).count() == len(seed_mod.FACTORS)
