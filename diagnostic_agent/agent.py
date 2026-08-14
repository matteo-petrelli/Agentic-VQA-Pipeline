"""Public API for the unanswerability diagnostic agent."""

from typing import Any

from diagnostic_agent.graph import build_diagnostic_graph
from diagnostic_agent.nodes import InferenceEngine
from diagnostic_agent.profiles import resolve_prompt_profile
from diagnostic_agent.schemas import AgentState, Confidence


class UnanswerabilityDiagnosticAgent:
    def __init__(
        self,
        engine: InferenceEngine,
        *,
        model_name: str,
        profile_name: str = "default",
        prompt_overrides: dict[str, Any] | None = None,
        max_diagnostic_tests: int = 4,
        min_evidence_coverage: float = 1.0,
    ):
        self.profile = resolve_prompt_profile(model_name, profile_name, prompt_overrides)
        self.graph = build_diagnostic_graph(
            engine,
            self.profile,
            max_diagnostic_tests=max_diagnostic_tests,
            min_evidence_coverage=min_evidence_coverage,
        )

    def process_question(self, question: str, image_paths: list[str]) -> dict[str, Any]:
        if not question.strip():
            raise ValueError("Question cannot be empty.")
        if not image_paths:
            raise ValueError("At least one document image is required.")

        initial_state: AgentState = {
            "question": question,
            "image_paths": image_paths,
            "trace": [],
            "diagnostic_results": [],
            "prompts_used": [],
            "tests_run": 0,
            "answerability_confidence": int(Confidence.LOW),
            "cause_confidence": int(Confidence.LOW),
            "answer_confidence": None,
            "forced_exit": False,
        }
        final_state = self.graph.invoke(initial_state)
        return {
            "answerability": final_state["answerability"],
            "primary_cause": final_state.get("primary_cause"),
            "cause_explanation": final_state.get("cause_explanation"),
            "secondary_causes": final_state.get("secondary_causes", []),
            "diagnostic_results": final_state.get("diagnostic_results", []),
            "evidence_coverage": final_state.get("evidence_coverage", 0.0),
            "extraction_errors": final_state.get("extraction_errors", []),
            "final_answer": final_state["final_answer"],
            "answerability_confidence": final_state.get("answerability_confidence", 1),
            "cause_confidence": final_state.get("cause_confidence", 1),
            "answer_confidence": final_state.get("answer_confidence"),
            "prompt_profile": self.profile.name,
            "prompts_used": final_state.get("prompts_used", []),
            "tests_run": final_state.get("tests_run", 0),
            "steps": len(final_state.get("trace", [])),
            "trace": final_state.get("trace", []),
        }