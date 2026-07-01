"""Pydantic response schemas for all API endpoints."""
from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel


class DimensionScoreSchema(BaseModel):
    name: str
    score: float
    rationale: str = ""
    weight: float = 0.1


class ScorecardSchema(BaseModel):
    technical_fit: float
    role_fit: float
    domain_expertise: float
    career_momentum: float
    leadership: float
    communication: float
    adaptability: float
    cultural_fit: float
    learning_potential: float
    evidence_strength: float
    final_score: float
    is_disqualified: bool = False
    disqualification_reason: str = ""
    dimensions: List[DimensionScoreSchema] = []


class RiskDimensionSchema(BaseModel):
    name: str
    risk_level: str
    risk_score: float
    explanation: str = ""


class RiskRadarSchema(BaseModel):
    technical_risk: RiskDimensionSchema
    retention_risk: RiskDimensionSchema
    adaptation_risk: RiskDimensionSchema
    communication_risk: RiskDimensionSchema
    leadership_risk: RiskDimensionSchema
    domain_risk: RiskDimensionSchema
    learning_risk: RiskDimensionSchema
    overall_risk: RiskDimensionSchema


class RecruitabilitySchema(BaseModel):
    tier: str
    overall_score: float
    skill_scarcity_score: float
    experience_uniqueness_score: float
    market_availability_score: float
    career_growth_score: float
    replacement_timeline_weeks: int
    reasoning: str


class OpportunityCostSchema(BaseModel):
    level: str
    overall_score: float
    candidate_rarity_factor: float
    competitive_demand_factor: float
    unique_expertise_factor: float
    business_value_factor: float
    reasoning: str
    cost_factors: List[str] = []


class ClaimEvidenceSchema(BaseModel):
    claim: str
    evidence_strength: str
    confidence: float
    supporting_text: str = ""
    notes: str = ""


class EvidenceReportSchema(BaseModel):
    is_honeypot: bool
    honeypot_score: float
    honeypot_flags: List[str] = []
    overall_evidence_strength: str
    consistency_score: float
    claim_evidences: List[ClaimEvidenceSchema] = []


class AlignmentScoresSchema(BaseModel):
    technical_alignment: float
    domain_alignment: float
    experience_alignment: float
    leadership_alignment: float
    growth_alignment: float
    communication_alignment: float
    adaptability_alignment: float
    semantic_similarity: float
    overall_alignment: float


class ExplainabilitySchema(BaseModel):
    why_selected: str
    key_strengths: List[str] = []
    key_weaknesses: List[str] = []
    tradeoffs: List[str] = []
    interview_focus_areas: List[str] = []
    missing_skills: List[str] = []
    improvement_suggestions: List[str] = []
    final_recommendation: str
    one_line_reasoning: str


class IntelligenceProfileSchema(BaseModel):
    candidate_id: str
    name: str
    headline: str
    current_title: str
    current_company: str
    years_of_experience: float
    location: str
    country: str
    ai_skill_count: int
    ai_skill_depth_score: float
    github_activity_score: float
    has_production_ml_evidence: bool
    has_leadership_evidence: bool
    is_entirely_services_firm: bool
    product_company_ratio: float
    career_progression_score: float
    education_tier_score: float
    avg_tenure_months: float
    title_alignment_score: float
    ai_assessment_avg_score: float
    top_ai_skills: List[str] = []
    summary_text: str = ""


class CandidateListItem(BaseModel):
    candidate_id: str
    rank: int
    final_score: float
    name: str
    headline: str
    current_title: str
    current_company: str
    years_of_experience: float
    location: str
    ai_skill_count: int
    github_activity_score: float
    is_honeypot: bool
    recruitability_tier: str
    opportunity_cost_level: str
    risk_overall: float
    one_line_reasoning: str


class CandidateDetailSchema(BaseModel):
    candidate_id: str
    rank: int
    final_score: float
    intelligence: IntelligenceProfileSchema
    scorecard: ScorecardSchema
    alignment: AlignmentScoresSchema
    risk_radar: RiskRadarSchema
    evidence: EvidenceReportSchema
    recruitability: RecruitabilitySchema
    opportunity_cost: OpportunityCostSchema
    explainability: ExplainabilitySchema


class DashboardStatsSchema(BaseModel):
    total_candidates: int
    top_matches: int  # score >= 0.7
    average_fit_score: float
    critical_talent_count: int  # Rare + Critical Talent
    high_opportunity_cost_count: int  # High + Critical
    high_risk_count: int
    honeypot_count: int
    avg_notice_period_days: float


class ChartDataSchema(BaseModel):
    score_distribution: List[dict]  # [{range, count}]
    risk_distribution: List[dict]   # [{level, count}]
    recruitability_distribution: List[dict]  # [{tier, count}]
    opportunity_cost_distribution: List[dict]  # [{level, count}]
    top_titles: List[dict]          # [{title, count}]


class RoleDNASchema(BaseModel):
    title: str
    company: str
    experience_min_years: float
    experience_max_years: float
    must_have_skills: List[str]
    preferred_skills: List[str]
    target_titles: List[str]
    responsibilities: List[str]
    success_indicators: List[str]
    hidden_expectations: List[str]
    technical_competencies: List[str]
    domain_knowledge: List[str]
    seniority_level: str
    leadership_requirements: str
    communication_expectations: str
    trainable_skills: List[str]
    notice_preference_days: int
    notice_max_days: int
    requires_production_experience: bool


class PaginatedCandidates(BaseModel):
    items: List[CandidateListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
