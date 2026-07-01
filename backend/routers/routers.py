"""FastAPI routers for all API endpoints."""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.schemas.schemas import (
    PaginatedCandidates, CandidateDetailSchema,
    DashboardStatsSchema, ChartDataSchema, RoleDNASchema
)
from backend.services.ranking_service import (
    get_ranked_candidates, get_candidate_detail,
    get_dashboard_stats, get_chart_data
)

# --- Candidates Router ---
candidates_router = APIRouter(prefix="/api/v1/candidates", tags=["candidates"])

@candidates_router.get("", response_model=PaginatedCandidates)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    exclude_honeypots: bool = Query(True),
):
    """Get paginated ranked candidates."""
    try:
        return get_ranked_candidates(
            page=page,
            page_size=page_size,
            min_score=min_score,
            exclude_honeypots=exclude_honeypots,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@candidates_router.get("/{candidate_id}", response_model=CandidateDetailSchema)
async def get_candidate(candidate_id: str):
    """Get full analysis for a specific candidate."""
    try:
        detail = get_candidate_detail(candidate_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        return detail
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# --- Dashboard Router ---
dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@dashboard_router.get("/stats", response_model=DashboardStatsSchema)
async def dashboard_stats():
    """Get dashboard summary statistics."""
    try:
        return get_dashboard_stats()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@dashboard_router.get("/charts", response_model=ChartDataSchema)
async def dashboard_charts():
    """Get chart data for dashboard visualizations."""
    try:
        return get_chart_data()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# --- Jobs/Role DNA Router ---
jobs_router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@jobs_router.get("/current", response_model=RoleDNASchema)
async def get_current_job():
    """Get the current job description and Role DNA."""
    import json, os
    from pathlib import Path

    role_dna_path = os.environ.get("ROLE_DNA_PATH", "./ai/role_dna/role_dna_output.json")
    p = Path(role_dna_path)
    if not p.exists():
        # Return default from engine
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from ai.role_dna.engine import build_role_dna_from_jd_text
        dna = build_role_dna_from_jd_text("", llm_provider=None)
    else:
        with open(str(p), "r", encoding="utf-8") as f:
            data = json.load(f)
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from ai.role_dna.engine import RoleDNA
        # Reconstruct (simplified for response)
        dna_dict = data

    return RoleDNASchema(
        title=dna_dict.get("title", "Senior AI Engineer"),
        company=dna_dict.get("company", "Redrob AI"),
        experience_min_years=float(dna_dict.get("experience_min_years", 5)),
        experience_max_years=float(dna_dict.get("experience_max_years", 9)),
        must_have_skills=dna_dict.get("must_have_skills", []),
        preferred_skills=dna_dict.get("preferred_skills", []),
        target_titles=dna_dict.get("target_titles", []),
        responsibilities=dna_dict.get("responsibilities", []),
        success_indicators=dna_dict.get("success_indicators", []),
        hidden_expectations=dna_dict.get("hidden_expectations", []),
        technical_competencies=dna_dict.get("technical_competencies", []),
        domain_knowledge=dna_dict.get("domain_knowledge", []),
        seniority_level=dna_dict.get("seniority_level", "senior"),
        leadership_requirements=dna_dict.get("leadership_requirements", ""),
        communication_expectations=dna_dict.get("communication_expectations", ""),
        trainable_skills=dna_dict.get("trainable_skills", []),
        notice_preference_days=int(dna_dict.get("notice_preference_days", 30)),
        notice_max_days=int(dna_dict.get("notice_max_days", 90)),
        requires_production_experience=bool(dna_dict.get("requires_production_experience", True)),
    )
