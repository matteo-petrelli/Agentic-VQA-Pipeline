"""Prompt policies selectable independently for each model.

The profiles below are configuration templates, not claims about model quality.
They can be replaced after comparing prompt performance by model and cause.
"""

from copy import deepcopy
from typing import Any

from diagnostic_agent.prompts.catalog import get_prompt, validate_prompt_for_cause
from diagnostic_agent.schemas import CauseCode, PromptProfile


DEFAULT_CAUSE_PROMPTS = {
    CauseCode.ENTITY_MISSING: "nlp_tag_cot",
    CauseCode.ENTITY_MISMATCH: "nlp_tag_cot",
    CauseCode.VALUE_MISMATCH: "nlp_tag_cot",
    CauseCode.RELATION_MISMATCH: "docel_cot_v4",
    CauseCode.ANSWER_TYPE_MISMATCH: "docel_cot_v4",
    CauseCode.DOCUMENT_ELEMENT_MISMATCH: "docel_cot_v4",
    CauseCode.SPATIAL_MISMATCH: "layout_v4",
    CauseCode.TEMPORAL_MISMATCH: "nlp_tag_cot",
    CauseCode.UNSUPPORTED_PRESUPPOSITION: "docel_cot_v4",
    CauseCode.AMBIGUOUS_TARGET: "nlp_list_ocr_cot",
    CauseCode.EVIDENCE_MISSING: "layout_v4",
    CauseCode.EXTRACTION_FAILURE: "answerability_verifier_v1",
}


PROMPT_PROFILES: dict[str, PromptProfile] = {
    "default": PromptProfile(
        name="default",
        cause_prompts=DEFAULT_CAUSE_PROMPTS,
        answerer_prompt="docel_cot_v4",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "initial configuration; requires model-specific evaluation"},
    ),
    "entity_focused": PromptProfile(
        name="entity_focused",
        cause_prompts={
            **DEFAULT_CAUSE_PROMPTS,
            CauseCode.RELATION_MISMATCH: "nlp_list_ocr_cot",
            CauseCode.UNSUPPORTED_PRESUPPOSITION: "nlp_list_ocr_cot",
        },
        answerer_prompt="nlp_list_ocr_cot",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "candidate profile; requires evaluation"},
    ),
    "document_focused": PromptProfile(
        name="document_focused",
        cause_prompts={
            **DEFAULT_CAUSE_PROMPTS,
            CauseCode.ENTITY_MISSING: "docel_cot_v3",
            CauseCode.ENTITY_MISMATCH: "docel_cot_v3",
            CauseCode.VALUE_MISMATCH: "docel_cot_v3",
            CauseCode.TEMPORAL_MISMATCH: "docel_cot_v3",
            CauseCode.AMBIGUOUS_TARGET: "docel_cot_v3",
        },
        answerer_prompt="docel_cot_v3",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "candidate profile; requires evaluation"},
    ),
    "layout_focused": PromptProfile(
        name="layout_focused",
        cause_prompts={
            **DEFAULT_CAUSE_PROMPTS,
            CauseCode.DOCUMENT_ELEMENT_MISMATCH: "layout_v3",
            CauseCode.SPATIAL_MISMATCH: "layout_v3",
            CauseCode.EVIDENCE_MISSING: "layout_v3",
        },
        answerer_prompt="baseline_ocr",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "candidate profile; requires evaluation"},
    ),
}


# Assign a profile name to a model after model-level prompt analysis. Exact model
# names and lowercase substrings are both accepted. Empty means use PROMPT_PROFILE.
MODEL_PROFILE_MAP: dict[str, str] = {}


def _validate_profile(profile: PromptProfile) -> None:
    get_prompt(profile.question_analyzer_prompt)
    get_prompt(profile.answerer_prompt)
    get_prompt(profile.verifier_prompt)
    missing = set(CauseCode).difference(profile.cause_prompts)
    if missing:
        raise ValueError(
            f"Profile '{profile.name}' has no prompts for: "
            + ", ".join(sorted(cause.value for cause in missing))
        )
    for cause, prompt_name in profile.cause_prompts.items():
        validate_prompt_for_cause(prompt_name, cause)


def _model_profile_name(model_name: str, fallback: str) -> str:
    normalized = model_name.lower()
    if normalized in MODEL_PROFILE_MAP:
        return MODEL_PROFILE_MAP[normalized]
    for model_pattern, profile_name in MODEL_PROFILE_MAP.items():
        if model_pattern.lower() in normalized:
            return profile_name
    return fallback


def resolve_prompt_profile(
    model_name: str,
    profile_name: str = "default",
    overrides: dict[str, Any] | None = None,
) -> PromptProfile:
    selected_name = _model_profile_name(model_name, profile_name)
    try:
        selected = deepcopy(PROMPT_PROFILES[selected_name])
    except KeyError as exc:
        available = ", ".join(sorted(PROMPT_PROFILES))
        raise ValueError(
            f"Unknown prompt profile '{selected_name}'. Available: {available}"
        ) from exc

    overrides = overrides or {}
    selected.name = f"{selected.name}@{model_name}"
    selected.question_analyzer_prompt = overrides.get(
        "question_analyzer_prompt", selected.question_analyzer_prompt
    )
    selected.answerer_prompt = overrides.get("answerer_prompt", selected.answerer_prompt)
    selected.verifier_prompt = overrides.get("verifier_prompt", selected.verifier_prompt)

    cause_overrides = overrides.get("cause_prompts", {})
    for cause_name, prompt_name in cause_overrides.items():
        selected.cause_prompts[CauseCode(cause_name)] = prompt_name

    _validate_profile(selected)
    return selected


for _profile in PROMPT_PROFILES.values():
    _validate_profile(_profile)