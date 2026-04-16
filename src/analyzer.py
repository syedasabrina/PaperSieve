# ---------------------------------------------------------------------------
# Analyzer — Gemini API Calls for Paper Screening
# ---------------------------------------------------------------------------
# This module sends extracted paper sections to Gemini and receives
# structured yes/no answers for the four screening criteria.
#
# Responsibilities:
#   1. Build a structured prompt from extracted sections and rubric.
#   2. Call Gemini API and parse the response into CriterionResult objects.
#   3. If confidence is low or response is ambiguous, trigger a retry with
#      a more targeted prompt on the relevant section only.
#   4. Log model version, prompt version, timestamp, and retry count.
#
# This retry-with-refinement loop is what makes this an agent rather than
# a simple batch script.
# ---------------------------------------------------------------------------


from __future__ import annotations
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.models import PaperSections, CriterionLabel, ConfidenceLevel, CriterionResult, PaperRecord, FinalBucket
from src.extractor import extract_sections


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"
RETRY_MODEL_NAME = "gemini-2.5-pro"
PROMPT_VERSION = "v1"
MAX_RETRIES_PER_CRITERION = 1


def call_with_backoff(fn, *args, max_attempts: int = 5, wait_seconds: int = 30, **kwargs):
    for attempt in range(max_attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "503" in str(e) and attempt < max_attempts - 1:
                wait = wait_seconds * (attempt + 1)
                print(f"  503 error, waiting {wait}s (attempt {attempt + 1}/{max_attempts})")
                time.sleep(wait)
                continue
            raise


def build_prompt(sections: dict[PaperSections, str]) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "screening_v1.txt"
    template = prompt_path.read_text()

    section_text = ""

    for section, text in sections.items():
        section_text += f"\n\n### {section.value.upper()}\n{text}"

    return template.replace("{{PAPER_SECTIONS}}", section_text)


def call_gemini(prompt: str, model: str = MODEL_NAME) -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return response.text


def parse_response(response_text: str) -> dict[str, CriterionResult]:
    clean = response_text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
        clean = clean.split("```", 1)[0]

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned non json output: {e}\n---\n{clean}")

    valid_sections = {s.value for s in PaperSections}

    results = {}
    for key in ["q1", "q2", "q3", "q4"]:
        q = data[key]

        raw_confidence = (q.get("confidence") or "low").lower()
        if raw_confidence not in ("high", "medium", "low"):
            raw_confidence = "low"

        raw_section = q.get("section", "").lower() if q.get("section") else None

        results[key] = CriterionResult(
            label=CriterionLabel(q["label"].lower()),
            confidence=ConfidenceLevel(raw_confidence),
            quote=q.get("quote"),
            section=PaperSections(raw_section) if raw_section in valid_sections else None,
            justification=q.get("justification"),
        )

    return results


def build_retry_prompt(criterion_id: str, previous_result: CriterionResult, section_text: str) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "retry_v1.txt"
    template = prompt_path.read_text()

    questions_path = Path(__file__).parent.parent / "prompts" / "criterion_questions.json"
    questions = json.loads(questions_path.read_text())

    return (
        template
        .replace("{{CRITERION_ID}}", criterion_id)
        .replace("{{CRITERION_QUESTION}}", questions[criterion_id])
        .replace("{{PREVIOUS_LABEL}}", previous_result.label.value)
        .replace("{{PREVIOUS_JUSTIFICATION}}", previous_result.justification or "none given")
        .replace("{{SECTION_TEXT}}", section_text)
    )


def run_retry(criterion_id: str, previous_result: CriterionResult, sections: dict[PaperSections, str], model: str = RETRY_MODEL_NAME) -> CriterionResult:
    section_key = None
    if previous_result.section:
        try:
            section_key = PaperSections(previous_result.section)
        except ValueError:
            pass

    if section_key is None or section_key not in sections:
        section_key = PaperSections.ABSTRACT if PaperSections.ABSTRACT in sections \
            else next(iter(sections))

    section_text = sections[section_key]

    prompt = build_retry_prompt(criterion_id, previous_result, section_text)
    raw = call_with_backoff(call_gemini, prompt, model=model)

    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
        clean = clean.rsplit("```", 1)[0]

    try:
        q = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"Retry parse failed for {criterion_id}: {e}\n---\n{clean}")

    valid_sections = {s.value for s in PaperSections}

    raw_confidence = (q.get("confidence") or "low").lower()
    if raw_confidence not in ("high", "medium", "low"):
        raw_confidence = "low"

    raw_section = q.get("section", "").lower() if q.get("section") else None

    return CriterionResult(
        label=CriterionLabel(q["label"].lower()),
        confidence=ConfidenceLevel(raw_confidence),
        quote=q.get("quote"),
        section=PaperSections(raw_section) if raw_section in valid_sections else None,
        justification=q.get("justification"),
    )


def analyze_paper(pdf_path: Path, paper_id: str, model: str = MODEL_NAME, retry_model: str = RETRY_MODEL_NAME) -> PaperRecord:
    sections = extract_sections(pdf_path)
    prompt = build_prompt(sections)
    raw = call_with_backoff(call_gemini, prompt, model=model)
    results = parse_response(raw)

    retry_used = False
    retry_count = 0
    for criterion_id, result in results.items():
        if result.confidence == ConfidenceLevel.LOW and retry_count < MAX_RETRIES_PER_CRITERION:
            results[criterion_id] = run_retry(criterion_id, result, sections, model=retry_model)
            retry_used = True
            retry_count += 1

    score = sum(1 for r in results.values() if r.label == CriterionLabel.YES)
    any_low = any(r.confidence == ConfidenceLevel.LOW for r in results.values())

    if score > 3 and not any_low:
        bucket = FinalBucket.TO_READ
    elif (score > 3 and any_low) or (score==3 and not any_low):
        bucket = FinalBucket.MAYBE_RECHECK
    elif score == 0 and not any_low:
        bucket = FinalBucket.FILTERED_OUT
    else:
        bucket = FinalBucket.MAYBE_BORDERLINE

    manual_review = any_low
    manual_review_reason = (
        "One or more criteria still low-confidence after retry" if any_low else None
    )

    return PaperRecord(
        paper_id=paper_id,
        title=pdf_path.stem,
        q1=results["q1"],
        q2=results["q2"],
        q3=results["q3"],
        q4=results["q4"],
        score=score,
        bucket=bucket,
        manual_review=manual_review,
        manual_review_reason=manual_review_reason,
        model_version=model,
        prompt_version=PROMPT_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        retry_used=retry_used,
        retry_count=retry_count,
    )