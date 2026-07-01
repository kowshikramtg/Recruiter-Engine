"""
Time Machine Engine — simulation engine for "what-if" analysis.
Allows replaying the pipeline with altered parameters.
"""
from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def simulate_alternative_scenario(
    candidate_ids: list[str],
    db_path: str,
    scenario_params: dict[str, Any],
) -> list[dict]:
    """
    Simulate a different hiring scenario by adjusting scoring weights.
    
    scenario_params can include:
    - weight_overrides: {dimension: new_weight}
    - exclude_services_firms: bool
    - min_github_score: float
    - max_notice_days: int
    - preferred_location_bonus: float
    
    Returns re-ranked list with delta from original ranking.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Load all specified candidates (or top 200 if none specified)
    if candidate_ids:
        placeholders = ",".join("?" * len(candidate_ids))
        rows = conn.execute(
            f"SELECT * FROM candidate_scores WHERE candidate_id IN ({placeholders})",
            candidate_ids
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM candidate_scores ORDER BY final_score DESC LIMIT 200"
        ).fetchall()
    conn.close()

    weight_overrides = scenario_params.get("weight_overrides", {})
    exclude_services = scenario_params.get("exclude_services_firms", False)
    min_github = float(scenario_params.get("min_github_score", -1))
    max_notice = int(scenario_params.get("max_notice_days", 180))

    results = []
    for row in rows:
        full = json.loads(row["full_analysis_json"] or "{}")
        intel = full.get("intelligence") or {}

        # Apply filters
        if exclude_services and intel.get("is_entirely_services_firm", False):
            continue
        if min_github >= 0 and intel.get("github_activity_score", -1) < min_github:
            continue

        signals = {}
        for entry in full.get("intelligence", {}).get("career_history", []):
            pass  # signals not stored separately

        # Compute simulated score with weight overrides
        sc = full.get("scorecard") or {}
        base_dims = {
            "technical_fit": float(sc.get("technical_fit", 0)) * weight_overrides.get("technical_fit", 0.28),
            "role_fit": float(sc.get("role_fit", 0)) * weight_overrides.get("role_fit", 0.18),
            "domain_expertise": float(sc.get("domain_expertise", 0)) * weight_overrides.get("domain_expertise", 0.10),
            "career_momentum": float(sc.get("career_momentum", 0)) * weight_overrides.get("career_momentum", 0.08),
            "leadership": float(sc.get("leadership", 0)) * weight_overrides.get("leadership", 0.05),
            "cultural_fit": float(sc.get("cultural_fit", 0)) * weight_overrides.get("cultural_fit", 0.05),
            "adaptability": float(sc.get("adaptability", 0)) * weight_overrides.get("adaptability", 0.04),
            "learning_potential": float(sc.get("learning_potential", 0)) * weight_overrides.get("learning_potential", 0.03),
        }

        simulated_score = sum(base_dims.values()) / 100.0
        original_score = float(row["final_score"])

        results.append({
            "candidate_id": row["candidate_id"],
            "original_score": round(original_score, 4),
            "simulated_score": round(min(simulated_score, 1.0), 4),
            "score_delta": round(simulated_score - original_score, 4),
            "name": intel.get("name", row["candidate_id"]),
            "current_title": intel.get("current_title", ""),
            "years_of_experience": intel.get("years_of_experience", 0),
        })

    # Re-rank by simulated score
    results.sort(key=lambda x: (-x["simulated_score"], x["candidate_id"]))
    for i, r in enumerate(results):
        r["simulated_rank"] = i + 1

    return results[:100]


def get_simulation_presets() -> list[dict]:
    """Return pre-built simulation scenarios."""
    return [
        {
            "id": "technical_heavy",
            "name": "Technical Skills First",
            "description": "What if we weighted technical skills at 50% instead of 28%?",
            "params": {
                "weight_overrides": {
                    "technical_fit": 0.50,
                    "role_fit": 0.15,
                    "domain_expertise": 0.10,
                    "career_momentum": 0.05,
                    "leadership": 0.05,
                    "cultural_fit": 0.05,
                    "adaptability": 0.05,
                    "learning_potential": 0.05,
                }
            }
        },
        {
            "id": "product_company_only",
            "name": "Product Company Only",
            "description": "What if we excluded all services-firm candidates?",
            "params": {
                "exclude_services_firms": True,
            }
        },
        {
            "id": "github_required",
            "name": "GitHub Activity Required",
            "description": "What if we required active GitHub presence (score >= 20)?",
            "params": {
                "min_github_score": 20.0,
            }
        },
        {
            "id": "leadership_focused",
            "name": "Leadership Focused",
            "description": "What if mentorship capacity was the primary filter?",
            "params": {
                "weight_overrides": {
                    "technical_fit": 0.25,
                    "role_fit": 0.15,
                    "leadership": 0.30,
                    "domain_expertise": 0.10,
                    "career_momentum": 0.08,
                    "cultural_fit": 0.07,
                    "adaptability": 0.03,
                    "learning_potential": 0.02,
                }
            }
        },
    ]
