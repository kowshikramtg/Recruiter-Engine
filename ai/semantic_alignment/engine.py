"""
Semantic Alignment Engine — computes multi-dimensional alignment between
candidate intelligence and role DNA using local sentence embeddings.

Uses sentence-transformers (all-MiniLM-L6-v2) — 22MB, fast on CPU.
Embeddings are pre-computed offline and cached as numpy arrays.
NO API calls at ranking time.
"""
from __future__ import annotations

import sys
import os
import numpy as np
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import CandidateIntelligence, RoleDNA, AlignmentScores

# Cached model reference
_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


# ---------------------------------------------------------------------------
# JD Reference Text Segments (for dimensional alignment)
# ---------------------------------------------------------------------------

JD_SEGMENTS = {
    "technical": (
        "Production experience with embeddings-based retrieval systems, vector databases, "
        "hybrid search infrastructure. Strong Python. Designing evaluation frameworks for "
        "ranking systems NDCG MRR MAP. Experience with sentence-transformers OpenAI embeddings "
        "BGE E5 Pinecone Weaviate Qdrant Milvus OpenSearch Elasticsearch FAISS. "
        "Handling embedding drift, index refresh, retrieval quality regression in production."
    ),
    "domain": (
        "Candidate-JD matching at scale. Ranking, retrieval, matching systems for recruiters. "
        "Search systems recommendation systems. HR-tech recruiting tech marketplace products. "
        "Intelligence layer of recruiting platform. BM25 rule-based scoring improvements."
    ),
    "experience": (
        "5 to 9 years experience. Applied ML AI roles at product companies. "
        "Shipped end-to-end ranking search recommendation systems to real users at meaningful scale. "
        "Not pure research environments. Production deployment experience. Writing code."
    ),
    "leadership": (
        "Mentoring next round of hires. Growing team from 4 to 12 engineers. "
        "Driving long-term architecture. Working closely with PM. Tech lead mentorship."
    ),
    "growth": (
        "Fast moving startup environment. Scrappy product-engineering attitude. "
        "Ship working ranker in a week. Learn from real users. Long-term 3 plus years commitment. "
        "Thinks about systems not frameworks. Builds from first principles."
    ),
    "communication": (
        "Async-first working style. Writes a lot. Documents decisions. "
        "Disagrees openly and decides quickly. Strong opinions backed by systems built. "
        "Can explain architecture and defend design choices."
    ),
    "adaptability": (
        "Two things that sound contradictory: deep technical depth and scrappy product-engineering. "
        "Comfortable with well-scoped roles and fast-changing environments. "
        "Company changes every six months. Early-stage startup growing quickly."
    ),
}

# Pre-computed JD segment embeddings (loaded once)
_jd_embeddings: Optional[dict[str, np.ndarray]] = None


def precompute_jd_embeddings() -> dict[str, np.ndarray]:
    """Compute and return JD segment embeddings."""
    global _jd_embeddings
    model = _get_model()
    _jd_embeddings = {
        dim: model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        for dim, text in JD_SEGMENTS.items()
    }
    return _jd_embeddings


def _get_jd_embeddings() -> dict[str, np.ndarray]:
    global _jd_embeddings
    if _jd_embeddings is None:
        precompute_jd_embeddings()
    return _jd_embeddings


# ---------------------------------------------------------------------------
# Candidate text composition
# ---------------------------------------------------------------------------

def _build_candidate_texts(intel: CandidateIntelligence) -> dict[str, str]:
    """Build dimensional candidate texts for alignment comparison."""
    skill_text = " ".join(s.name for s in intel.ai_skills)
    all_skill_text = " ".join(s.name for s in intel.all_skills)

    return {
        "technical": (
            f"{intel.summary_text} {skill_text} "
            f"{intel.career_description_combined[:1000]}"
        ),
        "domain": (
            f"{intel.headline} {intel.current_title} {intel.current_company} "
            f"{intel.summary_text[:300]} {intel.career_description_combined[:500]}"
        ),
        "experience": (
            f"{intel.years_of_experience} years experience. "
            f"Current role: {intel.current_title} at {intel.current_company}. "
            f"{intel.career_description_combined[:800]}"
        ),
        "leadership": (
            f"{intel.current_title} "
            f"{'led team managed mentored' if intel.has_leadership_evidence else 'individual contributor'} "
            f"{intel.career_description_combined[:400]}"
        ),
        "growth": (
            f"{intel.summary_text} career progression product company "
            f"{'startup' if intel.product_company_ratio > 0.5 else 'enterprise'} "
            f"{'open source' if intel.github_activity_score > 0 else ''}"
        ),
        "communication": (
            f"{'github active open source' if intel.github_activity_score > 0 else ''} "
            f"{intel.summary_text[:300]} "
            f"{'linkedin connected' if True else ''}"
        ),
        "adaptability": (
            f"{intel.summary_text[:400]} "
            f"{'product company startup' if intel.product_company_ratio > 0.3 else 'enterprise services'} "
            f"career diversity industries"
        ),
    }


def compute_semantic_alignment(intel: CandidateIntelligence) -> AlignmentScores:
    """
    Compute multi-dimensional semantic alignment scores (0-100 each).
    Uses cosine similarity between candidate text embeddings and JD segments.
    """
    model = _get_model()
    jd_embs = _get_jd_embeddings()
    candidate_texts = _build_candidate_texts(intel)

    scores = AlignmentScores(candidate_id=intel.candidate_id)
    dimension_scores = {}

    for dim, text in candidate_texts.items():
        if not text.strip():
            dimension_scores[dim] = 0.0
            continue
        cand_emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        similarity = float(np.dot(cand_emb, jd_embs[dim]))
        # Convert cosine similarity (-1 to 1) → 0-100 score
        score = max(0.0, (similarity + 1.0) / 2.0 * 100.0)
        dimension_scores[dim] = score

    scores.technical_alignment = dimension_scores.get("technical", 0.0)
    scores.domain_alignment = dimension_scores.get("domain", 0.0)
    scores.experience_alignment = dimension_scores.get("experience", 0.0)
    scores.leadership_alignment = dimension_scores.get("leadership", 0.0)
    scores.growth_alignment = dimension_scores.get("growth", 0.0)
    scores.communication_alignment = dimension_scores.get("communication", 0.0)
    scores.adaptability_alignment = dimension_scores.get("adaptability", 0.0)

    # Semantic similarity: full profile vs full JD
    full_text = f"{intel.summary_text} {intel.career_description_combined[:1500]}"
    full_jd = " ".join(JD_SEGMENTS.values())
    if full_text.strip():
        cand_full = model.encode(full_text[:2000], convert_to_numpy=True, normalize_embeddings=True)
        jd_full = model.encode(full_jd[:2000], convert_to_numpy=True, normalize_embeddings=True)
        scores.semantic_similarity = max(0.0, (float(np.dot(cand_full, jd_full)) + 1.0) / 2.0 * 100.0)

    # Overall alignment (weighted average — technical and domain weighted most)
    scores.overall_alignment = (
        0.30 * scores.technical_alignment +
        0.20 * scores.domain_alignment +
        0.20 * scores.experience_alignment +
        0.10 * scores.leadership_alignment +
        0.10 * scores.growth_alignment +
        0.05 * scores.communication_alignment +
        0.05 * scores.adaptability_alignment
    )

    return scores


def batch_compute_embeddings(
    candidates: list[CandidateIntelligence],
    batch_size: int = 256,
) -> list[AlignmentScores]:
    """
    Batch compute semantic alignments for efficiency.
    Processes candidates in batches to avoid memory issues.
    """
    model = _get_model()
    precompute_jd_embeddings()  # Ensure JD embeddings are ready

    results = []
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]
        batch_results = []

        # Build all texts for this batch
        all_texts = []
        dims = list(JD_SEGMENTS.keys())
        for intel in batch:
            texts = _build_candidate_texts(intel)
            for dim in dims:
                all_texts.append(texts.get(dim, ""))

        # Encode all at once
        embeddings = model.encode(
            all_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=64,
            show_progress_bar=False,
        )

        jd_embs = _get_jd_embeddings()
        for j, intel in enumerate(batch):
            scores = AlignmentScores(candidate_id=intel.candidate_id)
            for k, dim in enumerate(dims):
                emb = embeddings[j * len(dims) + k]
                sim = float(np.dot(emb, jd_embs[dim]))
                score = max(0.0, (sim + 1.0) / 2.0 * 100.0)
                setattr(scores, f"{dim}_alignment", score)

            scores.overall_alignment = (
                0.30 * scores.technical_alignment +
                0.20 * scores.domain_alignment +
                0.20 * scores.experience_alignment +
                0.10 * scores.leadership_alignment +
                0.10 * scores.growth_alignment +
                0.05 * scores.communication_alignment +
                0.05 * scores.adaptability_alignment
            )
            scores.semantic_similarity = scores.overall_alignment
            batch_results.append(scores)

        results.extend(batch_results)
        print(f"[SemanticAlignment] Processed {min(i + batch_size, len(candidates))}/{len(candidates)}")

    return results
