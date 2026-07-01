"use client";

import { Users, BarChart3, TrendingUp, Target } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Deep-dive into hiring pool composition and scoring methodology.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          {
            icon: Users,
            title: "Scoring Methodology",
            description: "Final score formula: Technical Fit (28%) + Role Fit (18%) + Domain Expertise (10%) + Career Momentum (8%) + Behavioral Composite (18%) + Cultural Fit (5%) + Leadership (5%) + Adaptability (4%) + Learning Potential (3%) + Evidence Strength (1%)",
            color: "var(--primary)",
          },
          {
            icon: Target,
            title: "Anti-Trap Signals",
            description: "JD explicitly flags: Marketing/HR titles with AI keywords (trap), services-firm-only careers, pure researchers without production deployment, keyword stuffers with no depth. Our scoring penalizes all of these.",
            color: "var(--warning)",
          },
          {
            icon: TrendingUp,
            title: "NDCG@10 Optimization",
            description: "Top 10 positions carry 50% of scoring weight. Our pipeline uses high-weight signals (title alignment, production ML evidence, product company ratio) to ensure the first 10 positions are genuinely strong fits.",
            color: "var(--success)",
          },
          {
            icon: BarChart3,
            title: "Honeypot Defense",
            description: "~80 honeypot candidates planted. Detection via consistency math: expert × 10 skills × 0 months = impossible. Career duration mismatch. These receive a 0.05× score multiplier, effectively de-ranking them to the bottom.",
            color: "var(--danger)",
          },
        ].map(({ icon: Icon, title, description, color }) => (
          <div key={title} className="card p-6">
            <div className="flex items-center gap-2 mb-3">
              <Icon size={16} style={{ color }} />
              <h3 className="text-sm font-semibold text-white">{title}</h3>
            </div>
            <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
