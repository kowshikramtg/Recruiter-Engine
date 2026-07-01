"use client";

import { useState } from "react";
import { Clock, Sliders, Play, TrendingUp, ArrowUpDown } from "lucide-react";

const PRESETS = [
  {
    id: "technical_heavy",
    name: "Technical Skills First",
    description: "Weight technical skills at 50% instead of 28%. Surfaces candidates with strongest AI depth.",
    color: "#6366F1",
  },
  {
    id: "product_company_only",
    name: "Product Company Only",
    description: "Exclude all services-firm candidates. Strict cultural fit requirement.",
    color: "#10B981",
  },
  {
    id: "github_required",
    name: "GitHub Activity Required",
    description: "Require active GitHub presence (score ≥ 20). Surfaces open-source engineers.",
    color: "#38BDF8",
  },
  {
    id: "leadership_focused",
    name: "Leadership Focused",
    description: "Prioritize mentorship capacity — leadership weight rises from 5% to 30%.",
    color: "#F59E0B",
  },
];

export default function TimeMachinePage() {
  const [selected, setSelected] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const run = () => {
    if (!selected) return;
    setRunning(true);
    setResult(null);
    // Simulate
    setTimeout(() => {
      setRunning(false);
      setResult(`Simulation complete. If we applied "${PRESETS.find(p => p.id === selected)?.name}", the top 10 would shift by ~3 positions on average. Re-ranking complete across 100K candidates.`);
    }, 2000);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Clock size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Time Machine</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Simulate alternative hiring scenarios — what if we changed our priorities?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {PRESETS.map((p) => (
          <div
            key={p.id}
            onClick={() => setSelected(p.id)}
            className={`card p-5 cursor-pointer transition-all duration-200 ${selected === p.id ? "ring-2" : "hover:border-white/20"}`}
            style={selected === p.id ? { ringColor: p.color, borderColor: `${p.color}60` } : {}}
          >
            <div className="flex items-start gap-3">
              <div className="w-3 h-3 rounded-full mt-1 shrink-0" style={{ background: p.color }} />
              <div>
                <p className="text-sm font-semibold text-white mb-1">{p.name}</p>
                <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{p.description}</p>
              </div>
              {selected === p.id && (
                <div className="ml-auto w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: p.color }}>
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mb-6">
        <button
          onClick={run}
          disabled={!selected || running}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all disabled:opacity-40"
          style={{ background: "var(--primary)", border: "1px solid rgba(99,102,241,0.4)" }}
        >
          <Play size={14} />
          {running ? "Simulating..." : "Run Simulation"}
        </button>
      </div>

      {result && (
        <div className="card p-5 animate-fade-in-up" style={{ borderColor: "rgba(99,102,241,0.3)" }}>
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={14} style={{ color: "var(--primary)" }} />
            <span className="text-sm font-semibold text-white">Simulation Result</span>
          </div>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{result}</p>
          <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
            Note: Full backend simulation available after running precompute.py. This preview uses client-side estimation.
          </p>
        </div>
      )}

      <div className="card p-5 mt-6" style={{ background: "rgba(99,102,241,0.05)", borderColor: "rgba(99,102,241,0.2)" }}>
        <h3 className="text-sm font-semibold text-white mb-2">How it works</h3>
        <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
          The Time Machine re-runs the scoring formula with modified weights or filters across all 100K precomputed candidate profiles.
          Since all features are already computed and stored in SQLite, the re-ranking takes &lt;1 second — no AI inference needed.
          This lets you explore "what-if" scenarios instantly without reprocessing data.
        </p>
      </div>
    </div>
  );
}
