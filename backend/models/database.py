"""
Database models and connection setup.
Uses SQLite + SQLAlchemy (async) — no PostgreSQL needed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from sqlalchemy import (
    Column, String, Float, Integer, Text, Boolean, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./backend/hiring_intelligence.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


class CandidateScore(Base):
    """Mirrors the precomputed_features.db schema for the UI backend."""
    __tablename__ = "candidate_scores"

    candidate_id = Column(String, primary_key=True)
    final_score = Column(Float, nullable=False)
    technical_fit = Column(Float, default=0.0)
    role_fit = Column(Float, default=0.0)
    domain_expertise = Column(Float, default=0.0)
    career_momentum = Column(Float, default=0.0)
    leadership = Column(Float, default=0.0)
    communication = Column(Float, default=0.0)
    adaptability = Column(Float, default=0.0)
    cultural_fit = Column(Float, default=0.0)
    learning_potential = Column(Float, default=0.0)
    evidence_strength = Column(Float, default=0.0)
    is_honeypot = Column(Integer, default=0)
    honeypot_score = Column(Float, default=0.0)
    honeypot_flags = Column(Text, default="[]")
    is_disqualified = Column(Integer, default=0)
    disqualification_reason = Column(Text, default="")
    overall_alignment = Column(Float, default=0.0)
    technical_alignment = Column(Float, default=0.0)
    domain_alignment = Column(Float, default=0.0)
    semantic_similarity = Column(Float, default=0.0)
    risk_overall = Column(Float, default=50.0)
    recruitability_tier = Column(String, default="Moderate")
    recruitability_score = Column(Float, default=0.5)
    opportunity_cost_level = Column(String, default="Medium")
    opportunity_cost_score = Column(Float, default=0.5)
    one_line_reasoning = Column(Text, default="")
    full_analysis_json = Column(Text, default="{}")
    processed_at = Column(Float, default=0.0)


async def get_db():
    """Dependency: async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize DB tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_precomputed_db_path() -> str:
    """Resolve path to the precomputed features SQLite DB."""
    paths = [
        "./ai/pipeline/precomputed_features.db",
        "../ai/pipeline/precomputed_features.db",
        os.environ.get("PRECOMPUTED_DB", ""),
    ]
    for p in paths:
        if p and Path(p).exists():
            return p
    return "./ai/pipeline/precomputed_features.db"
