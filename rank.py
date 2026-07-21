"""
rank.py — Competition submission script.

CONSTRAINTS (enforced by competition rules):
- No network calls (no OpenAI, Gemini, or any API)
- CPU only, no GPU
- Must complete in < 5 minutes
- Reads precomputed_features.db for O(1) score lookups
- Outputs submission.csv with exactly 100 ranked candidates

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv

Or with the precomputed DB explicitly:
    python rank.py --candidates ./candidates.jsonl --db ./ai/pipeline/precomputed_features.db --out ./submission.csv
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_precomputed_scores(db_path: str) -> dict[str, dict]:
    """
    Load all precomputed scores from SQLite.
    Returns dict: candidate_id -> score row.
    Fast: single SQL query, O(n) memory.
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"Precomputed features database not found: {db_path}\n"
            f"Run 'python precompute.py' first to generate it."
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT candidate_id, final_score, one_line_reasoning, "
        "       is_honeypot, honeypot_score, technical_fit, role_fit, "
        "       domain_expertise, career_momentum, recruitability_tier, "
        "       opportunity_cost_level, risk_overall "
        "FROM candidate_scores"
    ).fetchall()
    conn.close()
    return {row["candidate_id"]: dict(row) for row in rows}


def get_candidate_ids_from_jsonl(jsonl_path: str) -> list[str]:
    """Extract all candidate IDs from the candidates file."""
    ids = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                # Fast extraction without full JSON parse
                try:
                    idx = line.index('"candidate_id"')
                    start = line.index('"', idx + 14) + 1
                    end = line.index('"', start)
                    ids.append(line[start:end])
                except (ValueError, IndexError):
                    data = json.loads(line)
                    ids.append(data.get("candidate_id", ""))
    return [cid for cid in ids if cid]


def score_candidates_fallback(jsonl_path: str) -> list[tuple[str, float, str]]:
    """
    Fast fallback scoring if precomputed DB is unavailable.
    Uses rule-based scoring directly on JSONL. No LLM, no embeddings.
    Runs in < 3 minutes for 100K candidates.
    """
    from ai.role_dna.engine import (
        AI_CORE_SKILLS, SERVICES_FIRMS, TARGET_TITLES
    )

    results = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            cid = raw.get("candidate_id", "")
            if not cid:
                continue

            profile = raw.get("profile", {})
            signals = raw.get("redrob_signals", {})
            skills = raw.get("skills", [])
            career = raw.get("career_history", [])

            # Fast feature extraction
            yoe = float(profile.get("years_of_experience", 0))
            current_title = profile.get("current_title", "").lower()
            current_company = profile.get("current_company", "").lower()

            # AI skill count
            ai_count = sum(
                1 for s in skills
                if any(kw in s.get("name", "").lower() for kw in AI_CORE_SKILLS)
            )

            # Honeypot check
            expert_zero = sum(
                1 for s in skills
                if s.get("proficiency") in ("expert", "advanced") and int(s.get("duration_months", 0)) == 0
            )
            if expert_zero >= 3:
                results.append((cid, 0.01, "Profile consistency flags raised."))
                continue

            # Services firm check
            all_services = all(
                any(firm in c.get("company", "").lower() for firm in SERVICES_FIRMS)
                for c in career
            ) if career else False

            # Title alignment
            title_score = 1.0 if any(t in current_title for t in {"ai engineer", "ml engineer", "data scientist"}) else 0.0
            title_score = max(title_score, 0.4 if "engineer" in current_title or "scientist" in current_title else 0.0)

            # Behavioral
            rr = float(signals.get("recruiter_response_rate", 0))
            open_work = bool(signals.get("open_to_work_flag", False))
            github = float(signals.get("github_activity_score", -1))
            notice = int(signals.get("notice_period_days", 60))

            notice_score = 1.0 if notice <= 30 else (0.7 if notice <= 60 else (0.5 if notice <= 90 else 0.2))

            # Experience alignment
            exp_score = 1.0 if 5 <= yoe <= 9 else (0.75 if 3 <= yoe < 5 or 9 < yoe <= 12 else 0.3)

            # Final score (fast)
            score = (
                (ai_count / 10.0) * 0.35 +
                title_score * 0.20 +
                exp_score * 0.15 +
                rr * 0.10 +
                (max(github, 0) / 100.0) * 0.08 +
                (0.1 if open_work else 0.0) +
                notice_score * 0.07 +
                (float(signals.get("profile_completeness_score", 0)) / 100.0) * 0.05
            )

            if all_services:
                score *= 0.60

            reasoning = (
                f"{profile.get('current_title', '')} with {yoe:.1f}yrs; "
                f"{ai_count} AI skills; response rate {rr:.0%}."
            )
            results.append((cid, min(score, 1.0), reasoning))

    return results


def generate_submission(
    jsonl_path: str,
    db_path: str,
    out_path: str,
) -> None:
    """
    Core ranking logic — load precomputed scores, rank top 100, write CSV.
    Must complete in < 5 minutes with no network.
    """
    t_start = time.time()
    print(f"[rank.py] Starting ranking...")

    use_precomputed = Path(db_path).exists()

    if use_precomputed:
        print(f"[rank.py] Loading precomputed scores from {db_path}...")
        scores_map = load_precomputed_scores(db_path)
        print(f"[rank.py] Loaded {len(scores_map):,} precomputed scores")

        # Get all candidate IDs from JSONL (fast regex extraction)
        print(f"[rank.py] Reading candidate IDs from {jsonl_path}...")
        all_ids = get_candidate_ids_from_jsonl(jsonl_path)
        print(f"[rank.py] Found {len(all_ids):,} candidates")

        # Build ranked list
        scored = []
        missing = 0
        for cid in all_ids:
            if cid in scores_map:
                row = scores_map[cid]
                scored.append((
                    cid,
                    float(row["final_score"]),
                    str(row.get("one_line_reasoning", "") or ""),
                ))
            else:
                # Not precomputed — give minimal score
                scored.append((cid, 0.001, "Not analyzed."))
                missing += 1

        if missing > 0:
            print(f"[rank.py] WARNING: {missing} candidates not in precomputed DB")
    else:
        print(f"[rank.py] Precomputed DB not found. Running fallback scoring...")
        print(f"[rank.py] This may take 3-5 minutes for 100K candidates...")
        raw_results = score_candidates_fallback(jsonl_path)
        scored = raw_results

    # Sort by score descending
    scored.sort(key=lambda x: (-round(x[1], 4), x[0]))  # Score desc, candidate_id asc for ties

    # Take top 100
    top100 = scored[:100]

    # Assign ranks 1-100
    ranked = []
    for i, (cid, score, reasoning) in enumerate(top100):
        rank = i + 1
        ranked.append({
            "candidate_id": cid,
            "rank": rank,
            "score": round(score, 4),
            "reasoning": reasoning[:300],  # Trim to reasonable length
        })

    # Validate scores are non-increasing
    for i in range(len(ranked) - 1):
        if ranked[i]["score"] < ranked[i + 1]["score"]:
            # This shouldn't happen but fix it
            ranked[i + 1]["score"] = ranked[i]["score"]

    # Write CSV
    out_path_obj = Path(out_path)
    out_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(str(out_path_obj), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(ranked)

    elapsed = time.time() - t_start
    print(f"\n[rank.py] Submission generated in {elapsed:.1f}s")
    print(f"[rank.py] Output: {out_path}")
    print(f"[rank.py] Top 5 candidates:")
    for r in ranked[:5]:
        print(f"  #{r['rank']} {r['candidate_id']} | score={r['score']:.4f}")
    print(f"\nValidate with: python {_get_dataset_path()}/validate_submission.py {out_path}")


def _get_dataset_path() -> str:
    base = "./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge"
    return base


def main():
    parser = argparse.ArgumentParser(
        description="Hiring Intelligence Engine — Ranking Script (no network)"
    )
    parser.add_argument(
        "--candidates",
        default=r"./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl",
        help="Path to candidates.jsonl",
    )
    parser.add_argument(
        "--db",
        default="./ai/pipeline/precomputed_features.db",
        help="Path to precomputed features database",
    )
    parser.add_argument(
        "--out",
        default="./submission.csv",
        help="Output submission CSV path",
    )
    args = parser.parse_args()

    generate_submission(
        jsonl_path=args.candidates,
        db_path=args.db,
        out_path=args.out,
    )


if __name__ == "__main__":
    main()
