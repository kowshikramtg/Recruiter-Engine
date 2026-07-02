"""
FastAPI application — Hiring Intelligence Engine Backend.
"""
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.routers.routers import (
    candidates_router, dashboard_router, jobs_router,
    time_machine_router, compare_router
)

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    print("Hiring Intelligence Engine API starting...")
    # Verify precomputed DB is available
    from backend.models.database import get_precomputed_db_path
    db_path = get_precomputed_db_path()
    if Path(db_path).exists():
        import sqlite3
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM candidate_scores").fetchone()[0]
        conn.close()
        print(f"Precomputed database loaded: {count:,} candidates")
    else:
        print(f"WARNING: Precomputed database not found at {db_path}")
        print("  Run 'python precompute.py' to generate it first.")
        print("  API will return 503 errors until database is available.")
    yield
    print("Hiring Intelligence Engine API shutting down...")


app = FastAPI(
    title="Hiring Intelligence Engine",
    description=(
        "Enterprise AI Recruiter — evidence-driven, explainable, multi-dimensional hiring intelligence. "
        "Replaces ATS keyword matching with contextual reasoning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(candidates_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(time_machine_router)
app.include_router(compare_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    from backend.models.database import get_precomputed_db_path
    db_ready = Path(get_precomputed_db_path()).exists()
    return {
        "status": "healthy" if db_ready else "degraded",
        "database": "ready" if db_ready else "missing — run python precompute.py",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    return {
        "name": "Hiring Intelligence Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }
