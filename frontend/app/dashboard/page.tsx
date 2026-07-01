"use client";

import { useEffect, useState } from "react";
import { api, DashboardStats, ChartData, CandidateListItem } from "@/lib/api/client";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import {
  Users, TrendingUp, AlertTriangle, Star, DollarSign,
  Shield, Bot, Activity
} from "lucide-react";
import Link from "next/link";

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

// ─── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({
  icon: Icon, label, value, sub, color, delay = 0,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: string;
  color: string;
  delay?: number;
}) {
  return (
    <div
      className="card stat-card p-5 animate-fade-in-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
            {label}
          </p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {sub && <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>{sub}</p>}
        </div>
        <div
          className="p-2 rounded-lg"
          style={{ background: `${color}20` }}
        >
          <Icon size={20} style={{ color }} />
        </div>
      </div>
    </div>
  );
}

// ─── Top Candidate Row ─────────────────────────────────────────────────────────

function TopCandidateRow({ c, rank }: { c: CandidateListItem; rank: number }) {
  const scorePercent = Math.round(c.final_score * 100);
  const badgeClass = rank === 1 ? "rank-gold" : rank === 2 ? "rank-silver" : rank === 3 ? "rank-bronze" : "rank-default";
  const scoreColor = scorePercent >= 70 ? "#10B981" : scorePercent >= 50 ? "#F59E0B" : "#F43F5E";

  return (
    <Link href={`/candidates/${c.candidate_id}`}>
      <div className="flex items-center gap-4 p-3 rounded-lg hover:bg-white/5 transition-colors cursor-pointer">
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white ${badgeClass}`}>
          {rank}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{c.name}</p>
          <p className="text-xs truncate" style={{ color: "var(--text-muted)" }}>
            {c.current_title} · {c.current_company}
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-sm font-bold" style={{ color: scoreColor }}>{scorePercent}%</p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>fit score</p>
        </div>
      </div>
    </Link>
  );
}

// ─── Custom Tooltip ───────────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass px-3 py-2 rounded-lg text-xs">
      <p className="font-medium text-white">{label}</p>
      <p style={{ color: "var(--primary-light)" }}>{payload[0].value.toLocaleString()} candidates</p>
    </div>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [charts, setCharts] = useState<ChartData | null>(null);
  const [topCandidates, setTopCandidates] = useState<CandidateListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getDashboardStats(),
      api.getChartData(),
      api.getCandidates({ page: 1, page_size: 10 }),
    ])
      .then(([s, c, cands]) => {
        setStats(s);
        setCharts(c);
        setTopCandidates(cands.items);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!stats || !charts) return null;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Bot size={20} style={{ color: "var(--primary)" }} />
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--primary)" }}>
            Hiring Intelligence Engine
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-1">Recruiter Dashboard</h1>
        <p style={{ color: "var(--text-secondary)" }} className="text-sm">
          Evidence-driven, explainable candidate intelligence for Senior AI Engineer · Redrob AI
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Users} label="Total Analyzed" value={stats.total_candidates.toLocaleString()} sub="candidates in pool" color="var(--primary)" delay={0} />
        <StatCard icon={TrendingUp} label="Top Matches" value={stats.top_matches.toLocaleString()} sub="score ≥ 70%" color="var(--success)" delay={60} />
        <StatCard icon={Activity} label="Avg Fit Score" value={`${stats.average_fit_score.toFixed(1)}%`} sub="across all candidates" color="var(--info)" delay={120} />
        <StatCard icon={Star} label="Critical Talent" value={stats.critical_talent_count.toLocaleString()} sub="Rare + Critical tier" color="#A78BFA" delay={180} />
        <StatCard icon={DollarSign} label="High Opp Cost" value={stats.high_opportunity_cost_count.toLocaleString()} sub="rejection risk" color="var(--warning)" delay={240} />
        <StatCard icon={AlertTriangle} label="High Risk" value={stats.high_risk_count.toLocaleString()} sub="hiring risk flagged" color="var(--danger)" delay={300} />
        <StatCard icon={Shield} label="Honeypots" value={stats.honeypot_count.toLocaleString()} sub="detected & filtered" color="var(--text-muted)" delay={360} />
        <StatCard icon={Users} label="Avg Notice" value={`${stats.avg_notice_period_days.toFixed(0)}d`} sub="days notice period" color="var(--info)" delay={420} />
      </div>

      {/* Charts + Top Candidates */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Score Distribution */}
        <div className="card p-6 col-span-1 lg:col-span-2 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
          <h2 className="text-sm font-semibold text-white mb-4">Fit Score Distribution</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={charts.score_distribution} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
              <XAxis dataKey="range" tick={{ fontSize: 10, fill: "#475569" }} />
              <YAxis tick={{ fontSize: 10, fill: "#475569" }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recruitability Donut */}
        <div className="card p-6 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
          <h2 className="text-sm font-semibold text-white mb-4">Recruitability Index</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={charts.recruitability_distribution} dataKey="count" nameKey="tier" cx="50%" cy="50%" innerRadius={55} outerRadius={80}>
                {charts.recruitability_distribution.map((entry) => (
                  <Cell key={entry.tier} fill={RECR_COLORS[entry.tier] || "#6366F1"} />
                ))}
              </Pie>
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution */}
        <div className="card p-6 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
          <h2 className="text-sm font-semibold text-white mb-4">Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={charts.risk_distribution} dataKey="count" nameKey="level" cx="50%" cy="50%" innerRadius={45} outerRadius={70}>
                {charts.risk_distribution.map((entry) => (
                  <Cell key={entry.level} fill={RISK_COLORS[entry.level] || "#6366F1"} />
                ))}
              </Pie>
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Opportunity Cost */}
        <div className="card p-6 animate-fade-in-up" style={{ animationDelay: "250ms" }}>
          <h2 className="text-sm font-semibold text-white mb-4">Opportunity Cost</h2>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={charts.opportunity_cost_distribution} dataKey="count" nameKey="level" cx="50%" cy="50%" innerRadius={45} outerRadius={70}>
                {charts.opportunity_cost_distribution.map((entry) => (
                  <Cell key={entry.level} fill={OPP_COLORS[entry.level] || "#6366F1"} />
                ))}
              </Pie>
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top 10 Candidates */}
        <div className="card p-6 animate-fade-in-up" style={{ animationDelay: "300ms" }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Top Candidates</h2>
            <Link href="/candidates" className="text-xs hover:underline" style={{ color: "var(--primary-light)" }}>
              View all →
            </Link>
          </div>
          <div className="space-y-1">
            {topCandidates.slice(0, 8).map((c, i) => (
              <TopCandidateRow key={c.candidate_id} c={c} rank={i + 1} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="h-4 w-48 rounded-lg mb-3 animate-pulse" style={{ background: "var(--surface-2)" }} />
        <div className="h-8 w-72 rounded-lg mb-2 animate-pulse" style={{ background: "var(--surface-2)" }} />
        <div className="h-4 w-96 rounded-lg animate-pulse" style={{ background: "var(--surface-2)" }} />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="card p-5 animate-pulse" style={{ height: 90, background: "var(--surface-2)" }} />
        ))}
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="card p-8 text-center">
        <AlertTriangle size={48} className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
        <h2 className="text-xl font-bold text-white mb-2">Backend Unavailable</h2>
        <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
          {message}
        </p>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          Make sure the backend is running: <code className="px-1 py-0.5 rounded" style={{ background: "var(--surface-2)" }}>uvicorn backend.main:app --reload</code>
          <br />
          And the precomputed DB exists: <code className="px-1 py-0.5 rounded" style={{ background: "var(--surface-2)" }}>python precompute.py</code>
        </p>
      </div>
    </div>
  );
}
