"""
Hiring Risk Radar Engine — estimates multi-dimensional hiring risk.
Output formatted for Recharts RadarChart visualization.
"""
from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import (
    CandidateIntelligence, AlignmentScores, EvidenceReport,
    Scorecard, RiskRadar, RiskDimension, RiskLevel
)


def _risk_level(score: float) -> RiskLevel:
    """Convert risk score (0-100, higher=more risk) to RiskLevel."""
    if score < 25:
        return RiskLevel.LOW
    elif score < 50:
        return RiskLevel.MEDIUM
    elif score < 75:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def build_risk_radar(
    intel: CandidateIntelligence,
    alignment: AlignmentScores,
    evidence: EvidenceReport,
    scorecard: Scorecard,
    signals: dict,
) -> RiskRadar:
    """Compute 8-dimension risk radar from candidate intelligence."""
    radar = RiskRadar(candidate_id=intel.candidate_id)

    # Technical Risk: inverse of technical fit
    tech_risk = max(0.0, 100.0 - scorecard.technical_fit)
    radar.technical_risk = RiskDimension(
        "Technical Risk", _risk_level(tech_risk), tech_risk,
        explanation=_explain_technical_risk(intel, tech_risk),
    )

    # Retention Risk: services-firm culture shock + notice period + offer history
    offer_accept = float(signals.get("offer_acceptance_rate", -1))
    retention_risk = 0.0
    if intel.is_entirely_services_firm:
        retention_risk += 30.0
    if int(signals.get("notice_period_days", 60)) > 90:
        retention_risk += 20.0
    if offer_accept >= 0 and offer_accept < 0.5:
        retention_risk += 25.0
    elif offer_accept < 0:
        retention_risk += 10.0
    avg_tenure = intel.avg_tenure_months
    if avg_tenure < 12:
        retention_risk += 25.0  # Job hopper risk
    elif avg_tenure < 18:
        retention_risk += 10.0
    radar.retention_risk = RiskDimension(
        "Retention Risk", _risk_level(retention_risk), retention_risk,
        explanation=_explain_retention_risk(intel, signals, retention_risk),
    )

    # Adaptation Risk: services firm background, no startup experience
    adaptation_risk = max(0.0, 100.0 - scorecard.adaptability)
    radar.adaptation_risk = RiskDimension(
        "Adaptation Risk", _risk_level(adaptation_risk), adaptation_risk,
        explanation=f"Product company ratio: {intel.product_company_ratio:.0%}. "
                    f"{'Services firm background may struggle with startup pace.' if intel.is_entirely_services_firm else 'Has product company experience.'}",
    )

    # Communication Risk: low response rate, missing email/phone
    comm_risk = max(0.0, 100.0 - scorecard.communication)
    radar.communication_risk = RiskDimension(
        "Communication Risk", _risk_level(comm_risk), comm_risk,
        explanation=f"Recruiter response rate: {float(signals.get('recruiter_response_rate', 0)):.0%}. "
                    f"Interview completion: {float(signals.get('interview_completion_rate', 0)):.0%}.",
    )

    # Leadership Risk: senior role requires mentorship capacity
    leader_risk = max(0.0, 100.0 - scorecard.leadership)
    radar.leadership_risk = RiskDimension(
        "Leadership Risk", _risk_level(leader_risk), leader_risk,
        explanation=f"{'Leadership evidence found in career history.' if intel.has_leadership_evidence else 'Limited leadership signals — may need coaching for team mentorship.'}",
    )

    # Domain Risk: how far is the candidate from the recruiting/IR domain
    domain_risk = max(0.0, 100.0 - scorecard.domain_expertise)
    radar.domain_risk = RiskDimension(
        "Domain Risk", _risk_level(domain_risk), domain_risk,
        explanation=f"Domain alignment: {alignment.domain_alignment:.0f}/100. "
                    f"AI skills: {intel.ai_skill_count}.",
    )

    # Learning Risk: education tier + learning potential score
    learn_risk = max(0.0, 100.0 - scorecard.learning_potential)
    radar.learning_risk = RiskDimension(
        "Learning Risk", _risk_level(learn_risk), learn_risk,
        explanation=f"Education tier score: {intel.education_tier_score:.0f}/100. "
                    f"GitHub activity: {intel.github_activity_score:.0f}/100.",
    )

    # Overall Risk: weighted composite
    overall_risk = (
        tech_risk * 0.30 +
        retention_risk * 0.20 +
        adaptation_risk * 0.15 +
        comm_risk * 0.15 +
        leader_risk * 0.08 +
        domain_risk * 0.07 +
        learn_risk * 0.05
    )
    radar.overall_risk = RiskDimension(
        "Overall Risk", _risk_level(overall_risk), overall_risk,
        explanation=f"Composite hiring risk score. Primary concerns: "
                    f"{'technical depth, ' if tech_risk > 60 else ''}"
                    f"{'retention, ' if retention_risk > 60 else ''}"
                    f"{'adaptation to startup culture.' if adaptation_risk > 60 else 'manageable.'}",
    )

    return radar


def _explain_technical_risk(intel: CandidateIntelligence, risk: float) -> str:
    if risk < 25:
        return f"Strong technical fit. {intel.ai_skill_count} AI/ML skills with production deployment evidence."
    elif risk < 50:
        return f"Moderate technical fit. {intel.ai_skill_count} AI/ML skills but {'limited' if not intel.has_production_ml_evidence else 'some'} production evidence."
    elif risk < 75:
        return f"Technical gaps present. {intel.ai_skill_count} AI/ML skills, {'no production ML evidence' if not intel.has_production_ml_evidence else 'some production exposure'}."
    else:
        return f"High technical risk. Only {intel.ai_skill_count} AI skills detected, primary background appears non-ML."


def _explain_retention_risk(intel: CandidateIntelligence, signals: dict, risk: float) -> str:
    parts = []
    if intel.avg_tenure_months < 15:
        parts.append(f"Short avg tenure ({intel.avg_tenure_months:.0f} months) suggests job-hopping risk")
    if int(signals.get("notice_period_days", 60)) > 90:
        parts.append(f"Long notice period ({signals.get('notice_period_days')} days)")
    offer_accept = float(signals.get("offer_acceptance_rate", -1))
    if 0 <= offer_accept < 0.5:
        parts.append(f"Low historical offer acceptance ({offer_accept:.0%})")
    if not parts:
        return "Retention risk appears manageable based on available signals."
    return "; ".join(parts) + "."
