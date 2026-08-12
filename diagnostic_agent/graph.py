"""LangGraph assembly for the diagnostic workflow."""

from langgraph.graph import END, START, StateGraph

from diagnostic_agent.nodes import DiagnosticNodes, InferenceEngine
from diagnostic_agent.schemas import AgentState, PromptProfile


def build_diagnostic_graph(
    engine: InferenceEngine,
    profile: PromptProfile,
    *,
    max_diagnostic_tests: int,
    min_evidence_coverage: float,
):
    nodes = DiagnosticNodes(
        engine,
        profile,
        max_diagnostic_tests=max_diagnostic_tests,
        min_evidence_coverage=min_evidence_coverage,
    )
    graph = StateGraph(AgentState)
    graph.add_node("analyze_question", nodes.analyze_question)
    graph.add_node("extract_base_evidence", nodes.extract_base_evidence)
    graph.add_node("generate_cause_hypotheses", nodes.generate_cause_hypotheses)
    graph.add_node("select_diagnostic_test", nodes.select_diagnostic_test)
    graph.add_node("run_diagnostic_test", nodes.run_diagnostic_test)
    graph.add_node("assess_diagnostic_progress", nodes.assess_diagnostic_progress)
    graph.add_node("run_answerability_verifier", nodes.run_answerability_verifier)
    graph.add_node("decide_answerability", nodes.decide_answerability)
    graph.add_node("run_answerer", nodes.run_answerer)
    graph.add_node("finalize_diagnosis", nodes.finalize_diagnosis)

    graph.add_edge(START, "analyze_question")
    graph.add_edge("analyze_question", "extract_base_evidence")
    graph.add_edge("extract_base_evidence", "generate_cause_hypotheses")
    graph.add_edge("generate_cause_hypotheses", "select_diagnostic_test")
    graph.add_conditional_edges(
        "select_diagnostic_test",
        nodes.route_selected_test,
        {
            "run_test": "run_diagnostic_test",
            "verify": "run_answerability_verifier",
        },
    )
    graph.add_edge("run_diagnostic_test", "assess_diagnostic_progress")
    graph.add_conditional_edges(
        "assess_diagnostic_progress",
        nodes.route_progress,
        {
            "select_test": "select_diagnostic_test",
            "verify": "run_answerability_verifier",
            "finalize": "finalize_diagnosis",
        },
    )
    graph.add_edge("run_answerability_verifier", "decide_answerability")
    graph.add_conditional_edges(
        "decide_answerability",
        nodes.route_decision,
        {
            "answer": "run_answerer",
            "finalize": "finalize_diagnosis",
        },
    )
    graph.add_edge("run_answerer", "finalize_diagnosis")
    graph.add_edge("finalize_diagnosis", END)
    return graph.compile()