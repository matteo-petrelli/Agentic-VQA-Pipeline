# Unanswerability Diagnostic VQA Agent

LangGraph pipeline for diagnosing whether a question is answerable from document images, identifying possible unanswerability causes, and answering only after diagnostic checks pass.

The agent produces three distinct states:

- `answerable`: direct and contextually valid evidence supports an answer;
- `unanswerable`: a question constraint or presupposition conflicts with the document;
- `insufficient_evidence`: extraction quality or document coverage is not sufficient to decide.

This distinction prevents OCR failures and missing pages from being counted automatically as corrupted questions.

## Architecture

```text
question + document pages
    -> question decomposition
    -> OCR, document elements, entity tags, quadrants
    -> candidate cause generation
    -> model-specific prompt selection
    -> diagnostic test loop
    -> coverage and answerability decision
    -> answerer, only when answerable
    -> structured diagnosis
```

The diagnostic causes include entity, value, temporal, relation, answer-type, document-element and spatial mismatches, unsupported presuppositions, ambiguous targets, missing evidence and extraction failures.

## Prompt Catalog

The previous prompt experiments are available as named strategies under `diagnostic_agent/prompts/`:

- `baseline`, `baseline_ocr`;
- `docel`, `docel_cot_v1` through `docel_cot_v4`, `docel_cot_numvre`;
- `nlp_tag`, `nlp_tag_cot`;
- `nlp_list`, `nlp_list_cot`, `nlp_list_ocr`, `nlp_list_ocr_cot`;
- `layout_v1` through `layout_v4`.

Each prompt declares its required evidence, supported causes and whether document images must be attached. Historical strategy instructions are wrapped in a common JSON diagnostic contract so outputs remain comparable.

No profile is asserted to be optimal. Prompt choices are initial configurations intended to be replaced after model-level analysis.

## Model-Specific Selection

Choose a default profile in `config.py`:

```python
PROMPT_PROFILE = "default"
```

Available profiles are `default`, `gemma3_focused`, `gemma4_focused`, and `qwen3vl_focused`.

Map models to profiles:

```python
MODEL_PROMPT_PROFILES = {
    "gemma3": "gemma3_focused",
    "gemma4": "gemma4_focused",
    "qwen3-vl": "qwen3vl_focused",
}
```

Override individual causes or control prompts for one model:

```python
MODEL_PROMPT_OVERRIDES = {
    "qwen2.5vl": {
        "answerer_prompt": "docel_cot_v4",
        "verifier_prompt": "answerability_verifier_v1",
        "cause_prompts": {
            "VALUE_MISMATCH": "nlp_tag_cot",
            "SPATIAL_MISMATCH": "layout_v4",
        },
    },
}
```

The same overrides can be supplied at runtime as a JSON file:

```bash
python run_experiments.py \
    --model qwen2.5vl:3b \
  --prompt-profile default \
  --prompt-overrides prompt_overrides.json
```

An incompatible prompt/cause combination fails during agent initialization and lists compatible candidates.

## Project Structure

```text
diagnostic_agent/
    agent.py              public agent API
    engine.py             Ollama, DOTS.OCR and GLiNER integration
    evidence.py           multi-page evidence extraction and coverage
    graph.py              LangGraph assembly and routes
    nodes.py              diagnostic nodes and decision policy
    parsing.py            structured VLM output normalization
    profiles.py           selectable prompt profiles and overrides
    schemas.py            state, causes and prompt contracts
    prompts/              all specialized prompt families
tests/
    test_diagnostic_agent.py
agentic_pipeline.py       stable pipeline facade
config.py                 models, paths, profiles and thresholds
run_experiments.py        dataset runner with checkpointing
evaluate_results.py       QUR, FUR, causes, coverage and prompt metrics
proposta_agente_prompt_routing.md
```

## Setup

The production engine requires a CUDA environment for DOTS.OCR and GLiNER, plus a running Ollama server with the selected vision model.

```bash
python -m pip install -r requirements.txt
ollama serve
ollama pull qwen2.5vl:3b
```

Update dataset paths and model settings in `config.py`, then run:

```bash
python run_experiments.py --model qwen2.5vl:3b --prompt-profile default
python evaluate_results.py --file /path/to/unanswerability_diagnostic_results.json
```

## Output

Each `agentic_result` contains:

```json
{
  "answerability": "unanswerable",
  "primary_cause": "VALUE_MISMATCH",
  "secondary_causes": [],
  "diagnostic_results": [],
  "evidence_coverage": 1.0,
  "final_answer": "Unable to determine",
  "answerability_confidence": 3,
  "cause_confidence": 3,
  "answer_confidence": null,
    "prompt_profile": "default@qwen2.5vl:3b",
  "prompts_used": ["question_analysis_v1", "nlp_tag_cot"],
  "tests_run": 1,
  "trace": []
}
```

QUR and FUR use only the explicit `unanswerable` state. `insufficient_evidence` is reported separately.

## Tests

The graph can be tested without GPU, Ollama or model downloads:

```bash
python -m unittest discover -s tests -v
```