"""
Explainability Engine — generates transparent, specific, non-hallucinating
reasoning for every candidate recommendation.

Used both for the submission.csv reasoning column and the full UI report.
NO LLM at ranking time — template-based with real candidate facts.
"""
from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import (
    CandidateIntelligence, AlignmentScores, EvidenceReport,
    Scorecard, RiskRadar, RecruitabilityIndex, OpportunityCost,
    ExplainabilityReport, RoleDNA
)


def _top_ai_skills(intel: CandidateIntelligence, n: int = 3) -> str:
    """Get top N AI skills by proficiency + duration."""
    if not intel.ai_skills:
        return "no AI/ML skills detected"
    sorted_skills = sorted(
        intel.ai_skills,
        key=lambda s: (
            {"expert": 4, "advanced": 3, "intermediate": 2, "beginner": 1}.get(s.proficiency, 1),
            s.duration_months
        ),
        reverse=True
    )
    return ", ".join(s.name for s in sorted_skills[:n])


def _company_type_desc(intel: CandidateIntelligence) -> str:
    if intel.is_entirely_services_firm:
        return "services-firm career (no product company experience)"
    elif intel.product_company_ratio >= 0.7:
        return "strong product company background"
    elif intel.product_company_ratio >= 0.4:
        return "mixed product/services background"
    else:
        return "primarily services firm with some product exposure"


def _availability_desc(signals: dict) -> str:
    open_to = signals.get("open_to_work_flag", False)
    rr = float(signals.get("recruiter_response_rate", 0))
    last_active = signals.get("last_active_date", "")
    parts = []
    if open_to:
        parts.append("open to work")
    if rr >= 0.7:
        parts.append(f"high recruiter response rate ({rr:.0%})")
    elif rr < 0.2:
        parts.append(f"low recruiter response rate ({rr:.0%})")
    if not parts:
        return f"response rate {rr:.0%}"
    return "; ".join(parts)


def build_one_line_reasoning(
    intel: CandidateIntelligence,
    scorecard: Scorecard,
    evidence: EvidenceReport,
    signals: dict,
    rank: int,
) -> str:
    """
    Generate the reasoning column for submission.csv.
    Must be: specific facts, JD-connected, honest about concerns, no hallucination.
    """
    top_skills = _top_ai_skills(intel)
    company_desc = _company_type_desc(intel)
    avail = _availability_desc(signals)
    yoe = intel.years_of_experience
    notice = int(signals.get("notice_period_days", 60))
    gh = intel.github_activity_score

    # Concerns
    concerns = []
    if intel.is_entirely_services_firm:
        concerns.append("services-firm-only career")
    if notice > 90:
        concerns.append(f"{notice}-day notice period")
    if gh < 0:
        concerns.append("no GitHub activity")
    elif gh < 15:
        concerns.append("low GitHub activity")
    if not intel.has_production_ml_evidence:
        concerns.append("limited production ML evidence")
    if evidence.is_honeypot:
        concerns.append("profile consistency flags raised")

    # Build reasoning
    strengths_part = (
        f"{intel.current_title} with {yoe:.1f}yrs experience; "
        f"{intel.ai_skill_count} AI/ML skills ({top_skills}); "
        f"{company_desc}"
    )
    if gh > 0:
        strengths_part += f"; GitHub score {gh:.0f}/100"

    concern_part = ""
    if concerns:
        concern_part = f" Concerns: {', '.join(concerns[:2])}."

    avail_part = f" Availability: {avail}."

    return f"{strengths_part}.{concern_part}{avail_part}"[:300]  # Cap at 300 chars


def build_explainability_report(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
    evidence: EvidenceReport,
    scorecard: Scorecard,
    risk: RiskRadar,
    recruitability: RecruitabilityIndex,
    opportunity_cost: OpportunityCost,
    role_dna: RoleDNA,
    signals: dict,
    rank: int,
) -> ExplainabilityReport:
    """Build the full explainability report for the UI."""
    report = ExplainabilityReport(
        candidate_id=intel.candidate_id,
        rank=rank,
        final_score=scorecard.final_score,
    )

    # Why selected
    if rank <= 10:
        report.why_selected = (
            f"Ranked #{rank} because this candidate demonstrates strong alignment with the "
            f"Senior AI Engineer role: {_top_ai_skills(intel)} skills with "
            f"{'production deployment evidence, ' if intel.has_production_ml_evidence else ''}"
            f"{_company_type_desc(intel)}, and {intel.years_of_experience:.1f} years experience "
            f"{'in the target 5-9 year range.' if 5 <= intel.years_of_experience <= 9 else '.'}"
        )
    elif rank <= 50:
        report.why_selected = (
            f"Ranked #{rank} with moderate fit. "
            f"{intel.ai_skill_count} AI/ML skills and {intel.years_of_experience:.1f} years experience. "
            f"{'Behavioral signals are strong.' if float(signals.get('recruiter_response_rate', 0)) > 0.5 else 'Some availability concerns.'}"
        )
    else:
        report.why_selected = (
            f"Ranked #{rank} — below average fit for the Senior AI Engineer role. "
            f"Included based on {intel.ai_skill_count} AI skills and "
            f"{'availability signals' if signals.get('open_to_work_flag') else 'profile completeness'}."
        )

    # Key strengths
    strengths = []
    if intel.has_production_ml_evidence:
        strengths.append("Demonstrated production ML deployment experience in career history")
    if intel.ai_skill_count >= 5:
        strengths.append(f"Strong AI/ML skill breadth: {_top_ai_skills(intel)}")
    if intel.github_activity_score > 50:
        strengths.append(f"Active open-source contributor (GitHub score: {intel.github_activity_score:.0f}/100)")
    if intel.product_company_ratio >= 0.5:
        strengths.append(f"Product company background ({intel.product_company_ratio:.0%} of career)")
    if 5 <= intel.years_of_experience <= 9:
        strengths.append(f"{intel.years_of_experience:.1f} years in the JD's target range")
    if intel.ai_assessment_avg_score > 65:
        strengths.append(f"Strong platform assessment scores (avg {intel.ai_assessment_avg_score:.0f}/100)")
    if float(signals.get("recruiter_response_rate", 0)) > 0.7:
        strengths.append("High recruiter response rate — genuinely engaged in job market")
    if not strengths:
        strengths.append(f"{intel.ai_skill_count} AI/ML skills listed in profile")
    report.key_strengths = strengths[:5]

    # Key weaknesses
    weaknesses = []
    if intel.is_entirely_services_firm:
        weaknesses.append("Entire career at IT services firms — JD explicitly flags this as a concern")
    if not intel.has_production_ml_evidence:
        weaknesses.append("No clear evidence of production ML deployment in career descriptions")
    if intel.github_activity_score < 0:
        weaknesses.append("No GitHub account linked — JD emphasizes production + open-source visibility")
    elif intel.github_activity_score < 20:
        weaknesses.append(f"Low GitHub activity score ({intel.github_activity_score:.0f}/100)")
    if intel.years_of_experience < 4:
        weaknesses.append(f"Under-experienced at {intel.years_of_experience:.1f} years (JD wants 5-9)")
    if intel.years_of_experience > 14:
        weaknesses.append(f"Over-experienced at {intel.years_of_experience:.1f} years — possible overqualification/salary mismatch")
    notice = int(signals.get("notice_period_days", 60))
    if notice > 90:
        weaknesses.append(f"Long notice period ({notice} days) — JD prefers ≤30 days")
    if evidence.is_honeypot:
        weaknesses.append("Profile has consistency issues — verify details carefully")
    report.key_weaknesses = weaknesses[:4]

    # Tradeoffs
    report.tradeoffs = []
    if intel.product_company_ratio > 0.3 and intel.is_entirely_services_firm is False and intel.ai_skill_count < 4:
        report.tradeoffs.append("Good culture fit but technical depth needs verification")
    if intel.ai_skill_count >= 5 and intel.is_entirely_services_firm:
        report.tradeoffs.append("Strong AI skills but services-firm background may indicate different engineering culture")
    if intel.years_of_experience > 10 and scorecard.technical_fit > 70:
        report.tradeoffs.append("Senior experience is positive but compensation expectations may be high")

    # Interview focus areas
    focus_areas = []
    if not intel.has_production_ml_evidence:
        focus_areas.append("Probe: Have you deployed an ML model to production serving real users? What was the scale?")
    focus_areas.append("Probe: Describe your experience with embedding-based retrieval systems and how you handled embedding drift")
    focus_areas.append("Probe: How do you design offline evaluation for a ranking system? Walk me through NDCG/MRR interpretation")
    if intel.is_entirely_services_firm:
        focus_areas.append("Probe: How do you make product decisions under ambiguity? Give an example where you shipped something imperfect but learned from users")
    if not intel.has_leadership_evidence:
        focus_areas.append("Probe: This role involves mentoring junior engineers. What's your philosophy on technical mentorship?")
    if intel.github_activity_score < 0:
        focus_areas.append("Probe: Can you walk me through a system you built that is publicly visible or documentable?")
    focus_areas.append("Probe: Tell me about a ranking or retrieval system you built from scratch. What were the biggest failure modes?")
    focus_areas.append("Probe: How do you decide between fine-tuning a model vs. prompting an LLM vs. a classical ML approach?")
    report.interview_focus_areas = focus_areas[:6]

    # Missing skills
    missing = []
    from ai.role_dna.engine import get_ai_skill_taxonomy
    must_have_concepts = {
        "vector search", "embedding", "faiss", "retrieval", "ranking",
        "ndcg", "evaluation", "sentence-transformers", "python"
    }
    candidate_skills_lower = {s.name.lower() for s in intel.all_skills}
    for concept in must_have_concepts:
        if not any(concept in s for s in candidate_skills_lower):
            missing.append(concept)
    report.missing_skills = missing[:5]

    # Improvement suggestions
    suggestions = []
    if intel.github_activity_score < 0:
        suggestions.append("Link GitHub account to demonstrate open-source contributions and coding visibility")
    if not intel.certifications:
        suggestions.append("Add relevant ML certifications (AWS ML, GCP Professional ML, Databricks)")
    if float(signals.get("profile_completeness_score", 0)) < 70:
        suggestions.append("Improve profile completeness to increase recruiter discoverability")
    report.improvement_suggestions = suggestions[:3]

    # Final recommendation narrative
    score_pct = scorecard.final_score * 100
    if score_pct >= 70:
        recommendation_prefix = "STRONG FIT"
    elif score_pct >= 50:
        recommendation_prefix = "MODERATE FIT"
    elif score_pct >= 30:
        recommendation_prefix = "WEAK FIT"
    else:
        recommendation_prefix = "POOR FIT"

    report.final_recommendation = (
        f"{recommendation_prefix}: Final score {score_pct:.1f}/100. "
        f"Candidate is {recruitability.tier.value} in the market with "
        f"{'HIGH' if opportunity_cost.level.value in ('High','Critical') else 'MODERATE'} opportunity cost if rejected. "
        f"{'Recommend advancing to technical screen.' if score_pct >= 60 else 'Consider only if top candidates are unavailable.'}"
    )

    # One-line for submission CSV
    report.one_line_reasoning = build_one_line_reasoning(
        intel, scorecard, evidence, signals, rank
    )

    return report
