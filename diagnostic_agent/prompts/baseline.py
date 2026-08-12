"""Baseline strategies from the previous prompt experiments."""

from diagnostic_agent.prompts.common import make_strategy_spec
from diagnostic_agent.schemas import CauseCode


GENERAL_CAUSES = set(CauseCode) - {
    CauseCode.EVIDENCE_MISSING,
    CauseCode.EXTRACTION_FAILURE,
}


PROMPTS = {
    "baseline": make_strategy_spec(
        name="baseline",
        family="baseline",
        description="Image-only baseline reasoning.",
        strategy="Base every conclusion exclusively on visible document content.",
        required_evidence={"images"},
        supported_causes=GENERAL_CAUSES,
        include_images=True,
    ),
    "baseline_ocr": make_strategy_spec(
        name="baseline_ocr",
        family="baseline",
        description="Baseline using images and plain OCR.",
        strategy="Cross-check the visible document with plain OCR before reaching a conclusion.",
        required_evidence={"images", "plain_ocr"},
        supported_causes=GENERAL_CAUSES,
        include_images=True,
    ),
}