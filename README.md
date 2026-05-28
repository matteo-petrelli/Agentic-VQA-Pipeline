# Agentic VQA Pipeline

A two-pass agentic pipeline for **Question Unanswerable Recognition (QUR)** on document images, designed to detect corrupted/unanswerable questions in the [DUDE dataset](https://arxiv.org/abs/2305.08455).

## Architecture

The pipeline processes each question through two passes with confidence-based routing:

```
Question + Document Image(s)
         │
         ▼
┌─────────────────────┐
│  PASS 1: Layout     │  Pure visual/spatial reasoning (no OCR)
│  (VLM only)         │
└────────┬────────────┘
         │
    ┌────▼────┐
    │ Unable  │──Yes + High Conf──▶ Early Exit: "Unable to determine"
    │   ?     │
    └────┬────┘
         │ No / Low Conf
         ▼
┌─────────────────────┐
│  PASS 2: Unified    │  DOTS.OCR layout + GLiNER entity tags + VLM
│  (OCR + NLP + VLM)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Decision Logic     │  Consensus or Confidence-based tiebreaker
└─────────────────────┘
```

### Pass 1 — Layout Prompt (Visual Only)
- Sends the document image to the VLM with a spatial reasoning prompt
- Divides pages into quadrants (Q1-Q4) for positional analysis
- If the VLM returns "Unable to determine" with **High** confidence → early exit

### Pass 2 — Unified Prompt (OCR + NLP + VLM)
- **DOTS.OCR** extracts structured layout elements (titles, tables, text blocks)
- **GLiNER** tags semantic entities (dates, names, positions, etc.) in both document and question
- Combined enriched context is sent to the VLM for a second, informed pass

### Decision Logic
- **Consensus**: Both passes agree → use that answer
- **Disagreement**: Higher confidence wins
- **Tie**: Pass 2 wins (has more evidence)

## Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| VLM | Configurable via Ollama (e.g., `gemma3:4b`, `qwen2.5-vl:3b`, `phi3.5`) | Visual Q&A |
| OCR | [DOTS.OCR](https://huggingface.co/strangervisionhf/dots.ocr-base-fix) | Layout detection + text extraction |
| NER | [GLiNER medium-v2.1](https://huggingface.co/urchade/gliner_medium-v2.1) | Entity recognition & tagging |

## Project Structure

```
├── config.py              # All hyperparameters, model paths, I/O paths
├── preprocessing.py       # DOTS.OCR, GLiNER, and Ollama VLM engine
├── agentic_pipeline.py    # Two-pass pipeline with confidence routing
├── prompt_library.py      # Layout and Unified prompt templates
├── run_experiments.py      # Main entry point with checkpoint/resume
├── evaluate_results.py    # QUR, FUR, F1, confusion matrix evaluation
└── requirements.txt       # Python dependencies
```

## Setup (Kaggle)

```python
# 1. Install & start Ollama
!curl -fsSL https://ollama.com/install.sh | sh
import subprocess, time
subprocess.Popen(["ollama", "serve"])
time.sleep(5)

# 2. Pull model
!ollama pull gemma3:4b

# 3. Install deps
!pip install -q gliner paddleocr bitsandbytes

# 4. Add repo to path & run
import sys
sys.path.insert(0, "/kaggle/input/agentic-pipeline")
from run_experiments import main
main()
```

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **QUR** | Question Unanswerable Recognition rate (corrupted → "Unable") |
| **FUR** | False Unable Rate (original → incorrectly "Unable") |
| **F1** | Harmonic mean of Precision and Recall |

Results are broken down by corruption complexity (C1, C2, C3).

## License

MIT
