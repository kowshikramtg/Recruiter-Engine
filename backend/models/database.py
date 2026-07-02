"""
Database models and connection setup.
Uses plain SQLite (sqlite3) — no ORM, no async dependencies.
The precomputed DB is read-only at API time.
"""
from __future__ import annotations

import os
from pathlib import Path


def get_precomputed_db_path() -> str:
    """Resolve path to the precomputed features SQLite DB."""
    paths = [
        os.environ.get("PRECOMPUTED_DB", ""),
        "./ai/pipeline/precomputed_features.db",
        "../ai/pipeline/precomputed_features.db",
    ]
    for p in paths:
        if p and Path(p).exists():
            return p
    return "./ai/pipeline/precomputed_features.db"
