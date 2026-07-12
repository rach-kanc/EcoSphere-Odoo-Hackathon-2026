"""Standalone Emission Factor seed script (issue #14).

Seeds a realistic set of Emission Factors spanning every ActivityType, with no
dependency on departments/users/etc., so the Emission Factor module can be
exercised in isolation without a live ERP connection.

Idempotent — safe to re-run; skips any factor_code that already exists.

Usage (single command):
    python seed_emission_factors.py
"""
from __future__ import annotations

import sys
from datetime import date

sys.path.insert(0, ".")

from app.core.database import Base, SessionLocal, engine
from app.models.emission_factor import ActivityType, EmissionFactor

EFFECTIVE_START = date(2024, 1, 1)

FACTORS = [
    dict(factor_code="grid.electricity.in", name="India Grid Electricity",
         activity_type=ActivityType.ELECTRICITY, unit="kWh", co2e_per_unit=0.82, source="CEA 2024"),
    dict(factor_code="fuel.diesel", name="Diesel (road)",
         activity_type=ActivityType.FUEL, unit="litre", co2e_per_unit=2.68, source="IPCC 2024"),
    dict(factor_code="fuel.petrol", name="Petrol (road)",
         activity_type=ActivityType.FUEL, unit="litre", co2e_per_unit=2.31, source="IPCC 2024"),
    dict(factor_code="fuel.natural_gas", name="Natural Gas",
         activity_type=ActivityType.FUEL, unit="m3", co2e_per_unit=1.89, source="IPCC 2024"),
    dict(factor_code="travel.air.economy", name="Air Travel - Economy",
         activity_type=ActivityType.TRAVEL, unit="km", co2e_per_unit=0.15, source="DEFRA 2024"),
    dict(factor_code="travel.rail", name="Rail Travel",
         activity_type=ActivityType.TRAVEL, unit="km", co2e_per_unit=0.04, source="DEFRA 2024"),
    dict(factor_code="purchase.paper", name="Office Paper (purchased)",
         activity_type=ActivityType.PURCHASE, unit="kg", co2e_per_unit=0.96, source="EPA 2024"),
    dict(factor_code="purchase.electronics", name="Electronics Hardware (purchased)",
         activity_type=ActivityType.PURCHASE, unit="unit", co2e_per_unit=180.0, source="EPA 2024"),
    dict(factor_code="waste.landfill", name="Landfill Waste",
         activity_type=ActivityType.WASTE, unit="kg", co2e_per_unit=0.45, source="EPA 2024"),
    dict(factor_code="water.supply", name="Water Supply & Treatment",
         activity_type=ActivityType.WATER, unit="m3", co2e_per_unit=0.34, source="WRAP 2024"),
    dict(factor_code="other.remote_work", name="Remote Work (home energy share)",
         activity_type=ActivityType.OTHER, unit="day", co2e_per_unit=1.2, source="Estimate"),
]


def seed_emission_factors() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        existing_codes = {code for (code,) in db.query(EmissionFactor.factor_code).all()}
        to_add = [f for f in FACTORS if f["factor_code"] not in existing_codes]
        if not to_add:
            print("Emission factors already seeded - skipping.")
            return

        for f in to_add:
            EmissionFactor.new_version(db, effective_start=EFFECTIVE_START, **f)
        db.commit()
        print(f"Seeded {len(to_add)} emission factor(s).")


if __name__ == "__main__":
    seed_emission_factors()
