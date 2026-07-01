"""
Recruitability Index Engine — estimates how rare/replaceable a candidate is.
"""
from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from shared.types import CandidateIntelligence, RecruitabilityIndex, RecruitabilityTier, Scorecard


# Rare AI skills that are scarce in the market
RARE_AI_SKILLS = {
    "fine-tuning llms", "lora", "qlora", "peft", "learning to rank",
    "ndcg", "faiss", "vector search", "hybrid retrieval", "dense retrieval",
    "bm25", "ann", "milvus", "weaviate", "qdrant", "ranking systems",
    "embedding drift", "retrieval evaluation", "mrr", "map",
}


def build_recruitability_index(
    intel: CandidateIntelligence,
    scorecard: Scorecard,
) -> RecruitabilityIndex:
    idx = RecruitabilityIndex(candidate_id=intel.candidate_id)

    # Skill scarcity — how many rare skills does the candidate have?
    rare_count = sum(
        1 for s in intel.ai_skills
        if s.name.lower() in RARE_AI_SKILLS
        or any(rs in s.name.lower() for rs in RARE_AI_SKILLS)
    )
    idx.skill_scarcity_score = min(rare_count / 5.0, 1.0)

    # Experience uniqueness — senior + production ML + product company
    uniqueness = 0.0
    if intel.has_production_ml_evidence:
        uniqueness += 0.30
    if intel.product_company_ratio > 0.5:
        uniqueness += 0.25
    if 5 <= intel.years_of_experience <= 9:
        uniqueness += 0.20
    if intel.github_activity_score > 50:
        uniqueness += 0.15
    if intel.has_leadership_evidence:
        uniqueness += 0.10
    idx.experience_uniqueness_score = min(uniqueness, 1.0)

    # Market availability — behavioral signals
    idx.market_availability_score = min(1.0 - (scorecard.final_score * 0.5 + 0.3), 1.0)

    # Career growth trajectory
    idx.career_growth_score = min(scorecard.career_momentum / 100.0, 1.0)

    # Overall recruitability score
    idx.overall_score = (
        idx.skill_scarcity_score * 0.35 +
        idx.experience_uniqueness_score * 0.35 +
        idx.career_growth_score * 0.20 +
        (1 - idx.market_availability_score) * 0.10
    )

    # Tier classification
    if idx.overall_score >= 0.75:
        idx.tier = RecruitabilityTier.CRITICAL
        idx.replacement_timeline_weeks = 24
        idx.reasoning = (
            f"Critical talent. {rare_count} scarce AI/ML skills, production deployment experience, "
            f"{'strong GitHub presence, ' if intel.github_activity_score > 50 else ''}"
            f"product company background. Extremely difficult to replace."
        )
    elif idx.overall_score >= 0.55:
        idx.tier = RecruitabilityTier.RARE
        idx.replacement_timeline_weeks = 12
        idx.reasoning = (
            f"Rare profile. Strong AI/ML skills and production experience. "
            f"Would require 3+ months to find comparable replacement."
        )
    elif idx.overall_score >= 0.30:
        idx.tier = RecruitabilityTier.MODERATE
        idx.replacement_timeline_weeks = 8
        idx.reasoning = (
            f"Moderate recruitability. {intel.ai_skill_count} AI skills. "
            f"Comparable talent available in market within 2 months."
        )
    else:
        idx.tier = RecruitabilityTier.EASY
        idx.replacement_timeline_weeks = 4
        idx.reasoning = (
            f"Widely available profile. {intel.ai_skill_count} AI skills, "
            f"{'services firm background, ' if intel.is_entirely_services_firm else ''}"
            f"not specialized for this role."
        )

    return idx
