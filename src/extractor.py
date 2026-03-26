# ---------------------------------------------------------------------------
# Extractor — PDF Text Extraction into section buckets
# ---------------------------------------------------------------------------
# This module extracts text from ACL Anthology PDFs and organizes it by
# section. The goal is not perfect parsing — it is to give Gemini enough
# structured text to answer four yes/no screening questions reliably.
#
# Extraction strategy:
#   1. Extract full text from PDF using pypdf.
#   2. Detect section boundaries using header pattern matching.
#   3. Return a dict mapping PaperSections → extracted text.
#   4. If a section is not found, fall back to first N=3 pages of full text.
#
# Section mapping:
#   - Abstract      → PaperSections.ABSTRACT
#   - Introduction  → PaperSections.INTRODUCTION
#   - Conclusion / Discussion / Future Work → PaperSections.CONCLUSION
#   - Method / Annotation / Data Collection → PaperSections.METHODS
#   - Results / Experiments / Evaluation    → PaperSections.RESULTS
#   - Fallback (no sections found)          → PaperSections.FULL_TEXT_FALLBACK
# ---------------------------------------------------------------------------


from __future__ import annotations
import re
from pathlib import Path
from pypdf import PdfReader
from src.models import PaperSections


SECTION_PATTERNS: dict[PaperSections, list[str]] = {
    PaperSections.ABSTRACT: [
        r"abstract"
    ],
    PaperSections.INTRODUCTION: [
        r"\d*\.?\s*introduction"
    ],
    PaperSections.CONCLUSION: [
        r"\d*\.?\s*conclusion[s]?",
        r"\d*\.?\s*discussion",
        r"\d*\.?\s*future work",
        r"\d*\.?\s*future direction[s]?"
    ],
    PaperSections.METHODS: [
        r"\d*\.?\s*method[s]?",
        r"\d*\.?\s*methodology",
        r"\d*\.?\s*annotation[s]?",
        r"\d*\.?\s*data collection",
        r"\d*\.?\s*dataset[s]?",
    ],
    PaperSections.RESULTS: [
        r"\d*\.?\s*results?",
        r"\d*\.?\s*results?\s+and\s+discussion",
        r"\d*\.?\s*experiments?",
        r"\d*\.?\s*experimental setting[s]?",
        r"\d*\.?\s*evaluation"
    ],
}


def extract_raw_text(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return '\n'.join(pages)


def detect_sections(text: str) -> dict[PaperSections, str]:
    text_lower = text.lower()
    section_positions: list[tuple[int, PaperSections]] = []

    for section, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            match = re.search(
                rf"^\s*{pattern}\s*$", text_lower, re.MULTILINE | re.IGNORECASE
            )
            if match:
                section_positions.append((match.start(), section))
                break

    section_positions.sort(key=lambda x: x[0])

    results: dict[PaperSections, str] = {}
    for i, (start, section) in enumerate(section_positions):
        end = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)
        results[section] = text[start:end].strip()

    return results


def extract_fallback(pdf_path: Path, num_pages: int = 3) -> dict[PaperSections, str]:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages[:num_pages]:
        text = page.extract_text()
        if text:
            pages.append(text)
    return {PaperSections.FULL_TEXT_FALLBACK:"\n".join(pages)}


def extract_sections(pdf_path: Path) -> dict[PaperSections, str]:
    raw_text = extract_raw_text(pdf_path)
    if not raw_text.strip():
        return {PaperSections.FULL_TEXT_FALLBACK: ""}
    
    sections = detect_sections(raw_text)
    if not sections:
        return extract_fallback(pdf_path)
    return sections




