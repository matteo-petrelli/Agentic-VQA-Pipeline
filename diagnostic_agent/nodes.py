"""Nodes and routing rules for the unanswerability diagnostic graph."""

import re
from typing import Any, Protocol

from diagnostic_agent.evidence import EvidenceExtractor
from diagnostic_agent.parsing import (
    normalize_answer_result,
    normalize_diagnostic_result,
    normalize_question_analysis,
    parse_json_object,
)
from diagnostic_agent.prompts.catalog import get_prompt
from diagnostic_agent.schemas import (
    AgentState,
    Answerability,
    CauseCode,
    CauseStatus,
    Confidence,
    PromptProfile,
)


class InferenceEngine(Protocol):
    def get_layout(self, image_path: str) -> list[dict[str, Any]]: ...

    def tag_text_with_gliner(self, text: str) -> tuple[str, list[str]]: ...

    def infer(
        self,
        prompt: str,
        image_paths: list[str] | None = None,
        *,
        json_mode: bool = True,
        temperature: float | None = None,
    ) -> str: ...


PIPELINE_CAUSES = {CauseCode.EVIDENCE_MISSING, CauseCode.EXTRACTION_FAILURE}


class DiagnosticNodes:
    def __init__(
        self,
        engine: InferenceEngine,
        profile: PromptProfile,
        *,
        max_diagnostic_tests: int,
        min_evidence_coverage: float,
    ):
        self.engine = engine
        self.profile = profile
        self.extractor = EvidenceExtractor(engine)
        self.max_diagnostic_tests = max_diagnostic_tests
        self.min_evidence_coverage = min_evidence_coverage

    def analyze_question(self, state: AgentState) -> dict[str, Any]:
        spec = get_prompt(self.profile.question_analyzer_prompt)
        response = self.engine.infer(spec.builder(dict(state)), json_mode=True, temperature=0.0)
        analysis = normalize_question_analysis(parse_json_object(response))
        return {
            "question_analysis": analysis,
            "trace": state.get("trace", [])
            + [{"node": "analyze_question", "prompt": spec.name, "result": analysis}],
        }

    def extract_base_evidence(self, state: AgentState) -> dict[str, Any]:
        evidence = self.extractor.extract(state["question"], state["image_paths"])
        return {
            **evidence,
            "trace": state.get("trace", [])
            + [
                {
                    "node": "extract_base_evidence",
                    "coverage": evidence["evidence_coverage"],
                    "errors": evidence["extraction_errors"],
                }
            ],
        }

    def generate_cause_hypotheses(self, state: AgentState) -> dict[str, Any]:
        analysis = state.get("question_analysis", {})
        hypotheses: dict[CauseCode, dict[str, Any]] = {}

        def add(cause: CauseCode, rationale: str, priority: int) -> None:
            current = hypotheses.get(cause)
            if current is None or priority < current["priority"]:
                hypotheses[cause] = {
                    "cause": cause.value,
                    "status": CauseStatus.SUSPECTED.value,
                    "rationale": rationale,
                    "priority": priority,
                }

        if analysis.get("entities") or state.get("question_entities"):
            add(CauseCode.ENTITY_MISSING, "The question contains explicit entities.", 20)
            add(CauseCode.ENTITY_MISMATCH, "Question entities may differ from document entities.", 25)

        answer_type = str(analysis.get("answer_type", "other")).lower()
        if answer_type in {"date", "number", "currency", "percentage", "quantity"}:
            add(CauseCode.VALUE_MISMATCH, f"The requested answer type is {answer_type}.", 10)
        if answer_type == "date" or _contains_temporal_signal(state["question"]):
            add(CauseCode.TEMPORAL_MISMATCH, "The question contains a temporal constraint.", 12)
        if answer_type and answer_type != "other":
            add(CauseCode.ANSWER_TYPE_MISMATCH, "The expected answer type must be present.", 45)

        if analysis.get("relations"):
            add(CauseCode.RELATION_MISMATCH, "The question requires one or more relations.", 30)
        if analysis.get("constraints"):
            add(CauseCode.VALUE_MISMATCH, "The question includes explicit constraints.", 15)
        if analysis.get("presuppositions"):
            add(
                CauseCode.UNSUPPORTED_PRESUPPOSITION,
                "The question contains presuppositions that require verification.",
                18,
            )
        if analysis.get("spatial_references"):
            add(CauseCode.SPATIAL_MISMATCH, "The question refers to page or position.", 8)
        if analysis.get("document_element_references"):
            add(
                CauseCode.DOCUMENT_ELEMENT_MISMATCH,
                "The question refers to a specific document element.",
                9,
            )

        if state.get("extraction_errors"):
            add(CauseCode.EXTRACTION_FAILURE, "One or more evidence extractors failed.", 2)
        if state.get("evidence_coverage", 0.0) < 1.0:
            add(CauseCode.EVIDENCE_MISSING, "Not all document pages were extracted.", 1)

        ordered = sorted(hypotheses.values(), key=lambda item: item["priority"])
        return {
            "cause_hypotheses": ordered,
            "diagnostic_results": [],
            "current_hypothesis_index": 0,
            "tests_run": 0,
            "prompts_used": [self.profile.question_analyzer_prompt],
            "next_action": "select_test" if ordered else "answer",
            "trace": state.get("trace", [])
            + [{"node": "generate_cause_hypotheses", "hypotheses": ordered}],
        }

    def select_diagnostic_test(self, state: AgentState) -> dict[str, Any]:
        hypotheses = state.get("cause_hypotheses", [])
        index = state.get("current_hypothesis_index", 0)
        if index >= len(hypotheses) or state.get("tests_run", 0) >= self.max_diagnostic_tests:
            return {"next_action": "verify"}

        cause = CauseCode(hypotheses[index]["cause"])
        prompt_name = self.profile.cause_prompts[cause]
        return {
            "current_cause": cause.value,
            "selected_prompt": prompt_name,
            "next_action": "run_test",
            "trace": state.get("trace", [])
            + [
                {
                    "node": "select_diagnostic_test",
                    "cause": cause.value,
                    "prompt": prompt_name,
                }
            ],
        }

    def run_diagnostic_test(self, state: AgentState) -> dict[str, Any]:
        cause = CauseCode(state["current_cause"])
        prompt_name = state["selected_prompt"]
        spec = get_prompt(prompt_name)
        hypothesis = state["cause_hypotheses"][state["current_hypothesis_index"]]
        context = {
            **dict(state),
            "mode": "diagnostic",
            "cause": cause.value,
            "rationale": hypothesis.get("rationale", ""),
        }
        response = self.engine.infer(
            spec.builder(context),
            state["image_paths"] if spec.include_images else None,
            json_mode=True,
            temperature=0.0,
        )
        result = normalize_diagnostic_result(
            parse_json_object(response),
            cause,
            prompt_name,
            response,
            state.get("evidence_coverage", 0.0),
        )
        return {
            "diagnostic_results": state.get("diagnostic_results", []) + [result],
            "prompts_used": state.get("prompts_used", []) + [prompt_name],
            "tests_run": state.get("tests_run", 0) + 1,
            "current_hypothesis_index": state.get("current_hypothesis_index", 0) + 1,
            "trace": state.get("trace", [])
            + [{"node": "run_diagnostic_test", "result": result}],
        }

    def assess_diagnostic_progress(self, state: AgentState) -> dict[str, Any]:
        semantic_confirmation = _best_confirmed_semantic_result(state)
        if semantic_confirmation and _coverage_is_sufficient(
            semantic_confirmation, self.min_evidence_coverage
        ):
            return _unanswerable_update(state, semantic_confirmation)

        if _has_confirmed_pipeline_failure(state):
            return _insufficient_update(state, "A pipeline or evidence-coverage cause was confirmed.")

        has_more = (
            state.get("current_hypothesis_index", 0) < len(state.get("cause_hypotheses", []))
            and state.get("tests_run", 0) < self.max_diagnostic_tests
        )
        return {"next_action": "select_test" if has_more else "verify"}

    def run_answerability_verifier(self, state: AgentState) -> dict[str, Any]:
        unresolved = [
            result
            for result in state.get("diagnostic_results", [])
            if result.get("status") == CauseStatus.UNDETERMINED.value
            and CauseCode(result["cause"]) not in PIPELINE_CAUSES
        ]
        if not unresolved:
            return {"next_action": "decide"}

        candidate = max(unresolved, key=lambda result: result.get("confidence", 0))
        cause = CauseCode(candidate["cause"])
        spec = get_prompt(self.profile.verifier_prompt)
        context = {
            **dict(state),
            "mode": "diagnostic",
            "cause": cause.value,
            "rationale": "Resolve the strongest undetermined diagnostic result.",
        }
        response = self.engine.infer(spec.builder(context), json_mode=True, temperature=0.0)
        result = normalize_diagnostic_result(
            parse_json_object(response),
            cause,
            spec.name,
            response,
            state.get("evidence_coverage", 0.0),
        )
        return {
            "diagnostic_results": state.get("diagnostic_results", []) + [result],
            "prompts_used": state.get("prompts_used", []) + [spec.name],
            "tests_run": state.get("tests_run", 0) + 1,
            "next_action": "decide",
            "trace": state.get("trace", [])
            + [{"node": "run_answerability_verifier", "result": result}],
        }

    def decide_answerability(self, state: AgentState) -> dict[str, Any]:
        semantic_confirmation = _best_confirmed_semantic_result(state)
        if semantic_confirmation and _coverage_is_sufficient(
            semantic_confirmation, self.min_evidence_coverage
        ):
            return _unanswerable_update(state, semantic_confirmation)

        if (
            state.get("evidence_coverage", 0.0) < self.min_evidence_coverage
            or _has_confirmed_pipeline_failure(state)
        ):
            return _insufficient_update(state, "Evidence coverage is below the decision threshold.")

        return {
            "answerability": Answerability.ANSWERABLE.value,
            "answerability_confidence": int(Confidence.MEDIUM),
            "next_action": "answer",
        }

    def run_answerer(self, state: AgentState) -> dict[str, Any]:
        spec = get_prompt(self.profile.answerer_prompt)
        context = {**dict(state), "mode": "answer"}
        response = self.engine.infer(
            spec.builder(context),
            state["image_paths"] if spec.include_images else None,
            json_mode=True,
            temperature=0.0,
        )
        answer_result = normalize_answer_result(parse_json_object(response), response)
        status = answer_result["status"]
        if status == "supported" and answer_result.get("answer"):
            answerability = Answerability.ANSWERABLE.value
            final_answer = answer_result["answer"]
            confidence = answer_result["confidence"]
        elif status == "ambiguous":
            answerability = Answerability.UNANSWERABLE.value
            final_answer = "Unable to determine"
            confidence = answer_result["confidence"]
        else:
            answerability = Answerability.INSUFFICIENT_EVIDENCE.value
            final_answer = "Unable to determine"
            confidence = int(Confidence.LOW)

        return {
            "answer_result": answer_result,
            "answerability": answerability,
            "primary_cause": (
                CauseCode.AMBIGUOUS_TARGET.value if status == "ambiguous" else None
            ),
            "final_answer": final_answer,
            "answerability_confidence": confidence,
            "cause_confidence": confidence if status == "ambiguous" else int(Confidence.LOW),
            "answer_confidence": confidence if status == "supported" else None,
            "prompts_used": state.get("prompts_used", []) + [spec.name],
            "next_action": "finalize",
            "trace": state.get("trace", [])
            + [{"node": "run_answerer", "prompt": spec.name, "result": answer_result}],
        }

    def finalize_diagnosis(self, state: AgentState) -> dict[str, Any]:
        answerability = state.get("answerability") or Answerability.INSUFFICIENT_EVIDENCE.value
        final_answer = state.get("final_answer")
        if not final_answer:
            final_answer = (
                "Unable to determine"
                if answerability != Answerability.ANSWERABLE.value
                else "Unable to determine"
            )
        return {
            "answerability": answerability,
            "final_answer": final_answer,
            "secondary_causes": _secondary_causes(state),
            "trace": state.get("trace", [])
            + [{"node": "finalize_diagnosis", "answerability": answerability}],
        }

    @staticmethod
    def route_selected_test(state: AgentState) -> str:
        return state.get("next_action", "verify")

    @staticmethod
    def route_progress(state: AgentState) -> str:
        return state.get("next_action", "verify")

    @staticmethod
    def route_decision(state: AgentState) -> str:
        return state.get("next_action", "finalize")


def _contains_temporal_signal(question: str) -> bool:
    return bool(
        re.search(
            r"\b(?:19|20)\d{2}\b|\b(?:year|date|month|day|when|before|after|during)\b",
            question,
            flags=re.IGNORECASE,
        )
    )


def _best_confirmed_semantic_result(state: AgentState) -> dict[str, Any] | None:
    confirmed = [
        result
        for result in state.get("diagnostic_results", [])
        if result.get("status") == CauseStatus.CONFIRMED.value
        and CauseCode(result["cause"]) not in PIPELINE_CAUSES
        and result.get("evidence_for")
    ]
    return max(confirmed, key=lambda result: result.get("confidence", 0), default=None)


def _coverage_is_sufficient(result: dict[str, Any], threshold: float) -> bool:
    return float(result.get("coverage", 0.0)) >= threshold


def _has_confirmed_pipeline_failure(state: AgentState) -> bool:
    return any(
        result.get("status") == CauseStatus.CONFIRMED.value
        and CauseCode(result["cause"]) in PIPELINE_CAUSES
        for result in state.get("diagnostic_results", [])
    )


def _unanswerable_update(
    state: AgentState, result: dict[str, Any]
) -> dict[str, Any]:
    return {
        "answerability": Answerability.UNANSWERABLE.value,
        "primary_cause": result["cause"],
        "final_answer": "Unable to determine",
        "answerability_confidence": result.get("confidence", int(Confidence.MEDIUM)),
        "cause_confidence": result.get("confidence", int(Confidence.MEDIUM)),
        "answer_confidence": None,
        "next_action": "finalize",
    }


def _insufficient_update(state: AgentState, reason: str) -> dict[str, Any]:
    pipeline_results = [
        result
        for result in state.get("diagnostic_results", [])
        if CauseCode(result["cause"]) in PIPELINE_CAUSES
    ]
    primary = (
        pipeline_results[-1]["cause"]
        if pipeline_results
        else CauseCode.EVIDENCE_MISSING.value
    )
    return {
        "answerability": Answerability.INSUFFICIENT_EVIDENCE.value,
        "primary_cause": primary,
        "final_answer": "Unable to determine",
        "answerability_confidence": int(Confidence.LOW),
        "cause_confidence": int(Confidence.MEDIUM),
        "answer_confidence": None,
        "next_action": "finalize",
        "trace": state.get("trace", [])
        + [{"node": "insufficient_evidence", "reason": reason}],
    }


def _secondary_causes(state: AgentState) -> list[str]:
    primary = state.get("primary_cause")
    return sorted(
        {
            result["cause"]
            for result in state.get("diagnostic_results", [])
            if result.get("status") == CauseStatus.CONFIRMED.value
            and result["cause"] != primary
        }
    )