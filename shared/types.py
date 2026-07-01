"""
Shared type definitions used across all AI modules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class RecruitabilityTier(str, Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    RARE = "Rare"
    CRITICAL = "Critical Talent"


class OpportunityCostLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class EvidenceStrength(str, Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"
    INSUFFICIENT = "Insufficient"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ---------------------------------------------------------------------------
# Role DNA
# ---------------------------------------------------------------------------

@dataclass
class RoleDNA:
    """Structured intelligence extracted from a job description."""
    title: str = ""
    company: str = ""
    location_preferences: list[str] = field(default_factory=list)
    experience_min_years: float = 5.0
    experience_max_years: float = 9.0
    must_have_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    disqualifying_signals: list[str] = field(default_factory=list)
    target_titles: list[str] = field(default_factory=list)
    avoid_companies: list[str] = field(default_factory=list)
    notice_preference_days: int = 30
    notice_max_days: int = 90
    requires_production_experience: bool = True
    requires_github: bool = True
    prefers_product_company: bool = True
    responsibilities: list[str] = field(default_factory=list)
    success_indicators: list[str] = field(default_factory=list)
    hidden_expectations: list[str] = field(default_factory=list)
    technical_competencies: list[str] = field(default_factory=list)
    domain_knowledge: list[str] = field(default_factory=list)
    seniority_level: str = "senior"
    leadership_requirements: str = ""
    communication_expectations: str = ""
    trainable_skills: list[str] = field(default_factory=list)
    raw_jd_text: str = ""


# ---------------------------------------------------------------------------
# Candidate Intelligence
# ---------------------------------------------------------------------------

@dataclass
class SkillSignal:
    name: str
    proficiency: str
    endorsements: int
    duration_months: int
    assessment_score: Optional[float] = None
    is_ai_relevant: bool = False


@dataclass
class CareerEntry:
    company: str
    title: str
    duration_months: int
    is_current: bool
    industry: str
    company_size: str
    description: str
    is_product_company: bool = False
    is_services_firm: bool = False
    has_production_ml: bool = False
    has_team_leadership: bool = False


@dataclass
class EducationEntry:
    institution: str
    degree: str
    field_of_study: str
    tier: str
    is_ai_related: bool = False


@dataclass
class CandidateIntelligence:
    """Structured intelligence extracted from a candidate profile."""
    candidate_id: str = ""
    name: str = ""
    headline: str = ""
    current_title: str = ""
    current_company: str = ""
    years_of_experience: float = 0.0
    location: str = ""
    country: str = ""

    # Derived signals
    ai_skills: list[SkillSignal] = field(default_factory=list)
    all_skills: list[SkillSignal] = field(default_factory=list)
    career_history: list[CareerEntry] = field(default_factory=list)
    education: list[EducationEntry] = field(default_factory=list)
    certifications: list[dict] = field(default_factory=list)

    # Computed intelligence
    ai_skill_count: int = 0
    ai_skill_depth_score: float = 0.0
    ai_skill_duration_total_months: int = 0
    ai_assessment_avg_score: float = 0.0
    github_activity_score: float = -1.0
    total_career_months: int = 0
    is_entirely_services_firm: bool = False
    product_company_ratio: float = 0.0
    has_production_ml_evidence: bool = False
    has_leadership_evidence: bool = False
    career_progression_score: float = 0.0
    avg_tenure_months: float = 0.0
    title_alignment_score: float = 0.0
    education_tier_score: float = 0.0
    summary_text: str = ""
    career_description_combined: str = ""


# ---------------------------------------------------------------------------
# Alignment Scores
# ---------------------------------------------------------------------------

@dataclass
class AlignmentScores:
    """Multi-dimensional alignment between candidate and role."""
    candidate_id: str = ""
    technical_alignment: float = 0.0
    domain_alignment: float = 0.0
    experience_alignment: float = 0.0
    leadership_alignment: float = 0.0
    growth_alignment: float = 0.0
    communication_alignment: float = 0.0
    adaptability_alignment: float = 0.0
    semantic_similarity: float = 0.0
    overall_alignment: float = 0.0


# ---------------------------------------------------------------------------
# Evidence Validation
# ---------------------------------------------------------------------------

@dataclass
class ClaimEvidence:
    claim: str
    evidence_strength: EvidenceStrength
    confidence: float
    supporting_text: str = ""
    notes: str = ""


@dataclass
class EvidenceReport:
    candidate_id: str = ""
    is_honeypot: bool = False
    honeypot_score: float = 0.0
    honeypot_flags: list[str] = field(default_factory=list)
    claim_evidences: list[ClaimEvidence] = field(default_factory=list)
    overall_evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    consistency_score: float = 1.0


# ---------------------------------------------------------------------------
# Scorecard
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    name: str
    score: float  # 0-100
    rationale: str = ""
    weight: float = 0.1


@dataclass
class Scorecard:
    candidate_id: str = ""
    technical_fit: float = 0.0
    learning_potential: float = 0.0
    leadership: float = 0.0
    communication: float = 0.0
    role_fit: float = 0.0
    domain_expertise: float = 0.0
    career_momentum: float = 0.0
    adaptability: float = 0.0
    cultural_fit: float = 0.0
    evidence_strength: float = 0.0
    final_score: float = 0.0
    is_disqualified: bool = False
    disqualification_reason: str = ""
    dimensions: list[DimensionScore] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Risk Radar
# ---------------------------------------------------------------------------

@dataclass
class RiskDimension:
    name: str
    risk_level: RiskLevel
    risk_score: float  # 0-100 (higher = more risk)
    explanation: str = ""


@dataclass
class RiskRadar:
    candidate_id: str = ""
    technical_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Technical Risk", RiskLevel.MEDIUM, 50.0))
    retention_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Retention Risk", RiskLevel.MEDIUM, 50.0))
    adaptation_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Adaptation Risk", RiskLevel.MEDIUM, 50.0))
    communication_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Communication Risk", RiskLevel.MEDIUM, 50.0))
    leadership_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Leadership Risk", RiskLevel.MEDIUM, 50.0))
    domain_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Domain Risk", RiskLevel.MEDIUM, 50.0))
    learning_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Learning Risk", RiskLevel.MEDIUM, 50.0))
    overall_risk: RiskDimension = field(default_factory=lambda: RiskDimension("Overall Risk", RiskLevel.MEDIUM, 50.0))


# ---------------------------------------------------------------------------
# Recruitability
# ---------------------------------------------------------------------------

@dataclass
class RecruitabilityIndex:
    candidate_id: str = ""
    tier: RecruitabilityTier = RecruitabilityTier.MODERATE
    skill_scarcity_score: float = 0.5
    experience_uniqueness_score: float = 0.5
    market_availability_score: float = 0.5
    career_growth_score: float = 0.5
    overall_score: float = 0.5
    replacement_timeline_weeks: int = 8
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Opportunity Cost
# ---------------------------------------------------------------------------

@dataclass
class OpportunityCost:
    candidate_id: str = ""
    level: OpportunityCostLevel = OpportunityCostLevel.MEDIUM
    candidate_rarity_factor: float = 0.5
    competitive_demand_factor: float = 0.5
    unique_expertise_factor: float = 0.5
    business_value_factor: float = 0.5
    overall_score: float = 0.5
    reasoning: str = ""
    cost_factors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Explainability
# ---------------------------------------------------------------------------

@dataclass
class ExplainabilityReport:
    candidate_id: str = ""
    rank: int = 0
    final_score: float = 0.0
    why_selected: str = ""
    key_strengths: list[str] = field(default_factory=list)
    key_weaknesses: list[str] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)
    interview_focus_areas: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    final_recommendation: str = ""
    one_line_reasoning: str = ""  # for submission.csv reasoning column


# ---------------------------------------------------------------------------
# Full Analysis Result
# ---------------------------------------------------------------------------

@dataclass
class CandidateAnalysis:
    """Complete analysis result for a single candidate."""
    candidate_id: str = ""
    intelligence: Optional[CandidateIntelligence] = None
    alignment: Optional[AlignmentScores] = None
    evidence: Optional[EvidenceReport] = None
    scorecard: Optional[Scorecard] = None
    risk_radar: Optional[RiskRadar] = None
    recruitability: Optional[RecruitabilityIndex] = None
    opportunity_cost: Optional[OpportunityCost] = None
    explainability: Optional[ExplainabilityReport] = None
    final_score: float = 0.0
    rank: int = 0
