# Hiring Intelligence Engine

> Enterprise-grade AI Hiring Platform — evidence-driven, explainable, multi-dimensional candidate ranking. Competition submission for Redrob Intelligent Candidate Discovery & Ranking Challenge.

## Quick Start

### 1. Install Python dependencies
```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env: add GEMINI_API_KEY or OPENAI_API_KEY (for LLM enrichment, optional)
```

### 3. Pre-compute features (run once, ~10-30 min for 100K candidates)
```bash
python precompute.py
# With LLM enrichment: set GEMINI_API_KEY in .env first
# Without LLM (faster): python precompute.py --no-semantic
```

### 4. Generate submission CSV (no network, < 5 min)
```bash
python rank.py --candidates "./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" --out submission.csv
```

### 5. Validate submission
```bash
python "./Dataset/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" submission.csv
```

### 6. Start the full UI (optional)
```bash
# Backend
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```

## Architecture

```
OFFLINE PRE-COMPUTATION (precompute.py)
candidates.jsonl (464MB, 100K candidates)
    ↓
[1] Role DNA Engine          — JD → structured requirements (LLM, run once)
[2] Candidate Intelligence   — profile → 50+ features (pure Python, ~15s)
[3] Semantic Alignment       — local embeddings, 7 dimensions (~2 min batch)
[4] Evidence Validation      — honeypot detection + claim cross-check
[5] Multi-Dim Scorecard      — 10 dimensions + final score
[6] Risk Radar               — 8 hiring risk dimensions
[7] Recruitability Index     — candidate rarity estimation
[8] Opportunity Cost         — rejection cost estimation
[9] Explainability Engine    — template-based reasoning (no LLM)
    ↓
precomputed_features.db (SQLite, ~200MB)

ONLINE RANKING (rank.py — NO NETWORK, CPU ONLY, < 5 MIN)
candidates.jsonl + precomputed_features.db
    → sort by final_score
    → top 100
    → submission.csv
```

## Scoring Formula

```
final_score = (
    technical_fit         × 0.28 +
    role_fit              × 0.18 +
    domain_expertise      × 0.10 +
    career_momentum       × 0.08 +
    behavioral_composite  × 0.18 +  # availability + engagement + notice + location
    cultural_fit          × 0.05 +
    leadership            × 0.05 +
    adaptability          × 0.04 +
    learning_potential    × 0.03 +
    evidence_strength     × 0.01
) × penalties

# Penalties:
# Services-firm-only career: × 0.60
# Honeypot detected:         × 0.05
# No AI skills:              × 0.40
# Stale profile (>6mo):      × 0.70
```

## Anti-Trap Signals (per JD guidance)

The JD explicitly warns that "the right answer is NOT keyword matching". Our pipeline:
- **Services firm penalty**: TCS/Infosys/Wipro/Accenture/Cognizant/Capgemini → 40% penalty if entire career
- **Honeypot detection**: expert proficiency × 10 skills × 0 months usage = flagged
- **Title priority**: Marketing/HR/Accounting + AI keywords ≠ AI Engineer fit
- **Production evidence**: Descriptions searched for deployment/serving/production keywords
- **Career history weight**: Company type (product vs services) matters more than skill list

## Competition Constraints Met

| Constraint | Our Solution |
|---|---|
| No network during ranking | `rank.py` loads SQLite, zero API calls |
| < 5 min runtime | SQLite lookup is O(1) per candidate, <2 min total |
| CPU only | `all-MiniLM-L6-v2` runs on CPU, pre-computed offline |
| 16GB RAM | Peak RAM during precompute: ~3-4GB (embeddings in batches) |
| Honeypot rate < 10% | Consistency math detects all planted patterns |

## Frontend Pages

| Page | URL | Description |
|---|---|---|
| Dashboard | `/dashboard` | 8 stats, 3 charts, top candidates |
| Candidates | `/candidates` | Ranked list with filters, score bars |
| Candidate Detail | `/candidates/[id]` | 6-tab analysis: Overview, Scorecard, Risk Radar, Intelligence, Evidence, Interview |
| Role DNA | `/jobs` | Structured JD intelligence visualization |
| AI Pipeline | `/analysis` | 10-module pipeline documentation |
| Time Machine | `/time-machine` | What-if scenario simulation |
| Analytics | `/analytics` | Methodology and approach |

## Tech Stack

**AI Pipeline**: Python, sentence-transformers, SQLite/SQLAlchemy, numpy  
**Backend**: FastAPI, Pydantic, async SQLAlchemy, aiosqlite  
**Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, Recharts, Framer Motion, Lucide  
**LLM** (offline pre-compute only): Gemini 1.5 Flash / GPT-4o-mini  

## Dataset

Dataset files are **NOT committed** to this repository (`.gitignore`).  
Place the dataset at: `./Dataset/[PUB] India_runs_data_and_ai_challenge/`

```
Dataset/
└── [PUB] India_runs_data_and_ai_challenge/
    └── India_runs_data_and_ai_challenge/
        ├── candidates.jsonl          (464MB, 100K candidates)
        ├── candidate_schema.json
        ├── sample_candidates.json
        ├── job_description.docx
        ├── redrob_signals_doc.docx
        ├── README.docx
        ├── submission_spec.docx
        └── validate_submission.py
```
