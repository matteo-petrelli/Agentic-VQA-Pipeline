"""Document-element strategies from the previous prompt experiments."""

from diagnostic_agent.prompts.common import make_strategy_spec
from diagnostic_agent.schemas import CauseCode


DOCEL_CAUSES = {
    CauseCode.ENTITY_MISSING,
    CauseCode.ENTITY_MISMATCH,
    CauseCode.RELATION_MISMATCH,
    CauseCode.ANSWER_TYPE_MISMATCH,
    CauseCode.DOCUMENT_ELEMENT_MISMATCH,
    CauseCode.TEMPORAL_MISMATCH,
    CauseCode.UNSUPPORTED_PRESUPPOSITION,
    CauseCode.AMBIGUOUS_TARGET,
    CauseCode.VALUE_MISMATCH,
}


STRATEGIES = {
    "docel": """
Use structured OCR labels such as Title, Plain Text, Table, Figure, Header, Footer and Endnote.
Verify that a candidate fact occurs in the page, section and document element implied by the
question. Treat evidence from a mismatched context as invalid.
""",
    "docel_cot_v1": """
Identify key question entities; inventory document elements and their hierarchy; locate each
entity inside those elements; distinguish primary factual elements from secondary context;
then verify that the source element aligns with the question intent.
""",
    "docel_cot_v2": """
Identify question entities, categorize document elements, match entities within elements and
pages, and check contextual consistency. Secondary or unrelated sections cannot satisfy a
question that refers to primary content.
""",
    "docel_cot_v3": """
Identify entities and document elements, verify contextual consistency, then explicitly check
whether any element contradicts a fact or assumption in the question. Report the exact
conflicting text rather than treating uncertainty as contradiction.
""",
    "docel_cot_v4": """
Concise document-element reasoning: identify entities, locate their element, verify context,
and check explicit contradictions between document elements and question assumptions.
""",
    "docel_cot_numvre": """
Use document elements and their distribution across pages to identify the likely primary
evidence source. Verify entity context and contradictions, while treating pages dominated by
secondary elements as weaker rather than automatically invalid.
""",
}


PROMPTS = {
    name: make_strategy_spec(
        name=name,
        family="docel",
        description=f"Historical document-element strategy {name}.",
        strategy=strategy,
        required_evidence={"structured_ocr", "layout"},
        supported_causes=DOCEL_CAUSES,
    )
    for name, strategy in STRATEGIES.items()
}