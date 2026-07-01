"use client";

import { Target, ArrowLeftRight } from "lucide-react";

export default function ComparePage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <ArrowLeftRight size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Compare Candidates</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Side-by-side comparison of candidates across all dimensions.
        </p>
      </div>
      <div className="card p-8 text-center">
        <Target size={48} className="mx-auto mb-4" style={{ color: "var(--primary)" }} />
        <p className="text-sm text-white mb-2">Select candidates from the list to compare</p>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          Navigate to <a href="/candidates" className="underline" style={{ color: "var(--primary-light)" }}>Candidates</a> and click any candidate to view their profile, then return here to compare.
        </p>
      </div>
    </div>
  );
}
