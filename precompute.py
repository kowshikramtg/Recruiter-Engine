"""
precompute.py — Offline pre-computation entry point.

Run this ONCE (with network access and LLMs allowed) to generate all features.
Output: ai/pipeline/precomputed_features.db

Usage:
    python precompute.py [--candidates path] [--limit N] [--no-semantic]
"""
import argparse
import os
import sys
import time
import zipfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Hiring Intelligence Engine — Pre-computation")
    parser.add_argument(
        "--candidates",
        default=os.environ.get(
            "CANDIDATES_FILE",
            r"./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
        ),
        help="Path to candidates.jsonl (or .jsonl.gz)",
    )
    parser.add_argument(
        "--out-db",
        default=os.environ.get("PRECOMPUTED_DB", "./ai/pipeline/precomputed_features.db"),
        help="Output SQLite database path",
    )
    parser.add_argument(
        "--jd",
        default=r"./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/job_description.docx",
        help="Path to job_description.docx",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of candidates (for testing)",
    )
    parser.add_argument(
        "--no-semantic",
        action="store_true",
        help="Skip semantic embedding computation (faster, lower quality)",
    )
    parser.add_argument(
        "--llm-provider",
        default=os.environ.get("LLM_PROVIDER", "gemini"),
        help="LLM provider: 'gemini' or 'openai'",
    )
    parser.add_argument(
        "--role-dna-out",
        default=os.environ.get("ROLE_DNA_PATH", "./ai/role_dna/role_dna_output.json"),
    )
    args = parser.parse_args()

    print("\n" + "="*60)
    print("HIRING INTELLIGENCE ENGINE — Pre-computation")
    print("="*60)
    print(f"Candidates: {args.candidates}")
    print(f"Output DB:  {args.out_db}")

    # --- Step 1: Build Role DNA ---
    print("\n[Step 1] Building Role DNA from job description...")
    from ai.role_dna.engine import build_role_dna_from_jd_text, save_role_dna

    # Read JD text
    jd_text = _read_jd(args.jd)
    print(f"JD text length: {len(jd_text)} chars")

    # Check if we have an LLM key
    has_llm = bool(
        os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
    )
    provider = args.llm_provider if has_llm else None
    if has_llm:
        print(f"LLM provider: {args.llm_provider} (enrichment enabled)")
    else:
        print("No LLM API key found — using rule-based Role DNA extraction")

    role_dna = build_role_dna_from_jd_text(jd_text, llm_provider=provider)
    save_role_dna(role_dna, args.role_dna_out)
    print(f"Role DNA saved: {args.role_dna_out}")
    print(f"  Must-have skills: {len(role_dna.must_have_skills)}")
    print(f"  Target titles: {len(role_dna.target_titles)}")

    # --- Step 2: Resolve candidates file ---
    candidates_path = _resolve_candidates_path(args.candidates)
    print(f"\n[Step 2] Candidates file: {candidates_path}")

    # --- Step 3: Run pipeline ---
    from ai.pipeline.orchestrator import run_pipeline
    stats = run_pipeline(
        jsonl_path=candidates_path,
        db_path=args.out_db,
        role_dna=role_dna,
        use_semantic=not args.no_semantic,
        limit=args.limit,
    )

    print(f"\n✓ Pre-computation complete!")
    print(f"  Candidates: {stats['total']:,}")
    print(f"  Honeypots: {stats['honeypots']}")
    print(f"  Runtime: {stats['elapsed_seconds']:.1f}s")
    print(f"  DB: {stats['db_path']}")
    print(f"\nNext step: python rank.py --candidates {args.candidates} --out submission.csv")


def _read_jd(jd_path: str) -> str:
    """Read job description text from docx or txt."""
    path = Path(jd_path)
    if not path.exists():
        # Fallback: use the hardcoded JD text
        print(f"WARNING: JD file not found at {jd_path}, using embedded JD text")
        return _FALLBACK_JD_TEXT

    if path.suffix.lower() == ".docx":
        import zipfile
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(str(path), "r") as z:
            with z.open("word/document.xml") as f:
                tree = ET.parse(f)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for para in tree.findall(".//w:p", ns):
            texts = [node.text or "" for node in para.findall(".//w:t", ns)]
            line = "".join(texts).strip()
            if line:
                paragraphs.append(line)
        return "\n".join(paragraphs)
    else:
        return path.read_text(encoding="utf-8")


def _resolve_candidates_path(path: str) -> str:
    """Resolve candidates file path, supporting .jsonl and .jsonl.gz."""
    p = Path(path)
    if p.exists():
        return str(p)
    # Try .gz
    gz_path = Path(str(p) + ".gz")
    if gz_path.exists():
        # Extract to temp location
        out_path = p.parent / p.stem
        print(f"Extracting {gz_path}...")
        import gzip, shutil
        with gzip.open(str(gz_path), "rb") as f_in:
            with open(str(out_path), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return str(out_path)
    raise FileNotFoundError(f"Candidates file not found: {path}")


# Embedded JD text as fallback (key points)
_FALLBACK_JD_TEXT = """
Senior AI Engineer - Founding Team at Redrob AI (Series A AI-native talent intelligence platform).
Location: Pune/Noida, India (Hybrid). Experience Required: 5-9 years.

We need: Deep technical depth in modern ML systems (embeddings, retrieval, ranking, LLMs, fine-tuning)
plus scrappy product-engineering attitude.

Things you absolutely need:
- Production experience with embeddings-based retrieval systems deployed to real users
- Production experience with vector databases or hybrid search infrastructure (Pinecone, Weaviate, Qdrant, Milvus, FAISS)
- Strong Python
- Hands-on experience designing evaluation frameworks for ranking systems (NDCG, MRR, MAP)

Things we explicitly do NOT want:
- Title-chasers switching companies every 1.5 years
- People who have only worked at consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini)
- Pure researchers without production deployment

The ideal candidate: 6-8 years total, 4-5 in applied ML at product companies.
Has shipped at least one end-to-end ranking or search system to real users at scale.
"""


if __name__ == "__main__":
    main()
