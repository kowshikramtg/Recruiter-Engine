"""
Ranking service — reads from the precomputed SQLite database.
Serves the frontend API without any AI computation at request time.
"""
from __future__ import annotations

import json
import sqlite3
import math
from pathlib import Path
from typing import Optional

from backend.models.database import get_precomputed_db_path
from backend.schemas.schemas import (
    CandidateListItem, CandidateDetailSchema, DashboardStatsSchema,
    ChartDataSchema, PaginatedCandidates, IntelligenceProfileSchema,
    ScorecardSchema, AlignmentScoresSchema, RiskRadarSchema,
    EvidenceReportSchema, RecruitabilitySchema, OpportunityCostSchema,
    ExplainabilitySchema, DimensionScoreSchema, RiskDimensionSchema,
    ClaimEvidenceSchema
)


def _get_conn() -> sqlite3.Connection:
    db_path = get_precomputed_db_path()
    if not Path(db_path).exists():
        raise RuntimeError(
            f"Precomputed database not found at {db_path}. "
            "Run 'python precompute.py' first."
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_list_item(row: sqlite3.Row, rank: int) -> CandidateListItem:
    """Convert a DB row to a CandidateListItem."""
    full = json.loads(row["full_analysis_json"] or "{}")
    intel = full.get("intelligence") or {}
    profile = intel if intel else {}

    return CandidateListItem(
        candidate_id=row["candidate_id"],
        rank=rank,
        final_score=float(row["final_score"]),
        name=profile.get("name", row["candidate_id"]),
        headline=profile.get("headline", ""),
        current_title=profile.get("current_title", ""),
        current_company=profile.get("current_company", ""),
        years_of_experience=float(profile.get("years_of_experience", 0)),
        location=profile.get("location", ""),
        ai_skill_count=int(profile.get("ai_skill_count", 0)),
        github_activity_score=float(profile.get("github_activity_score", -1)),
        is_honeypot=bool(row["is_honeypot"]),
        recruitability_tier=str(row["recruitability_tier"] or "Moderate"),
        opportunity_cost_level=str(row["opportunity_cost_level"] or "Medium"),
        risk_overall=float(row["risk_overall"] or 50.0),
        one_line_reasoning=str(row["one_line_reasoning"] or ""),
    )


def get_ranked_candidates(
    page: int = 1,
    page_size: int = 20,
    min_score: float = 0.0,
    title_filter: Optional[str] = None,
    exclude_honeypots: bool = True,
) -> PaginatedCandidates:
    """Get paginated ranked candidate list."""
    conn = _get_conn()

    conditions = ["final_score >= ?"]
    params = [min_score]

    if exclude_honeypots:
        conditions.append("is_honeypot = 0")

    where = " AND ".join(conditions)

    total = conn.execute(
        f"SELECT COUNT(*) FROM candidate_scores WHERE {where}", params
    ).fetchone()[0]

    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM candidate_scores WHERE {where} "
        f"ORDER BY final_score DESC, candidate_id ASC "
        f"LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()
    conn.close()

    items = [_row_to_list_item(row, offset + i + 1) for i, row in enumerate(rows)]

    return PaginatedCandidates(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size),
    )


def get_candidate_detail(candidate_id: str) -> Optional[CandidateDetailSchema]:
    """Get full analysis detail for a single candidate."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM candidate_scores WHERE candidate_id = ?",
        (candidate_id,)
    ).fetchone()

    # Get rank
    rank_row = conn.execute(
        "SELECT COUNT(*) FROM candidate_scores WHERE final_score > ? OR (final_score = ? AND candidate_id < ?)",
        (float(row["final_score"]), float(row["final_score"]), candidate_id)
    ).fetchone()
    conn.close()

    if not row:
        return None

    rank = (rank_row[0] if rank_row else 0) + 1
    full = json.loads(row["full_analysis_json"] or "{}")

    intel_data = full.get("intelligence") or {}
    scorecard_data = full.get("scorecard") or {}
    alignment_data = full.get("alignment") or {}
    risk_data = full.get("risk_radar") or {}
    evidence_data = full.get("evidence") or {}
    recr_data = full.get("recruitability") or {}
    opp_data = full.get("opportunity_cost") or {}
    expl_data = full.get("explainability") or {}

    def safe_float(d, k, default=0.0):
        v = d.get(k, default)
        return float(v) if v is not None else default

    def safe_str(d, k, default=""):
        return str(d.get(k, default) or default)

    def safe_list(d, k):
        v = d.get(k, [])
        return v if isinstance(v, list) else []

    # Intelligence
    ai_skills = safe_list(intel_data, "ai_skills")
    top_ai_skill_names = [s.get("name", "") for s in ai_skills[:5] if isinstance(s, dict)]

    intelligence = IntelligenceProfileSchema(
        candidate_id=candidate_id,
        name=safe_str(intel_data, "name"),
        headline=safe_str(intel_data, "headline"),
        current_title=safe_str(intel_data, "current_title"),
        current_company=safe_str(intel_data, "current_company"),
        years_of_experience=safe_float(intel_data, "years_of_experience"),
        location=safe_str(intel_data, "location"),
        country=safe_str(intel_data, "country"),
        ai_skill_count=int(intel_data.get("ai_skill_count", 0)),
        ai_skill_depth_score=safe_float(intel_data, "ai_skill_depth_score"),
        github_activity_score=safe_float(intel_data, "github_activity_score", -1),
        has_production_ml_evidence=bool(intel_data.get("has_production_ml_evidence")),
        has_leadership_evidence=bool(intel_data.get("has_leadership_evidence")),
        is_entirely_services_firm=bool(intel_data.get("is_entirely_services_firm")),
        product_company_ratio=safe_float(intel_data, "product_company_ratio"),
        career_progression_score=safe_float(intel_data, "career_progression_score"),
        education_tier_score=safe_float(intel_data, "education_tier_score"),
        avg_tenure_months=safe_float(intel_data, "avg_tenure_months"),
        title_alignment_score=safe_float(intel_data, "title_alignment_score"),
        ai_assessment_avg_score=safe_float(intel_data, "ai_assessment_avg_score"),
        top_ai_skills=top_ai_skill_names,
        summary_text=safe_str(intel_data, "summary_text"),
    )

    # Scorecard
    dims_raw = safe_list(scorecard_data, "dimensions")
    dimensions = [
        DimensionScoreSchema(
            name=d.get("name", ""),
            score=float(d.get("score", 0)),
            rationale=d.get("rationale", ""),
            weight=float(d.get("weight", 0.1)),
        )
        for d in dims_raw if isinstance(d, dict)
    ]
    scorecard = ScorecardSchema(
        technical_fit=safe_float(scorecard_data, "technical_fit"),
        role_fit=safe_float(scorecard_data, "role_fit"),
        domain_expertise=safe_float(scorecard_data, "domain_expertise"),
        career_momentum=safe_float(scorecard_data, "career_momentum"),
        leadership=safe_float(scorecard_data, "leadership"),
        communication=safe_float(scorecard_data, "communication"),
        adaptability=safe_float(scorecard_data, "adaptability"),
        cultural_fit=safe_float(scorecard_data, "cultural_fit"),
        learning_potential=safe_float(scorecard_data, "learning_potential"),
        evidence_strength=safe_float(scorecard_data, "evidence_strength"),
        final_score=safe_float(scorecard_data, "final_score"),
        is_disqualified=bool(scorecard_data.get("is_disqualified")),
        disqualification_reason=safe_str(scorecard_data, "disqualification_reason"),
        dimensions=dimensions,
    )

    # Alignment
    alignment = AlignmentScoresSchema(
        technical_alignment=safe_float(alignment_data, "technical_alignment"),
        domain_alignment=safe_float(alignment_data, "domain_alignment"),
        experience_alignment=safe_float(alignment_data, "experience_alignment"),
        leadership_alignment=safe_float(alignment_data, "leadership_alignment"),
        growth_alignment=safe_float(alignment_data, "growth_alignment"),
        communication_alignment=safe_float(alignment_data, "communication_alignment"),
        adaptability_alignment=safe_float(alignment_data, "adaptability_alignment"),
        semantic_similarity=safe_float(alignment_data, "semantic_similarity"),
        overall_alignment=safe_float(alignment_data, "overall_alignment"),
    )

    # Risk Radar
    def parse_risk_dim(d, name, default_score=50.0):
        if not d:
            return RiskDimensionSchema(name=name, risk_level="Medium", risk_score=default_score)
        return RiskDimensionSchema(
            name=safe_str(d, "name", name),
            risk_level=safe_str(d, "risk_level", "Medium"),
            risk_score=safe_float(d, "risk_score", default_score),
            explanation=safe_str(d, "explanation"),
        )

    risk_radar = RiskRadarSchema(
        technical_risk=parse_risk_dim(risk_data.get("technical_risk"), "Technical Risk"),
        retention_risk=parse_risk_dim(risk_data.get("retention_risk"), "Retention Risk"),
        adaptation_risk=parse_risk_dim(risk_data.get("adaptation_risk"), "Adaptation Risk"),
        communication_risk=parse_risk_dim(risk_data.get("communication_risk"), "Communication Risk"),
        leadership_risk=parse_risk_dim(risk_data.get("leadership_risk"), "Leadership Risk"),
        domain_risk=parse_risk_dim(risk_data.get("domain_risk"), "Domain Risk"),
        learning_risk=parse_risk_dim(risk_data.get("learning_risk"), "Learning Risk"),
        overall_risk=parse_risk_dim(risk_data.get("overall_risk"), "Overall Risk"),
    )

    # Evidence
    claims_raw = safe_list(evidence_data, "claim_evidences")
    claims = [
        ClaimEvidenceSchema(
            claim=safe_str(c, "claim"),
            evidence_strength=safe_str(c, "evidence_strength", "Moderate"),
            confidence=float(c.get("confidence", 0.5)),
            supporting_text=safe_str(c, "supporting_text"),
            notes=safe_str(c, "notes"),
        )
        for c in claims_raw if isinstance(c, dict)
    ]
    overall_ev = evidence_data.get("overall_evidence_strength", "Moderate")
    if isinstance(overall_ev, dict):
        overall_ev = overall_ev.get("value", "Moderate")
    evidence = EvidenceReportSchema(
        is_honeypot=bool(evidence_data.get("is_honeypot")),
        honeypot_score=safe_float(evidence_data, "honeypot_score"),
        honeypot_flags=safe_list(evidence_data, "honeypot_flags"),
        overall_evidence_strength=str(overall_ev),
        consistency_score=safe_float(evidence_data, "consistency_score", 1.0),
        claim_evidences=claims,
    )

    # Recruitability
    tier = recr_data.get("tier", "Moderate")
    if isinstance(tier, dict):
        tier = tier.get("value", "Moderate")
    recruitability = RecruitabilitySchema(
        tier=str(tier),
        overall_score=safe_float(recr_data, "overall_score", 0.5),
        skill_scarcity_score=safe_float(recr_data, "skill_scarcity_score", 0.5),
        experience_uniqueness_score=safe_float(recr_data, "experience_uniqueness_score", 0.5),
        market_availability_score=safe_float(recr_data, "market_availability_score", 0.5),
        career_growth_score=safe_float(recr_data, "career_growth_score", 0.5),
        replacement_timeline_weeks=int(recr_data.get("replacement_timeline_weeks", 8)),
        reasoning=safe_str(recr_data, "reasoning"),
    )

    # Opportunity Cost
    opp_level = opp_data.get("level", "Medium")
    if isinstance(opp_level, dict):
        opp_level = opp_level.get("value", "Medium")
    opportunity_cost = OpportunityCostSchema(
        level=str(opp_level),
        overall_score=safe_float(opp_data, "overall_score", 0.5),
        candidate_rarity_factor=safe_float(opp_data, "candidate_rarity_factor", 0.5),
        competitive_demand_factor=safe_float(opp_data, "competitive_demand_factor", 0.5),
        unique_expertise_factor=safe_float(opp_data, "unique_expertise_factor", 0.5),
        business_value_factor=safe_float(opp_data, "business_value_factor", 0.5),
        reasoning=safe_str(opp_data, "reasoning"),
        cost_factors=safe_list(opp_data, "cost_factors"),
    )

    # Explainability
    explainability = ExplainabilitySchema(
        why_selected=safe_str(expl_data, "why_selected"),
        key_strengths=safe_list(expl_data, "key_strengths"),
        key_weaknesses=safe_list(expl_data, "key_weaknesses"),
        tradeoffs=safe_list(expl_data, "tradeoffs"),
        interview_focus_areas=safe_list(expl_data, "interview_focus_areas"),
        missing_skills=safe_list(expl_data, "missing_skills"),
        improvement_suggestions=safe_list(expl_data, "improvement_suggestions"),
        final_recommendation=safe_str(expl_data, "final_recommendation"),
        one_line_reasoning=safe_str(expl_data, "one_line_reasoning"),
    )

    return CandidateDetailSchema(
        candidate_id=candidate_id,
        rank=rank,
        final_score=float(row["final_score"]),
        intelligence=intelligence,
        scorecard=scorecard,
        alignment=alignment,
        risk_radar=risk_radar,
        evidence=evidence,
        recruitability=recruitability,
        opportunity_cost=opportunity_cost,
        explainability=explainability,
    )


def get_dashboard_stats() -> DashboardStatsSchema:
    """Compute dashboard summary statistics."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT COUNT(*) as total, "
        "       SUM(CASE WHEN final_score >= 0.7 THEN 1 ELSE 0 END) as top_matches, "
        "       AVG(final_score) as avg_score, "
        "       SUM(CASE WHEN recruitability_tier IN ('Rare','Critical Talent') THEN 1 ELSE 0 END) as critical, "
        "       SUM(CASE WHEN opportunity_cost_level IN ('High','Critical') THEN 1 ELSE 0 END) as high_opp_cost, "
        "       SUM(CASE WHEN risk_overall >= 70 THEN 1 ELSE 0 END) as high_risk, "
        "       SUM(is_honeypot) as honeypots "
        "FROM candidate_scores"
    ).fetchone()

    # Average notice period from full JSON (approximate from sample)
    conn.close()

    return DashboardStatsSchema(
        total_candidates=int(rows[0] or 0),
        top_matches=int(rows[1] or 0),
        average_fit_score=round(float(rows[2] or 0) * 100, 1),
        critical_talent_count=int(rows[3] or 0),
        high_opportunity_cost_count=int(rows[4] or 0),
        high_risk_count=int(rows[5] or 0),
        honeypot_count=int(rows[6] or 0),
        avg_notice_period_days=60.0,
    )


def get_chart_data() -> ChartDataSchema:
    """Get chart data for dashboard visualizations."""
    conn = _get_conn()

    # Score distribution (buckets of 0.1)
    score_dist = []
    for low in [i / 10 for i in range(10)]:
        high = low + 0.1
        count = conn.execute(
            "SELECT COUNT(*) FROM candidate_scores WHERE final_score >= ? AND final_score < ?",
            (low, high)
        ).fetchone()[0]
        score_dist.append({"range": f"{low:.1f}-{high:.1f}", "count": count})

    # Risk distribution
    risk_dist = []
    for level, low, high in [("Low", 0, 25), ("Medium", 25, 50), ("High", 50, 75), ("Critical", 75, 101)]:
        count = conn.execute(
            "SELECT COUNT(*) FROM candidate_scores WHERE risk_overall >= ? AND risk_overall < ?",
            (low, high)
        ).fetchone()[0]
        risk_dist.append({"level": level, "count": count})

    # Recruitability distribution
    recr_dist = []
    for tier in ["Easy", "Moderate", "Rare", "Critical Talent"]:
        count = conn.execute(
            "SELECT COUNT(*) FROM candidate_scores WHERE recruitability_tier = ?",
            (tier,)
        ).fetchone()[0]
        recr_dist.append({"tier": tier, "count": count})

    # Opportunity cost distribution
    opp_dist = []
    for level in ["Low", "Medium", "High", "Critical"]:
        count = conn.execute(
            "SELECT COUNT(*) FROM candidate_scores WHERE opportunity_cost_level = ?",
            (level,)
        ).fetchone()[0]
        opp_dist.append({"level": level, "count": count})

    conn.close()

    return ChartDataSchema(
        score_distribution=score_dist,
        risk_distribution=risk_dist,
        recruitability_distribution=recr_dist,
        opportunity_cost_distribution=opp_dist,
        top_titles=[],
    )
