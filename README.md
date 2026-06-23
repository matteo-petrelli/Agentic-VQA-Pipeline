# Agentic VQA Pipeline

A **ReAct-style agentic pipeline** for **Question Unanswerable Recognition (QUR)** on document images, designed to detect corrupted/unanswerable questions in the [DUDE dataset](https://arxiv.org/abs/2305.08455).

The agent autonomously decides which tools to use (visual inspection, OCR, entity tagging) through a **Thought → Action → Observation** reasoning loop, following the ReAct framework (Yao et al., 2023).

## Architecture

The agent processes each question through a dynamic reasoning loop:

```
Question + Document Image
         │
         ▼
┌─────────────────────────────────────────────┐
│              ReAct AGENT LOOP               │
│                                             │
│  ┌─────────┐                                │
│  │ THINK   │ "What do I know? What do I     │
│  │         │  need to answer this question?" │
│  └────┬────┘                                │
│       │                                     │
│       ▼                                     │
│  ┌─────────┐    ┌─────────────────────┐     │
│  │  ACT    │───▶│ Choose a tool:      │     │
│  │         │    │  • visual_inspect   │     │
│  └────┬────┘    │  • ocr_extract     │     │
│       │         │  • entity_tag      │     │
│       │         │  • final_answer    │     │
│       │         └─────────────────────┘     │
│       ▼                                     │
│  ┌─────────┐                                │
│  │ OBSERVE │ Receive tool output,           │
│  │         │ loop back to THINK             │
│  └─────────┘                                │
│                                             │
│  Repeat until final_answer (max 4 steps)    │
└─────────────────────────────────────────────┘
```

### Available Tools

| Tool | What it does | When the agent uses it |
|------|-------------|----------------------|
| `visual_inspect` | Spatial/layout analysis of the document image | First step — get document overview |
| `ocr_extract` | DOTS.OCR structured text extraction | When precise text reading is needed |
| `entity_tag` | GLiNER semantic entity tagging | After OCR, to match question entities |
| `final_answer` | Terminates loop with answer + confidence | When evidence is sufficient |

### Key Properties
- **Autonomous**: The VLM decides which tools to call based on the question and document
- **Iterative**: Up to 4 reasoning steps (configurable via `MAX_ITERATIONS`)
- **Efficient**: Simple questions may need only 2 steps; complex ones use all tools
- **Traceable**: Full Thought/Action/Observation trace is logged for analysis

## Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| VLM + Agent | Configurable via Ollama (e.g., `qwen2.5-vl:3b`, `phi3.5`, `gemma3:4b`) | Reasoning agent + Visual Q&A |
| OCR | [DOTS.OCR](https://huggingface.co/strangervisionhf/dots.ocr-base-fix) | Layout detection + text extraction |
| NER | [GLiNER medium-v2.1](https://huggingface.co/urchade/gliner_medium-v2.1) | Entity recognition & tagging |

## Project Structure

```
├── config.py              # All hyperparameters, model paths, ReAct settings
├── react_agent.py         # Core ReAct loop with tool registry (NEW)
├── preprocessing.py       # DOTS.OCR, GLiNER, and Ollama VLM engine
├── agentic_pipeline.py    # Thin wrapper delegating to ReActAgent
├── prompt_library.py      # ReAct system prompt + tool prompts
├── run_experiments.py     # Main entry point with checkpoint/resume
├── evaluate_results.py    # QUR, FUR, F1 + ReAct metrics (steps, tool usage)
└── requirements.txt       # Python dependencies
```

## Setup (Kaggle)

### Prerequisites
1. **GPU enabled**: Settings → Accelerator → GPU T4 x2 or P100
2. **Add 3 datasets as Input**:
   - Your repo upload (e.g., `agentic-pipeline`)
   - `dude-train` — document images
   - `dude-questions` — JSON with corrupted/original questions

### Cell 1 — Install & Start Ollama + Pull Model
```python
import subprocess, time

!curl -fsSL https://ollama.com/install.sh | sh
subprocess.Popen(["ollama", "serve"])
time.sleep(5)

MODEL = "qwen2.5-vl:3b"  # Change per test: "phi3.5", "gemma3:4b"
!ollama pull {MODEL}
```

### Cell 2 — Install Dependencies
```python
!pip install -q gliner paddleocr bitsandbytes nltk
```

### Cell 3 — Configure & Override
```python
import sys
sys.path.insert(0, "/kaggle/input/agentic-pipeline")

import config
config.OLLAMA_VLM = MODEL
config.SAMPLING_PERCENTAGE = 0.1  # 10% for quick test, 1.0 for full run
```

### Cell 4 — Run Pipeline
```python
from run_experiments import main
main()
```

### Cell 5 — Evaluate Results
```python
from evaluate_results import evaluate_results
evaluate_results(config.OUTPUT_JSON_PATH)
```

## Evaluation Metrics

### Core Metrics
| Metric | Description |
|--------|-------------|
| **QUR** | Question Unanswerable Recognition rate (corrupted → "Unable") |
| **FUR** | False Unable Rate (original → incorrectly "Unable") |
| **F1** | Harmonic mean of Precision and Recall |

### ReAct Agent Metrics
| Metric | Description |
|--------|-------------|
| **Avg Steps** | Average number of reasoning steps per question |
| **Tool Usage** | Frequency of each tool being called |
| **Forced Exits** | Questions where MAX_ITERATIONS was reached |
| **Step Distribution** | Histogram of steps per question |

Results are broken down by corruption complexity (C1, C2, C3).

## License

MIT
