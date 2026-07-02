"use client";

import { useEffect, useState } from "react";
import { api, SimulationPreset, SimulationResult } from "@/lib/api/client";
import { Clock, Play, TrendingUp, TrendingDown, ArrowUpDown, AlertTriangle, Minus } from "lucide-react";

// ─── Delta Badge ──────────────────────────────────────────────────────────────

function DeltaBadge({ delta }: { delta: number }) {
  if (Math.abs(delta) < 0.005) {
    return (
      <span className="flex items-center gap-1 text-[10px] font-medium" style={{ color: "var(--text-muted)" }}>
        <Minus size={10} /> No change
      </span>
    );
  }
  const positive = delta > 0;
  return (
    <span
      className="flex items-center gap-1 text-[10px] font-medium"
      style={{ color: positive ? "#10B981" : "#F43F5E" }}
    >
      {positive ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
      {positive ? "+" : ""}{(delta * 100).toFixed(1)}%
    </span>
  );
}

// ─── Result Row ───────────────────────────────────────────────────────────────

function ResultRow({ r, index }: { r: SimulationResult; index: number }) {
  const scorePercent = Math.round(r.simulated_score * 100);
  const scoreColor = scorePercent >= 70 ? "#10B981" : scorePercent >= 50 ? "#F59E0B" : "#F43F5E";
  return (
    <div className="flex items-center gap-4 p-3 rounded-lg hover:bg-white/5 transition-colors">
      <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
        style={{ background: "rgba(99,102,241,0.25)" }}>
        #{r.simulated_rank}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{r.name || r.candidate_id}</p>
        <p className="text-xs truncate" style={{ color: "var(--text-muted)" }}>
          {r.current_title} · {r.years_of_experience.toFixed(1)}y exp
        </p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-sm font-bold" style={{ color: scoreColor }}>{scorePercent}%</p>
        <DeltaBadge delta={r.score_delta} />
      </div>
    </div>
  );
}

// ─── Time Machine Page ────────────────────────────────────────────────────────

const PRESET_COLORS: Record<string, string> = {
  technical_heavy: "#6366F1",
  product_company_only: "#10B981",
  github_required: "#38BDF8",
  leadership_focused: "#F59E0B",
};

export default function TimeMachinePage() {
  const [presets, setPresets] = useState<SimulationPreset[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<SimulationResult[] | null>(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [backendAvailable, setBackendAvailable] = useState(true);

  useEffect(() => {
    api.getSimulationPresets()
      .then(setPresets)
      .catch(() => {
        setBackendAvailable(false);
        // Show fallback presets
        setPresets([
          {
            id: "technical_heavy",
            name: "Technical Skills First",
            description: "Weight technical skills at 50% instead of 28%. Surfaces candidates with strongest AI depth.",
            params: {},
          },
          {
            id: "product_company_only",
            name: "Product Company Only",
            description: "Exclude all services-firm candidates. Strict cultural fit requirement.",
            params: {},
          },
          {
            id: "github_required",
            name: "GitHub Activity Required",
            description: "Require active GitHub presence (score ≥ 20). Surfaces open-source engineers.",
            params: {},
          },
          {
            id: "leadership_focused",
            name: "Leadership Focused",
            description: "Prioritize mentorship capacity — leadership weight rises from 5% to 30%.",
            params: {},
          },
        ]);
      });
  }, []);

  const run = async () => {
    if (!selected) return;
    setRunning(true);
    setResults(null);
    setError(null);

    if (!backendAvailable) {
      // Simulated result
      setTimeout(() => {
        setRunning(false);
        const preset = presets.find((p) => p.id === selected);
        setError(`Backend not available. If precompute.py has been run, the simulation would show re-ranked results for: "${preset?.name}". Start the backend with: uvicorn backend.main:app --reload`);
      }, 1500);
      return;
    }

    try {
      const result = await api.runSimulation(selected);
      setResults(result.results);
      setTotal(result.total);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Clock size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Time Machine</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Simulate alternative hiring scenarios — what if we changed our scoring priorities?
        </p>
      </div>

      {!backendAvailable && (
        <div className="card p-4 mb-6 animate-fade-in-up" style={{ borderColor: "rgba(245,158,11,0.3)", background: "rgba(245,158,11,0.05)" }}>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle size={13} style={{ color: "var(--warning)" }} />
            <span className="text-xs font-semibold" style={{ color: "var(--warning)" }}>Backend Offline</span>
          </div>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Showing scenario presets. Start the backend for live simulations:
            <code className="ml-1 px-1 py-0.5 rounded text-[10px]" style={{ background: "var(--surface-2)" }}>
              uvicorn backend.main:app --reload
            </code>
          </p>
        </div>
      )}

      {/* Scenario presets */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {presets.map((p) => {
          const color = PRESET_COLORS[p.id] || "#6366F1";
          return (
            <div
              key={p.id}
              onClick={() => setSelected(p.id)}
              className={`card p-5 cursor-pointer transition-all duration-200 ${selected === p.id ? "" : "hover:border-white/20"}`}
              style={selected === p.id ? { outline: `2px solid ${color}`, borderColor: `${color}60` } : {}}
            >
              <div className="flex items-start gap-3">
                <div className="w-3 h-3 rounded-full mt-1 shrink-0" style={{ background: color }} />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white mb-1">{p.name}</p>
                  <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{p.description}</p>
                </div>
                {selected === p.id && (
                  <div className="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                    style={{ background: color }}>
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Run button */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={run}
          disabled={!selected || running}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-40"
          style={{ background: "var(--primary)", border: "1px solid rgba(99,102,241,0.4)" }}
        >
          <Play size={14} />
          {running ? "Simulating..." : "Run Simulation"}
        </button>
      </div>

      {/* Error / offline message */}
      {error && (
        <div className="card p-4 mb-6 animate-fade-in-up" style={{ borderColor: "rgba(245,158,11,0.3)" }}>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{error}</p>
        </div>
      )}

      {/* Results */}
      {results && results.length > 0 && (
        <div className="animate-fade-in-up space-y-4">
          <div className="card p-5">
            <div className="flex items-center gap-2 mb-1">
              <ArrowUpDown size={14} style={{ color: "var(--primary)" }} />
              <span className="text-sm font-semibold text-white">
                Re-ranked Results ({total} candidates affected)
              </span>
            </div>
            <p className="text-xs mb-4" style={{ color: "var(--text-muted)" }}>
              Showing top {results.length} candidates under the "{presets.find((p) => p.id === selected)?.name}" scenario.
              Green delta = moved up, red = moved down.
            </p>
            <div className="space-y-1">
              {results.map((r, i) => (
                <ResultRow key={r.candidate_id} r={r} index={i} />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* How it works */}
      <div className="card p-5 mt-6 animate-fade-in-up" style={{ background: "rgba(99,102,241,0.05)", borderColor: "rgba(99,102,241,0.2)" }}>
        <h3 className="text-sm font-semibold text-white mb-2">How it works</h3>
        <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
          The Time Machine re-applies the scoring formula with modified weights or filters across all precomputed candidate profiles in SQLite.
          Since all 10 dimension scores are already computed and stored, re-ranking is instant — no AI inference needed.
          This enables exploring "what-if" hiring scenarios without reprocessing data.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
          {[
            { label: "Precomputed profiles", value: "100K+" },
            { label: "Re-rank latency", value: "<1s" },
            { label: "Network required", value: "None" },
            { label: "Scenarios available", value: `${presets.length}` },
          ].map(({ label, value }) => (
            <div key={label} className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <p className="text-xs font-bold text-white">{value}</p>
              <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
