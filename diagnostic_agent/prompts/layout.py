"""Layout and quadrant strategies from the previous prompt experiments."""

from diagnostic_agent.prompts.common import make_strategy_spec
from diagnostic_agent.schemas import CauseCode


LAYOUT_CAUSES = {
    CauseCode.DOCUMENT_ELEMENT_MISMATCH,
    CauseCode.SPATIAL_MISMATCH,
    CauseCode.EVIDENCE_MISSING,
}


STRATEGIES = {
    "layout_v1": """
Divide every page into four quadrants. Locate relevant visual entities in-page and compare their
positions across pages. Treat inconsistent positioning as a signal to investigate, not as a
semantic contradiction by itself.
""",
    "layout_v2": """
Use Q1 top-left, Q2 top-right, Q3 bottom-left and Q4 bottom-right. Apply layout heuristics for
titles, headers, tables, core facts, references and footnotes, then assess spatial coherence.
""",
    "layout_v3": """
Perform quadrant and cross-page analysis, account for document length, and test whether layout
evidence directly contradicts a page, section or position presupposed by the question.
""",
    "layout_v4": """
Perform explicit page-aware quadrant analysis over all attached pages. Verify page count,
document element type and spatial references before confirming a spatial mismatch.
""",
}


PROMPTS = {
    name: make_strategy_spec(
        name=name,
        family="layout",
        description=f"Historical spatial strategy {name}.",
        strategy=strategy,
        required_evidence={"images", "layout"},
        supported_causes=LAYOUT_CAUSES,
        include_images=True,
    )
    for name, strategy in STRATEGIES.items()
}