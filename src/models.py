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
    MAYBE = 'maybe'
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





