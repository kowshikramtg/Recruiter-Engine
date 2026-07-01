"""
Opportunity Cost Engine — estimates the organizational loss if this candidate is rejected.
"""
from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from shared.types import (
    CandidateIntelligence, RecruitabilityIndex, Scorecard,
    OpportunityCost, OpportunityCostLevel, RecruitabilityTier
)


def build_opportunity_cost(
    intel: CandidateIntelligence,
    recruitability: RecruitabilityIndex,
    scorecard: Scorecard,
) -> OpportunityCost:
    cost = OpportunityCost(candidate_id=intel.candidate_id)

    # Candidate rarity — how hard to find a replacement
    cost.candidate_rarity_factor = recruitability.overall_score

    # Competitive demand — score above average means competitors want them
    cost.competitive_demand_factor = min(scorecard.final_score * 1.2, 1.0)

    # Unique expertise — rare skill combinations
    cost.unique_expertise_factor = recruitability.skill_scarcity_score

    # Business value — how impactful for the specific role
    cost.business_value_factor = min(
        (scorecard.technical_fit / 100.0 * 0.5) +
        (scorecard.role_fit / 100.0 * 0.3) +
        (scorecard.domain_expertise / 100.0 * 0.2),
        1.0
    )

    # Overall opportunity cost score
    cost.overall_score = (
        cost.candidate_rarity_factor * 0.30 +
        cost.competitive_demand_factor * 0.30 +
        cost.unique_expertise_factor * 0.25 +
        cost.business_value_factor * 0.15
    )

    # Level classification
    if cost.overall_score >= 0.70:
        cost.level = OpportunityCostLevel.CRITICAL
        cost.reasoning = (
            f"CRITICAL: Rejecting this candidate risks significant organizational loss. "
            f"Replacement timeline: {recruitability.replacement_timeline_weeks} weeks. "
            f"Strong competitive demand and rare skill profile ({recruitability.tier.value})."
        )
        cost.cost_factors = [
            f"Replacement takes ~{recruitability.replacement_timeline_weeks} weeks at high recruitment cost",
            "Competitors will likely pursue this candidate",
            f"Rare combination: {', '.join(s.name for s in intel.ai_skills[:3])}",
            "High business value for the intelligence-layer mandate",
        ]
    elif cost.overall_score >= 0.50:
        cost.level = OpportunityCostLevel.HIGH
        cost.reasoning = (
            f"HIGH opportunity cost. This candidate is above average for the role. "
            f"Replacement would take ~{recruitability.replacement_timeline_weeks} weeks. "
            f"Recruitability tier: {recruitability.tier.value}."
        )
        cost.cost_factors = [
            f"~{recruitability.replacement_timeline_weeks} weeks to find comparable candidate",
            "Above-average technical fit for this role",
            f"{intel.ai_skill_count} relevant AI/ML skills",
        ]
    elif cost.overall_score >= 0.30:
        cost.level = OpportunityCostLevel.MEDIUM
        cost.reasoning = (
            f"MEDIUM opportunity cost. Candidate has relevant skills but is findable in market. "
            f"Replacement estimated at {recruitability.replacement_timeline_weeks} weeks."
        )
        cost.cost_factors = [
            f"Moderate {recruitability.replacement_timeline_weeks}-week replacement window",
            "Some relevant skills but not uniquely specialized",
        ]
    else:
        cost.level = OpportunityCostLevel.LOW
        cost.reasoning = (
            f"LOW opportunity cost. Profile is broadly available in the market. "
            f"Easy replacement within {recruitability.replacement_timeline_weeks} weeks."
        )
        cost.cost_factors = [
            "Widely available profile",
            f"Only {intel.ai_skill_count} AI/ML skills — not specialized for role",
        ]

    return cost
