"""Main FastAPI application with modular routers."""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from models import HealthResponse
from routers import users, products, purchases

# Load environment variables from .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# Validate Neo4j environment variables
if not os.getenv("NEO4J_URI"):
    raise RuntimeError("NEO4J_URI is missing. Ensure .env is correctly configured.")
if not os.getenv("NEO4J_PASSWORD"):
    raise RuntimeError("NEO4J_PASSWORD is missing. Ensure .env is correctly configured.")

# Initialize FastAPI app
app = FastAPI(
    title="Markwave Live Services API",
    version="1.0.0",
    description=(
        "Buffalokart / Markwave live services API. "
        "Provides user onboarding, verification, product and purchase endpoints "
        "backed by Neo4j."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(purchases.router)


# Root and health endpoints
@app.get("/", include_in_schema=False)
async def read_root():
    """Redirect to the interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Simple liveness probe that returns an OK status if the service is up.",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
