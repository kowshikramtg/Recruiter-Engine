"use client";

import { useEffect, useState } from "react";
import { Settings, Database, Server, CheckCircle, XCircle, AlertTriangle, Copy, ExternalLink } from "lucide-react";

interface HealthStatus {
  status: string;
  database: string;
  version: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      {ok ? (
        <CheckCircle size={13} style={{ color: "var(--success)" }} />
      ) : (
        <XCircle size={13} style={{ color: "var(--danger)" }} />
      )}
      <span className="text-xs font-medium" style={{ color: ok ? "var(--success)" : "var(--danger)" }}>
        {label}
      </span>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      className="text-[10px] px-1.5 py-0.5 rounded transition-colors"
      style={{ color: copied ? "var(--success)" : "var(--text-muted)", background: "var(--surface-2)" }}
    >
      {copied ? "Copied!" : <Copy size={10} />}
    </button>
  );
}

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [checking, setChecking] = useState(true);
  const [backendUrl, setBackendUrl] = useState(API_BASE);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "offline", database: "unreachable", version: "—" }))
      .finally(() => setChecking(false));
  }, []);

  const isBackendUp = health?.status === "healthy" || health?.status === "degraded";
  const isDbReady = health?.database === "ready";

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Settings size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Settings</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          System configuration, connection status, and developer tools.
        </p>
      </div>

      {/* System Status */}
      <div className="card p-5 mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-4">
          <Server size={14} style={{ color: "var(--primary)" }} />
          <h2 className="text-sm font-semibold text-white">System Status</h2>
        </div>
        {checking ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-4 rounded animate-pulse" style={{ background: "var(--surface-2)", width: `${60 + i * 10}%` }} />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Backend API</span>
              <StatusBadge ok={isBackendUp} label={isBackendUp ? "Online" : "Offline"} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Precomputed Database</span>
              <StatusBadge ok={isDbReady} label={isDbReady ? "Ready" : "Missing — run precompute.py"} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>API Version</span>
              <span className="text-xs font-medium text-white">{health?.version || "—"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>API Endpoint</span>
              <div className="flex items-center gap-1">
                <code className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--surface-2)", color: "var(--primary-light)" }}>
                  {API_BASE}
                </code>
                <CopyButton text={API_BASE} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Database info */}
      <div className="card p-5 mb-6 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
        <div className="flex items-center gap-2 mb-4">
          <Database size={14} style={{ color: "var(--info)" }} />
          <h2 className="text-sm font-semibold text-white">Database & Pipeline</h2>
        </div>
        <div className="space-y-4">
          <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
            <p className="text-xs font-semibold text-white mb-1">Pre-computation (run once)</p>
            <div className="flex items-center gap-2 mb-1">
              <code className="text-[10px] px-2 py-0.5 rounded flex-1" style={{ background: "rgba(0,0,0,0.3)", color: "var(--success)" }}>
                python precompute.py --candidates ./Dataset/...candidates.jsonl
              </code>
              <CopyButton text="python precompute.py" />
            </div>
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              Runs all 10 AI modules on 100K candidates. Stores results in SQLite. Requires ~2-5 min.
            </p>
          </div>
          <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
            <p className="text-xs font-semibold text-white mb-1">Competition Submission</p>
            <div className="flex items-center gap-2 mb-1">
              <code className="text-[10px] px-2 py-0.5 rounded flex-1" style={{ background: "rgba(0,0,0,0.3)", color: "var(--primary-light)" }}>
                python rank.py --candidates ./candidates.jsonl --out submission.csv
              </code>
              <CopyButton text="python rank.py --candidates ./candidates.jsonl --out submission.csv" />
            </div>
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              No network. CPU only. Reads precomputed DB. Outputs top 100 ranked candidates.
            </p>
          </div>
          <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
            <p className="text-xs font-semibold text-white mb-1">Backend API</p>
            <div className="flex items-center gap-2 mb-1">
              <code className="text-[10px] px-2 py-0.5 rounded flex-1" style={{ background: "rgba(0,0,0,0.3)", color: "var(--info)" }}>
                uvicorn backend.main:app --reload --port 8000
              </code>
              <CopyButton text="uvicorn backend.main:app --reload --port 8000" />
            </div>
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              Serves this dashboard. Reads from precomputed SQLite. No AI inference at runtime.
            </p>
          </div>
          <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
            <p className="text-xs font-semibold text-white mb-1">Frontend</p>
            <div className="flex items-center gap-2 mb-1">
              <code className="text-[10px] px-2 py-0.5 rounded flex-1" style={{ background: "rgba(0,0,0,0.3)", color: "#F97316" }}>
                cd frontend && npm run dev
              </code>
              <CopyButton text="cd frontend && npm run dev" />
            </div>
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              Next.js development server. Connects to backend on port 8000.
            </p>
          </div>
        </div>
      </div>

      {/* Competition constraints */}
      <div className="card p-5 mb-6 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
        <h2 className="text-sm font-semibold text-white mb-4">Competition Compliance</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { label: "Network at ranking time", value: "None", ok: true, desc: "rank.py makes zero network calls" },
            { label: "GPU usage", value: "None", ok: true, desc: "CPU-only pipeline" },
            { label: "Max runtime", value: "< 5 minutes", ok: true, desc: "rank.py reads precomputed DB in O(1)" },
            { label: "Max RAM", value: "< 16GB", ok: true, desc: "SQLite + lightweight Python" },
            { label: "Embedding model", value: "22MB local", ok: true, desc: "all-MiniLM-L6-v2 (offline only)" },
            { label: "Output format", value: "CSV (100 rows)", ok: true, desc: "candidate_id, rank, score, reasoning" },
          ].map(({ label, value, ok, desc }) => (
            <div key={label} className="flex items-start gap-3 p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              {ok ? (
                <CheckCircle size={13} className="mt-0.5 shrink-0" style={{ color: "var(--success)" }} />
              ) : (
                <AlertTriangle size={13} className="mt-0.5 shrink-0" style={{ color: "var(--warning)" }} />
              )}
              <div>
                <p className="text-xs font-medium text-white">{label}</p>
                <p className="text-xs font-bold" style={{ color: ok ? "var(--success)" : "var(--warning)" }}>{value}</p>
                <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* API Links */}
      <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
        <h2 className="text-sm font-semibold text-white mb-4">API Documentation</h2>
        <div className="space-y-2">
          {[
            { label: "Swagger UI", href: `${API_BASE}/docs`, desc: "Interactive API explorer" },
            { label: "OpenAPI Schema", href: `${API_BASE}/openapi.json`, desc: "JSON schema for all endpoints" },
            { label: "Health Check", href: `${API_BASE}/health`, desc: "Backend + database status" },
            { label: "Top Candidates", href: `${API_BASE}/api/v1/candidates?page=1&page_size=10`, desc: "First 10 ranked candidates" },
            { label: "Dashboard Stats", href: `${API_BASE}/api/v1/dashboard/stats`, desc: "Summary statistics" },
          ].map(({ label, href, desc }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-colors"
            >
              <div>
                <p className="text-xs font-medium text-white">{label}</p>
                <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{desc}</p>
              </div>
              <ExternalLink size={12} style={{ color: "var(--primary-light)" }} />
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
