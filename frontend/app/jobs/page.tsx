"use client";

import { useEffect, useState } from "react";
import { api, RoleDNA } from "@/lib/api/client";
import {
  Briefcase, CheckCircle, XCircle, Target, Brain, Users,
  Clock, Shield, Star, Code, MessageSquare, TrendingUp, AlertTriangle
} from "lucide-react";

function SkillBadge({ skill, variant = "default" }: { skill: string; variant?: "must" | "preferred" | "trainable" | "default" }) {
  const styles: Record<string, React.CSSProperties> = {
    must: { background: "rgba(99,102,241,0.15)", color: "#818CF8", border: "1px solid rgba(99,102,241,0.35)" },
    preferred: { background: "rgba(16,185,129,0.12)", color: "#10B981", border: "1px solid rgba(16,185,129,0.3)" },
    trainable: { background: "rgba(245,158,11,0.12)", color: "#F59E0B", border: "1px solid rgba(245,158,11,0.3)" },
    default: { background: "rgba(100,116,139,0.12)", color: "#94A3B8", border: "1px solid rgba(100,116,139,0.2)" },
  };
  return (
    <span className="text-[11px] px-2.5 py-1 rounded-full font-medium inline-flex items-center gap-1" style={styles[variant]}>
      {skill}
    </span>
  );
}

function Section({ title, icon: Icon, color, children }: {
  title: string; icon: React.ElementType; color: string; children: React.ReactNode;
}) {
  return (
    <div className="card p-5 animate-fade-in-up">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${color}20` }}>
          <Icon size={14} style={{ color }} />
        </div>
        <h2 className="text-sm font-semibold text-white">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function ListItems({ items, icon: Icon, iconColor }: {
  items: string[];
  icon: React.ElementType;
  iconColor: string;
}) {
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
          <Icon size={11} className="mt-0.5 shrink-0" style={{ color: iconColor }} />
          {item}
        </li>
      ))}
    </ul>
  );
}

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

  if (loading) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="card p-5 animate-pulse" style={{ height: 140, background: "var(--surface-2)" }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !dna) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="card p-8 text-center">
          <AlertTriangle size={40} className="mx-auto mb-3" style={{ color: "var(--warning)" }} />
          <p className="text-sm text-white mb-1">Could not load Role DNA</p>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            {error || "Backend unavailable. Run uvicorn backend.main:app --reload"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-1">
          <Briefcase size={18} style={{ color: "var(--primary)" }} />
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--primary)" }}>
            Role DNA — Extracted Intelligence
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-1">{dna.title}</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {dna.company} · {dna.seniority_level} level · {dna.experience_min_years}–{dna.experience_max_years} years
        </p>
      </div>

      {/* Quick summary bar */}
      <div className="card p-4 mb-6 animate-fade-in-up" style={{ animationDelay: "50ms" }}>
        <div className="flex items-center gap-6 flex-wrap">
          <div className="flex items-center gap-2">
            <Clock size={13} style={{ color: "var(--primary)" }} />
            <span className="text-xs text-white font-medium">{dna.experience_min_years}–{dna.experience_max_years}y exp</span>
          </div>
          <div className="flex items-center gap-2">
            <Target size={13} style={{ color: "var(--success)" }} />
            <span className="text-xs text-white font-medium">≤{dna.notice_preference_days}d preferred notice (max {dna.notice_max_days}d)</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle size={13} style={{ color: "#10B981" }} />
            <span className="text-xs font-medium" style={{ color: "#10B981" }}>Production experience required</span>
          </div>
          <div className="flex items-center gap-2">
            <Users size={13} style={{ color: "#A78BFA" }} />
            <span className="text-xs font-medium" style={{ color: "#A78BFA" }}>Product company preferred</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Must-have skills */}
        <Section title="Must-Have Skills" icon={Shield} color="#F43F5E">
          <div className="flex flex-wrap gap-2">
            {dna.must_have_skills.map((s) => (
              <SkillBadge key={s} skill={s} variant="must" />
            ))}
          </div>
        </Section>

        {/* Preferred skills */}
        <Section title="Preferred Skills" icon={Star} color="#10B981">
          <div className="flex flex-wrap gap-2">
            {dna.preferred_skills.map((s) => (
              <SkillBadge key={s} skill={s} variant="preferred" />
            ))}
          </div>
        </Section>

        {/* Technical competencies */}
        <Section title="Technical Competencies" icon={Code} color="#6366F1">
          <ListItems
            items={dna.technical_competencies}
            icon={CheckCircle}
            iconColor="var(--primary-light)"
          />
        </Section>

        {/* Domain knowledge */}
        <Section title="Domain Knowledge" icon={Brain} color="#38BDF8">
          <ListItems
            items={dna.domain_knowledge}
            icon={CheckCircle}
            iconColor="var(--info)"
          />
          <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <p className="text-xs mb-2 font-medium" style={{ color: "var(--text-muted)" }}>Trainable (not blocking)</p>
            <div className="flex flex-wrap gap-2">
              {dna.trainable_skills.map((s) => (
                <SkillBadge key={s} skill={s} variant="trainable" />
              ))}
            </div>
          </div>
        </Section>

        {/* Responsibilities */}
        <Section title="Key Responsibilities" icon={Target} color="#F59E0B">
          <ListItems
            items={dna.responsibilities}
            icon={CheckCircle}
            iconColor="var(--warning)"
          />
        </Section>

        {/* Success indicators */}
        <Section title="Success Indicators" icon={TrendingUp} color="#A78BFA">
          <ListItems
            items={dna.success_indicators}
            icon={Star}
            iconColor="#A78BFA"
          />
        </Section>

        {/* Hidden expectations */}
        <Section title="Hidden Expectations" icon={Brain} color="#F97316">
          <p className="text-xs mb-3 leading-relaxed" style={{ color: "var(--text-muted)" }}>
            These are not stated explicitly in the JD but inferred from context and company culture signals.
          </p>
          <ListItems
            items={dna.hidden_expectations}
            icon={AlertTriangle}
            iconColor="#F97316"
          />
        </Section>

        {/* Cultural signals */}
        <div className="card p-5 animate-fade-in-up">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "rgba(56,189,248,0.15)" }}>
              <MessageSquare size={14} style={{ color: "var(--info)" }} />
            </div>
            <h2 className="text-sm font-semibold text-white">Culture & Communication</h2>
          </div>
          <div className="space-y-3">
            <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <p className="text-xs font-medium mb-1" style={{ color: "var(--info)" }}>Leadership Requirements</p>
              <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{dna.leadership_requirements}</p>
            </div>
            <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <p className="text-xs font-medium mb-1" style={{ color: "var(--info)" }}>Communication Expectations</p>
              <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{dna.communication_expectations}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Target titles */}
      <div className="card p-5 mt-6 animate-fade-in-up">
        <div className="flex items-center gap-2 mb-4">
          <Briefcase size={14} style={{ color: "var(--primary)" }} />
          <h2 className="text-sm font-semibold text-white">Target Candidate Titles</h2>
          <span className="text-xs ml-auto" style={{ color: "var(--text-muted)" }}>{dna.target_titles.length} titles tracked</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {dna.target_titles.slice(0, 20).map((t) => (
            <SkillBadge key={t} skill={t} variant="default" />
          ))}
        </div>
      </div>

      {/* Scoring note */}
      <div className="card p-4 mt-6 animate-fade-in-up" style={{ background: "rgba(99,102,241,0.05)", borderColor: "rgba(99,102,241,0.2)" }}>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          <span style={{ color: "var(--primary-light)" }}>How Role DNA is used: </span>
          This structured intelligence drives the scoring formula. Must-have skills map to Technical Fit (28% weight).
          Target titles drive Title Alignment. Hidden expectations inform the Explainability Engine.
          Services-firm-only background reduces score by 40%.
        </p>
      </div>
    </div>
  );
}
