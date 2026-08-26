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
    "gemma3_focused": PromptProfile(
        name="gemma3_focused",
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
        metadata={"status": "gemma3:4b optimized profile based on prompt benchmark"},
    ),
    "gemma4_focused": PromptProfile(
        name="gemma4_focused",
        cause_prompts={
            **DEFAULT_CAUSE_PROMPTS,
            CauseCode.ENTITY_MISSING: "nlp_list_ocr_cot",
            CauseCode.ENTITY_MISMATCH: "nlp_list_ocr_cot",
            CauseCode.SPATIAL_MISMATCH: "layout_v4",
            CauseCode.DOCUMENT_ELEMENT_MISMATCH: "layout_v4",
            CauseCode.VALUE_MISMATCH: "nlp_tag_cot",
            CauseCode.TEMPORAL_MISMATCH: "nlp_tag_cot",
            CauseCode.AMBIGUOUS_TARGET: "nlp_list_ocr_cot",
        },
        answerer_prompt="nlp_tag_cot",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "gemma4:e4b optimized profile based on metrics_summary_1.csv"},
    ),
    "qwen3vl_focused": PromptProfile(
        name="qwen3vl_focused",
        cause_prompts={
            # Layout v4 dominates: QUR=0.8824, UR=0.9714, best overall for spatial causes
            CauseCode.SPATIAL_MISMATCH: "layout_v4",
            CauseCode.DOCUMENT_ELEMENT_MISMATCH: "layout_v4",
            CauseCode.EVIDENCE_MISSING: "layout_v4",
            # DocEl CoT v3: QUR=0.7112, UR=0.9269, strong on document structure
            CauseCode.RELATION_MISMATCH: "docel_cot_v3",
            CauseCode.ANSWER_TYPE_MISMATCH: "docel_cot_v3",
            CauseCode.UNSUPPORTED_PRESUPPOSITION: "docel_cot_v3",
            # NLP List OCR: QUR=0.6310, UR=0.8994, best for entity/value causes
            # (NLP Tag avoided: QUR=0.4064, Error Rate=6.42%)
            CauseCode.ENTITY_MISSING: "nlp_list_ocr",
            CauseCode.ENTITY_MISMATCH: "nlp_list_ocr",
            CauseCode.VALUE_MISMATCH: "nlp_list_ocr",
            CauseCode.TEMPORAL_MISMATCH: "nlp_list_ocr",
            CauseCode.AMBIGUOUS_TARGET: "nlp_list_ocr_cot",
            CauseCode.EXTRACTION_FAILURE: "answerability_verifier_v1",
        },
        # Layout v4 as answerer: best QUR/UR overall for Qwen3-VL 8B
        answerer_prompt="layout_v4",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "qwen3-vl:8b optimized profile based on metrics_summary_1.csv"},
    ),
    "phi35_focused": PromptProfile(
        name="phi35_focused",
        cause_prompts={
            # Layout v1 dominates: QUR=0.8503, UR=0.9576, best overall for Phi-3.5
            CauseCode.SPATIAL_MISMATCH: "layout_v1",
            CauseCode.DOCUMENT_ELEMENT_MISMATCH: "layout_v1",
            CauseCode.EVIDENCE_MISSING: "layout_v1",
            # DocEl CoT v3: QUR=0.7433, UR=0.9195, strong on document structure
            CauseCode.RELATION_MISMATCH: "docel_cot_v3",
            CauseCode.ANSWER_TYPE_MISMATCH: "docel_cot_v3",
            CauseCode.UNSUPPORTED_PRESUPPOSITION: "docel_cot_v3",
            # DocEl CoT v3 also used for entity/value/temporal causes because
            # NLP List and NLP Tag crash on Phi-3.5 (error rate >60% / ~6%)
            CauseCode.ENTITY_MISSING: "docel_cot_v3",
            CauseCode.ENTITY_MISMATCH: "docel_cot_v3",
            CauseCode.VALUE_MISMATCH: "docel_cot_v3",
            CauseCode.TEMPORAL_MISMATCH: "docel_cot_v3",
            CauseCode.AMBIGUOUS_TARGET: "docel_cot_v3",
            CauseCode.EXTRACTION_FAILURE: "answerability_verifier_v1",
        },
        # Layout v1 as answerer: best QUR/UR overall for Phi-3.5-Vision
        answerer_prompt="layout_v1",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "phi-3.5-vision optimized profile based on metrics_summary.csv"},
    ),
    "qwen25_focused": PromptProfile(
        name="qwen25_focused",
        cause_prompts={
            # NLP Tag CoT dominates on Qwen 2.5: QUR=0.8235, UR=0.9554 (highest overall)
            CauseCode.ENTITY_MISSING: "nlp_tag_cot",
            CauseCode.ENTITY_MISMATCH: "nlp_tag_cot",
            CauseCode.VALUE_MISMATCH: "nlp_tag_cot",
            CauseCode.TEMPORAL_MISMATCH: "nlp_tag_cot",
            CauseCode.RELATION_MISMATCH: "nlp_tag_cot",
            # NLP List CoT: strong on ambiguous targets & presuppositions (QUR=0.5187, UR=0.8333)
            CauseCode.AMBIGUOUS_TARGET: "nlp_list_cot",
            CauseCode.UNSUPPORTED_PRESUPPOSITION: "nlp_list_cot",
            # Layout v4: best for geometric & structural causes (QUR=0.4332, UR=0.6985)
            CauseCode.SPATIAL_MISMATCH: "layout_v4",
            CauseCode.DOCUMENT_ELEMENT_MISMATCH: "layout_v4",
            CauseCode.EVIDENCE_MISSING: "layout_v4",
            # DocEl CoT v4 for answer type consistency
            CauseCode.ANSWER_TYPE_MISMATCH: "docel_cot_v4",
            CauseCode.EXTRACTION_FAILURE: "answerability_verifier_v1",
        },
        # NLP Tag CoT as answerer: highest QUR (82.35%) and UR (95.54%) for Qwen 2.5
        answerer_prompt="nlp_tag_cot",
        verifier_prompt="answerability_verifier_v1",
        metadata={"status": "qwen2.5-vl:3b optimized profile based on metrics_summary.csv"},
    ),
}


# Assign a profile name to a model after model-level prompt analysis. Exact model
# names and lowercase substrings are both accepted. Empty means use PROMPT_PROFILE.
MODEL_PROFILE_MAP: dict[str, str] = {
    "gemma3": "gemma3_focused",
    "gemma-3": "gemma3_focused",
    "gemma4": "gemma4_focused",
    "gemma-4": "gemma4_focused",
    "qwen3-vl": "qwen3vl_focused",
    "qwen3vl": "qwen3vl_focused",
    "qwen2.5": "qwen25_focused",
    "qwen2-5": "qwen25_focused",
    "qwen25": "qwen25_focused",
    "phi3.5": "phi35_focused",
    "phi-3.5": "phi35_focused",
    "phi35": "phi35_focused",
}


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
