"""Prompt construction shared by all strategy families."""

import json
from collections.abc import Iterable
from typing import Any

from diagnostic_agent.schemas import CauseCode, PromptSpec


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def _evidence_sections(context: dict[str, Any], requirements: Iterable[str]) -> str:
    sections = []
    required = set(requirements)

    if "plain_ocr" in required:
        sections.append(f"### PLAIN OCR\n{context.get('plain_ocr') or '[not available]'}")
    if "structured_ocr" in required:
        sections.append(
            f"### STRUCTURED OCR AND DOCUMENT ELEMENTS\n"
            f"{context.get('structured_ocr') or '[not available]'}"
        )
    if "tagged_ocr" in required:
        sections.append(
            f"### OCR WITH INLINE ENTITY TAGS\n"
            f"{context.get('tagged_ocr') or '[not available]'}"
        )
    if "entity_lists" in required:
        sections.append(
            "### ENTITY LISTS\n"
            f"Question entities: {_json(context.get('question_entities', []))}\n"
            f"Document entities: {_json(context.get('document_entities', []))}"
        )
    if "layout" in required:
        sections.append(
            "### LAYOUT SUMMARY\n"
            f"Document elements: {_json(context.get('document_elements', []))}\n"
            f"Observed quadrants: {_json(context.get('quadrants', []))}\n"
            f"Page count: {len(context.get('image_paths', []))}"
        )
    if "images" in required:
        sections.append(
            "### DOCUMENT IMAGES\n"
            "The document page images are attached to this request. Inspect every attached page."
        )

    return "\n\n".join(sections)


def _diagnostic_contract(context: dict[str, Any]) -> str:
    return f"""
### DIAGNOSTIC TASK
Test this candidate cause only: {context.get('cause')}.
Candidate rationale: {context.get('rationale', '')}
Question analysis:
{_json(context.get('question_analysis', {}))}

Search for evidence both FOR and AGAINST the candidate cause. A missing match is not
enough to confirm unanswerability when page coverage or extraction quality is incomplete.

Return one JSON object and no other text:
{{
  "cause": "{context.get('cause')}",
  "status": "confirmed | rejected | undetermined",
  "expected": "value or null",
  "observed": ["values found in the document"],
  "evidence_for": [
    {{"page": 1, "document_element": "Table", "quadrant": "Q3", "snippet": "exact evidence"}}
  ],
  "evidence_against": [],
  "explanation": "1-2 sentence plain-language explanation of why this cause was confirmed, rejected, or left undetermined, referencing the specific evidence found",
  "confidence": "high | medium | low",
  "next_test": null
}}
""".strip()


def _answer_contract(context: dict[str, Any]) -> str:
    return f"""
### ANSWERING TASK
The diagnostic tests did not confirm an unanswerability cause. Determine whether a direct,
contextually valid answer is supported by the evidence. Do not infer missing information.

Question analysis:
{_json(context.get('question_analysis', {}))}

Diagnostic results:
{_json(context.get('diagnostic_results', []))}

Return one JSON object and no other text:
{{
  "status": "supported | unsupported | ambiguous",
  "answer": "concise answer or null",
  "evidence": [
    {{"page": 1, "document_element": "Plain Text", "snippet": "exact support"}}
  ],
  "confidence": "high | medium | low"
}}
""".strip()


def make_strategy_spec(
    *,
    name: str,
    family: str,
    description: str,
    strategy: str,
    required_evidence: Iterable[str],
    supported_causes: Iterable[CauseCode],
    include_images: bool = False,
) -> PromptSpec:
    requirements = frozenset(required_evidence)

    def builder(context: dict[str, Any]) -> str:
        mode = context.get("mode", "diagnostic")
        contract = _answer_contract(context) if mode == "answer" else _diagnostic_contract(context)
        return (
            "You are a document VQA evidence analyst. Use the selected reasoning strategy, "
            "but follow the structured task and output contract below.\n\n"
            f"### SELECTED STRATEGY: {name}\n{strategy.strip()}\n\n"
            f"### QUESTION\n{context.get('question', '')}\n\n"
            f"{_evidence_sections(context, requirements)}\n\n"
            f"{contract}"
        )

    return PromptSpec(
        name=name,
        family=family,
        description=description,
        required_evidence=requirements,
        supported_causes=frozenset(supported_causes),
        include_images=include_images,
        builder=builder,
    )


def build_question_analysis_prompt(context: dict[str, Any]) -> str:
    return f"""You analyze document questions before looking for an answer.

Question: {context.get('question', '')}
Document page count: {len(context.get('image_paths', []))}

Decompose the question without deciding whether it is answerable. Return one JSON object:
{{
  "answer_type": "person | organization | location | date | number | text | boolean | other",
  "entities": [{{"text": "entity", "type": "semantic type"}}],
  "relations": ["relations required by the question"],
  "constraints": ["counts, dates, comparisons, or other restrictions"],
  "spatial_references": ["page, section, quadrant, table, figure, header, footer"],
  "document_element_references": ["Table", "Figure"],
  "presuppositions": ["facts the question assumes to be true"]
}}
Return JSON only."""


QUESTION_ANALYSIS_SPEC = PromptSpec(
    name="question_analysis_v1",
    family="control",
    description="Structured decomposition of the question before evidence inspection.",
    required_evidence=frozenset(),
    supported_causes=frozenset(),
    include_images=False,
    builder=build_question_analysis_prompt,
)


VERIFIER_SPEC = make_strategy_spec(
    name="answerability_verifier_v1",
    family="control",
    description="Cross-evidence verifier for unresolved diagnostic hypotheses.",
    strategy="""
Compare the question constraints against all available evidence. Distinguish a semantic
contradiction from missing pages, weak OCR, or extraction failure. Confirm a cause only when
the mismatch is explicit and no valid supporting context was found in the covered pages.
""",
    required_evidence={"structured_ocr", "tagged_ocr", "entity_lists", "layout"},
    supported_causes=set(CauseCode),
)