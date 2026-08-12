"""Shared contracts for the unanswerability diagnostic graph."""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Callable, TypedDict


class Answerability(str, Enum):
    ANSWERABLE = "answerable"
    UNANSWERABLE = "unanswerable"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class CauseCode(str, Enum):
    ENTITY_MISSING = "ENTITY_MISSING"
    ENTITY_MISMATCH = "ENTITY_MISMATCH"
    VALUE_MISMATCH = "VALUE_MISMATCH"
    RELATION_MISMATCH = "RELATION_MISMATCH"
    ANSWER_TYPE_MISMATCH = "ANSWER_TYPE_MISMATCH"
    DOCUMENT_ELEMENT_MISMATCH = "DOCUMENT_ELEMENT_MISMATCH"
    SPATIAL_MISMATCH = "SPATIAL_MISMATCH"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    UNSUPPORTED_PRESUPPOSITION = "UNSUPPORTED_PRESUPPOSITION"
    AMBIGUOUS_TARGET = "AMBIGUOUS_TARGET"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    EXTRACTION_FAILURE = "EXTRACTION_FAILURE"


class CauseStatus(str, Enum):
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    UNDETERMINED = "undetermined"


class Confidence(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class EvidenceBlock(TypedDict, total=False):
    page: int
    image_path: str
    document_element: str
    quadrant: str
    snippet: str
    bbox: list[float]


class CauseHypothesis(TypedDict, total=False):
    cause: str
    status: str
    rationale: str
    priority: int


class DiagnosticResult(TypedDict, total=False):
    cause: str
    status: str
    expected: Any
    observed: list[Any]
    evidence_for: list[EvidenceBlock]
    evidence_against: list[EvidenceBlock]
    coverage: float
    confidence: int
    prompt_name: str
    raw_response: str
    next_test: str | None


class AgentState(TypedDict, total=False):
    question: str
    image_paths: list[str]
    question_analysis: dict[str, Any]
    pages: list[dict[str, Any]]
    structured_ocr: str
    tagged_ocr: str
    plain_ocr: str
    question_entities: list[str]
    document_entities: list[str]
    document_elements: list[str]
    quadrants: list[str]
    extraction_errors: list[str]
    evidence_coverage: float
    cause_hypotheses: list[CauseHypothesis]
    diagnostic_results: list[DiagnosticResult]
    current_hypothesis_index: int
    current_cause: str | None
    selected_prompt: str | None
    prompts_used: list[str]
    tests_run: int
    next_action: str
    answerability: str | None
    primary_cause: str | None
    secondary_causes: list[str]
    answer_result: dict[str, Any]
    final_answer: str | None
    answerability_confidence: int
    cause_confidence: int
    answer_confidence: int | None
    forced_exit: bool
    trace: list[dict[str, Any]]


PromptBuilder = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class PromptSpec:
    name: str
    family: str
    description: str
    required_evidence: frozenset[str]
    supported_causes: frozenset[CauseCode]
    include_images: bool
    builder: PromptBuilder


@dataclass
class PromptProfile:
    name: str
    cause_prompts: dict[CauseCode, str]
    answerer_prompt: str
    verifier_prompt: str
    question_analyzer_prompt: str = "question_analysis_v1"
    metadata: dict[str, Any] = field(default_factory=dict)