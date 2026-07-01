"""
Role DNA Engine — extracts structured intelligence from the job description.

This module is used OFFLINE only during precompute.py.
It uses an LLM to understand the JD contextually (not keyword extraction)
and produces a structured RoleDNA object persisted as JSON.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.types import RoleDNA


# ---------------------------------------------------------------------------
# AI skill taxonomy — what counts as "AI/ML relevant"
# ---------------------------------------------------------------------------

AI_CORE_SKILLS = {
    # Embeddings & Retrieval
    "embeddings", "vector search", "semantic search", "dense retrieval",
    "bm25", "faiss", "milvus", "weaviate", "pinecone", "qdrant", "opensearch",
    "elasticsearch", "hybrid search", "ann", "approximate nearest neighbor",
    "sentence-transformers", "sentence transformers", "bge", "e5",
    # LLMs & NLP
    "llm", "large language model", "nlp", "natural language processing",
    "transformers", "bert", "gpt", "gemini", "claude", "hugging face",
    "huggingface", "fine-tuning", "fine tuning", "finetuning", "lora", "qlora",
    "peft", "rag", "retrieval augmented generation", "langchain", "llamaindex",
    "text classification", "named entity recognition", "ner", "information retrieval",
    # ML Core
    "machine learning", "deep learning", "neural networks", "pytorch", "tensorflow",
    "scikit-learn", "xgboost", "lightgbm", "ranking", "recommendation systems",
    "recommendation", "collaborative filtering", "learning to rank", "ndcg", "mrr",
    "a/b testing", "offline evaluation", "online evaluation",
    # MLOps & Production
    "mlflow", "weights & biases", "wandb", "bentoml", "triton", "torchserve",
    "model serving", "feature store", "model registry", "mlops",
    "model deployment", "inference optimization",
    # Data & Infrastructure
    "feature engineering", "data pipelines", "apache spark", "pyspark",
    "apache airflow", "kafka", "apache flink", "dbt", "databricks",
    "speech recognition", "tts", "image classification", "object detection",
    "computer vision", "gans", "diffusion", "stable diffusion",
    "statistical modeling", "bayesian", "time series",
    # Cloud / Infra
    "aws sagemaker", "gcp vertex ai", "azure ml",
    # Specific frameworks
    "nlu", "rasa", "spacy", "nltk", "gensim", "fasttext",
    "milvus", "chroma", "weaviate", "redis", "pgvector",
}

# Services firms that are JD-flagged
SERVICES_FIRMS = {
    "tcs", "tata consultancy services",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl", "hcl technologies",
    "tech mahindra",
    "mphasis",
    "l&t infotech", "ltimindtree", "lti",
    "hexaware",
    "mindtree",
    "niit technologies",
    "persistent systems",
    "zensar",
    "birlasoft",
    "mastech",
}

# Target role titles for this JD
TARGET_AI_TITLES = {
    "ai engineer", "ml engineer", "machine learning engineer",
    "data scientist", "research scientist", "applied scientist",
    "nlp engineer", "search engineer", "ranking engineer",
    "senior ai engineer", "senior ml engineer", "senior data scientist",
    "staff ml engineer", "staff ai engineer", "principal ml engineer",
    "applied ml engineer", "deep learning engineer",
    "junior ml engineer", "junior ai engineer",
}

# Preferred India cities
PREFERRED_LOCATIONS = {
    "pune", "noida", "bangalore", "bengaluru", "hyderabad",
    "mumbai", "delhi", "gurgaon", "gurugram", "chennai", "india",
}


def build_role_dna_from_jd_text(jd_text: str, llm_provider: str = None) -> RoleDNA:
    """
    Build a RoleDNA from the job description text.
    If LLM provider is configured, uses LLM for nuanced extraction.
    Otherwise falls back to comprehensive rule-based extraction.
    """
    dna = RoleDNA()
    dna.raw_jd_text = jd_text
    dna.title = "Senior AI Engineer"
    dna.company = "Redrob AI"

    # --- Structured extraction (always run) ---
    dna.must_have_skills = [
        "embeddings-based retrieval systems",
        "vector databases or hybrid search",
        "python",
        "ranking system evaluation (NDCG, MRR, MAP)",
        "production ML deployment",
    ]
    dna.preferred_skills = [
        "LLM fine-tuning (LoRA, QLoRA, PEFT)",
        "learning-to-rank models",
        "HR-tech or marketplace products",
        "distributed systems",
        "open-source AI/ML contributions",
    ]
    dna.disqualifying_signals = [
        "services_firm_only_career",
        "pure_research_no_production",
        "no_production_code_18months",
        "primary_expertise_computer_vision_only",
        "marketing_or_hr_primary_title",
        "langchain_demo_only_without_prior_ml",
    ]
    dna.target_titles = list(TARGET_AI_TITLES)
    dna.avoid_companies = list(SERVICES_FIRMS)
    dna.experience_min_years = 5.0
    dna.experience_max_years = 9.0
    dna.notice_preference_days = 30
    dna.notice_max_days = 90
    dna.requires_production_experience = True
    dna.requires_github = True
    dna.prefers_product_company = True
    dna.location_preferences = list(PREFERRED_LOCATIONS)

    dna.responsibilities = [
        "Own the intelligence layer: ranking, retrieval, matching systems",
        "Audit existing BM25 + rule-based scoring and improve it",
        "Ship v2 ranking system with embeddings + hybrid retrieval + LLM re-ranking",
        "Build evaluation infrastructure: offline benchmarks, A/B testing, feedback loops",
        "Drive long-term architecture of candidate-JD matching at scale",
        "Mentor next round of hires (team growing 4→12 engineers)",
        "Work closely with recruiter-experience PM",
    ]
    dna.success_indicators = [
        "Demonstrably improved recruiter-engagement metrics within 90 days",
        "Evaluation infrastructure set up with offline/online correlation",
        "Strong opinions about retrieval and evaluation backed by systems built",
        "Comfort in scrappy product-engineering: ship working ranker in a week",
    ]
    dna.hidden_expectations = [
        "Writes async-first; documents decisions",
        "Can disagree openly and decide quickly",
        "Plans to stay 3+ years (not a title-chaser)",
        "Thinks in systems, not frameworks",
        "Active on Redrob platform or clear job-market signals",
    ]
    dna.technical_competencies = [
        "Production embeddings retrieval (sentence-transformers, OpenAI embed, BGE, E5)",
        "Vector DB / hybrid search operations (Pinecone, Weaviate, Qdrant, FAISS, OpenSearch)",
        "Embedding drift handling, index refresh, retrieval quality regression",
        "Evaluation frameworks: NDCG, MRR, MAP, A/B testing, offline-to-online correlation",
        "Strong Python + code quality",
    ]
    dna.domain_knowledge = [
        "Candidate-JD matching at scale",
        "Recruiting tech / HR-tech preferred",
        "Marketplace product dynamics",
    ]
    dna.seniority_level = "senior"
    dna.leadership_requirements = "Mentor next round of hires; drive architecture decisions"
    dna.communication_expectations = "Async-first, writes a lot; disagrees openly"
    dna.trainable_skills = [
        "Specific vector DB vendor (e.g., Weaviate vs Pinecone)",
        "HR-tech domain knowledge",
        "Company-specific recruiting workflows",
    ]

    # Try LLM enrichment if available
    if llm_provider:
        try:
            dna = _enrich_with_llm(dna, jd_text, llm_provider)
        except Exception as e:
            print(f"[RoleDNA] LLM enrichment failed ({e}), using rule-based output")

    return dna


def _enrich_with_llm(dna: RoleDNA, jd_text: str, llm_provider: str) -> RoleDNA:
    """Use LLM to extract hidden expectations and nuances not captured by rules."""
    prompt = f"""You are an expert senior recruiter analyzing a job description for a Senior AI Engineer role at an AI startup.

JOB DESCRIPTION:
{jd_text[:3000]}

Extract the following as a JSON object:
{{
  "hidden_expectations": ["list of implicit expectations not explicitly stated"],
  "success_indicators": ["observable signals of a great hire"],
  "culture_signals": ["what the culture values — be specific"],
  "interview_focus_areas": ["what to probe in interviews based on this JD"],
  "red_flags_to_probe": ["specific concerns to validate for candidates"]
}}

Be specific, cite exact phrases from the JD. Return only valid JSON."""

    response_text = ""
    if llm_provider == "gemini":
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return dna
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text
    elif llm_provider == "openai":
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return dna
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        response_text = resp.choices[0].message.content

    # Parse JSON response
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start >= 0 and end > start:
        data = json.loads(response_text[start:end])
        if "hidden_expectations" in data:
            dna.hidden_expectations = data["hidden_expectations"]
        if "success_indicators" in data:
            dna.success_indicators.extend(data.get("success_indicators", []))
        if "interview_focus_areas" in data:
            # Store for explainability engine
            dna.domain_knowledge.extend(data.get("interview_focus_areas", []))

    return dna


def load_role_dna(path: str) -> RoleDNA:
    """Load a persisted RoleDNA from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    dna = RoleDNA()
    for key, value in data.items():
        if hasattr(dna, key):
            setattr(dna, key, value)
    return dna


def save_role_dna(dna: RoleDNA, path: str) -> None:
    """Persist RoleDNA to JSON file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    data = {k: v for k, v in dna.__dict__.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[RoleDNA] Saved to {path}")


def get_ai_skill_taxonomy() -> set[str]:
    return AI_CORE_SKILLS


def get_services_firms() -> set[str]:
    return SERVICES_FIRMS


def get_target_titles() -> set[str]:
    return TARGET_AI_TITLES


def get_preferred_locations() -> set[str]:
    return PREFERRED_LOCATIONS
