"""
Evidence Validation Engine — validates resume claims against evidence
and detects honeypot candidates.

Honeypot detection is critical: >10% honeypot rate in top 100 = disqualification.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import (
    CandidateIntelligence, EvidenceReport, ClaimEvidence,
    EvidenceStrength, RoleDNA
)


# ---------------------------------------------------------------------------
# Honeypot Detection Rules
# ---------------------------------------------------------------------------

def detect_honeypot(
    intel: CandidateIntelligence,
    raw: dict[str, Any]
) -> tuple[bool, float, list[str]]:
    """
    Detect honeypot candidates using consistency checks.
    Returns: (is_honeypot, honeypot_score, flags)
    
    Honeypot patterns from submission spec:
    - 8 years experience at a company founded 3 years ago
    - "expert" proficiency in 10 skills with 0 years used
    - Any other statistically impossible profiles
    """
    flags = []
    suspicion_score = 0.0

    # --- Rule 1: Expert skills with zero duration ---
    raw_skills = raw.get("skills", [])
    expert_zero_duration = [
        s for s in raw_skills
        if s.get("proficiency") in ("expert", "advanced")
        and int(s.get("duration_months", 0)) == 0
    ]
    if len(expert_zero_duration) >= 3:
        flags.append(f"Expert/Advanced proficiency claimed on {len(expert_zero_duration)} skills with 0 months used")
        suspicion_score += 0.4

    # --- Rule 2: Total skill duration >> career duration ---
    career_months = intel.total_career_months
    total_skill_duration = sum(int(s.get("duration_months", 0)) for s in raw_skills)
    # Allow for parallel usage (can use 3 skills simultaneously), so max realistic is 3x career months
    if career_months > 0 and total_skill_duration > career_months * 5:
        flags.append(
            f"Total skill duration ({total_skill_duration}mo) far exceeds career duration ({career_months}mo)"
        )
        suspicion_score += 0.3

    # --- Rule 3: Years of experience claim vs actual career history ---
    stated_yoe = intel.years_of_experience
    career_years = career_months / 12.0
    if career_years > 0 and abs(stated_yoe - career_years) > 2.5:
        flags.append(
            f"YOE mismatch: stated {stated_yoe:.1f}y vs career history {career_years:.1f}y"
        )
        suspicion_score += 0.2

    # --- Rule 4: Expert in many skills with very short duration per skill ---
    expert_skills = [
        s for s in raw_skills if s.get("proficiency") == "expert"
    ]
    if len(expert_skills) >= 8:
        avg_dur = sum(int(s.get("duration_months", 0)) for s in expert_skills) / len(expert_skills)
        if avg_dur < 6:
            flags.append(
                f"Expert in {len(expert_skills)} skills with avg {avg_dur:.1f}mo each"
            )
            suspicion_score += 0.35

    # --- Rule 5: Profile completeness perfect but engagement zero ---
    signals = raw.get("redrob_signals", {})
    completeness = float(signals.get("profile_completeness_score", 0))
    response_rate = float(signals.get("recruiter_response_rate", 0))
    if completeness >= 95 and response_rate < 0.05:
        flags.append("Near-perfect profile completeness with near-zero recruiter response rate")
        suspicion_score += 0.1

    # --- Rule 6: Very high endorsements on all skills with 0 assessment scores ---
    high_endorse_skills = [s for s in raw_skills if int(s.get("endorsements", 0)) > 80]
    if len(high_endorse_skills) > 5 and not signals.get("skill_assessment_scores"):
        flags.append(f"{len(high_endorse_skills)} skills with >80 endorsements but zero assessments completed")
        suspicion_score += 0.15

    # Cap at 1.0
    suspicion_score = min(suspicion_score, 1.0)
    is_honeypot = suspicion_score >= 0.65

    return is_honeypot, suspicion_score, flags


# ---------------------------------------------------------------------------
# Claim Validation
# ---------------------------------------------------------------------------

def validate_claims(
    intel: CandidateIntelligence,
    role_dna: RoleDNA
) -> list[ClaimEvidence]:
    """
    Validate whether candidate's claims have supporting evidence.
    Never marks candidate as dishonest — only reports evidence availability.
    """
    evidences = []

    # Claim 1: AI/ML technical expertise
    if intel.ai_skill_count > 0:
        ai_skill_names = [s.name for s in intel.ai_skills[:3]]
        if intel.has_production_ml_evidence:
            evidences.append(ClaimEvidence(
                claim=f"AI/ML expertise ({', '.join(ai_skill_names)})",
                evidence_strength=EvidenceStrength.STRONG,
                confidence=0.85,
                supporting_text="Career history contains production ML deployment evidence",
                notes="Skills backed by actual deployment experience",
            ))
        elif intel.ai_assessment_avg_score > 60:
            evidences.append(ClaimEvidence(
                claim=f"AI/ML expertise ({', '.join(ai_skill_names)})",
                evidence_strength=EvidenceStrength.MODERATE,
                confidence=0.65,
                supporting_text=f"Platform assessment score: {intel.ai_assessment_avg_score:.0f}/100",
                notes="Assessments support claims but no production evidence found",
            ))
        else:
            evidences.append(ClaimEvidence(
                claim=f"AI/ML expertise ({', '.join(ai_skill_names)})",
                evidence_strength=EvidenceStrength.WEAK,
                confidence=0.40,
                supporting_text="Skills listed but no assessment or production evidence",
                notes="Consider probing depth in interview",
            ))

    # Claim 2: Leadership (if claimed via title or career)
    leadership_claim = any(
        kw in intel.current_title.lower()
        for kw in ["lead", "manager", "head", "director", "principal", "staff"]
    )
    if leadership_claim:
        if intel.has_leadership_evidence:
            evidences.append(ClaimEvidence(
                claim="Team leadership / management",
                evidence_strength=EvidenceStrength.STRONG,
                confidence=0.80,
                supporting_text="Career history explicitly mentions team management",
            ))
        else:
            evidences.append(ClaimEvidence(
                claim="Team leadership / management",
                evidence_strength=EvidenceStrength.INSUFFICIENT,
                confidence=0.30,
                supporting_text="Leadership title but no explicit management evidence in descriptions",
                notes="Probe team size and direct reports in interview",
            ))

    # Claim 3: Years of experience
    stated = intel.years_of_experience
    actual_career_yrs = intel.total_career_months / 12.0
    if abs(stated - actual_career_yrs) < 1.5:
        evidences.append(ClaimEvidence(
            claim=f"{stated:.1f} years of experience",
            evidence_strength=EvidenceStrength.STRONG,
            confidence=0.90,
            supporting_text=f"Career history accounts for {actual_career_yrs:.1f} years",
        ))
    else:
        evidences.append(ClaimEvidence(
            claim=f"{stated:.1f} years of experience",
            evidence_strength=EvidenceStrength.WEAK,
            confidence=0.50,
            supporting_text=f"Career history only accounts for {actual_career_yrs:.1f} years",
            notes="Gap may include freelance, education, or unlisted roles",
        ))

    # Claim 4: Production deployment
    if intel.has_production_ml_evidence:
        evidences.append(ClaimEvidence(
            claim="Production ML deployment experience",
            evidence_strength=EvidenceStrength.STRONG,
            confidence=0.80,
            supporting_text="Deployment/serving keywords found in career descriptions",
        ))

    # Claim 5: GitHub activity
    if intel.github_activity_score > 0:
        strength = EvidenceStrength.STRONG if intel.github_activity_score > 50 else EvidenceStrength.MODERATE
        evidences.append(ClaimEvidence(
            claim=f"Active open-source contributor (GitHub score: {intel.github_activity_score:.0f}/100)",
            evidence_strength=strength,
            confidence=0.85,
            supporting_text="GitHub activity verified by platform integration",
        ))

    return evidences


def build_evidence_report(
    intel: CandidateIntelligence,
    raw: dict[str, Any],
    role_dna: RoleDNA
) -> EvidenceReport:
    """Build the complete evidence report for a candidate."""
    is_honeypot, honeypot_score, honeypot_flags = detect_honeypot(intel, raw)
    claim_evidences = validate_claims(intel, role_dna)

    # Compute overall evidence strength
    if not claim_evidences:
        overall = EvidenceStrength.INSUFFICIENT
        consistency = 0.3
    else:
        strength_values = {
            EvidenceStrength.STRONG: 3,
            EvidenceStrength.MODERATE: 2,
            EvidenceStrength.WEAK: 1,
            EvidenceStrength.INSUFFICIENT: 0,
        }
        avg = sum(strength_values[c.evidence_strength] for c in claim_evidences) / len(claim_evidences)
        if avg >= 2.5:
            overall = EvidenceStrength.STRONG
        elif avg >= 1.5:
            overall = EvidenceStrength.MODERATE
        elif avg >= 0.5:
            overall = EvidenceStrength.WEAK
        else:
            overall = EvidenceStrength.INSUFFICIENT
        consistency = 1.0 - honeypot_score

    return EvidenceReport(
        candidate_id=intel.candidate_id,
        is_honeypot=is_honeypot,
        honeypot_score=honeypot_score,
        honeypot_flags=honeypot_flags,
        claim_evidences=claim_evidences,
        overall_evidence_strength=overall,
        consistency_score=consistency,
    )
