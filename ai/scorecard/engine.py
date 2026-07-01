"""
Multi-Dimensional Scorecard Engine — combines all upstream signals into
10 independent dimension scores and one final ranking score.

No LLM. Pure deterministic scoring logic validated against dataset patterns.
Scoring weights derived from JD analysis and competition metric emphasis (NDCG@10).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import (
    CandidateIntelligence, AlignmentScores, EvidenceReport,
    RoleDNA, Scorecard, DimensionScore,
)


# ---------------------------------------------------------------------------
# Behavioral signal scoring helpers
# ---------------------------------------------------------------------------

def _score_availability(signals: dict, today_str: str = "2026-07-01") -> float:
    """
    Availability score (0-100) from behavioral signals.
    Weights: open_to_work, recency of last_active, applications_submitted.
    """
    score = 0.0

    # Open to work is a strong positive signal
    if signals.get("open_to_work_flag", False):
        score += 30.0

    # Recency of last active
    last_active = signals.get("last_active_date", "")
    if last_active:
        try:
            from datetime import date
            la_date = date.fromisoformat(last_active)
            today = date.fromisoformat(today_str)
            days_ago = (today - la_date).days
            if days_ago <= 30:
                score += 35.0
            elif days_ago <= 90:
                score += 25.0
            elif days_ago <= 180:
                score += 10.0
            else:
                score += 0.0  # Stale — this is a significant negative
        except Exception:
            score += 10.0

    # Active applications signal
    apps = int(signals.get("applications_submitted_30d", 0))
    if apps >= 3:
        score += 20.0
    elif apps >= 1:
        score += 12.0

    # Profile views (market interest)
    views = int(signals.get("profile_views_received_30d", 0))
    if views >= 20:
        score += 15.0
    elif views >= 5:
        score += 8.0

    return min(score, 100.0)


def _score_engagement(signals: dict) -> float:
    """
    Platform engagement score (0-100).
    Recruiter response rate and interview completion are key signals.
    """
    response_rate = float(signals.get("recruiter_response_rate", 0.0))
    interview_rate = float(signals.get("interview_completion_rate", 0.0))
    offer_accept = float(signals.get("offer_acceptance_rate", -1.0))

    score = (response_rate * 50.0) + (interview_rate * 30.0)

    if offer_accept >= 0:
        score += offer_accept * 20.0
    else:
        score += 10.0  # No history — neutral

    return min(score, 100.0)


def _score_notice_period(notice_days: int) -> float:
    """
    Score notice period (0-100). JD prefers ≤30 days.
    """
    if notice_days <= 15:
        return 100.0
    elif notice_days <= 30:
        return 90.0
    elif notice_days <= 60:
        return 70.0
    elif notice_days <= 90:
        return 50.0
    elif notice_days <= 120:
        return 25.0
    else:
        return 10.0


def _score_location(intel: CandidateIntelligence, signals: dict) -> float:
    """Score location fit for Pune/Noida preference."""
    from ai.role_dna.engine import get_preferred_locations
    preferred = get_preferred_locations()

    loc_lower = (intel.location or "").lower()
    country_lower = (intel.country or "").lower()

    if any(city in loc_lower for city in preferred):
        return 100.0
    if country_lower == "india":
        if signals.get("willing_to_relocate", False):
            return 80.0
        return 65.0
    # Outside India
    if signals.get("willing_to_relocate", False):
        return 30.0
    return 15.0


def _score_platform_trust(signals: dict) -> float:
    """Platform trust / presence signals."""
    score = 0.0
    score += float(signals.get("profile_completeness_score", 0)) * 0.4
    score += 15.0 if signals.get("verified_email") else 0.0
    score += 10.0 if signals.get("verified_phone") else 0.0
    score += 10.0 if signals.get("linkedin_connected") else 0.0
    conn = min(int(signals.get("connection_count", 0)), 500) / 500.0
    score += conn * 15.0
    return min(score, 100.0)


# ---------------------------------------------------------------------------
# Disqualification checks
# ---------------------------------------------------------------------------

def _check_disqualification(
    intel: CandidateIntelligence,
    evidence: EvidenceReport,
    signals: dict,
) -> tuple[bool, str]:
    """
    Hard disqualification rules from the JD.
    Returns (is_disqualified, reason).
    """
    # Honeypot is not disqualified but severely de-ranked (handled in final score)

    # Rule 1: Entirely services firm career with NO product company experience
    if intel.is_entirely_services_firm and intel.product_company_ratio == 0.0:
        # Soft disqualification (multiply score down, not zero)
        return False, ""  # Not hard-disqualified, just de-ranked

    # Rule 2: Zero AI skills and mismatched title (Marketing/HR/Accountant with AI keywords only)
    non_ai_titles = {"marketing manager", "hr manager", "accountant", "civil engineer",
                     "mechanical engineer", "customer support", "sales executive",
                     "content writer", "graphic designer", "project manager"}
    title_lower = intel.current_title.lower()
    if any(t in title_lower for t in non_ai_titles) and intel.ai_skill_count < 2:
        return False, ""  # De-ranked but not disqualified

    return False, ""


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _technical_fit_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
    signals: dict,
) -> float:
    """Technical fit dimension (0-100)."""
    # AI skill depth (40%)
    skill_score = intel.ai_skill_depth_score * 0.40
    # Semantic technical alignment (25%)
    sem_score = alignment.technical_alignment * 0.25
    # GitHub activity (20%)
    gh = intel.github_activity_score
    gh_score = (max(gh, 0) / 100.0) * 20.0 if gh >= 0 else 0.0
    # Assessment scores (15%)
    assess_score = (intel.ai_assessment_avg_score / 100.0) * 15.0

    return min(skill_score + sem_score + gh_score + assess_score, 100.0)


def _learning_potential_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
) -> float:
    """Learning potential / growth velocity (0-100)."""
    score = 50.0

    # Education quality base
    score = intel.education_tier_score * 0.3

    # Career trajectory toward AI (was there a pivot?)
    if intel.has_production_ml_evidence:
        score += 25.0

    # Growth alignment semantic score
    score += alignment.growth_alignment * 0.30

    # GitHub activity shows continuous learning
    if intel.github_activity_score > 50:
        score += 20.0
    elif intel.github_activity_score > 10:
        score += 10.0

    # Certifications in AI/ML
    ai_certs = [
        c for c in intel.certifications
        if any(kw in c.get("name", "").lower() for kw in
               ["aws", "ml", "tensorflow", "pytorch", "databricks", "google", "azure"])
    ]
    score += min(len(ai_certs) * 8.0, 20.0)

    return min(max(score, 0.0), 100.0)


def _leadership_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
) -> float:
    """Leadership and mentorship potential (0-100)."""
    score = 30.0  # baseline for senior engineers

    if intel.has_leadership_evidence:
        score += 40.0

    # Title signals
    title_lower = intel.current_title.lower()
    if any(kw in title_lower for kw in ["lead", "principal", "staff", "director", "head"]):
        score += 20.0
    elif any(kw in title_lower for kw in ["senior", "sr"]):
        score += 10.0

    # Semantic
    score += alignment.leadership_alignment * 0.20

    return min(score, 100.0)


def _communication_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
    signals: dict,
) -> float:
    """Communication and async-work readiness (0-100)."""
    score = 0.0

    # GitHub (open-source communication proxy)
    if intel.github_activity_score > 50:
        score += 30.0
    elif intel.github_activity_score > 10:
        score += 15.0

    # Platform engagement
    if signals.get("linkedin_connected"):
        score += 15.0
    if signals.get("verified_email") and signals.get("verified_phone"):
        score += 10.0

    # Response rate (communication reliability)
    rr = float(signals.get("recruiter_response_rate", 0))
    score += rr * 30.0

    # Completeness (async documentation proxy)
    score += float(signals.get("profile_completeness_score", 0)) * 0.15

    return min(score, 100.0)


def _role_fit_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
) -> float:
    """Overall role fit (title + experience + production) (0-100)."""
    score = 0.0

    # Title alignment is primary signal
    score += intel.title_alignment_score * 0.40

    # Experience range (5-9 years optimal)
    yoe = intel.years_of_experience
    if 5 <= yoe <= 9:
        exp_score = 100.0
    elif 4 <= yoe < 5 or 9 < yoe <= 12:
        exp_score = 75.0
    elif 3 <= yoe < 4 or 12 < yoe <= 15:
        exp_score = 50.0
    elif yoe < 3:
        exp_score = 20.0
    else:
        exp_score = 35.0  # 15+ years — overqualified risk
    score += exp_score * 0.30

    # Production ML evidence
    if intel.has_production_ml_evidence:
        score += 20.0

    # Semantic experience alignment
    score += alignment.experience_alignment * 0.10

    return min(score, 100.0)


def _domain_expertise_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
) -> float:
    """Domain expertise in AI/ML/IR (0-100)."""
    # Primary: semantic domain alignment
    score = alignment.domain_alignment * 0.50
    # AI skill count contribution
    score += min(intel.ai_skill_count / 10.0, 1.0) * 30.0
    # Duration in AI roles
    score += min(intel.ai_skill_duration_total_months / 60.0, 1.0) * 20.0
    return min(score, 100.0)


def _career_momentum_score(
    intel: CandidateIntelligence,
) -> float:
    """Career momentum / progression velocity (0-100)."""
    score = intel.career_progression_score

    # Recent title check: still growing?
    title_lower = intel.current_title.lower()
    if any(kw in title_lower for kw in ["senior", "principal", "staff", "lead", "director"]):
        score += 10.0

    # Avg tenure bonus for stability without stagnation
    if 18 <= intel.avg_tenure_months <= 36:
        score += 10.0

    return min(score, 100.0)


def _adaptability_score(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
) -> float:
    """Adaptability to startup/fast-change environment (0-100)."""
    score = alignment.adaptability_alignment * 0.40

    # Product company experience = startup adaptability proxy
    score += intel.product_company_ratio * 35.0

    # Career diversity (multiple industries = adaptable)
    industries = set(e.industry for e in intel.career_history if e.industry)
    industry_diversity = min(len(industries) / 4.0, 1.0) * 15.0
    score += industry_diversity

    # Not entirely services firm
    if not intel.is_entirely_services_firm:
        score += 10.0

    return min(score, 100.0)


def _cultural_fit_score(
    intel: CandidateIntelligence,
    signals: dict,
    alignment: AlignmentScores,
) -> float:
    """Cultural alignment with async-first, product-focused startup (0-100)."""
    score = 0.0

    # Product company background = cultural alignment proxy
    score += intel.product_company_ratio * 40.0

    # Open source engagement
    if intel.github_activity_score > 0:
        score += min(intel.github_activity_score, 100.0) * 0.25

    # Not title-chasing (good avg tenure)
    if intel.avg_tenure_months >= 24:
        score += 20.0
    elif intel.avg_tenure_months >= 18:
        score += 10.0

    # Communication alignment
    score += alignment.communication_alignment * 0.15

    return min(score, 100.0)


def _evidence_strength_score(evidence: EvidenceReport) -> float:
    """Convert evidence report to 0-100 score."""
    if evidence.is_honeypot:
        return 0.0
    strength_map = {"Strong": 90.0, "Moderate": 65.0, "Weak": 35.0, "Insufficient": 10.0}
    base = strength_map.get(evidence.overall_evidence_strength.value, 50.0)
    return base * evidence.consistency_score


# ---------------------------------------------------------------------------
# Main scorecard builder
# ---------------------------------------------------------------------------

def build_scorecard(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
    evidence: EvidenceReport,
    raw_signals: dict,
    role_dna: RoleDNA,
) -> Scorecard:
    """
    Build the complete 10-dimension scorecard and compute final ranking score.
    
    Final score formula (validated against JD priorities):
    - Technical Fit: 30%
    - Role Fit: 20%
    - Career Momentum: 10%
    - Domain Expertise: 10%
    - Availability/Behavioral: 15%  
    - Leadership: 5%
    - Cultural Fit: 5%
    - Adaptability: 5%
    - Other dimensions contribute to display but less to ranking
    """
    card = Scorecard(candidate_id=intel.candidate_id)

    # Compute all 10 dimensions
    card.technical_fit = _technical_fit_score(intel, alignment, raw_signals)
    card.learning_potential = _learning_potential_score(intel, alignment)
    card.leadership = _leadership_score(intel, alignment)
    card.communication = _communication_score(intel, alignment, raw_signals)
    card.role_fit = _role_fit_score(intel, alignment)
    card.domain_expertise = _domain_expertise_score(intel, alignment)
    card.career_momentum = _career_momentum_score(intel)
    card.adaptability = _adaptability_score(intel, alignment)
    card.cultural_fit = _cultural_fit_score(intel, raw_signals, alignment)
    card.evidence_strength = _evidence_strength_score(evidence)

    # Behavioral composite
    availability = _score_availability(raw_signals)
    engagement = _score_engagement(raw_signals)
    notice = _score_notice_period(int(raw_signals.get("notice_period_days", 60)))
    location = _score_location(intel, raw_signals)
    behavioral_composite = (
        availability * 0.35 +
        engagement * 0.30 +
        notice * 0.20 +
        location * 0.15
    )

    # Check disqualification
    card.is_disqualified, card.disqualification_reason = _check_disqualification(
        intel, evidence, raw_signals
    )

    # Final score
    raw_score = (
        card.technical_fit * 0.28 +
        card.role_fit * 0.18 +
        card.domain_expertise * 0.10 +
        card.career_momentum * 0.08 +
        behavioral_composite * 0.18 +
        card.cultural_fit * 0.05 +
        card.leadership * 0.05 +
        card.adaptability * 0.04 +
        card.learning_potential * 0.03 +
        card.evidence_strength * 0.01
    )

    # Penalty modifiers
    # Services firm only (not product company) — significant penalty
    if intel.is_entirely_services_firm:
        raw_score *= 0.60

    # Honeypot penalty
    if evidence.is_honeypot:
        raw_score *= 0.05
    elif evidence.honeypot_score > 0.4:
        raw_score *= (1.0 - evidence.honeypot_score * 0.5)

    # No AI skills at all for an AI Engineer role
    if intel.ai_skill_count == 0:
        raw_score *= 0.40

    # Stale profile (last active > 6 months AND not open to work)
    last_active_stale = False
    last_active = raw_signals.get("last_active_date", "")
    if last_active:
        try:
            from datetime import date
            days_ago = (date.fromisoformat("2026-07-01") - date.fromisoformat(last_active)).days
            if days_ago > 180 and not raw_signals.get("open_to_work_flag", False):
                raw_score *= 0.70
                last_active_stale = True
        except Exception:
            pass

    card.final_score = min(max(raw_score / 100.0, 0.0), 1.0)  # Normalize to 0-1

    # Build dimension list for UI display
    card.dimensions = [
        DimensionScore("Technical Fit", card.technical_fit, weight=0.28),
        DimensionScore("Role Fit", card.role_fit, weight=0.18),
        DimensionScore("Domain Expertise", card.domain_expertise, weight=0.10),
        DimensionScore("Career Momentum", card.career_momentum, weight=0.08),
        DimensionScore("Leadership", card.leadership, weight=0.05),
        DimensionScore("Communication", card.communication, weight=0.05),
        DimensionScore("Adaptability", card.adaptability, weight=0.04),
        DimensionScore("Cultural Fit", card.cultural_fit, weight=0.05),
        DimensionScore("Learning Potential", card.learning_potential, weight=0.03),
        DimensionScore("Evidence Strength", card.evidence_strength, weight=0.01),
    ]

    return card
