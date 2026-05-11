# ---------------------------------------------------------------------------
# Verifier Models — Pydantic Data Models for Verifiability Pipeline
# ---------------------------------------------------------------------------
# Mirrors the structure of models.py but for the three verifiability prompts.
#
# Enums:
#   - SubjectivityDefType     : Explicit / Implicit / None
#   - PillarMatch             : Pillar 1 / Pillar 2 / Pillar 3
#   - MatchesWorkingDef       : Full / Partial / No
#   - AuthorTaskLabel         : Subjective / Objective / Mixed / Not Claimed
#   - TaxonomyCategoryMatch   : Category A / B / C / Contradicts / New Task
#   - ReasoningCode           : R1–R7
#   - StrategyCode            : A1–A5, B1–B9
#   - PipelineStage           : Annotation / Training / Evaluation / Dataset Release
#   - PrimaryPosition         : Noise / Signal / Mixed
#   - InternalConsistency     : Consistent / Inconsistent / Not Applicable
#
# Models:
#   - DefinitionResult        : output of definition_v1 prompt for one paper
#   - FocalTask               : one task entry inside TaxonomyResult
#   - TaxonomyResult          : output of taxonomy_v1 prompt for one paper
#   - HandlingStrategy        : one strategy entry inside HandlingResult
#   - HandlingResult          : output of handling_v1 prompt for one paper
# ---------------------------------------------------------------------------

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class PillarMatch(str, Enum):
    PILLAR_1 = "Pillar 1"
    PILLAR_2 = "Pillar 2"
    PILLAR_3 = "Pillar 3"


# ---------------------------------------------------------------------------
# Definition prompt enums and model
# ---------------------------------------------------------------------------

class SubjectivityDefType(str, Enum):
    EXPLICIT = "Explicit"
    IMPLICIT = "Implicit"
    NONE = "None"


class MatchesWorkingDef(str, Enum):
    FULL = "Full"
    PARTIAL = "Partial"
    NO = "No"


class DefinitionResult(BaseModel):
    paper_id: str
    subjectivity_def_type: SubjectivityDefType
    pillar_match: list[PillarMatch]
    matches_working_definition: MatchesWorkingDef
    definition_gap_identified: str | None = None
    subjectivity_distinguished_from: list[str] | str | None = None
    supporting_definition_quote: str | None = None
    thought_process: str | None = None


# ---------------------------------------------------------------------------
# Taxonomy prompt enums and models
# ---------------------------------------------------------------------------

class AuthorTaskLabel(str, Enum):
    SUBJECTIVE = "Subjective"
    OBJECTIVE = "Objective"
    MIXED = "Mixed"
    PARTIALLY_SUBJECTIVE = "Partially Subjective"
    NOT_CLAIMED = "Not Claimed"


class TaxonomyCategoryMatch(str, Enum):
    CATEGORY_A = "Category A"
    CATEGORY_B = "Category B"
    CATEGORY_C = "Category C"
    CONTRADICTS = "Contradicts Taxonomy"
    EXTENDS = "Extends Taxonomy"
    NEW_TASK = "New Task"


class ReasoningCode(str, Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"


class FocalTask(BaseModel):
    task_name: str
    author_task_label: AuthorTaskLabel
    taxonomy_category_match: TaxonomyCategoryMatch
    reasoning_codes: list[ReasoningCode]
    reasoning_gap: str | None = None
    task_supporting_quote: str | None = None
    alignment_note: str | None = None


class TaxonomyResult(BaseModel):
    paper_id: str
    focal_tasks: list[FocalTask]
    thought_process: str | None = None


# ---------------------------------------------------------------------------
# Handling prompt enums and models
# ---------------------------------------------------------------------------

class StrategyCode(str, Enum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    B5 = "B5"
    B6 = "B6"
    B7 = "B7"
    B8 = "B8"
    B9 = "B9"


class PipelineStage(str, Enum):
    ANNOTATION = "Annotation"
    TRAINING = "Training"
    EVALUATION = "Evaluation"
    DATASET_RELEASE = "Dataset Release"


class PrimaryPosition(str, Enum):
    NOISE = "Noise (A)"
    SIGNAL = "Signal (B)"
    MIXED = "Mixed"


class InternalConsistency(str, Enum):
    CONSISTENT = "Consistent"
    INCONSISTENT = "Inconsistent"
    NOT_APPLICABLE = "Not Applicable"


class HandlingStrategy(BaseModel):
    strategy_code: StrategyCode
    pipeline_stage: PipelineStage
    quantification_metric: str | None = None
    handling_supporting_quote: str | None = None


class HandlingResult(BaseModel):
    paper_id: str
    handling_strategies: list[HandlingStrategy]
    primary_position: PrimaryPosition
    handling_gap_identified: str | None = None
    internal_consistency: InternalConsistency
    inconsistency_note: str | None = None
    thought_process: str | None = None