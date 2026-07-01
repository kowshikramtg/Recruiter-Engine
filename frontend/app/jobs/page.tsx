"use client";

import { useEffect, useState } from "react";
import { api, RoleDNA } from "@/lib/api/client";
import { Briefcase, CheckCircle, XCircle, Star, Target, Users, Clock, AlertTriangle } from "lucide-react";

export default function JobsPage() {
  const [dna, setDna] = useState<RoleDNA | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getCurrentJob()
      .then(setDna)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8"><div className="card p-8 animate-pulse" style={{ height: 300 }} /></div>;
  if (error || !dna) return (
    <div className="p-8"><div className="card p-8 text-center">
      <AlertTriangle size={32} className="mx-auto mb-3" style={{ color: "var(--warning)" }} />
      <p className="text-sm">{error || "Failed to load"}</p>
    </div></div>
  );

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Briefcase size={18} style={{ color: "var(--primary)" }} />
          <h1 className="text-3xl font-bold text-white">Role DNA</h1>
        </div>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Structured intelligence extracted from the job description — used by all AI modules.
        </p>
      </div>

      {/* Job header */}
      <div className="card p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">{dna.title}</h2>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{dna.company}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-white">{dna.experience_min_years}–{dna.experience_max_years} years</p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>experience required</p>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-4 flex-wrap">
          <span className="text-xs px-2 py-1 rounded-full capitalize" style={{ background: "rgba(99,102,241,0.15)", color: "var(--primary-light)", border: "1px solid rgba(99,102,241,0.3)" }}>
            {dna.seniority_level}
          </span>
          <span className="text-xs px-2 py-1 rounded-full" style={{ background: "var(--success-dim)", color: "var(--success)", border: "1px solid rgba(16,185,129,0.3)" }}>
            Notice ≤ {dna.notice_preference_days}d preferred
          </span>
          {dna.requires_production_experience && (
            <span className="text-xs px-2 py-1 rounded-full" style={{ background: "var(--warning-dim)", color: "var(--warning)", border: "1px solid rgba(245,158,11,0.3)" }}>
              Production ML Required
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Must-have skills */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <CheckCircle size={13} style={{ color: "var(--success)" }} /> Must-Have Skills
          </h3>
          <ul className="space-y-2">
            {dna.must_have_skills.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                <CheckCircle size={10} className="mt-0.5 shrink-0" style={{ color: "var(--success)" }} />{s}
              </li>
            ))}
          </ul>
        </div>

        {/* Preferred skills */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Star size={13} style={{ color: "var(--warning)" }} /> Preferred Skills
          </h3>
          <ul className="space-y-2">
            {dna.preferred_skills.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                <Star size={10} className="mt-0.5 shrink-0" style={{ color: "var(--warning)" }} />{s}
              </li>
            ))}
          </ul>
        </div>

        {/* Responsibilities */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Target size={13} style={{ color: "var(--primary)" }} /> Key Responsibilities
          </h3>
          <ul className="space-y-2">
            {dna.responsibilities.map((r, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--primary)" }}>→</span>{r}
              </li>
            ))}
          </ul>
        </div>

        {/* Success indicators */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "250ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <CheckCircle size={13} style={{ color: "var(--info)" }} /> Success Indicators
          </h3>
          <ul className="space-y-2">
            {dna.success_indicators.map((s, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--info)" }}>✓</span>{s}
              </li>
            ))}
          </ul>
        </div>

        {/* Hidden expectations */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "300ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <AlertTriangle size={13} style={{ color: "var(--warning)" }} /> Hidden Expectations
          </h3>
          <ul className="space-y-2">
            {dna.hidden_expectations.map((h, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--warning)" }}>⚡</span>{h}
              </li>
            ))}
          </ul>
        </div>

        {/* Technical competencies */}
        <div className="card p-5 animate-fade-in-up" style={{ animationDelay: "350ms" }}>
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Users size={13} style={{ color: "var(--success)" }} /> Technical Competencies
          </h3>
          <ul className="space-y-2">
            {dna.technical_competencies.map((t, i) => (
              <li key={i} className="text-xs flex gap-2" style={{ color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--success)" }}>•</span>{t}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Target titles */}
      <div className="card p-5 mt-6 animate-fade-in-up" style={{ animationDelay: "400ms" }}>
        <h3 className="text-sm font-semibold text-white mb-3">Target Titles</h3>
        <div className="flex flex-wrap gap-2">
          {dna.target_titles.slice(0, 15).map((t) => (
            <span key={t} className="text-xs px-2 py-1 rounded-full capitalize"
              style={{ background: "rgba(99,102,241,0.12)", color: "var(--primary-light)", border: "1px solid rgba(99,102,241,0.25)" }}>
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Trainable skills */}
      <div className="card p-5 mt-6 animate-fade-in-up" style={{ animationDelay: "450ms" }}>
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Clock size={13} style={{ color: "var(--info)" }} /> Trainable (Nice-to-Have)
        </h3>
        <div className="flex flex-wrap gap-2">
          {dna.trainable_skills.map((s) => (
            <span key={s} className="text-xs px-2 py-1 rounded-full"
              style={{ background: "var(--info-dim)", color: "var(--info)", border: "1px solid rgba(56,189,248,0.3)" }}>
              {s}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
