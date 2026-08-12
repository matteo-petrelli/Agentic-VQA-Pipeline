"""Registry of every selectable prompt strategy."""

from diagnostic_agent.prompts.baseline import PROMPTS as BASELINE_PROMPTS
from diagnostic_agent.prompts.common import QUESTION_ANALYSIS_SPEC, VERIFIER_SPEC
from diagnostic_agent.prompts.docel import PROMPTS as DOCEL_PROMPTS
from diagnostic_agent.prompts.layout import PROMPTS as LAYOUT_PROMPTS
from diagnostic_agent.prompts.nlp_list import PROMPTS as NLP_LIST_PROMPTS
from diagnostic_agent.prompts.nlp_tag import PROMPTS as NLP_TAG_PROMPTS
from diagnostic_agent.schemas import CauseCode, PromptSpec


PROMPT_CATALOG: dict[str, PromptSpec] = {
    QUESTION_ANALYSIS_SPEC.name: QUESTION_ANALYSIS_SPEC,
    VERIFIER_SPEC.name: VERIFIER_SPEC,
}

for family in (
    BASELINE_PROMPTS,
    DOCEL_PROMPTS,
    NLP_TAG_PROMPTS,
    NLP_LIST_PROMPTS,
    LAYOUT_PROMPTS,
):
    duplicates = set(PROMPT_CATALOG).intersection(family)
    if duplicates:
        raise RuntimeError(f"Duplicate prompt names: {sorted(duplicates)}")
    PROMPT_CATALOG.update(family)


def get_prompt(name: str) -> PromptSpec:
    try:
        return PROMPT_CATALOG[name]
    except KeyError as exc:
        available = ", ".join(sorted(PROMPT_CATALOG))
        raise ValueError(f"Unknown prompt '{name}'. Available prompts: {available}") from exc


def prompts_for_cause(cause: CauseCode | str) -> list[str]:
    cause_code = CauseCode(cause)
    return sorted(
        spec.name
        for spec in PROMPT_CATALOG.values()
        if cause_code in spec.supported_causes
    )


def validate_prompt_for_cause(prompt_name: str, cause: CauseCode | str) -> None:
    spec = get_prompt(prompt_name)
    cause_code = CauseCode(cause)
    if cause_code not in spec.supported_causes:
        raise ValueError(
            f"Prompt '{prompt_name}' does not support {cause_code.value}. "
            f"Candidates: {', '.join(prompts_for_cause(cause_code))}"
        )