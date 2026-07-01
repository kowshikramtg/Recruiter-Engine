"use client";

import { useEffect, useState } from "react";
import { api, CandidateListItem, PaginatedCandidates } from "@/lib/api/client";
import Link from "next/link";
import {
  Search, Filter, Github, MapPin, Clock, TrendingUp,
  ChevronLeft, ChevronRight, AlertTriangle, Star, Zap
} from "lucide-react";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function scoreColor(score: number) {
  const pct = score * 100;
  if (pct >= 70) return "#10B981";
  if (pct >= 50) return "#F59E0B";
  return "#F43F5E";
}

function scoreGradient(score: number) {
  const pct = score * 100;
  if (pct >= 70) return "linear-gradient(90deg, #059669, #10B981)";
  if (pct >= 50) return "linear-gradient(90deg, #D97706, #F59E0B)";
  return "linear-gradient(90deg, #E11D48, #F43F5E)";
}

function tierClass(tier: string): string {
  if (tier === "Critical Talent") return "tier-critical";
  if (tier === "Rare") return "tier-rare";
  if (tier === "Easy") return "tier-easy";
  return "tier-moderate";
}

function oppColor(level: string): string {
  if (level === "Critical") return "var(--danger)";
  if (level === "High") return "var(--risk-high)";
  if (level === "Medium") return "var(--warning)";
  return "var(--success)";
}

// ─── Rank Badge ───────────────────────────────────────────────────────────────

function RankBadge({ rank }: { rank: number }) {
  const badgeClass = rank === 1 ? "rank-gold" : rank === 2 ? "rank-silver" : rank === 3 ? "rank-bronze" : "rank-default";
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 ${badgeClass}`}>
      {rank}
    </div>
  );
}

// ─── Candidate Row ─────────────────────────────────────────────────────────────

function CandidateRow({ candidate }: { candidate: CandidateListItem }) {
  const scorePercent = Math.round(candidate.final_score * 100);
  const clr = scoreColor(candidate.final_score);
  const grad = scoreGradient(candidate.final_score);

  return (
    <Link href={`/candidates/${candidate.candidate_id}`}>
      <div className="card p-4 hover:border-indigo-500/30 transition-all duration-200 cursor-pointer group">
        <div className="flex items-start gap-4">
          <RankBadge rank={candidate.rank} />

          {/* Main info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-1">
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                    {candidate.name}
                  </span>
                  {candidate.is_honeypot && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                      style={{ background: "var(--danger-dim)", color: "var(--danger)", border: "1px solid rgba(244,63,94,0.3)" }}>
                      ⚠ Honeypot
                    </span>
                  )}
                </div>
                <p className="text-xs truncate" style={{ color: "var(--text-secondary)" }}>
                  {candidate.current_title} · {candidate.current_company}
                </p>
              </div>

              {/* Score */}
              <div className="text-right shrink-0">
                <p className="text-xl font-bold" style={{ color: clr }}>{scorePercent}%</p>
                <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>fit score</p>
              </div>
            </div>

            {/* Score bar */}
            <div className="score-bar mb-3">
              <div
                className="score-bar-fill"
                style={{ width: `${scorePercent}%`, background: grad }}
              />
            </div>

            {/* Meta row */}
            <div className="flex items-center gap-4 flex-wrap">
              <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                <Clock size={11} />
                {candidate.years_of_experience.toFixed(1)}y exp
              </span>
              <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                <MapPin size={11} />
                {candidate.location || "India"}
              </span>
              <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                <Zap size={11} />
                {candidate.ai_skill_count} AI skills
              </span>
              {candidate.github_activity_score > 0 && (
                <span className="flex items-center gap-1 text-xs" style={{ color: "var(--success)" }}>
                  <Github size={11} />
                  {candidate.github_activity_score.toFixed(0)}/100
                </span>
              )}

              {/* Badges */}
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${tierClass(candidate.recruitability_tier)}`}>
                {candidate.recruitability_tier}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                style={{
                  background: `${oppColor(candidate.opportunity_cost_level)}20`,
                  color: oppColor(candidate.opportunity_cost_level),
                  border: `1px solid ${oppColor(candidate.opportunity_cost_level)}40`
                }}>
                {candidate.opportunity_cost_level} Opp Cost
              </span>

              {/* Risk */}
              {candidate.risk_overall > 70 && (
                <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full"
                  style={{ background: "var(--danger-dim)", color: "var(--danger)", border: "1px solid rgba(244,63,94,0.3)" }}>
                  <AlertTriangle size={9} /> High Risk
                </span>
              )}
            </div>

            {/* Reasoning */}
            {candidate.one_line_reasoning && (
              <p className="text-[11px] mt-2 line-clamp-2" style={{ color: "var(--text-muted)" }}>
                {candidate.one_line_reasoning}
              </p>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

// ─── Candidates Page ──────────────────────────────────────────────────────────

export default function CandidatesPage() {
  const [data, setData] = useState<PaginatedCandidates | null>(null);
  const [page, setPage] = useState(1);
  const [minScore, setMinScore] = useState(0);
  const [excludeHoneypots, setExcludeHoneypots] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getCandidates({ page, page_size: 20, min_score: minScore / 100, exclude_honeypots: excludeHoneypots })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [page, minScore, excludeHoneypots]);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 animate-fade-in-up">
        <h1 className="text-3xl font-bold text-white mb-1">Ranked Candidates</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {data ? `${data.total.toLocaleString()} candidates ranked · showing ${(page - 1) * 20 + 1}–${Math.min(page * 20, data.total)}` : "Loading..."}
        </p>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-6 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter size={14} style={{ color: "var(--text-muted)" }} />
            <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>Filters</span>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs" style={{ color: "var(--text-secondary)" }}>Min Score:</label>
            <select
              value={minScore}
              onChange={(e) => { setMinScore(Number(e.target.value)); setPage(1); }}
              className="text-xs rounded px-2 py-1 border outline-none"
              style={{ background: "var(--surface-2)", borderColor: "var(--border-subtle)", color: "var(--text-primary)" }}
            >
              {[0, 30, 50, 60, 70, 80].map(v => (
                <option key={v} value={v}>{v}%+</option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: "var(--text-secondary)" }}>
            <input
              type="checkbox"
              checked={excludeHoneypots}
              onChange={(e) => { setExcludeHoneypots(e.target.checked); setPage(1); }}
              className="accent-indigo-500"
            />
            Exclude Honeypots
          </label>
          <span className="text-xs px-2 py-1 rounded-full" style={{ background: "var(--surface-2)", color: "var(--text-muted)" }}>
            NDCG@10 = 50% · Top 10 matters most
          </span>
        </div>
      </div>

      {/* Candidates list */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card p-4 animate-pulse" style={{ height: 120, background: "var(--surface-2)" }} />
          ))}
        </div>
      ) : error ? (
        <div className="card p-8 text-center">
          <AlertTriangle size={32} className="mx-auto mb-3" style={{ color: "var(--warning)" }} />
          <p className="text-sm text-white mb-1">Failed to load candidates</p>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{error}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data?.items.map((c) => (
            <div key={c.candidate_id} className="animate-fade-in-up">
              <CandidateRow candidate={c} />
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-3 mt-8">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm disabled:opacity-40 transition-colors hover:bg-white/10"
            style={{ color: "var(--text-secondary)", border: "1px solid var(--border-subtle)" }}
          >
            <ChevronLeft size={14} /> Prev
          </button>
          <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {page} / {data.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm disabled:opacity-40 transition-colors hover:bg-white/10"
            style={{ color: "var(--text-secondary)", border: "1px solid var(--border-subtle)" }}
          >
            Next <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
