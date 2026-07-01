"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, CandidateDetail } from "@/lib/api/client";
import Link from "next/link";
import {
  ArrowLeft, Github, MapPin, Clock, Star, AlertTriangle,
  CheckCircle, XCircle, Target, TrendingUp, Shield, Zap,
  Brain, MessageSquare, Users, BarChart3, ChevronRight,
  Briefcase, BookOpen
} from "lucide-react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip
} from "recharts";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const TABS = ["Overview", "Scorecard", "Risk Radar", "Intelligence", "Evidence", "Interview"] as const;
type Tab = typeof TABS[number];

function scoreColor(score: number) {
  if (score >= 70) return "#10B981";
  if (score >= 50) return "#F59E0B";
  return "#F43F5E";
}

function scoreGrad(score: number) {
  if (score >= 70) return "linear-gradient(90deg, #059669, #10B981)";
  if (score >= 50) return "linear-gradient(90deg, #D97706, #F59E0B)";
  return "linear-gradient(90deg, #E11D48, #F43F5E)";
}

function riskColor(level: string) {
  if (level === "Low") return "#10B981";
  if (level === "Medium") return "#F59E0B";
  if (level === "High") return "#F97316";
  return "#F43F5E";
}

function evidenceIcon(strength: string) {
  if (strength === "Strong") return <CheckCircle size={12} style={{ color: "#10B981" }} />;
  if (strength === "Moderate") return <CheckCircle size={12} style={{ color: "#38BDF8" }} />;
  if (strength === "Weak") return <AlertTriangle size={12} style={{ color: "#F59E0B" }} />;
  return <XCircle size={12} style={{ color: "#F43F5E" }} />;
}

function evidenceStrengthClass(strength: string) {
  if (strength === "Strong") return "evidence-strong";
  if (strength === "Moderate") return "evidence-moderate";
  if (strength === "Weak") return "evidence-weak";
  return "evidence-insufficient";
}

// ─── Score Bar ─────────────────────────────────────────────────────────────────

function ScoreBar({ label, score, weight }: { label: string; score: number; weight?: number }) {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setWidth(score), 100);
    return () => clearTimeout(t);
  }, [score]);

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>{label}</span>
        <span className="text-xs font-bold" style={{ color: scoreColor(score) }}>{score.toFixed(0)}</span>
      </div>
      <div className="score-bar">
        <div className="score-bar-fill" style={{ width: `${width}%`, background: scoreGrad(score) }} />
      </div>
    </div>
  );
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────

function TabBar({ active, onChange }: { active: Tab; onChange: (t: Tab) => void }) {
  return (
    <div className="flex border-b overflow-x-auto" style={{ borderColor: "var(--border-subtle)" }}>
      {TABS.map((t) => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`px-4 py-3 text-xs font-medium whitespace-nowrap transition-colors ${
            active === t ? "tab-active" : "hover:text-white"
          }`}
          style={{ color: active === t ? "var(--primary-light)" : "var(--text-muted)" }}
        >
          {t}
        </button>
      ))}
    </div>
  );
}

// ─── Overview Tab ─────────────────────────────────────────────────────────────

function OverviewTab({ data }: { data: CandidateDetail }) {
  const { intelligence: i, explainability: ex, scorecard: sc, recruitability, opportunity_cost } = data;

  return (
    <div className="space-y-6">
      {/* Why selected */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Brain size={14} style={{ color: "var(--primary)" }} />
          <span className="text-sm font-semibold text-white">Why This Candidate?</span>
        </div>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{ex.why_selected}</p>
      </div>

      {/* Strengths + Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Star size={13} style={{ color: "var(--success)" }} /> Key Strengths
          </h3>
          <ul className="space-y-2">
            {ex.key_strengths.map((s, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                <CheckCircle size={11} className="mt-0.5 shrink-0" style={{ color: "var(--success)" }} />
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <AlertTriangle size={13} style={{ color: "var(--warning)" }} /> Concerns
          </h3>
          <ul className="space-y-2">
            {ex.key_weaknesses.length > 0 ? ex.key_weaknesses.map((w, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                <XCircle size={11} className="mt-0.5 shrink-0" style={{ color: "var(--warning)" }} />
                {w}
              </li>
            )) : (
              <li className="text-xs" style={{ color: "var(--text-muted)" }}>No major concerns identified</li>
            )}
          </ul>
        </div>
      </div>

      {/* Recruitability + Opp Cost */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Target size={13} style={{ color: "#A78BFA" }} />
            <span className="text-sm font-semibold text-white">Recruitability</span>
          </div>
          <p className="text-xs mb-3" style={{ color: "var(--text-secondary)" }}>{recruitability.reasoning}</p>
          <div className="flex items-center gap-2">
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
              recruitability.tier === "Critical Talent" ? "tier-critical" :
              recruitability.tier === "Rare" ? "tier-rare" :
              recruitability.tier === "Easy" ? "tier-easy" : "tier-moderate"
            }`}>{recruitability.tier}</span>
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>~{recruitability.replacement_timeline_weeks} weeks to replace</span>
          </div>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={13} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-semibold text-white">Opportunity Cost</span>
          </div>
          <p className="text-xs mb-3 line-clamp-3" style={{ color: "var(--text-secondary)" }}>{opportunity_cost.reasoning}</p>
          <span className="text-xs px-2 py-1 rounded-full font-medium"
            style={{
              background: opportunity_cost.level === "Critical" ? "var(--danger-dim)" :
                          opportunity_cost.level === "High" ? "rgba(249,115,22,0.15)" :
                          "var(--warning-dim)",
              color: opportunity_cost.level === "Critical" ? "var(--danger)" :
                     opportunity_cost.level === "High" ? "#F97316" : "var(--warning)"
            }}>
            {opportunity_cost.level} Cost if Rejected
          </span>
        </div>
      </div>

      {/* Final Recommendation */}
      <div className="card p-5">
        <p className="text-sm font-semibold text-white mb-1">Final Recommendation</p>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{ex.final_recommendation}</p>
      </div>
    </div>
  );
}

// ─── Scorecard Tab ────────────────────────────────────────────────────────────

function ScorecardTab({ data }: { data: CandidateDetail }) {
  const sc = data.scorecard;
  const dimensions = [
    { label: "Technical Fit", score: sc.technical_fit },
    { label: "Role Fit", score: sc.role_fit },
    { label: "Domain Expertise", score: sc.domain_expertise },
    { label: "Career Momentum", score: sc.career_momentum },
    { label: "Leadership", score: sc.leadership },
    { label: "Communication", score: sc.communication },
    { label: "Adaptability", score: sc.adaptability },
    { label: "Cultural Fit", score: sc.cultural_fit },
    { label: "Learning Potential", score: sc.learning_potential },
    { label: "Evidence Strength", score: sc.evidence_strength },
  ];

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <span className="text-sm font-semibold text-white">10-Dimension Scorecard</span>
          <div className="text-right">
            <span className="text-2xl font-bold" style={{ color: scoreColor(sc.final_score * 100) }}>
              {(sc.final_score * 100).toFixed(1)}%
            </span>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>overall fit</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
          {dimensions.map((d) => (
            <ScoreBar key={d.label} label={d.label} score={d.score} />
          ))}
        </div>
      </div>

      {sc.is_disqualified && (
        <div className="card p-4" style={{ borderColor: "rgba(244,63,94,0.3)", background: "var(--danger-dim)" }}>
          <p className="text-sm text-white font-medium">⚠ Disqualified</p>
          <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>{sc.disqualification_reason}</p>
        </div>
      )}

      {/* Alignment scores */}
      <div className="card p-6">
        <span className="text-sm font-semibold text-white block mb-4">Semantic Alignment Scores</span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
          {[
            { label: "Technical Alignment", score: data.alignment.technical_alignment },
            { label: "Domain Alignment", score: data.alignment.domain_alignment },
            { label: "Experience Alignment", score: data.alignment.experience_alignment },
            { label: "Leadership Alignment", score: data.alignment.leadership_alignment },
            { label: "Growth Alignment", score: data.alignment.growth_alignment },
            { label: "Semantic Similarity", score: data.alignment.semantic_similarity },
          ].map((d) => (
            <ScoreBar key={d.label} label={d.label} score={d.score} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Risk Radar Tab ───────────────────────────────────────────────────────────

function RiskRadarTab({ data }: { data: CandidateDetail }) {
  const rr = data.risk_radar;
  const radarData = [
    { subject: "Technical", value: rr.technical_risk.risk_score },
    { subject: "Retention", value: rr.retention_risk.risk_score },
    { subject: "Adaptation", value: rr.adaptation_risk.risk_score },
    { subject: "Communication", value: rr.communication_risk.risk_score },
    { subject: "Leadership", value: rr.leadership_risk.risk_score },
    { subject: "Domain", value: rr.domain_risk.risk_score },
    { subject: "Learning", value: rr.learning_risk.risk_score },
  ];

  const riskEntries = [
    { name: "Technical Risk", dim: rr.technical_risk },
    { name: "Retention Risk", dim: rr.retention_risk },
    { name: "Adaptation Risk", dim: rr.adaptation_risk },
    { name: "Communication Risk", dim: rr.communication_risk },
    { name: "Leadership Risk", dim: rr.leadership_risk },
    { name: "Domain Risk", dim: rr.domain_risk },
    { name: "Learning Risk", dim: rr.learning_risk },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <span className="text-sm font-semibold text-white block mb-4">Risk Radar (higher = more risk)</span>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: "#64748B" }} />
              <Radar name="Risk" dataKey="value" stroke="#F43F5E" fill="#F43F5E" fillOpacity={0.15} />
              <Tooltip
                contentStyle={{ background: "var(--surface)", border: "1px solid var(--border-subtle)", borderRadius: 8, fontSize: 11 }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold text-white">Overall Risk</span>
            <span className="text-lg font-bold" style={{ color: riskColor(rr.overall_risk.risk_level) }}>
              {rr.overall_risk.risk_level}
            </span>
          </div>
          <p className="text-xs mb-4" style={{ color: "var(--text-secondary)" }}>
            {rr.overall_risk.explanation}
          </p>
          <div className="space-y-2">
            {riskEntries.map(({ name, dim }) => (
              <div key={name} className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full shrink-0" style={{ background: riskColor(dim.risk_level) }} />
                <span className="text-xs flex-1" style={{ color: "var(--text-secondary)" }}>{name}</span>
                <span className="text-xs font-medium" style={{ color: riskColor(dim.risk_level) }}>
                  {dim.risk_level}
                </span>
                <span className="text-xs w-8 text-right" style={{ color: "var(--text-muted)" }}>
                  {dim.risk_score.toFixed(0)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk explanations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {riskEntries.map(({ name, dim }) => (
          <div key={name} className="card p-4" style={{
            borderColor: dim.risk_level === "Critical" ? "rgba(244,63,94,0.2)" :
                         dim.risk_level === "High" ? "rgba(249,115,22,0.2)" : "var(--border-subtle)"
          }}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full" style={{ background: riskColor(dim.risk_level) }} />
              <span className="text-xs font-semibold text-white">{name}</span>
              <span className="ml-auto text-xs font-medium" style={{ color: riskColor(dim.risk_level) }}>
                {dim.risk_level} ({dim.risk_score.toFixed(0)}/100)
              </span>
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>{dim.explanation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Intelligence Tab ─────────────────────────────────────────────────────────

function IntelligenceTab({ data }: { data: CandidateDetail }) {
  const i = data.intelligence;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Experience", value: `${i.years_of_experience.toFixed(1)}y` },
          { label: "AI Skills", value: i.ai_skill_count },
          { label: "GitHub Score", value: i.github_activity_score > 0 ? `${i.github_activity_score.toFixed(0)}/100` : "—" },
          { label: "Assessment", value: i.ai_assessment_avg_score > 0 ? `${i.ai_assessment_avg_score.toFixed(0)}/100` : "—" },
        ].map(({ label, value }) => (
          <div key={label} className="card p-4">
            <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>{label}</p>
            <p className="text-xl font-bold text-white">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Career Signals</span>
          <div className="space-y-2">
            {[
              { label: "Production ML Evidence", value: i.has_production_ml_evidence, positive: true },
              { label: "Leadership Evidence", value: i.has_leadership_evidence, positive: true },
              { label: "Services Firm Only", value: i.is_entirely_services_firm, positive: false },
            ].map(({ label, value, positive }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-xs" style={{ color: "var(--text-secondary)" }}>{label}</span>
                <span className="text-xs font-medium" style={{ color: value ? (positive ? "#10B981" : "#F43F5E") : "#475569" }}>
                  {value ? (positive ? "✓ Yes" : "⚠ Yes") : "✗ No"}
                </span>
              </div>
            ))}
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Product Company Ratio</span>
              <span className="text-xs font-medium" style={{ color: i.product_company_ratio > 0.5 ? "#10B981" : "#F59E0B" }}>
                {(i.product_company_ratio * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Profile Quality</span>
          <div className="space-y-2">
            {[
              { label: "Title Alignment", score: i.title_alignment_score },
              { label: "Career Progression", score: i.career_progression_score },
              { label: "Education Tier", score: i.education_tier_score },
              { label: "AI Skill Depth", score: i.ai_skill_depth_score },
            ].map(({ label, score }) => (
              <ScoreBar key={label} label={label} score={score} />
            ))}
          </div>
        </div>
      </div>

      {i.top_ai_skills.length > 0 && (
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Top AI Skills</span>
          <div className="flex flex-wrap gap-2">
            {i.top_ai_skills.map((skill) => (
              <span key={skill} className="text-xs px-2 py-1 rounded-full"
                style={{ background: "rgba(99,102,241,0.15)", color: "var(--primary-light)", border: "1px solid rgba(99,102,241,0.3)" }}>
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {i.summary_text && (
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-2">Profile Summary</span>
          <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{i.summary_text}</p>
        </div>
      )}
    </div>
  );
}

// ─── Evidence Tab ─────────────────────────────────────────────────────────────

function EvidenceTab({ data }: { data: CandidateDetail }) {
  const ev = data.evidence;
  return (
    <div className="space-y-6">
      {/* Honeypot alert */}
      {ev.is_honeypot && (
        <div className="card p-4" style={{ borderColor: "rgba(244,63,94,0.4)", background: "rgba(244,63,94,0.08)" }}>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={14} style={{ color: "var(--danger)" }} />
            <span className="text-sm font-semibold" style={{ color: "var(--danger)" }}>Honeypot Detected</span>
            <span className="text-xs px-2 py-0.5 rounded-full ml-auto" style={{ background: "var(--danger-dim)", color: "var(--danger)" }}>
              Score: {(ev.honeypot_score * 100).toFixed(0)}%
            </span>
          </div>
          <ul className="space-y-1">
            {ev.honeypot_flags.map((flag, i) => (
              <li key={i} className="text-xs" style={{ color: "var(--text-secondary)" }}>• {flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Overall evidence */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm font-semibold text-white">Evidence Report</span>
          <span className={`text-sm font-medium ${evidenceStrengthClass(ev.overall_evidence_strength)}`}>
            {ev.overall_evidence_strength} Evidence
          </span>
        </div>
        <div className="space-y-4">
          {ev.claim_evidences.map((claim, idx) => (
            <div key={idx} className="border-b pb-3 last:border-0 last:pb-0" style={{ borderColor: "var(--border-subtle)" }}>
              <div className="flex items-center gap-2 mb-1">
                {evidenceIcon(claim.evidence_strength)}
                <span className="text-xs font-medium text-white">{claim.claim}</span>
                <span className={`text-[10px] ml-auto font-medium ${evidenceStrengthClass(claim.evidence_strength)}`}>
                  {claim.evidence_strength} · {(claim.confidence * 100).toFixed(0)}%
                </span>
              </div>
              {claim.supporting_text && (
                <p className="text-xs ml-5" style={{ color: "var(--text-secondary)" }}>{claim.supporting_text}</p>
              )}
              {claim.notes && (
                <p className="text-xs ml-5 mt-1" style={{ color: "var(--text-muted)" }}>💡 {claim.notes}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Interview Tab ─────────────────────────────────────────────────────────────

function InterviewTab({ data }: { data: CandidateDetail }) {
  const ex = data.explainability;
  return (
    <div className="space-y-6">
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare size={14} style={{ color: "var(--primary)" }} />
          <span className="text-sm font-semibold text-white">Interview Focus Areas</span>
        </div>
        <div className="space-y-3">
          {ex.interview_focus_areas.map((q, i) => (
            <div key={i} className="flex gap-3 p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <span className="text-xs font-bold shrink-0 mt-0.5" style={{ color: "var(--primary)" }}>Q{i + 1}</span>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{q}</p>
            </div>
          ))}
        </div>
      </div>

      {ex.missing_skills.length > 0 && (
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Missing JD Requirements</span>
          <div className="flex flex-wrap gap-2">
            {ex.missing_skills.map((s) => (
              <span key={s} className="text-xs px-2 py-1 rounded-full"
                style={{ background: "var(--danger-dim)", color: "var(--danger)", border: "1px solid rgba(244,63,94,0.3)" }}>
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {ex.tradeoffs.length > 0 && (
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Tradeoffs to Consider</span>
          <ul className="space-y-2">
            {ex.tradeoffs.map((t, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--warning)" }}>⚡</span>{t}
              </li>
            ))}
          </ul>
        </div>
      )}

      {ex.improvement_suggestions.length > 0 && (
        <div className="card p-5">
          <span className="text-sm font-semibold text-white block mb-3">Candidate Growth Suggestions</span>
          <ul className="space-y-2">
            {ex.improvement_suggestions.map((s, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--info)" }}>→</span>{s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Candidate Detail Page ─────────────────────────────────────────────────────

export default function CandidateDetailPage() {
  const params = useParams();
  const candidateId = params?.id as string;
  const [data, setData] = useState<CandidateDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("Overview");

  useEffect(() => {
    if (!candidateId) return;
    api.getCandidateDetail(candidateId)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [candidateId]);

  if (loading) {
    return (
      <div className="p-8">
        <div className="h-4 w-32 rounded-lg animate-pulse mb-8" style={{ background: "var(--surface-2)" }} />
        <div className="card p-8 animate-pulse" style={{ height: 200 }} />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="card p-8 text-center">
          <AlertTriangle size={32} className="mx-auto mb-3" style={{ color: "var(--warning)" }} />
          <p className="text-sm text-white">{error || "Candidate not found"}</p>
        </div>
      </div>
    );
  }

  const i = data.intelligence;
  const scorePercent = Math.round(data.final_score * 100);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6 text-xs" style={{ color: "var(--text-muted)" }}>
        <Link href="/candidates" className="hover:text-white transition-colors">Candidates</Link>
        <ChevronRight size={12} />
        <span style={{ color: "var(--text-secondary)" }}>{data.candidate_id}</span>
      </div>

      {/* Header */}
      <div className="card p-6 mb-6 animate-fade-in-up">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            {/* Rank badge */}
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0 ${
              data.rank <= 3 ? (data.rank === 1 ? "rank-gold" : data.rank === 2 ? "rank-silver" : "rank-bronze") : "rank-default"
            }`}>
              #{data.rank}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{i.name}</h1>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                {i.current_title} · {i.current_company}
              </p>
              <div className="flex items-center gap-3 mt-2 flex-wrap">
                <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                  <MapPin size={11} /> {i.location || "India"}
                </span>
                <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                  <Clock size={11} /> {i.years_of_experience.toFixed(1)} years exp
                </span>
                {i.github_activity_score > 0 && (
                  <span className="flex items-center gap-1 text-xs" style={{ color: "var(--success)" }}>
                    <Github size={11} /> GitHub {i.github_activity_score.toFixed(0)}/100
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Score */}
          <div className="text-right shrink-0">
            <div className="text-4xl font-bold mb-1" style={{ color: scoreColor(scorePercent) }}>
              {scorePercent}%
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>Fit Score</p>
            <div className="flex items-center gap-2 mt-2 justify-end flex-wrap">
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                data.recruitability.tier === "Critical Talent" ? "tier-critical" :
                data.recruitability.tier === "Rare" ? "tier-rare" :
                data.recruitability.tier === "Easy" ? "tier-easy" : "tier-moderate"
              }`}>{data.recruitability.tier}</span>
            </div>
          </div>
        </div>

        {/* One-line reasoning */}
        {data.explainability.one_line_reasoning && (
          <div className="mt-4 pt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              <span style={{ color: "var(--primary-light)" }}>AI Summary: </span>
              {data.explainability.one_line_reasoning}
            </p>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="card overflow-hidden animate-fade-in-up" style={{ animationDelay: "100ms" }}>
        <TabBar active={activeTab} onChange={setActiveTab} />
        <div className="p-6">
          {activeTab === "Overview" && <OverviewTab data={data} />}
          {activeTab === "Scorecard" && <ScorecardTab data={data} />}
          {activeTab === "Risk Radar" && <RiskRadarTab data={data} />}
          {activeTab === "Intelligence" && <IntelligenceTab data={data} />}
          {activeTab === "Evidence" && <EvidenceTab data={data} />}
          {activeTab === "Interview" && <InterviewTab data={data} />}
        </div>
      </div>
    </div>
  );
}
