"""
AI Pipeline Orchestrator — runs all 10 modules in correct dependency order
and stores results in SQLite for fast retrieval at ranking time.

This is the OFFLINE pre-computation step.
Run once with: python precompute.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Iterator

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import CandidateAnalysis, RoleDNA
from ai.candidate_intelligence.engine import extract_candidate_intelligence
from ai.evidence_validation.engine import build_evidence_report
from ai.scorecard.engine import build_scorecard
from ai.risk_radar.engine import build_risk_radar
from ai.recruitability.engine import build_recruitability_index
from ai.opportunity_cost.engine import build_opportunity_cost
from ai.explainability.engine import build_explainability_report, build_one_line_reasoning


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS candidate_scores (
    candidate_id TEXT PRIMARY KEY,
    final_score REAL NOT NULL,
    technical_fit REAL,
    role_fit REAL,
    domain_expertise REAL,
    career_momentum REAL,
    leadership REAL,
    communication REAL,
    adaptability REAL,
    cultural_fit REAL,
    learning_potential REAL,
    evidence_strength REAL,
    is_honeypot INTEGER DEFAULT 0,
    honeypot_score REAL DEFAULT 0.0,
    honeypot_flags TEXT DEFAULT '[]',
    is_disqualified INTEGER DEFAULT 0,
    disqualification_reason TEXT DEFAULT '',
    overall_alignment REAL,
    technical_alignment REAL,
    domain_alignment REAL,
    semantic_similarity REAL,
    risk_overall REAL,
    recruitability_tier TEXT,
    recruitability_score REAL,
    opportunity_cost_level TEXT,
    opportunity_cost_score REAL,
    one_line_reasoning TEXT,
    full_analysis_json TEXT,
    processed_at REAL
);

CREATE INDEX IF NOT EXISTS idx_final_score ON candidate_scores(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_honeypot ON candidate_scores(is_honeypot);
"""


def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database with schema."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(DB_SCHEMA)
    conn.commit()
    return conn


def iter_candidates(jsonl_path: str, limit: int = None) -> Iterator[dict]:
    """Stream candidates from JSONL file."""
    count = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
            count += 1
            if limit and count >= limit:
                break


def _to_json_safe(obj) -> str:
    """Convert dataclass to JSON-safe dict."""
    if hasattr(obj, "__dict__"):
        d = {}
        for k, v in obj.__dict__.items():
            if hasattr(v, "__dict__"):
                d[k] = _to_json_safe(v)
            elif isinstance(v, list):
                d[k] = [_to_json_safe(i) if hasattr(i, "__dict__") else i for i in v]
            elif hasattr(v, "value"):
                d[k] = v.value
            else:
                d[k] = v
        return d
    elif hasattr(obj, "value"):
        return obj.value
    return obj


def process_single_candidate(
    raw: dict[str, Any],
    role_dna: RoleDNA,
    alignment_scores_map: dict = None,  # pre-computed semantic scores
) -> CandidateAnalysis:
    """Run the full AI pipeline for one candidate."""
    analysis = CandidateAnalysis(candidate_id=raw["candidate_id"])
    signals = raw.get("redrob_signals", {})

    # Module 1 (Role DNA already done)
    # Module 2: Candidate Intelligence
    analysis.intelligence = extract_candidate_intelligence(raw)

    # Module 3: Semantic Alignment (from precomputed if available)
    if alignment_scores_map and raw["candidate_id"] in alignment_scores_map:
        analysis.alignment = alignment_scores_map[raw["candidate_id"]]
    else:
        # Fallback: compute inline (slow)
        from ai.semantic_alignment.engine import compute_semantic_alignment
        analysis.alignment = compute_semantic_alignment(analysis.intelligence)

    # Module 4: Evidence Validation
    analysis.evidence = build_evidence_report(analysis.intelligence, raw, role_dna)

    # Module 5: Scorecard
    analysis.scorecard = build_scorecard(
        analysis.intelligence, analysis.alignment,
        analysis.evidence, signals, role_dna
    )
    analysis.final_score = analysis.scorecard.final_score

    # Module 6: Risk Radar
    analysis.risk_radar = build_risk_radar(
        analysis.intelligence, analysis.alignment,
        analysis.evidence, analysis.scorecard, signals
    )

    # Module 7: Recruitability
    analysis.recruitability = build_recruitability_index(
        analysis.intelligence, analysis.scorecard
    )

    # Module 8: Opportunity Cost
    analysis.opportunity_cost = build_opportunity_cost(
        analysis.intelligence, analysis.recruitability, analysis.scorecard
    )

    # Module 10: Explainability (rank assigned later, placeholder 0)
    analysis.explainability = build_explainability_report(
        analysis.intelligence, analysis.alignment, analysis.evidence,
        analysis.scorecard, analysis.risk_radar, analysis.recruitability,
        analysis.opportunity_cost, role_dna, signals, rank=0
    )

    return analysis


def save_analysis_to_db(conn: sqlite3.Connection, analysis: CandidateAnalysis) -> None:
    """Store analysis result in SQLite."""
    sc = analysis.scorecard
    al = analysis.alignment
    ri = analysis.risk_radar
    re = analysis.recruitability
    oc = analysis.opportunity_cost
    ev = analysis.evidence
    ex = analysis.explainability

    full_json = json.dumps(_to_json_safe(analysis), ensure_ascii=False)

    conn.execute(
        """INSERT OR REPLACE INTO candidate_scores VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )""",
        (
            analysis.candidate_id,
            float(analysis.final_score),
            float(sc.technical_fit) if sc else 0.0,
            float(sc.role_fit) if sc else 0.0,
            float(sc.domain_expertise) if sc else 0.0,
            float(sc.career_momentum) if sc else 0.0,
            float(sc.leadership) if sc else 0.0,
            float(sc.communication) if sc else 0.0,
            float(sc.adaptability) if sc else 0.0,
            float(sc.cultural_fit) if sc else 0.0,
            float(sc.learning_potential) if sc else 0.0,
            float(sc.evidence_strength) if sc else 0.0,
            1 if (ev and ev.is_honeypot) else 0,
            float(ev.honeypot_score) if ev else 0.0,
            json.dumps(ev.honeypot_flags) if ev else "[]",
            1 if (sc and sc.is_disqualified) else 0,
            (sc.disqualification_reason if sc else ""),
            float(al.overall_alignment) if al else 0.0,
            float(al.technical_alignment) if al else 0.0,
            float(al.domain_alignment) if al else 0.0,
            float(al.semantic_similarity) if al else 0.0,
            float(ri.overall_risk.risk_score) if ri else 50.0,
            (re.tier.value if re else "Moderate"),
            float(re.overall_score) if re else 0.5,
            (oc.level.value if oc else "Medium"),
            float(oc.overall_score) if oc else 0.5,
            (ex.one_line_reasoning if ex else ""),
            full_json,
            time.time(),
        )
    )


def run_pipeline(
    jsonl_path: str,
    db_path: str,
    role_dna: RoleDNA,
    use_semantic: bool = True,
    batch_size: int = 1000,
    limit: int = None,
) -> dict:
    """
    Main pipeline: process all candidates and store to SQLite.
    
    Phase 1: Extract candidate intelligence for all candidates
    Phase 2 (optional): Batch compute semantic embeddings
    Phase 3: Score, evaluate, and store all candidates
    """
    print(f"\n{'='*60}")
    print("HIRING INTELLIGENCE ENGINE — Pre-computation Pipeline")
    print(f"{'='*60}")
    print(f"Input: {jsonl_path}")
    print(f"Output: {db_path}")
    print(f"Semantic alignment: {'enabled' if use_semantic else 'disabled'}")

    conn = init_database(db_path)
    start_time = time.time()

    # --- Phase 1: Load all candidates ---
    print("\n[Phase 1] Loading candidate profiles...")
    all_raw = list(iter_candidates(jsonl_path, limit=limit))
    total = len(all_raw)
    print(f"Loaded {total:,} candidates in {time.time()-start_time:.1f}s")

    # --- Phase 2: Extract intelligence for all ---
    print("\n[Phase 2] Extracting candidate intelligence...")
    t2 = time.time()
    all_intelligence = []
    for i, raw in enumerate(all_raw):
        intel = extract_candidate_intelligence(raw)
        all_intelligence.append(intel)
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i+1:,}/{total:,}")
    print(f"Intelligence extraction: {time.time()-t2:.1f}s")

    # --- Phase 3: Semantic alignment (batch) ---
    alignment_map = {}
    if use_semantic:
        print("\n[Phase 3] Computing semantic alignments (batch)...")
        t3 = time.time()
        from ai.semantic_alignment.engine import batch_compute_embeddings
        alignments = batch_compute_embeddings(all_intelligence, batch_size=256)
        for al in alignments:
            alignment_map[al.candidate_id] = al
        print(f"Semantic alignment: {time.time()-t3:.1f}s")

    # --- Phase 4: Score, validate, store ---
    print("\n[Phase 4] Running full AI pipeline and storing results...")
    t4 = time.time()
    honeypot_count = 0

    conn.execute("BEGIN TRANSACTION")
    for i, (raw, intel) in enumerate(zip(all_raw, all_intelligence)):
        try:
            signals = raw.get("redrob_signals", {})
            alignment = alignment_map.get(intel.candidate_id)

            if alignment is None:
                from ai.semantic_alignment.engine import compute_semantic_alignment
                alignment = compute_semantic_alignment(intel)

            from ai.evidence_validation.engine import build_evidence_report
            evidence = build_evidence_report(intel, raw, role_dna)

            scorecard = build_scorecard(intel, alignment, evidence, signals, role_dna)
            risk = build_risk_radar(intel, alignment, evidence, scorecard, signals)
            recruitability = build_recruitability_index(intel, scorecard)
            opportunity_cost = build_opportunity_cost(intel, recruitability, scorecard)
            explainability = build_explainability_report(
                intel, alignment, evidence, scorecard, risk,
                recruitability, opportunity_cost, role_dna, signals, rank=0
            )

            analysis = CandidateAnalysis(
                candidate_id=intel.candidate_id,
                intelligence=intel,
                alignment=alignment,
                evidence=evidence,
                scorecard=scorecard,
                risk_radar=risk,
                recruitability=recruitability,
                opportunity_cost=opportunity_cost,
                explainability=explainability,
                final_score=scorecard.final_score,
            )

            save_analysis_to_db(conn, analysis)

            if evidence.is_honeypot:
                honeypot_count += 1

        except Exception as e:
            print(f"  [ERROR] {raw.get('candidate_id', '?')}: {e}")

        if (i + 1) % batch_size == 0:
            conn.execute("COMMIT")
            conn.execute("BEGIN TRANSACTION")
            elapsed = time.time() - t4
            rate = (i + 1) / elapsed
            eta = (total - i - 1) / rate
            print(f"  {i+1:,}/{total:,} | {rate:.0f}/s | ETA {eta:.0f}s")

    conn.execute("COMMIT")
    conn.close()

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Pipeline complete in {elapsed:.1f}s")
    print(f"Processed: {total:,} candidates")
    print(f"Honeypots detected: {honeypot_count} ({honeypot_count/total*100:.1f}%)")
    print(f"Database: {db_path}")
    print(f"{'='*60}\n")

    return {
        "total": total,
        "honeypots": honeypot_count,
        "elapsed_seconds": elapsed,
        "db_path": db_path,
    }
