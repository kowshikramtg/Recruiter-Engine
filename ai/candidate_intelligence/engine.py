"""
Candidate Intelligence Engine — extracts structured intelligence from raw candidate JSON.

This runs during offline precomputation. Pure Python, no LLM required.
Processes all 100K candidates efficiently using batch operations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import (
    CandidateIntelligence, SkillSignal, CareerEntry, EducationEntry
)
from ai.role_dna.engine import (
    get_ai_skill_taxonomy, get_services_firms,
    get_target_titles, get_preferred_locations
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EDUCATION_TIER_SCORES = {
    "tier_1": 1.0,
    "tier_2": 0.8,
    "tier_3": 0.6,
    "tier_4": 0.4,
    "unknown": 0.3,
}

AI_RELATED_FIELDS = {
    "computer science", "machine learning", "artificial intelligence",
    "data science", "information technology", "software engineering",
    "electronics", "electrical engineering", "mathematics", "statistics",
    "computational", "neural", "cognitive science",
}

PRODUCTION_ML_KEYWORDS = [
    "deployed", "production", "shipped", "real users", "live system",
    "serving", "inference", "api endpoint", "model serving", "mlops",
    "a/b test", "latency", "throughput", "scale", "millions of",
    "recommendation system", "search system", "ranking system",
    "retrieval system", "embedding", "vector search", "semantic search",
    "feature store", "model registry", "mlflow", "wandb",
]

LEADERSHIP_KEYWORDS = [
    "led", "managed", "mentored", "team of", "team lead", "tech lead",
    "drove", "owned", "built team", "hired", "grew team",
    "founded", "co-founded", "director", "head of",
    "principal", "staff", "architect",
]

WRITING_COMMUNICATION_KEYWORDS = [
    "wrote", "published", "documented", "presented", "blog",
    "paper", "conference", "talk", "open source", "github",
    "contributed", "rfc", "design doc", "async",
]

AI_SKILL_TAXONOMY = get_ai_skill_taxonomy()
SERVICES_FIRMS = get_services_firms()
TARGET_TITLES = get_target_titles()
PREFERRED_LOCATIONS = get_preferred_locations()


# ---------------------------------------------------------------------------
# Core extraction logic
# ---------------------------------------------------------------------------

def extract_candidate_intelligence(raw: dict[str, Any]) -> CandidateIntelligence:
    """
    Extract structured intelligence from a raw candidate JSON record.
    This is the main entry point for the Candidate Intelligence Engine.
    """
    intel = CandidateIntelligence()
    intel.candidate_id = raw.get("candidate_id", "")

    # --- Profile ---
    profile = raw.get("profile", {})
    intel.name = profile.get("anonymized_name", "")
    intel.headline = profile.get("headline", "")
    intel.current_title = profile.get("current_title", "")
    intel.current_company = profile.get("current_company", "")
    intel.years_of_experience = float(profile.get("years_of_experience", 0))
    intel.location = profile.get("location", "")
    intel.country = profile.get("country", "")
    intel.summary_text = profile.get("summary", "")

    # --- Signals ---
    signals = raw.get("redrob_signals", {})
    intel.github_activity_score = float(signals.get("github_activity_score", -1))

    # --- Skills ---
    raw_skills = raw.get("skills", [])
    skill_assessment = signals.get("skill_assessment_scores", {})
    intel.all_skills, intel.ai_skills = _extract_skills(raw_skills, skill_assessment)
    intel.ai_skill_count = len(intel.ai_skills)
    intel.ai_skill_depth_score = _compute_skill_depth_score(intel.ai_skills)
    intel.ai_skill_duration_total_months = sum(s.duration_months for s in intel.ai_skills)
    ai_assessed = [s.assessment_score for s in intel.ai_skills if s.assessment_score is not None]
    intel.ai_assessment_avg_score = sum(ai_assessed) / len(ai_assessed) if ai_assessed else 0.0

    # --- Career history ---
    raw_career = raw.get("career_history", [])
    intel.career_history = _extract_career(raw_career)
    intel.total_career_months = sum(e.duration_months for e in intel.career_history)

    all_companies = [e.company.lower() for e in intel.career_history]
    services_count = sum(1 for e in intel.career_history if e.is_services_firm)
    total = len(intel.career_history) if intel.career_history else 1
    intel.is_entirely_services_firm = services_count == len(intel.career_history) and len(intel.career_history) > 0
    product_count = sum(1 for e in intel.career_history if e.is_product_company)
    intel.product_company_ratio = product_count / total

    intel.has_production_ml_evidence = any(e.has_production_ml for e in intel.career_history)
    intel.has_leadership_evidence = any(e.has_team_leadership for e in intel.career_history)

    # Average tenure (stability signal)
    durations = [e.duration_months for e in intel.career_history if e.duration_months > 0]
    intel.avg_tenure_months = sum(durations) / len(durations) if durations else 0.0

    # Career description combined text (for semantic alignment)
    intel.career_description_combined = " ".join(
        e.description for e in intel.career_history
    )

    # --- Career progression score ---
    intel.career_progression_score = _compute_career_progression(intel)

    # --- Title alignment ---
    intel.title_alignment_score = _compute_title_alignment(intel.current_title)

    # --- Education ---
    raw_edu = raw.get("education", [])
    intel.education = _extract_education(raw_edu)
    intel.education_tier_score = _compute_education_score(intel.education)

    # --- Certifications ---
    intel.certifications = raw.get("certifications", [])

    return intel


def _extract_skills(
    raw_skills: list[dict],
    skill_assessment: dict[str, float]
) -> tuple[list[SkillSignal], list[SkillSignal]]:
    """Extract and categorize all skills."""
    all_skills = []
    ai_skills = []

    for s in raw_skills:
        name = s.get("name", "")
        skill = SkillSignal(
            name=name,
            proficiency=s.get("proficiency", "beginner"),
            endorsements=int(s.get("endorsements", 0)),
            duration_months=int(s.get("duration_months", 0)),
            assessment_score=skill_assessment.get(name),
            is_ai_relevant=_is_ai_skill(name),
        )
        all_skills.append(skill)
        if skill.is_ai_relevant:
            ai_skills.append(skill)

    return all_skills, ai_skills


def _is_ai_skill(skill_name: str) -> bool:
    """Check if a skill is AI/ML relevant using the taxonomy."""
    name_lower = skill_name.lower()
    # Direct match
    if name_lower in AI_SKILL_TAXONOMY:
        return True
    # Partial match for compound skills
    for keyword in AI_SKILL_TAXONOMY:
        if keyword in name_lower or name_lower in keyword:
            return True
    return False


def _compute_skill_depth_score(ai_skills: list[SkillSignal]) -> float:
    """
    Weighted skill score based on proficiency, duration, and endorsements.
    Returns 0-100.
    """
    if not ai_skills:
        return 0.0

    proficiency_weights = {
        "expert": 4.0, "advanced": 3.0, "intermediate": 2.0, "beginner": 1.0
    }
    total = 0.0
    for s in ai_skills:
        prof_score = proficiency_weights.get(s.proficiency, 1.0)
        # Duration bonus (normalize to 0-1 over 36 months)
        dur_bonus = min(s.duration_months / 36.0, 1.0) * 0.5
        # Endorsement bonus (normalize over 50)
        end_bonus = min(s.endorsements / 50.0, 1.0) * 0.3
        # Assessment bonus if available
        assess_bonus = (s.assessment_score / 100.0) * 0.5 if s.assessment_score else 0.0
        skill_score = (prof_score / 4.0) * (1.0 + dur_bonus + end_bonus + assess_bonus)
        total += skill_score

    # Normalize to 0-100, cap at 10 skills effectively
    normalized = min(total / max(len(ai_skills), 1), 2.0) * 50.0
    return min(normalized, 100.0)


def _extract_career(raw_career: list[dict]) -> list[CareerEntry]:
    """Extract structured career entries with derived signals."""
    entries = []
    for c in raw_career:
        company = c.get("company", "")
        title = c.get("title", "")
        description = c.get("description", "")
        desc_lower = description.lower()

        entry = CareerEntry(
            company=company,
            title=title,
            duration_months=int(c.get("duration_months", 0)),
            is_current=bool(c.get("is_current", False)),
            industry=c.get("industry", ""),
            company_size=c.get("company_size", ""),
            description=description,
            is_product_company=_is_product_company(company, c.get("industry", ""), c.get("company_size", "")),
            is_services_firm=_is_services_firm(company),
            has_production_ml=_has_production_ml(desc_lower, title.lower()),
            has_team_leadership=_has_leadership(desc_lower, title.lower()),
        )
        entries.append(entry)
    return entries


def _is_services_firm(company_name: str) -> bool:
    """Check if company is a known IT services firm."""
    name_lower = company_name.lower()
    return any(firm in name_lower for firm in SERVICES_FIRMS)


def _is_product_company(company: str, industry: str, size: str) -> bool:
    """
    Heuristic: product company signals.
    - Not a services firm
    - In software/tech/AI/fintech/saas industry
    - Not paper products/manufacturing/etc.
    """
    if _is_services_firm(company):
        return False
    product_industries = {
        "software", "saas", "fintech", "ai", "ml", "tech", "internet",
        "startup", "e-commerce", "marketplace", "product", "platform",
    }
    ind_lower = industry.lower()
    return any(pi in ind_lower for pi in product_industries)


def _has_production_ml(desc_lower: str, title_lower: str) -> bool:
    """Check if the role has evidence of production ML deployment."""
    # Title signals
    prod_titles = {"ai engineer", "ml engineer", "data scientist", "nlp engineer",
                   "search engineer", "ranking engineer", "research scientist"}
    if any(t in title_lower for t in prod_titles):
        # Check description for production keywords
        return any(kw in desc_lower for kw in PRODUCTION_ML_KEYWORDS)
    return False


def _has_leadership(desc_lower: str, title_lower: str) -> bool:
    """Check for leadership / management evidence."""
    leadership_titles = {"lead", "manager", "head", "director", "principal", "staff", "vp"}
    if any(t in title_lower for t in leadership_titles):
        return True
    return any(kw in desc_lower for kw in LEADERSHIP_KEYWORDS)


def _compute_career_progression(intel: CandidateIntelligence) -> float:
    """
    Score career progression quality (0-100).
    Rewards: increasing seniority, product company experience, ML trajectory,
             reasonable tenure (not job-hopping, not stagnating)
    """
    if not intel.career_history:
        return 0.0

    score = 50.0  # baseline

    # Stability bonus: avg tenure > 18 months
    if intel.avg_tenure_months >= 24:
        score += 15.0
    elif intel.avg_tenure_months >= 18:
        score += 8.0
    elif intel.avg_tenure_months < 12:
        score -= 15.0

    # Product company bonus
    score += intel.product_company_ratio * 20.0

    # Services firm penalty
    if intel.is_entirely_services_firm:
        score -= 30.0

    # Production ML evidence bonus
    if intel.has_production_ml_evidence:
        score += 15.0

    return max(0.0, min(100.0, score))


def _compute_title_alignment(current_title: str) -> float:
    """Score how well the current title aligns with target AI engineer roles."""
    if not current_title:
        return 0.0
    title_lower = current_title.lower()
    # Exact or near match
    if title_lower in TARGET_TITLES:
        return 100.0
    # Partial match
    for t in TARGET_TITLES:
        if t in title_lower or title_lower in t:
            return 80.0
    # Technical adjacent
    technical_adjacent = {"engineer", "developer", "scientist", "analyst", "architect", "researcher"}
    if any(w in title_lower for w in technical_adjacent):
        return 40.0
    return 0.0


def _extract_education(raw_edu: list[dict]) -> list[EducationEntry]:
    """Extract education entries with AI-relevance flags."""
    entries = []
    for e in raw_edu:
        field = e.get("field_of_study", "").lower()
        entries.append(EducationEntry(
            institution=e.get("institution", ""),
            degree=e.get("degree", ""),
            field_of_study=e.get("field_of_study", ""),
            tier=e.get("tier", "unknown"),
            is_ai_related=any(f in field for f in AI_RELATED_FIELDS),
        ))
    return entries


def _compute_education_score(education: list[EducationEntry]) -> float:
    """Score education quality based on tier and AI relevance."""
    if not education:
        return 0.3

    best_score = 0.0
    for e in education:
        base = EDUCATION_TIER_SCORES.get(e.tier, 0.3)
        bonus = 0.1 if e.is_ai_related else 0.0
        # Advanced degree bonus
        degree_lower = e.degree.lower()
        if any(d in degree_lower for d in ["ph.d", "phd", "m.tech", "m.e.", "m.sc", "master"]):
            bonus += 0.1
        score = min(base + bonus, 1.0)
        best_score = max(best_score, score)

    return best_score * 100.0
