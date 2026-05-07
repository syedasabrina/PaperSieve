# ---------------------------------------------------------------------------
# Verifier — Gemini API Calls for Verifiability Pipeline
# ---------------------------------------------------------------------------
# Mirrors analyzer.py but runs three prompts per paper instead of one.
#
# Responsibilities:
#   1. Extract sections from PDF using existing extract_sections().
#   2. Concatenate sections into a single paper_text string.
#   3. Slot paper_text into each of the three prompt templates.
#   4. Call Gemini and parse each response into its Pydantic model.
#   5. On JSON parse failure: one retry, same model.
#   6. Return a VerifierRecord containing all three results.
# ---------------------------------------------------------------------------

from __future__ import annotations
import os
import re
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.extractor import extract_sections
from src.analyzer import call_with_backoff
from src.verifier_models import (
    DefinitionResult, TaxonomyResult, HandlingResult,
    SubjectivityDefType, PillarMatch, MatchesWorkingDef,
    AuthorTaskLabel, TaxonomyCategoryMatch, ReasoningCode,
    FocalTask, StrategyCode, PipelineStage, PrimaryPosition,
    InternalConsistency, HandlingStrategy,
)
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DEFAULT_VERIFY_MODEL = "gemini-2.5-flash"
PROMPT_VERSION = "v1"
MAX_PARSE_RETRIES = 1

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Data model for the combined output of all three prompts for one paper
# ---------------------------------------------------------------------------

class VerifierRecord(BaseModel):
    paper_id: str
    definition: DefinitionResult
    taxonomy: TaxonomyResult
    handling: HandlingResult
    model_version: str
    prompt_version: str
    timestamp: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sections_to_text(sections: dict) -> str:
    parts = []
    for section, text in sections.items():
        label = section.value.upper() if hasattr(section, "value") else str(section).upper()
        parts.append(f"### {label}\n{text}")
    return "\n\n".join(parts)


def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def build_prompt(template: str, paper_id: str, paper_text: str) -> str:
    return (
        template
        .replace("{{paper_id}}", paper_id)
        .replace("{{paper_text}}", paper_text)
    )


def clean_json(raw: str) -> str:
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
        clean = clean.rsplit("```", 1)[0]
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)
    return clean.strip()


def normalize_none_strings(obj):
    """Gemini often returns the string 'None' instead of JSON null.
    Recursively replace 'None' strings with Python None."""
    if isinstance(obj, dict):
        return {k: normalize_none_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_none_strings(i) for i in obj]
    if obj == "None":
        return None
    return obj


def call_gemini(prompt: str, model: str = DEFAULT_VERIFY_MODEL) -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return response.text


def call_with_parse_retry(prompt: str, parse_fn, model: str = DEFAULT_VERIFY_MODEL):
    """Call Gemini and parse the response. On JSON parse failure, retry once."""
    raw = call_with_backoff(call_gemini, prompt, model=model)
    try:
        return parse_fn(raw)
    except (ValueError, KeyError) as e:
        print(f"  Parse failed ({e}), retrying once...")
        time.sleep(5)
        raw = call_with_backoff(call_gemini, prompt, model=model)
        return parse_fn(raw)


# ---------------------------------------------------------------------------
# Parse functions — one per prompt
# ---------------------------------------------------------------------------

def parse_definition(raw: str, paper_id: str) -> DefinitionResult:
    data = normalize_none_strings(json.loads(clean_json(raw)))
    
    raw_dist = data.get("subjectivity_distinguished_from")
    if isinstance(raw_dist, list):
        raw_dist = ", ".join(raw_dist)

    return DefinitionResult(
        paper_id=paper_id,
        subjectivity_def_type=SubjectivityDefType(data["subjectivity_def_type"]),
        pillar_match=[PillarMatch(p) for p in (data.get("pillar_match") or [])],
        matches_working_definition=MatchesWorkingDef(data["matches_working_definition"]),
        definition_gap_identified=data.get("definition_gap_identified"),
        subjectivity_distinguished_from=raw_dist,
        supporting_definition_quote=data.get("supporting_definition_quote"),
        thought_process=data.get("thought_process"),
    )


def parse_taxonomy(raw: str, paper_id: str) -> TaxonomyResult:
    data = normalize_none_strings(json.loads(clean_json(raw)))
    focal_tasks = []
    for t in (data.get("focal_tasks") or []):
        focal_tasks.append(FocalTask(
            task_name=t["task_name"],
            author_task_label=AuthorTaskLabel(t["author_task_label"]),
            taxonomy_category_match=TaxonomyCategoryMatch(t["taxonomy_category_match"]),
            reasoning_codes=[ReasoningCode(r) for r in (t.get("reasoning_codes") or [])],
            reasoning_gap=t.get("reasoning_gap"),
            task_supporting_quote=t.get("task_supporting_quote"),
            alignment_note=t.get("alignment_note"),
        ))
    return TaxonomyResult(
        paper_id=paper_id,
        focal_tasks=focal_tasks,
        thought_process=data.get("thought_process"),
    )


def parse_handling(raw: str, paper_id: str) -> HandlingResult:
    data = normalize_none_strings(json.loads(clean_json(raw)))
    strategies = []
    for s in (data.get("handling_strategies") or []):
        strategies.append(HandlingStrategy(
            strategy_code=StrategyCode(s["strategy_code"]),
            pipeline_stage=PipelineStage(s["pipeline_stage"]),
            quantification_metric=s.get("quantification_metric"),
            handling_supporting_quote=s.get("handling_supporting_quote"),
        ))
    return HandlingResult(
        paper_id=paper_id,
        handling_strategies=strategies,
        primary_position=PrimaryPosition(data["primary_position"]),
        handling_gap_identified=data.get("handling_gap_identified"),
        internal_consistency=InternalConsistency(data["internal_consistency"]),
        inconsistency_note=data.get("inconsistency_note"),
        thought_process=data.get("thought_process"),
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def verify_paper(pdf_path: Path, paper_id: str, model: str = DEFAULT_VERIFY_MODEL) -> VerifierRecord:
    sections = extract_sections(pdf_path)
    paper_text = sections_to_text(sections)

    def_template = load_prompt("definition_verifiability_v1.txt")
    tax_template = load_prompt("taxonomy_verifiability_v1.txt")
    han_template = load_prompt("handling_verifiability_v1.txt")

    def_prompt = build_prompt(def_template, paper_id, paper_text)
    tax_prompt = build_prompt(tax_template, paper_id, paper_text)
    han_prompt = build_prompt(han_template, paper_id, paper_text)

    definition = call_with_parse_retry(
        def_prompt,
        lambda raw: parse_definition(raw, paper_id),
        model=model,
    )
    taxonomy = call_with_parse_retry(
        tax_prompt,
        lambda raw: parse_taxonomy(raw, paper_id),
        model=model,
    )
    handling = call_with_parse_retry(
        han_prompt,
        lambda raw: parse_handling(raw, paper_id),
        model=model,
    )

    return VerifierRecord(
        paper_id=paper_id,
        definition=definition,
        taxonomy=taxonomy,
        handling=handling,
        model_version=model,
        prompt_version=PROMPT_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )