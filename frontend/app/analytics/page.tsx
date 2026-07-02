"use client";

import { useEffect, useState } from "react";
import { api, ChartData, DashboardStats } from "@/lib/api/client";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend
} from "recharts";
import {
  Users, BarChart3, TrendingUp, Target, Shield, Zap, Brain, AlertTriangle
} from "lucide-react";

// ─── Color maps ───────────────────────────────────────────────────────────────

const RISK_COLORS: Record<string, string> = {
  Low: "#10B981", Medium: "#F59E0B", High: "#F97316", Critical: "#F43F5E",
};
const RECR_COLORS: Record<string, string> = {
  Easy: "#10B981", Moderate: "#38BDF8", Rare: "#A78BFA", "Critical Talent": "#F43F5E",
};
const OPP_COLORS: Record<string, string> = {
  Low: "#10B981", Medium: "#F59E0B", High: "#F97316", Critical: "#F43F5E",
};

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass px-3 py-2 rounded-lg text-xs">
      <p className="font-medium text-white">{label}</p>
      <p style={{ color: "var(--primary-light)" }}>{payload[0].value.toLocaleString()} candidates</p>
    </div>
  );
}

// ─── Static Methodology Cards ─────────────────────────────────────────────────

const METHODOLOGY_CARDS = [
  {
    icon: Brain,
    title: "Scoring Methodology",
    color: "var(--primary)",
    content: "Final score formula: Technical Fit (28%) + Role Fit (18%) + Domain Expertise (10%) + Career Momentum (8%) + Behavioral Composite (18%) + Cultural Fit (5%) + Leadership (5%) + Adaptability (4%) + Learning Potential (3%) + Evidence Strength (1%)",
  },
  {
    icon: Target,
    title: "Anti-Trap Signal Detection",
    color: "var(--warning)",
    content: "JD explicitly flags: Marketing/HR titles with AI keywords (trap), services-firm-only careers, pure researchers without production deployment, keyword stuffers with no depth. Services-firm career → 40% score penalty. Zero AI skills → 60% penalty.",
  },
  {
    icon: TrendingUp,
    title: "NDCG@10 Optimization",
    color: "var(--success)",
    content: "Top 10 positions carry 50% of scoring weight. High-weight signals — title alignment, production ML evidence, product company ratio — ensure the first 10 positions are genuinely strong fits before secondary signals matter.",
  },
  {
    icon: Shield,
    title: "Honeypot Defense System",
    color: "var(--danger)",
    content: "~80 honeypot candidates planted in the dataset. Detection via consistency math: expert × 10 skills × 0 months experience = impossible. Career duration mismatch flags. Honeypots receive 0.05× score multiplier — effectively ranked last.",
  },
  {
    icon: Zap,
    title: "Behavioral Signal Weighting",
    color: "var(--info)",
    content: "18% of final score comes from behavioral composite: availability (35%), platform engagement (30%), notice period (20%), location fit (15%). Open-to-work flag + recent last-active date + strong recruiter response rate = top behavioral signals.",
  },
  {
    icon: Users,
    title: "Semantic Alignment (Soft Signal)",
    color: "#A78BFA",
    content: "7-dimensional semantic alignment via sentence-transformers (all-MiniLM-L6-v2, 22MB CPU model). Used as 10% soft signal, not primary driver. JD explicitly warns against pure embedding matching — this prevents over-relying on semantic similarity.",
  },
];

// ─── Analytics Page ───────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const [charts, setCharts] = useState<ChartData | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendAvailable, setBackendAvailable] = useState(true);

  useEffect(() => {
    Promise.all([api.getChartData(), api.getDashboardStats()])
      .then(([c, s]) => {
        setCharts(c);
        setStats(s);
      })
      .catch(() => setBackendAvailable(false))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Hiring pool composition, scoring distribution, and methodology details.
        </p>
      </div>

      {/* Live Charts */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card p-5 animate-pulse" style={{ height: 220, background: "var(--surface-2)" }} />
          ))}
        </div>
      ) : backendAvailable && charts && stats ? (
        <div className="space-y-6 mb-8">
          {/* Summary numbers */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in-up">
            {[
              { label: "Total Analyzed", value: stats.total_candidates.toLocaleString(), color: "var(--primary)" },
              { label: "Top Matches (≥70%)", value: stats.top_matches.toLocaleString(), color: "var(--success)" },
              { label: "Avg Fit Score", value: `${stats.average_fit_score.toFixed(1)}%`, color: "var(--info)" },
              { label: "Honeypots Caught", value: stats.honeypot_count.toLocaleString(), color: "var(--danger)" },
            ].map(({ label, value, color }) => (
              <div key={label} className="card p-4">
                <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>{label}</p>
                <p className="text-2xl font-bold" style={{ color }}>{value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Score distribution */}
            <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
              <h2 className="text-sm font-semibold text-white mb-4">Fit Score Distribution</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={charts.score_distribution} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <XAxis dataKey="range" tick={{ fontSize: 9, fill: "#475569" }} />
                  <YAxis tick={{ fontSize: 9, fill: "#475569" }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Recruitability donut */}
            <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
              <h2 className="text-sm font-semibold text-white mb-4">Recruitability Distribution</h2>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={charts.recruitability_distribution} dataKey="count" nameKey="tier" cx="50%" cy="50%" innerRadius={50} outerRadius={75}>
                    {charts.recruitability_distribution.map((entry) => (
                      <Cell key={entry.tier} fill={RECR_COLORS[entry.tier] || "#6366F1"} />
                    ))}
                  </Pie>
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Risk distribution */}
            <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
              <h2 className="text-sm font-semibold text-white mb-4">Risk Level Distribution</h2>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={charts.risk_distribution} dataKey="count" nameKey="level" cx="50%" cy="50%" innerRadius={50} outerRadius={75}>
                    {charts.risk_distribution.map((entry) => (
                      <Cell key={entry.level} fill={RISK_COLORS[entry.level] || "#6366F1"} />
                    ))}
                  </Pie>
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Opportunity cost */}
            <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
              <h2 className="text-sm font-semibold text-white mb-4">Opportunity Cost Distribution</h2>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={charts.opportunity_cost_distribution} dataKey="count" nameKey="level" cx="50%" cy="50%" innerRadius={50} outerRadius={75}>
                    {charts.opportunity_cost_distribution.map((entry) => (
                      <Cell key={entry.level} fill={OPP_COLORS[entry.level] || "#6366F1"} />
                    ))}
                  </Pie>
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : !loading && !backendAvailable ? (
        <div className="card p-5 mb-8 animate-fade-in-up" style={{ borderColor: "rgba(245,158,11,0.3)", background: "rgba(245,158,11,0.05)" }}>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={14} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-semibold" style={{ color: "var(--warning)" }}>Backend Offline</span>
          </div>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Live charts require the backend. Run: <code className="px-1 py-0.5 rounded text-[10px]" style={{ background: "var(--surface-2)" }}>uvicorn backend.main:app --reload</code>
          </p>
        </div>
      ) : null}

      {/* Methodology Cards */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-white mb-1">Scoring Methodology</h2>
        <p className="text-xs mb-4" style={{ color: "var(--text-secondary)" }}>
          How the 10-module AI pipeline drives each candidate's ranking
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {METHODOLOGY_CARDS.map(({ icon: Icon, title, color, content }, idx) => (
          <div
            key={title}
            className="card p-5 animate-fade-in-up"
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${color}20` }}>
                <Icon size={14} style={{ color }} />
              </div>
              <h3 className="text-sm font-semibold text-white">{title}</h3>
            </div>
            <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{content}</p>
          </div>
        ))}
      </div>

      {/* Weight breakdown */}
      <div className="card p-5 mt-6 animate-fade-in-up">
        <h2 className="text-sm font-semibold text-white mb-4">Scoring Weight Breakdown</h2>
        <div className="space-y-3">
          {[
            { label: "Technical Fit", weight: 28, color: "#6366F1" },
            { label: "Role Fit", weight: 18, color: "#10B981" },
            { label: "Behavioral Composite", weight: 18, color: "#38BDF8" },
            { label: "Domain Expertise", weight: 10, color: "#F59E0B" },
            { label: "Career Momentum", weight: 8, color: "#A78BFA" },
            { label: "Cultural Fit", weight: 5, color: "#F97316" },
            { label: "Leadership", weight: 5, color: "#818CF8" },
            { label: "Adaptability", weight: 4, color: "#34D399" },
            { label: "Learning Potential", weight: 3, color: "#FCA5A5" },
            { label: "Evidence Strength", weight: 1, color: "#94A3B8" },
          ].map(({ label, weight, color }) => (
            <div key={label}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs" style={{ color: "var(--text-secondary)" }}>{label}</span>
                <span className="text-xs font-bold" style={{ color }}>{weight}%</span>
              </div>
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${weight * 3.3}%`, background: color }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
