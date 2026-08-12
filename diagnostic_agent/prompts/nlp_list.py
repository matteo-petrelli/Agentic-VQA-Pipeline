"""Entity-list strategies from the previous prompt experiments."""

from diagnostic_agent.prompts.common import make_strategy_spec
from diagnostic_agent.schemas import CauseCode


LIST_CAUSES = {
    CauseCode.ENTITY_MISSING,
    CauseCode.ENTITY_MISMATCH,
    CauseCode.VALUE_MISMATCH,
    CauseCode.TEMPORAL_MISMATCH,
    CauseCode.RELATION_MISMATCH,
    CauseCode.UNSUPPORTED_PRESUPPOSITION,
    CauseCode.AMBIGUOUS_TARGET,
}


DEFINITIONS = {
    "nlp_list": (
        {"entity_lists"},
        "Match question entities against document entities by semantic type and value.",
    ),
    "nlp_list_cot": (
        {"entity_lists"},
        "Identify entities, locate same-type matches, check semantic context and resolve ambiguous candidates.",
    ),
    "nlp_list_ocr": (
        {"entity_lists", "plain_ocr"},
        "Match entity lists, then use raw OCR to verify context and explicit contradictions.",
    ),
    "nlp_list_ocr_cot": (
        {"entity_lists", "plain_ocr"},
        """
Identify entities, locate same-type matches, verify their OCR context, resolve ambiguity and
check whether document evidence disproves a question assumption. Search for valid matches that
could falsify the mismatch hypothesis.
""",
    ),
}


PROMPTS = {
    name: make_strategy_spec(
        name=name,
        family="nlp_list",
        description=f"Historical entity-list strategy {name}.",
        strategy=strategy,
        required_evidence=requirements,
        supported_causes=LIST_CAUSES,
    )
    for name, (requirements, strategy) in DEFINITIONS.items()
}