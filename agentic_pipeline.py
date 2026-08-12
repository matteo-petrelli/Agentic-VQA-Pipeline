"""Stable pipeline facade for the LangGraph diagnostic agent."""

from typing import Any

import config
from diagnostic_agent import UnanswerabilityDiagnosticAgent


def _model_setting(mapping: dict[str, Any], model_name: str, default: Any) -> Any:
    normalized = model_name.lower()
    if normalized in mapping:
        return mapping[normalized]
    for pattern, value in mapping.items():
        if pattern.lower() in normalized:
            return value
    return default


class AgenticPipeline:
    def __init__(
        self,
        engine,
        *,
        model_name: str | None = None,
        profile_name: str | None = None,
        prompt_overrides: dict[str, Any] | None = None,
    ):
        selected_model = model_name or config.OLLAMA_VLM
        selected_profile = profile_name or _model_setting(
            config.MODEL_PROMPT_PROFILES,
            selected_model,
            config.PROMPT_PROFILE,
        )
        selected_overrides = prompt_overrides or _model_setting(
            config.MODEL_PROMPT_OVERRIDES, selected_model, {}
        )
        self.agent = UnanswerabilityDiagnosticAgent(
            engine,
            model_name=selected_model,
            profile_name=selected_profile,
            prompt_overrides=selected_overrides,
            max_diagnostic_tests=config.MAX_DIAGNOSTIC_TESTS,
            min_evidence_coverage=config.MIN_EVIDENCE_COVERAGE,
        )

    def process_question(self, question: str, image_paths: list[str]) -> dict[str, Any]:
        return self.agent.process_question(question, image_paths)
