# ---------------------------------------------------------------------------
# Tests — PaperRecord and CriterionResult Pydantic Models
# ---------------------------------------------------------------------------
# Validates that:
#   1. A valid PaperRecord initializes correctly.
#   2. A mismatched score raises a ValueError.
#   3. A low confidence criterion without manual_review=True raises a ValueError.
#   4. A missing required field raises a ValueError.
# ---------------------------------------------------------------------------


import pytest 
from src.models import (
    CriterionLabel, ConfidenceLevel, FinalBucket, PaperSections, CriterionResult, PaperRecord
)

def make_criterion(label, confidence, quote=None, section=None):
    return CriterionResult(
        label=label, confidence=confidence, quote=quote, section=section, justification=None
        )

#testing initialization
def test_valid_paper_record():
    record = PaperRecord(
        paper_id = 'test-1',
        title = 'title-1',
        q1 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
        q2 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
        q3 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
        q4 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
        score = 2,
        bucket = FinalBucket.MAYBE,
        manual_review = False,
        model_version='gemini',
        prompt_version='v1',
        timestamp="2026-01-01T00:00:00"
    )
    assert record.score == 2

#testing if setting wrong score raises error
def test_invalid_score():
    with pytest.raises(ValueError):
        PaperRecord(
            paper_id = 'test-2',
            title = 'title-2',
            q1 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
            q2 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH, quote='test-quote'),
            q3 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            q4 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            score = 2,
            bucket = FinalBucket.FILTERED_OUT,
            manual_review = False,
            model_version='gemini',
            prompt_version='v1',
            timestamp="2026-01-01T00:00:00"
        )

#testing manual review raises error for a LOW confidence record with a false flag.
def test_manual_review():
    with pytest.raises(ValueError):
        PaperRecord(
            paper_id = 'test-3',
            title = 'title-3',
            q1 = make_criterion(CriterionLabel.YES, ConfidenceLevel.LOW, quote='test-quote'),
            q2 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
            q3 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            q4 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            score = 2,
            bucket = FinalBucket.FILTERED_OUT,
            manual_review = False,
            model_version='gemini',
            prompt_version='v1',
            timestamp="2026-01-01T00:00:00"
        )

#model version is a required field. it should raise error if we do not define it
def test_required_fields():
    with pytest.raises(ValueError):
        PaperRecord(
            paper_id = 'test-4',
            title = 'title-4',
            q1 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
            q2 = make_criterion(CriterionLabel.YES, ConfidenceLevel.HIGH, quote='test-quote'),
            q3 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            q4 = make_criterion(CriterionLabel.NO, ConfidenceLevel.HIGH),
            score = 2,
            bucket = FinalBucket.FILTERED_OUT,
            manual_review = False,
            prompt_version='v1',
            timestamp="2026-01-01T00:00:00"
        )