# ---------------------------------------------------------------------------
# Models — Pydantic Data Models for Screening papers
# ---------------------------------------------------------------------------
# Defines the core data structures used across the pipeline.
#
# Enums:
#   - CriterionLabel    : yes / no answer for each screening question
#   - ConfidenceLevel   : high / medium / low model confidence
#   - FinalBucket       : routing destination (to_read, maybe_recheck, maybe_borderline,
#                         filtered_out)
#   - PaperSections     : sections extracted from PDF by extractor.py
#
# Models:
#   - CriterionResult   : stores label, confidence, quote, section, and
#                         justification for a single screening question
#   - PaperRecord       : full record for one paper moving through the
#                         pipeline, containing four CriterionResult objects
#                         and pipeline metadata
#
# Validators:
#   - score must equal the number of yes answers across q1–q4
#   - manual_review must be True if any criterion has low confidence
# ---------------------------------------------------------------------------


from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, model_validator


class CriterionLabel(str, Enum):
    YES = 'yes'
    NO = 'no'


class ConfidenceLevel(str, Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class FinalBucket(str, Enum):
    TO_READ = 'to_read'
    MAYBE_RECHECK = 'maybe_recheck'
    MAYBE_BORDERLINE = 'maybe_borderline'
    FILTERED_OUT = 'filtered_out'


class PaperSections(str, Enum):
    ABSTRACT = 'abstract'
    INTRODUCTION = 'introduction'
    CONCLUSION = 'conclusion'
    METHODS = 'methods'
    RESULTS = 'results'
    APPENDIX = 'appendix'
    FULL_TEXT_FALLBACK = 'full_text_fallback'


class CriterionResult(BaseModel):
    label: CriterionLabel
    confidence: ConfidenceLevel
    quote: str | None = None
    section: PaperSections | None = None
    justification: str | None = None


class PaperRecord(BaseModel):
    paper_id: str
    title: str | None = None

    q1: CriterionResult
    q2: CriterionResult
    q3: CriterionResult
    q4: CriterionResult

    score: int
    bucket: FinalBucket
    manual_review: bool = False
    manual_review_reason: str | None = None

    model_version: str
    prompt_version: str
    timestamp: str
    retry_used: bool = False
    retry_count: int = 0

    @model_validator(mode = 'after')
    def check_score_matching_labels(self) -> PaperRecord:
        score = sum(
            int(q.label == CriterionLabel.YES) for q in [self.q1, self.q2, self.q3, self.q4]
        )
        if self.score != score:
            raise ValueError(f"Score {self.score} does not match actual yes count {score}")
        return self
    
    @model_validator(mode = 'after')
    def check_manual_review_flag(self) -> PaperRecord:
        low_confidence = any(
            q.confidence == ConfidenceLevel.LOW for q in [self.q1, self.q2, self.q3, self.q4]
        )
        if low_confidence and not self.manual_review:
            raise ValueError("manual review must be True if any of the criterion has low confidence")
        return self





