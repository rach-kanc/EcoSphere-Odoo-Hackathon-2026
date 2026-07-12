from fastapi import FastAPI
from app.api.v1.governance import router as governance_router

app = FastAPI(
    title="EcoSphere ESG Platform",
    description="Backend API for EcoSphere ESG management and compliance tracking.",
    version="1.0.0"
)

# Include Routers
app.include_router(governance_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoSphere ESG Platform API"}
