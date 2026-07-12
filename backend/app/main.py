"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

import app.models  # noqa: F401  (register models on Base.metadata)
from app.api.v1.categories import router as categories_router
from app.api.v1.csr_activities import router as csr_activities_router
from app.api.v1.gamification import router as gamification_router

app = FastAPI(title="EcoSphere API", version="1.0.0")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(csr_activities_router, prefix="/api/v1")
app.include_router(gamification_router, prefix="/api/v1")
