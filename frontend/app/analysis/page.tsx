"use client";

import { Cpu, Zap, CheckCircle, Database, Brain, Eye, TrendingUp, Shield, Target, BarChart3 } from "lucide-react";

const PIPELINE_MODULES = [
  {
    id: 1,
    name: "Role DNA Engine",
    icon: Brain,
    color: "#6366F1",
    description: "Extracts structured intelligence from the JD using contextual reasoning, not keyword extraction. Identifies must-haves, hidden expectations, and disqualifiers.",
    outputs: ["must_have_skills[]", "hidden_expectations[]", "disqualifying_signals[]", "target_titles[]"],
    timing: "Offline, run once",
    llm: true,
  },
  {
    id: 2,
    name: "Candidate Intelligence Engine",
    icon: Database,
    color: "#38BDF8",
    description: "Extracts structured features from 100K raw candidate JSON profiles. Pure Python, no LLM. Classifies companies as services/product, detects production ML evidence, leadership signals.",
    outputs: ["ai_skill_count", "product_company_ratio", "has_production_ml_evidence", "career_progression_score"],
    timing: "~15s for 100K candidates",
    llm: false,
  },
  {
    id: 3,
    name: "Semantic Alignment Engine",
    icon: Target,
    color: "#10B981",
    description: "Computes 7-dimensional semantic alignment using sentence-transformers (all-MiniLM-L6-v2, 22MB). Soft signal — JD explicitly warns against pure embedding matching.",
    outputs: ["technical_alignment", "domain_alignment", "experience_alignment", "semantic_similarity"],
    timing: "~2 min for 100K (batch=256)",
    llm: false,
  },
  {
    id: 4,
    name: "Evidence Validation Engine",
    icon: Shield,
    color: "#F59E0B",
    description: "Validates resume claims against supporting evidence. Detects honeypots via consistency checks: expert×10 skills×0 months, career duration mismatches, impossible profiles.",
    outputs: ["is_honeypot", "honeypot_score", "claim_evidences[]", "consistency_score"],
    timing: "O(n) per candidate",
    llm: false,
  },
  {
    id: 5,
    name: "Multi-Dimensional Scorecard",
    icon: BarChart3,
    color: "#A78BFA",
    description: "Combines all upstream signals into 10 dimension scores and one final ranking score. Applies services-firm penalties, honeypot de-ranking, stale profile adjustments.",
    outputs: ["technical_fit", "role_fit", "final_score", "10 dimension scores"],
    timing: "O(1) per candidate",
    llm: false,
  },
  {
    id: 6,
    name: "Risk Radar Engine",
    icon: Eye,
    color: "#F43F5E",
    description: "Computes 8-dimension hiring risk profile. Technical risk, retention risk, adaptation risk, communication risk — each with specific explanations.",
    outputs: ["technical_risk", "retention_risk", "overall_risk", "risk_explanations"],
    timing: "O(1) per candidate",
    llm: false,
  },
  {
    id: 7,
    name: "Recruitability Index Engine",
    icon: TrendingUp,
    color: "#F97316",
    description: "Estimates candidate rarity in the market. Identifies rare AI/ML skill combinations, production experience uniqueness, and estimated replacement timeline.",
    outputs: ["tier (Easy/Moderate/Rare/Critical)", "replacement_timeline_weeks", "skill_scarcity_score"],
    timing: "O(1) per candidate",
    llm: false,
  },
  {
    id: 8,
    name: "Opportunity Cost Engine",
    icon: Zap,
    color: "#F59E0B",
    description: "Estimates organizational cost of rejecting each candidate. Factors: rarity, competitive demand, unique expertise, business value for the specific role.",
    outputs: ["level (Low/Medium/High/Critical)", "cost_factors[]", "overall_score"],
    timing: "O(1) per candidate",
    llm: false,
  },
  {
    id: 9,
    name: "Explainability Engine",
    icon: Brain,
    color: "#818CF8",
    description: "Generates transparent, specific reasoning for every recommendation. Template-based with real candidate facts — no hallucination. Produces submission.csv reasoning column.",
    outputs: ["why_selected", "key_strengths[]", "interview_focus_areas[]", "one_line_reasoning"],
    timing: "O(1) per candidate",
    llm: false,
  },
];

const CONSTRAINTS = [
  { label: "Network during ranking", value: "None (all offline)", color: "var(--danger)", icon: "🚫" },
  { label: "Runtime constraint", value: "< 5 minutes", color: "var(--warning)", icon: "⏱" },
  { label: "Compute", value: "CPU only, 16GB RAM", color: "var(--info)", icon: "💻" },
  { label: "Top candidates", value: "100 of 100,000", color: "var(--success)", icon: "🏆" },
  { label: "Primary metric", value: "NDCG@10 (50%)", color: "#A78BFA", icon: "📊" },
  { label: "Embedding model", value: "all-MiniLM-L6-v2 (22MB)", color: "var(--info)", icon: "🤖" },
];

export default function AnalysisPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Cpu size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">AI Pipeline</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          10-module reasoning pipeline — from raw JD to ranked candidates with full explainability.
        </p>
      </div>

      {/* Competition constraints */}
      <div className="card p-5 mb-8 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
        <h2 className="text-sm font-semibold text-white mb-4">Competition Constraints (Enforced)</h2>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {CONSTRAINTS.map((c) => (
            <div key={c.label} className="flex items-center gap-3 p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <span className="text-lg">{c.icon}</span>
              <div>
                <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{c.label}</p>
                <p className="text-xs font-semibold" style={{ color: c.color }}>{c.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline modules */}
      <div className="space-y-4">
        {PIPELINE_MODULES.map((mod, idx) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.id}
              className="card p-5 animate-fade-in-up"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="flex items-start gap-4">
                {/* Module number + icon */}
                <div className="flex flex-col items-center gap-1 shrink-0">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: `${mod.color}20`, border: `1px solid ${mod.color}40` }}
                  >
                    <Icon size={18} style={{ color: mod.color }} />
                  </div>
                  <span className="text-[10px] font-bold" style={{ color: "var(--text-muted)" }}>
                    #{mod.id}
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1 flex-wrap">
                    <h3 className="text-sm font-semibold text-white">{mod.name}</h3>
                    {mod.llm ? (
                      <span className="text-[10px] px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(99,102,241,0.15)", color: "var(--primary-light)", border: "1px solid rgba(99,102,241,0.3)" }}>
                        LLM (offline only)
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(16,185,129,0.15)", color: "var(--success)", border: "1px solid rgba(16,185,129,0.3)" }}>
                        No LLM · Pure Logic
                      </span>
                    )}
                    <span className="text-[10px] ml-auto" style={{ color: "var(--text-muted)" }}>
                      ⏱ {mod.timing}
                    </span>
                  </div>
                  <p className="text-xs mb-3 leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {mod.description}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {mod.outputs.map((o) => (
                      <code key={o} className="text-[10px] px-1.5 py-0.5 rounded"
                        style={{ background: "var(--surface-2)", color: mod.color }}>
                        {o}
                      </code>
                    ))}
                  </div>
                </div>
              </div>

              {/* Arrow to next */}
              {idx < PIPELINE_MODULES.length - 1 && (
                <div className="flex justify-start ml-14 mt-3">
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>↓</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Final output */}
      <div className="card p-5 mt-6 animate-fade-in-up" style={{ borderColor: "rgba(99,102,241,0.3)", background: "rgba(99,102,241,0.06)" }}>
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle size={16} style={{ color: "var(--primary-light)" }} />
          <h3 className="text-sm font-semibold text-white">Output: submission.csv</h3>
        </div>
        <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
          100 ranked candidates · fields: candidate_id, rank, score, reasoning · generated by rank.py in &lt;5 min · no network
        </p>
        <div className="flex gap-2 mt-3 flex-wrap">
          {["candidate_id", "rank", "score", "reasoning"].map((f) => (
            <code key={f} className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--surface-2)", color: "var(--primary-light)" }}>
              {f}
            </code>
          ))}
        </div>
      </div>
    </div>
  );
}
