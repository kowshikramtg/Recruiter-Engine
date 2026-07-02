/**
 * API client — typed functions for all backend endpoints.
 * Uses NEXT_PUBLIC_API_URL environment variable.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface DimensionScore {
  name: string;
  score: number;
  rationale: string;
  weight: number;
}

export interface Scorecard {
  technical_fit: number;
  role_fit: number;
  domain_expertise: number;
  career_momentum: number;
  leadership: number;
  communication: number;
  adaptability: number;
  cultural_fit: number;
  learning_potential: number;
  evidence_strength: number;
  final_score: number;
  is_disqualified: boolean;
  disqualification_reason: string;
  dimensions: DimensionScore[];
}

export interface RiskDimension {
  name: string;
  risk_level: "Low" | "Medium" | "High" | "Critical";
  risk_score: number;
  explanation: string;
}

export interface RiskRadar {
  technical_risk: RiskDimension;
  retention_risk: RiskDimension;
  adaptation_risk: RiskDimension;
  communication_risk: RiskDimension;
  leadership_risk: RiskDimension;
  domain_risk: RiskDimension;
  learning_risk: RiskDimension;
  overall_risk: RiskDimension;
}

export interface Recruitability {
  tier: "Easy" | "Moderate" | "Rare" | "Critical Talent";
  overall_score: number;
  skill_scarcity_score: number;
  experience_uniqueness_score: number;
  market_availability_score: number;
  career_growth_score: number;
  replacement_timeline_weeks: number;
  reasoning: string;
}

export interface OpportunityCost {
  level: "Low" | "Medium" | "High" | "Critical";
  overall_score: number;
  candidate_rarity_factor: number;
  competitive_demand_factor: number;
  unique_expertise_factor: number;
  business_value_factor: number;
  reasoning: string;
  cost_factors: string[];
}

export interface ClaimEvidence {
  claim: string;
  evidence_strength: "Strong" | "Moderate" | "Weak" | "Insufficient";
  confidence: number;
  supporting_text: string;
  notes: string;
}

export interface EvidenceReport {
  is_honeypot: boolean;
  honeypot_score: number;
  honeypot_flags: string[];
  overall_evidence_strength: string;
  consistency_score: number;
  claim_evidences: ClaimEvidence[];
}

export interface AlignmentScores {
  technical_alignment: number;
  domain_alignment: number;
  experience_alignment: number;
  leadership_alignment: number;
  growth_alignment: number;
  communication_alignment: number;
  adaptability_alignment: number;
  semantic_similarity: number;
  overall_alignment: number;
}

export interface Explainability {
  why_selected: string;
  key_strengths: string[];
  key_weaknesses: string[];
  tradeoffs: string[];
  interview_focus_areas: string[];
  missing_skills: string[];
  improvement_suggestions: string[];
  final_recommendation: string;
  one_line_reasoning: string;
}

export interface IntelligenceProfile {
  candidate_id: string;
  name: string;
  headline: string;
  current_title: string;
  current_company: string;
  years_of_experience: number;
  location: string;
  country: string;
  ai_skill_count: number;
  ai_skill_depth_score: number;
  github_activity_score: number;
  has_production_ml_evidence: boolean;
  has_leadership_evidence: boolean;
  is_entirely_services_firm: boolean;
  product_company_ratio: number;
  career_progression_score: number;
  education_tier_score: number;
  avg_tenure_months: number;
  title_alignment_score: number;
  ai_assessment_avg_score: number;
  top_ai_skills: string[];
  summary_text: string;
}

export interface CandidateListItem {
  candidate_id: string;
  rank: number;
  final_score: number;
  name: string;
  headline: string;
  current_title: string;
  current_company: string;
  years_of_experience: number;
  location: string;
  ai_skill_count: number;
  github_activity_score: number;
  is_honeypot: boolean;
  recruitability_tier: string;
  opportunity_cost_level: string;
  risk_overall: number;
  one_line_reasoning: string;
}

export interface CandidateDetail {
  candidate_id: string;
  rank: number;
  final_score: number;
  intelligence: IntelligenceProfile;
  scorecard: Scorecard;
  alignment: AlignmentScores;
  risk_radar: RiskRadar;
  evidence: EvidenceReport;
  recruitability: Recruitability;
  opportunity_cost: OpportunityCost;
  explainability: Explainability;
}

export interface PaginatedCandidates {
  items: CandidateListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardStats {
  total_candidates: number;
  top_matches: number;
  average_fit_score: number;
  critical_talent_count: number;
  high_opportunity_cost_count: number;
  high_risk_count: number;
  honeypot_count: number;
  avg_notice_period_days: number;
}

export interface ChartData {
  score_distribution: { range: string; count: number }[];
  risk_distribution: { level: string; count: number }[];
  recruitability_distribution: { tier: string; count: number }[];
  opportunity_cost_distribution: { level: string; count: number }[];
  top_titles: { title: string; count: number }[];
}

export interface RoleDNA {
  title: string;
  company: string;
  experience_min_years: number;
  experience_max_years: number;
  must_have_skills: string[];
  preferred_skills: string[];
  target_titles: string[];
  responsibilities: string[];
  success_indicators: string[];
  hidden_expectations: string[];
  technical_competencies: string[];
  domain_knowledge: string[];
  seniority_level: string;
  leadership_requirements: string;
  communication_expectations: string;
  trainable_skills: string[];
  notice_preference_days: number;
  notice_max_days: number;
  requires_production_experience: boolean;
}

export interface SimulationPreset {
  id: string;
  name: string;
  description: string;
  params: Record<string, unknown>;
}

export interface SimulationResult {
  candidate_id: string;
  original_score: number;
  simulated_score: number;
  score_delta: number;
  name: string;
  current_title: string;
  years_of_experience: number;
  simulated_rank: number;
}

// ─── Fetch helper ─────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }
  return res.json() as Promise<T>;
}

// ─── API Functions ────────────────────────────────────────────────────────────

export const api = {
  // Dashboard
  getDashboardStats: () => apiFetch<DashboardStats>("/api/v1/dashboard/stats"),
  getChartData: () => apiFetch<ChartData>("/api/v1/dashboard/charts"),

  // Candidates
  getCandidates: (params: {
    page?: number;
    page_size?: number;
    min_score?: number;
    exclude_honeypots?: boolean;
  } = {}) => {
    const q = new URLSearchParams({
      page: String(params.page ?? 1),
      page_size: String(params.page_size ?? 20),
      min_score: String(params.min_score ?? 0),
      exclude_honeypots: String(params.exclude_honeypots ?? true),
    });
    return apiFetch<PaginatedCandidates>(`/api/v1/candidates?${q}`);
  },

  getCandidateDetail: (id: string) =>
    apiFetch<CandidateDetail>(`/api/v1/candidates/${id}`),

  // Jobs / Role DNA
  getCurrentJob: () => apiFetch<RoleDNA>("/api/v1/jobs/current"),

  // Time Machine
  getSimulationPresets: () => apiFetch<SimulationPreset[]>("/api/v1/time-machine/presets"),
  runSimulation: (scenarioId: string, candidateIds?: string[]) =>
    apiFetch<{ scenario_id: string; results: SimulationResult[]; total: number }>(
      "/api/v1/time-machine/simulate",
      {
        method: "POST",
        body: JSON.stringify({ scenario_id: scenarioId, candidate_ids: candidateIds ?? [] }),
      }
    ),

  // Compare
  compareCandidates: (candidateIds: string[]) =>
    apiFetch<{ candidates: CandidateDetail[] }>("/api/v1/compare/candidates", {
      method: "POST",
      body: JSON.stringify({ candidate_ids: candidateIds }),
    }),
  getTopForCompare: (limit = 20) =>
    apiFetch<PaginatedCandidates>(`/api/v1/compare/top?limit=${limit}`),
};
