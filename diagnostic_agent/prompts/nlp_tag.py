"""Inline entity-tag strategies from the previous prompt experiments."""

from diagnostic_agent.prompts.common import make_strategy_spec
from diagnostic_agent.schemas import CauseCode


TAG_CAUSES = {
    CauseCode.ENTITY_MISSING,
    CauseCode.ENTITY_MISMATCH,
    CauseCode.VALUE_MISMATCH,
    CauseCode.TEMPORAL_MISMATCH,
    CauseCode.RELATION_MISMATCH,
}


PROMPTS = {
    "nlp_tag": make_strategy_spec(
        name="nlp_tag",
        family="nlp_tag",
        description="OCR with inline semantic entity tags.",
        strategy="""
Use inline entity tags to locate names, dates, values, places and organizations. Verify that
matching entities occur in the section and relation implied by the question.
""",
        required_evidence={"tagged_ocr"},
        supported_causes=TAG_CAUSES,
    ),
    "nlp_tag_cot": make_strategy_spec(
        name="nlp_tag_cot",
        family="nlp_tag",
        description="Stepwise reasoning over inline entity tags.",
        strategy="""
Break down the question, identify relevant tagged entities, locate them in OCR, verify their
sentence/page context, and resolve multiple matches. Distinguish an absent entity from a tagger
or OCR failure before confirming a mismatch.
""",
        required_evidence={"tagged_ocr", "entity_lists"},
        supported_causes=TAG_CAUSES,
    ),
}