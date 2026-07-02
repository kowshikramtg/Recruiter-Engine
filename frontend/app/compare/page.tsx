"use client";

import { useEffect, useState } from "react";
import { api, CandidateListItem, CandidateDetail } from "@/lib/api/client";
import {
  ArrowLeftRight, Plus, X, GitBranch, MapPin, Clock, Zap,
  CheckCircle, XCircle, AlertTriangle, Star, Target, TrendingUp
} from "lucide-react";

// ─── Color helpers ─────────────────────────────────────────────────────────────

function scoreColor(score: number) {
  if (score >= 70) return "#10B981";
  if (score >= 50) return "#F59E0B";
  return "#F43F5E";
}

function riskColor(level: string) {
  if (level === "Low") return "#10B981";
  if (level === "Medium") return "#F59E0B";
  if (level === "High") return "#F97316";
  return "#F43F5E";
}

// ─── Candidate Picker ─────────────────────────────────────────────────────────

function CandidatePicker({
  candidates,
  selected,
  onSelect,
  onRemove,
  maxSelect,
}: {
  candidates: CandidateListItem[];
  selected: string[];
  onSelect: (id: string) => void;
  onRemove: (id: string) => void;
  maxSelect: number;
}) {
  const [search, setSearch] = useState("");
  const filtered = candidates.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.current_title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-3">
        <Plus size={14} style={{ color: "var(--primary)" }} />
        <span className="text-sm font-semibold text-white">Select Candidates to Compare</span>
        <span className="text-xs ml-auto" style={{ color: "var(--text-muted)" }}>
          {selected.length}/{maxSelect} selected
        </span>
      </div>

      {/* Selected chips */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selected.map((id) => {
            const c = candidates.find((x) => x.candidate_id === id);
            return (
              <div
                key={id}
                className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                style={{ background: "rgba(99,102,241,0.2)", color: "var(--primary-light)", border: "1px solid rgba(99,102,241,0.3)" }}
              >
                {c?.name || id}
                <button onClick={() => onRemove(id)} className="ml-1 hover:opacity-70">
                  <X size={10} />
                </button>
              </div>
            );
          })}
        </div>
      )}

      <input
        type="text"
        placeholder="Search by name or title..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-3 py-2 rounded-lg text-xs outline-none mb-2"
        style={{
          background: "var(--surface-2)",
          border: "1px solid var(--border-subtle)",
          color: "var(--text-primary)",
        }}
      />

      <div className="max-h-48 overflow-y-auto space-y-1">
        {filtered.slice(0, 30).map((c) => {
          const isSelected = selected.includes(c.candidate_id);
          const canSelect = !isSelected && selected.length < maxSelect;
          return (
            <button
              key={c.candidate_id}
              onClick={() => isSelected ? onRemove(c.candidate_id) : canSelect && onSelect(c.candidate_id)}
              disabled={!isSelected && !canSelect}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors hover:bg-white/5 disabled:opacity-40"
              style={isSelected ? { background: "rgba(99,102,241,0.12)" } : {}}
            >
              <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-xs font-bold text-white"
                style={{ background: isSelected ? "var(--primary)" : "var(--surface-2)" }}>
                {isSelected ? <CheckCircle size={12} /> : c.rank}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{c.name}</p>
                <p className="text-[10px] truncate" style={{ color: "var(--text-muted)" }}>{c.current_title}</p>
              </div>
              <span className="text-xs font-bold shrink-0" style={{ color: scoreColor(c.final_score * 100) }}>
                {Math.round(c.final_score * 100)}%
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ─── Comparison Table ─────────────────────────────────────────────────────────

const PALETTE = ["#6366F1", "#10B981", "#F59E0B", "#F43F5E", "#38BDF8"];

function ComparisonGrid({ details }: { details: CandidateDetail[] }) {
  if (details.length === 0) return null;

  const dims = [
    { label: "Technical Fit", key: "technical_fit" as const },
    { label: "Role Fit", key: "role_fit" as const },
    { label: "Domain Expertise", key: "domain_expertise" as const },
    { label: "Career Momentum", key: "career_momentum" as const },
    { label: "Leadership", key: "leadership" as const },
    { label: "Communication", key: "communication" as const },
    { label: "Adaptability", key: "adaptability" as const },
    { label: "Cultural Fit", key: "cultural_fit" as const },
    { label: "Learning Potential", key: "learning_potential" as const },
  ];

  return (
    <div className="space-y-6">
      {/* Header row */}
      <div className="card p-5">
        <div className="grid gap-4" style={{ gridTemplateColumns: `180px repeat(${details.length}, 1fr)` }}>
          <div />
          {details.map((d, i) => (
            <div key={d.candidate_id} className="text-center">
              <div className="w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center text-xs font-bold text-white"
                style={{ background: PALETTE[i] }}>
                #{d.rank}
              </div>
              <p className="text-sm font-semibold text-white truncate">{d.intelligence.name}</p>
              <p className="text-[10px] truncate" style={{ color: "var(--text-muted)" }}>
                {d.intelligence.current_title}
              </p>
              <div className="text-2xl font-bold mt-2" style={{ color: scoreColor(d.final_score * 100) }}>
                {Math.round(d.final_score * 100)}%
              </div>
              <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>fit score</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick signals */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Key Signals</h3>
        <div className="space-y-3">
          {[
            { label: "Experience (yrs)", render: (d: CandidateDetail) => `${d.intelligence.years_of_experience.toFixed(1)}y` },
            { label: "AI Skills", render: (d: CandidateDetail) => d.intelligence.ai_skill_count },
            { label: "GitHub", render: (d: CandidateDetail) => d.intelligence.github_activity_score > 0 ? `${d.intelligence.github_activity_score.toFixed(0)}/100` : "—" },
            { label: "Production ML", render: (d: CandidateDetail) => d.intelligence.has_production_ml_evidence ? "✓ Yes" : "✗ No" },
            { label: "Leadership", render: (d: CandidateDetail) => d.intelligence.has_leadership_evidence ? "✓ Yes" : "—" },
            { label: "Services Only", render: (d: CandidateDetail) => d.intelligence.is_entirely_services_firm ? "⚠ Yes" : "✓ No" },
            { label: "Recruitability", render: (d: CandidateDetail) => d.recruitability.tier },
            { label: "Opp. Cost", render: (d: CandidateDetail) => d.opportunity_cost.level },
            { label: "Risk Level", render: (d: CandidateDetail) => d.risk_radar.overall_risk.risk_level },
          ].map(({ label, render }) => (
            <div key={label} className="grid items-center gap-4" style={{ gridTemplateColumns: `180px repeat(${details.length}, 1fr)` }}>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>{label}</span>
              {details.map((d) => {
                const val = render(d);
                const isPositive = String(val).startsWith("✓");
                const isNegative = String(val).startsWith("⚠") || String(val).startsWith("✗");
                return (
                  <span key={d.candidate_id} className="text-xs font-medium text-center"
                    style={{ color: isPositive ? "#10B981" : isNegative ? "#F43F5E" : "var(--text-secondary)" }}>
                    {String(val)}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Dimension score bars */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4">10-Dimension Scorecard Comparison</h3>
        <div className="space-y-4">
          {dims.map(({ label, key }) => {
            const best = Math.max(...details.map((d) => d.scorecard[key]));
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs" style={{ color: "var(--text-secondary)" }}>{label}</span>
                  <div className="flex gap-4">
                    {details.map((d, i) => (
                      <span key={d.candidate_id} className="text-xs font-bold w-10 text-right"
                        style={{ color: d.scorecard[key] === best ? PALETTE[i] : "var(--text-muted)" }}>
                        {d.scorecard[key].toFixed(0)}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex gap-1">
                  {details.map((d, i) => (
                    <div key={d.candidate_id} className="flex-1">
                      <div className="score-bar">
                        <div
                          className="score-bar-fill"
                          style={{
                            width: `${d.scorecard[key]}%`,
                            background: PALETTE[i],
                            opacity: d.scorecard[key] === best ? 1 : 0.45,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strengths comparison */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Key Strengths</h3>
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${details.length}, 1fr)` }}>
          {details.map((d, i) => (
            <div key={d.candidate_id}>
              <p className="text-xs font-semibold mb-2" style={{ color: PALETTE[i] }}>
                {d.intelligence.name}
              </p>
              <ul className="space-y-1.5">
                {d.explainability.key_strengths.slice(0, 4).map((s, si) => (
                  <li key={si} className="flex items-start gap-1.5 text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    <CheckCircle size={10} className="shrink-0 mt-0.5" style={{ color: "#10B981" }} />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Risk comparison */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Risk Overview</h3>
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${details.length}, 1fr)` }}>
          {details.map((d, i) => {
            const rr = d.risk_radar;
            return (
              <div key={d.candidate_id}>
                <p className="text-xs font-semibold mb-2" style={{ color: PALETTE[i] }}>
                  {d.intelligence.name}
                </p>
                <div className="space-y-1">
                  {[
                    { name: "Technical", dim: rr.technical_risk },
                    { name: "Retention", dim: rr.retention_risk },
                    { name: "Adaptation", dim: rr.adaptation_risk },
                  ].map(({ name, dim }) => (
                    <div key={name} className="flex items-center justify-between">
                      <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>{name}</span>
                      <span className="text-[10px] font-medium" style={{ color: riskColor(dim.risk_level) }}>
                        {dim.risk_level}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Interview focus */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Interview Focus Areas</h3>
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${details.length}, 1fr)` }}>
          {details.map((d, i) => (
            <div key={d.candidate_id}>
              <p className="text-xs font-semibold mb-2" style={{ color: PALETTE[i] }}>{d.intelligence.name}</p>
              <ul className="space-y-1.5">
                {d.explainability.interview_focus_areas.slice(0, 3).map((q, qi) => (
                  <li key={qi} className="text-[11px] flex gap-1.5" style={{ color: "var(--text-secondary)" }}>
                    <span style={{ color: "var(--primary)" }}>Q{qi + 1}</span>
                    <span className="line-clamp-2">{q}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Compare Page ─────────────────────────────────────────────────────────────

export default function ComparePage() {
  const [topCandidates, setTopCandidates] = useState<CandidateListItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [compareDetails, setCompareDetails] = useState<CandidateDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTopForCompare(40)
      .then((r) => setTopCandidates(r.items))
      .catch((e) => setError(e.message))
      .finally(() => setListLoading(false));
  }, []);

  const handleSelect = (id: string) => {
    setSelectedIds((prev) => [...prev, id]);
  };

  const handleRemove = (id: string) => {
    setSelectedIds((prev) => prev.filter((x) => x !== id));
    setCompareDetails((prev) => prev.filter((d) => d.candidate_id !== id));
  };

  const runCompare = async () => {
    if (selectedIds.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.compareCandidates(selectedIds);
      setCompareDetails(result.candidates);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <ArrowLeftRight size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Compare Candidates</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Side-by-side multi-dimensional analysis of up to 5 candidates.
        </p>
      </div>

      {/* Picker */}
      {listLoading ? (
        <div className="card p-5 animate-pulse mb-6" style={{ height: 200, background: "var(--surface-2)" }} />
      ) : (
        <div className="mb-6">
          <CandidatePicker
            candidates={topCandidates}
            selected={selectedIds}
            onSelect={handleSelect}
            onRemove={handleRemove}
            maxSelect={5}
          />
        </div>
      )}

      {/* Compare button */}
      {selectedIds.length >= 2 && (
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={runCompare}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-50"
            style={{ background: "var(--primary)", border: "1px solid rgba(99,102,241,0.4)" }}
          >
            <ArrowLeftRight size={15} />
            {loading ? "Loading comparison..." : `Compare ${selectedIds.length} Candidates`}
          </button>
          {selectedIds.length < 2 && (
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>Select at least 2 candidates</p>
          )}
        </div>
      )}

      {selectedIds.length < 2 && !listLoading && (
        <div className="card p-8 text-center animate-fade-in-up">
          <ArrowLeftRight size={40} className="mx-auto mb-3" style={{ color: "var(--primary)", opacity: 0.5 }} />
          <p className="text-sm text-white mb-1">Select 2–5 candidates above to compare</p>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            Showing top 40 candidates. Use search to filter by name or title.
          </p>
        </div>
      )}

      {error && (
        <div className="card p-4 mb-6" style={{ borderColor: "rgba(244,63,94,0.3)" }}>
          <p className="text-xs" style={{ color: "var(--danger)" }}>{error}</p>
        </div>
      )}

      {/* Results */}
      {compareDetails.length >= 2 && (
        <div className="animate-fade-in-up">
          <ComparisonGrid details={compareDetails} />
        </div>
      )}
    </div>
  );
}
