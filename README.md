# Unanswerability Diagnostic VQA Agent

LangGraph pipeline for diagnosing whether a question is answerable from document images, identifying possible unanswerability causes, and answering only after diagnostic checks pass.

The agent produces three distinct states:
- `answerable`: direct and contextually valid evidence supports an answer;
- `unanswerable`: a question constraint or presupposition conflicts with the document;
- `insufficient_evidence`: extraction quality or document coverage is not sufficient to decide.

This distinction prevents OCR failures and missing pages from being counted automatically as corrupted questions.

---

## 🏛️ Architecture

```text
question + document pages
    -> question decomposition
    -> OCR, document elements, entity tags, quadrants
    -> candidate cause generation
    -> model-specific prompt routing
    -> diagnostic test loop (LangGraph)
    -> coverage and answerability decision
    -> answerer, only when answerable
    -> structured diagnosis & explanation
```

Diagnostic causes include:
`ENTITY_MISMATCH`, `ENTITY_MISSING`, `VALUE_MISMATCH`, `TEMPORAL_MISMATCH`, `SPATIAL_MISMATCH`, `DOCUMENT_ELEMENT_MISMATCH`, `UNSUPPORTED_PRESUPPOSITION`, `RELATION_MISMATCH`, `ANSWER_TYPE_MISMATCH`, `AMBIGUOUS_TARGET`, `MISSING_EVIDENCE`, `EXTRACTION_FAILURE`.

---

## 📁 Repository Structure

```text
Agentic-VQA-Pipeline/
│
├── README.md                           # Overview del progetto e quickstart
├── requirements.txt                    # Dipendenze Python
├── config.py                           # Parametri globali (GPU, VLM, token limits, percorsi)
├── kaggle_utils.py                     # Bootstrap ambiente, GPU detection & Ollama manager
├── agentic_pipeline.py                 # API Python entrypoint per l'agente
│
├── diagnostic_agent/                   # [CORE ENGINE] Architettura LangGraph & VLM Engine
│   ├── agent.py                        # DiagnosticAgent orchestrator
│   ├── graph.py                        # Definizione StateGraph e routing nodi
│   ├── nodes.py                        # Nodi decisori, validatori ed estrattori
│   ├── schemas.py                      # Schemi Pydantic e contratti di stato
│   ├── engine.py                       # VLM inference (Ollama & Transformers) + DOTS/GLiNER
│   ├── evidence.py                     # Estrattore evidenze e coverage multi-pagina
│   ├── parsing.py                      # Parser JSON robusto e fuzzy normalizer
│   ├── profiles.py                     # Profili di routing prompt specifici per modello
│   └── prompts/                        # Catalogo strategie di prompting (docel, layout, nlp, ecc.)
│
├── notebooks/                          # [KAGGLE RUNNERS] Notebook pronti per l'esecuzione
│   ├── kaggle_dual_t4_pipeline.ipynb       # Runner per Gemma 3 / Gemma 4 / Qwen 2.5 (Dual T4)
│   ├── kaggle_qwen3vl_8b_pipeline.ipynb    # Runner per Qwen3-VL 8B (Dual T4 + Context esteso)
│   └── kaggle_phi35_vision_pipeline.ipynb  # Runner per Phi-3.5-Vision (HuggingFace FP16 nativo)
│
├── scripts/                            # [CLI TOOLS] Script di benchmark, sampling e utility
│   ├── run_experiments.py              # Esecuzione benchmark DUDE da riga di comando
│   ├── evaluate_diagnostic_accuracy.py # Calcolo metriche forensi e precision/recall cause
│   ├── evaluate_results.py             # Valutazione base delle risposte
│   ├── generate_human_review_sample.py # Stratified sampling (5 macro-cat) + LLM Judge a 6 assi
│   └── generate_google_forms_script.py # Generatore automatico Google Apps Script per Form
│
├── docs/                               # [DOCUMENTATION & REPORTS] Relazioni tecniche
│   ├── report_analisi_risultati_vqa.md # Report comparativo completo sui modelli valutati
│   ├── funzionamento_agente_spiegazione.md # Spiegazione tecnica approfondita dell'agente
│   └── proposta_agente_prompt_routing.md   # Proposta architetturale del prompt routing
│
├── Agentic_results/                    # [EXPERIMENT ARTIFACTS] Risultati strutturati
│   ├── raw/                            # Output JSON completi degli esperimenti (~20MB)
│   ├── human_review/                   # Campioni 50 domande per la review umana
│   │   ├── md/                         # File Markdown formattati con rubric
│   │   └── json/                       # File JSON con rubric e note precompilate
│   └── google_forms/                   # Script .js per generare i Google Form
│
└── tests/                              # [TESTS] Test unitari e di integrazione
    └── test_diagnostic_agent.py
```

---

## 🎯 Model-Specific Prompt Profiles

I profili ottimizzano le strategie di prompting per modello in base ai risultati empirici:

- `gemma3_focused`: ottimizzato per Gemma 3 4B (Layout v4 + DocEl CoT v3);
- `gemma4_focused`: ottimizzato per Gemma 4 E4B;
- `qwen25_focused`: ottimizzato per Qwen 2.5 3B (NLP List OCR CoT + Layout v4);
- `qwen3vl_focused`: ottimizzato per Qwen3-VL 8B;
- `phi35_focused`: ottimizzato per Phi-3.5-Vision (Layout v1 + DocEl CoT v3, evita NLP).

---

## 🚀 Quickstart

### 1. Esecuzione su Kaggle
Carica il notebook corrispondente al modello da [`notebooks/`](notebooks/) su Kaggle con **GPU T4 x2** e **Internet: On**.

### 2. Generazione Campioni per Human Review (Stratified Sampling)
Esegui il campionamento stratificato sulle 5 macro-categorie (10 domande per categoria = 50 totali):
```bash
python scripts/generate_human_review_sample.py --all
```

### 3. Generazione Google Forms per la Revisione Umana
Genera gli script Google Apps Script (`.js`) per creare istantaneamente i form di valutazione:
```bash
python scripts/generate_google_forms_script.py
```
Incolla il contenuto dello script `.js` su [script.google.com](https://script.google.com/) ed esegui `createHumanReviewForm()`.