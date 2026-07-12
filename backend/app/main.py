"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

import app.models  # noqa: F401
from app.api.v1.categories import router as categories_router
from app.api.v1.governance import router as governance_router

app = FastAPI(
      title="EcoSphere ESG Platform",
      description="Backend API for EcoSphere ESG management and compliance tracking.",
      version="1.0.0"
)

# Include Routers
app.include_router(categories_router, prefix="/api/v1")
app.include_router(governance_router)

@app.get("/")
def read_root():
      return {"message": "Welcome to EcoSphere ESG Platform API"}