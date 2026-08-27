"""Parsing and normalization for model-produced structured outputs."""

import json
import re
from typing import Any

from diagnostic_agent.schemas import CauseCode, CauseStatus, Confidence


def parse_json_object(response: str) -> dict[str, Any]:
    cleaned = re.sub(r"<think>.*?</think>", "", str(response), flags=re.DOTALL)
    cleaned = re.sub(r"```(?:json)?|```", "", cleaned).strip()
    try:
        value = json.loads(cleaned)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start == -1:
        return {}

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
        elif not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(cleaned[start : index + 1])
                    except json.JSONDecodeError:
                        return {}
    return {}


def confidence_value(value: Any) -> int:
    if isinstance(value, int):
        return max(Confidence.LOW, min(Confidence.HIGH, value))
    normalized = str(value or "").strip().lower()
    if normalized == "high":
        return Confidence.HIGH
    if normalized == "medium":
        return Confidence.MEDIUM
    return Confidence.LOW


def normalize_question_analysis(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "answer_type": str(data.get("answer_type") or "other"),
        "entities": data.get("entities") if isinstance(data.get("entities"), list) else [],
        "relations": data.get("relations") if isinstance(data.get("relations"), list) else [],
        "constraints": data.get("constraints") if isinstance(data.get("constraints"), list) else [],
        "spatial_references": (
            data.get("spatial_references")
            if isinstance(data.get("spatial_references"), list)
            else []
        ),
        "document_element_references": (
            data.get("document_element_references")
            if isinstance(data.get("document_element_references"), list)
            else []
        ),
        "presuppositions": (
            data.get("presuppositions")
            if isinstance(data.get("presuppositions"), list)
            else []
        ),
    }


def normalize_diagnostic_result(
    data: dict[str, Any],
    cause: CauseCode | str,
    prompt_name: str,
    raw_response: str,
    coverage: float,
) -> dict[str, Any]:
    cause_code = CauseCode(cause)
    status_value = str(data.get("status") or CauseStatus.UNDETERMINED.value).lower()
    try:
        status = CauseStatus(status_value).value
    except ValueError:
        status = CauseStatus.UNDETERMINED.value

    return {
        "cause": cause_code.value,
        "status": status,
        "expected": data.get("expected"),
        "observed": data.get("observed") if isinstance(data.get("observed"), list) else [],
        "evidence_for": (
            data.get("evidence_for") if isinstance(data.get("evidence_for"), list) else []
        ),
        "evidence_against": (
            data.get("evidence_against")
            if isinstance(data.get("evidence_against"), list)
            else []
        ),
        "explanation": str(data.get("explanation") or ""),
        "coverage": max(0.0, min(1.0, float(coverage))),
        "confidence": int(confidence_value(data.get("confidence"))),
        "prompt_name": prompt_name,
        "raw_response": raw_response,
        "next_test": data.get("next_test"),
    }


def normalize_answer_result(data: dict[str, Any], raw_response: str) -> dict[str, Any]:
    status = str(data.get("status") or "unsupported").lower()
    if status not in {"supported", "unsupported", "ambiguous"}:
        status = "unsupported"
    answer = data.get("answer")
    return {
        "status": status,
        "answer": str(answer).strip() if answer is not None else None,
        "evidence": data.get("evidence") if isinstance(data.get("evidence"), list) else [],
        "confidence": int(confidence_value(data.get("confidence"))),
        "raw_response": raw_response,
    }