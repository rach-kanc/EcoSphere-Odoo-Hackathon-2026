"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

import app.models  # noqa: F401  (register models on Base.metadata)
from app.api.v1.auth import router as auth_router
from app.api.v1.auto_calculation import router as auto_calculation_router
from app.api.v1.carbon_transactions import router as carbon_transactions_router
from app.api.v1.categories import router as categories_router
from app.api.v1.csr_activities import router as csr_activities_router
from app.api.v1.departments import router as departments_router
from app.api.v1.emission_factor_mappings import router as emission_factor_mappings_router
from app.api.v1.emission_factors import router as emission_factors_router
from app.api.v1.policies import router as policies_router
from app.api.v1.settings import router as settings_router

app = FastAPI(title="EcoSphere API", version="1.0.0")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(auto_calculation_router, prefix="/api/v1")
app.include_router(carbon_transactions_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(csr_activities_router, prefix="/api/v1")
app.include_router(departments_router, prefix="/api/v1")
app.include_router(emission_factor_mappings_router, prefix="/api/v1")
app.include_router(emission_factors_router, prefix="/api/v1")
app.include_router(policies_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
