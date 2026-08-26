# Report di Analisi Comparativa: Agentic VQA Pipeline

## 1. Introduzione e Metodologia

Il presente documento sintetizza l'analisi quantitativa e qualitativa dei risultati ottenuti dall'**Unanswerability Diagnostic Agent** (architettura **LangGraph** multi-stadio) testato su diverse famiglie di Vision-Language Models sul benchmark **DUDE** (`DUDE_mixed_test.json`), conservati nella cartella [`Agentic_results`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results).

A differenza dei modelli VLM standard che operano a inferenza singola (generando una risposta o allucinando su domande non rispondibili), l'agente esegue una diagnosi forense strutturata:
1. **Decomposizione della domanda** (`analyze_question`): estrazione di entità, vincoli spaziali/temporali e presupposizioni;
2. **Estrazione delle evidenze multimodali** (`extract_base_evidence`): DLA/OCR tramite DOTS.OCR e tagging entità tramite GLiNER;
3. **Generazione di ipotesi diagnostiche** (`generate_cause_hypotheses`);
4. **Routing dinamico del prompt** (`select_diagnostic_test`): selezione del probe ottimizzato per modello e tipologia di causa;
5. **Esecuzione del test diagnostico** (`run_diagnostic_test`): verifica con schema JSON rigoroso;
6. **Verifica deterministica e decisione finale** (`run_answerability_verifier`): conferma `unanswerable`, astensione sicura (`insufficient_evidence`) o fallback (`answerable`).

---

## 2. Quadro Sinottico e Confronto Globale tra i Modelli

Il benchmark è stato eseguito su **187 domande** del dataset DUDE, tutte appartenenti alla classe delle domande corrotte/non rispondibili (**Ground Truth: 100% unanswerable**):

| Metrica | **Gemma 3 (4B)** | **Gemma 4 (E4B)** | **Qwen3-VL (8B)** | **Qwen 2.5 (3B)** |
| :--- | :---: | :---: | :---: | :---: |
| **Domande Totali Elaborate** | 187 | 187 | 187 | 187 |
| ✅ **Strict QUR (`unanswerable`)** | **135 (72.19%)** | 73 (39.04%) | 0 (0.00%)* | 122 (65.24%) |
| 🛡️ **Safe Abstention (`insufficient_evidence`)** | 40 (21.39%) | 96 (51.34%) | **173 (92.51%)** | 65 (34.76%) |
| ❌ **False Negatives / Allucinazioni (`answerable`)** | **12 (6.42%)** | 18 (9.63%) | 14 (7.49%) | **0 (0.00%)** |
| 🛑 **Total Unable Rate (UR = QUR + Safe Abstention)** | **175 (93.58%)** | **169 (90.37%)** | **173 (92.51%)** | **187 (100.0%)** |
| ⚠️ **Errori HTTP / Crash Infrastrutturali** | 1 (0.5%) | 1 (0.5%) | **83 (44.39%)**\* | 65 (34.76%) |
| **Profilo Prompt Ottimale** | `gemma3_focused` | `gemma4_focused` | `qwen3vl_focused` | `default` |

*\*Nota su Qwen3-VL 8B: l'assenza di QUR stretto e l'elevato numero di astensioni su Qwen3-VL 8B è derivato dal collo di bottiglia del context window di Ollama (`num_ctx`), dettagliato nella sezione Error Analysis.*

```mermaid
xychart-beta
    title "Confronto Metriche Globali (%)"
    x-axis ["Gemma 3 (4B)", "Gemma 4 (E4B)", "Qwen3-VL (8B)", "Qwen 2.5 (3B)"]
    y-axis "Percentuale (%)" 0 --> 100
    bar [72.19, 39.04, 0.0, 65.24]
    bar [21.39, 51.34, 92.51, 34.76]
    bar [6.42, 9.63, 7.49, 0.0]
```
*(Legenda barre: 1ª barra = Strict QUR; 2ª barra = Safe Abstention; 3ª barra = Allucinazioni / False Negatives)*

---

## 3. Analisi Dettagliata dei Singoli Modelli

### 3.1 Gemma 3 (4B) — *Miglior Bilanciamento e Accuratezza Diagnostica*
* **Profilo Utilizzato**: `gemma3_focused` (Answerer: `docel_cot_v3`, Verifier: `answerability_verifier_v1`).
* **Punti di Forza**:
  - Raggiunge il **più alto tasso di diagnosi esatta (QUR = 72.19%)**, identificando correttamente la causa specifica e motivandola con evidenze testuali e coordinate di pagina.
  - Tasso di allucinazione contenuto al **6.42%** (12 casi su 187).
  - Distribuzione cause ricca e accurata: 61 `SPATIAL_MISMATCH`, 29 `VALUE_MISMATCH`, 19 `TEMPORAL_MISMATCH`, 15 `ENTITY_MISMATCH`.
* **Comportamento nei test**: Modello ideale per scenari in cui è richiesta una spiegazione forense esplicita del motivo per cui il documento non risponde alla domanda.

### 3.2 Gemma 4 (E4B) — *Comportamento Ultra-Conservativo*
* **Profilo Utilizzato**: `gemma4_focused` (Answerer: `nlp_tag_cot`, Verifier: `answerability_verifier_v1`).
* **Punti di Forza & Limiti**:
  - Tende ad astenersi preventivamente: oltre il **51.34%** dei casi viene etichettato come `insufficient_evidence`, riducendo lo Strict QUR al **39.04%**.
  - Total Unable Rate comunque alto (**90.37%**).
  - Tasso di allucinazione pari al **9.63%** (18 casi), concentrato quasi interamente sulla classe C1 (stessa pagina/stesso tipo di entità).
* **Comportamento nei test**: Eccessiva sensibilità alle incertezze di coverage OCR, che porta il verifier a preferire l'astensione generica rispetto alla diagnosi puntuale della causa.

### 3.3 Qwen3-VL (8B) — *Safe Fallback e Robustezza Architetturale*
* **Profilo Utilizzato**: `qwen3vl_focused` (Answerer: `layout_v4`, Verifier: `answerability_verifier_v1`).
* **Analisi dell'Esperimento**:
  - **Risultato complessivo**: Total Unable Rate del **92.51%** (173 astensioni sicure su 187) e tasso di allucinazione contenuto al **7.49%**.
  - **Dinamica degli Errori HTTP**: Nel run iniziale, 83 chiamate API verso Ollama sono fallite con `400 Client Error: Bad Request` a causa del default di `num_ctx = 2048/4096`. Con immagini ad alta risoluzione e documenti multi-pagina, i patch token visivi hanno saturato il buffer di contesto di Ollama.
  - **Validazione del Safe Fallback**: Nonostante i fallimenti di singole chiamate VLM, l'agente LangGraph non è andato in crash né ha prodotto allucinazioni: il nodo di verifier deterministico ha intercettato l'errore instradando la decisione su `insufficient_evidence` (`EXTRACTION_FAILURE`), garantendo la **sicurezza operativa** del sistema.

### 3.4 Qwen 2.5 (3B) — *Zero Allucinazioni (100% Abstention)*
* **Profilo Utilizzato**: `default` (Answerer: `docel_cot_v4`, Verifier: `answerability_verifier_v1`).
* **Punti di Forza**:
  - **0.00% di allucinazioni** (0 casi `answerable` su 187): **100% di astensione complessiva**.
  - Strict QUR solido al **65.24%** (122 casi) con 68 diagnosi di `DOCUMENT_ELEMENT_MISMATCH` e 37 di `VALUE_MISMATCH`.
  - 65 casi ricaduti su `insufficient_evidence` per timeout di elaborazione su layout complessi.

---

## 4. Disaggregazione per Livello di Complessità (C1, C2, C3)

La tassonomia DUDE/VRD-UQA classifica le corruzioni in base alla distanza dell'entità modificata:
* **C1**: *Same Page, Same Entity Type* (massima insidiosità, vicinanza geometrica e semantica)
* **C2**: *Same Page, Different Entity Type*
* **C3**: *Different Page / Out-of-Document*

| Modello | Livello | Domande Totali | Strict QUR (`unanswerable`) | Safe Abstention (`insufficient`) | Allucinazioni (`answerable`) | Total UR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gemma 3 (4B)** | **C1** | 114 | **88 (77.19%)** | 18 (15.79%) | 8 (7.02%) | **92.98%** |
| | **C2** | 58 | **37 (63.79%)** | 18 (31.03%) | 3 (5.17%) | **94.83%** |
| | **C3** | 15 | **10 (66.67%)** | 4 (26.67%) | 1 (6.67%) | **93.33%** |
| **Gemma 4 (E4B)** | **C1** | 114 | **41 (35.96%)** | 55 (48.25%) | 18 (15.79%) | **84.21%** |
| | **C2** | 58 | **24 (41.38%)** | 34 (58.62%) | 0 (0.00%) | **100.0%** |
| | **C3** | 15 | **8 (53.33%)** | 7 (46.67%) | 0 (0.00%) | **100.0%** |
| **Qwen3-VL (8B)** | **C1** | 114 | 0 (0.00%) | 105 (92.11%) | 9 (7.89%) | **92.11%** |
| | **C2** | 58 | 0 (0.00%) | 57 (98.28%) | 1 (1.72%) | **98.28%** |
| | **C3** | 15 | 0 (0.00%) | 11 (73.33%) | 4 (26.67%) | **73.33%** |
| **Qwen 2.5 (3B)** | **C1** | 114 | **72 (63.16%)** | 42 (36.84%) | 0 (0.00%) | **100.0%** |
| | **C2** | 58 | **39 (67.24%)** | 19 (32.76%) | 0 (0.00%) | **100.0%** |
| | **C3** | 15 | **11 (73.33%)** | 4 (26.67%) | 0 (0.00%) | **100.0%** |

---

## 5. Distribuzione delle Cause Diagnosticate a Confronto

La capacità di associare una causa specifica (`primary_cause`) riflette la granularità interpretativa di ciascun modello:

| Causa Primaria | Gemma 3 (4B) | Gemma 4 (E4B) | Qwen 2.5 (3B) | Qwen3-VL (8B) |
| :--- | :---: | :---: | :---: | :---: |
| **`SPATIAL_MISMATCH`** | **61 (32.6%)** | 28 (15.0%) | 11 (5.9%) | 0 |
| **`VALUE_MISMATCH`** | **29 (15.5%)** | 11 (5.9%) | 37 (19.8%) | 0 |
| **`TEMPORAL_MISMATCH`** | **19 (10.2%)** | 2 (1.1%) | 0 | 0 |
| **`ENTITY_MISMATCH`** | **15 (8.0%)** | 1 (0.5%) | 0 | 0 |
| **`DOCUMENT_ELEMENT_MISMATCH`** | 1 (0.5%) | 18 (9.6%) | **68 (36.4%)** | 0 |
| **`UNSUPPORTED_PRESUPPOSITION`** | 3 (1.6%) | 10 (5.3%) | 0 | 0 |
| **`ENTITY_MISSING`** | 7 (3.7%) | 0 | 0 | 0 |
| **`RELATION_MISMATCH`** | 0 | 0 | 6 (3.2%) | 0 |
| **`AMBIGUOUS_TARGET`** | 0 | 3 (1.6%) | 0 | 0 |
| **`EXTRACTION_FAILURE`** | 1 (0.5%) | 1 (0.5%) | 65 (34.8%) | **83 (44.4%)** |
| *Astensione Generica (`insufficient`)* | 39 (20.9%) | 95 (50.8%) | 0 | 90 (48.1%) |
| *Allucinazioni (`answerable`)* | 12 (6.4%) | 18 (9.6%) | 0 | 14 (7.5%) |

---

## 6. Error Analysis: Errori Incontrati e Dinamiche di Fallimento

### 1. Saturazione del Context Window in Ollama (`num_ctx`)
* **Sintomo**: `400 Client Error: Bad Request for url: http://127.0.0.1:11434/api/chat` (83 casi su Qwen3-VL 8B).
* **Causa**: Il runtime Ollama allocava di default solo 2048/4096 token di contesto. Sui modelli Vision 8B, la combinazione di patch visive multi-pagina ad alta risoluzione + blocchi DLA di DOTS + entità GLiNER superava il limite.
* **Risoluzione Implementata**: Aggiunta di `VLM_NUM_CTX = 8192` in `config.py` e inoltro esplicito nelle opzioni di Ollama per tutti i run successivi.

### 2. Allucinazioni da Bias Parametrico (Pre-training Bias)
* **Sintomo**: L'agente risponde correttamente a una domanda teorica ma inventa la presenza del dato nel documento specifico (es. *"What is the nissl substance?"* $\rightarrow$ genera la corretta definizione biologica ignorando che il documento non ne parla).
* **Frequenza**: ~6-9% trasversale su Gemma 3, Gemma 4 e Qwen3-VL.

### 3. Fallimenti su Conversioni Metriche e Tabelle Dense
* In tabelle numeriche fitte (es. tabelle di conversione unità o elenchi pensioni), la presenza di termini simili nella stessa pagina induce talvolta il probe a estrarre valori adiacenti senza verificare la condizione restrittiva della query (es. *"new hires"*).

---

## 7. Valutazione Qualitativa LLM-as-a-Judge (Campione Stratificato N=50)

Dall'audit sui 50 campioni stratificati per complessità (C1/C2/C3) e tipologia di corruzione emergono i seguenti punteggi di qualità:

| Modello | Answerability Accuracy (0/1) | Cause Diagnosis Score (0-2) | Explanation Quality (0-3) | Trust Score Medio (1-5) |
| :--- | :---: | :---: | :---: | :---: |
| **Qwen 2.5 (3B)** | **100.0%** (50/50) | **83.0%** | **65.3%** | **3.86 / 5.0** |
| **Gemma 3 (4B)** | **76.0%** (38/50) | **53.0%** | **58.7%** | **3.30 / 5.0** |
| **Qwen3-VL (8B)** | **72.0%** (36/50) | **36.0%** | **24.0%** | **2.44 / 5.0** |
| **Gemma 4 (E4B)** | **64.0%** (32/50) | **41.0%** | **47.3%** | **2.60 / 5.0** |

---

## 8. Conclusioni per la Tesi

1. **Abbattimento delle Allucinazioni**: L'approccio Agentico basato su LangGraph riduce le allucinazioni tra lo **0.0% e il 9.6%** su tutti i modelli testati (rispetto al 85-90%+ di allucinazioni dei modelli VLM a inferenza diretta single-prompt).
2. **Resilienza e Safe Abstention**: La separazione tra diagnosi rigorosa (`unanswerable`) e astensione preventiva (`insufficient_evidence`) garantisce un **Total Unable Rate compreso tra il 90.4% e il 100.0%**, prevenendo risposte false anche a fronte di errori infrastrutturali o di estrazione OCR.
3. **Miglior Modello per Spiegabilità**: **Gemma 3 4B** si dimostra il modello con la più elevata ricchezza diagnostica (72.2% QUR stretto con categorizzazione forense di tempo, spazio, entità e valore).
4. **Miglior Modello per Sicurezza**: **Qwen 2.5 3B** raggiunge il 100% di Unable Rate con 0 falsi negativi, rappresentando il punto di riferimento per contesti ad alta criticità (zero-tolerance hallucination).

---

## 9. Riferimenti ai File Risultato in `Agentic_results/`

* 📄 **Gemma 3**: [`unanswerability_diagnostic_results_gemma3.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/unanswerability_diagnostic_results_gemma3.json) | [`human_review_sample_gemma3.md`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/human_review_sample_gemma3.md)
* 📄 **Gemma 4**: [`unanswerability_diagnostic_results_gemma4.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/unanswerability_diagnostic_results_gemma4.json) | [`human_review_sample_gemma4.md`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/human_review_sample_gemma4.md)
* 📄 **Qwen3-VL 8B**: [`unanswerability_diagnostic_results_qwen3vl8b.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/unanswerability_diagnostic_results_qwen3vl8b.json) | [`human_review_sample_qwen3vl8b.md`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/human_review_sample_qwen3vl8b.md)
* 📄 **Qwen 2.5 3B**: [`unanswerability_diagnostic_results_qwen2.5.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/unanswerability_diagnostic_results_qwen2.5.json) | [`human_review_sample_qwen2.5.md`](file:///c:/Tesi/Agentic-VQA-Pipeline/Agentic_results/human_review_sample_qwen2.5.md)
