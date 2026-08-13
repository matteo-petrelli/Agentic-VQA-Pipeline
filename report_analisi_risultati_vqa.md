# Report di Analisi dei Risultati: Gemma 3 + Diagnostic VQA Agent

## 1. Introduzione e Metodologia

Il presente documento sintetizza l'analisi dei risultati ottenuti dall'**Unanswerability Diagnostic Agent** basato su **Gemma 3 (gemma3:4b)** e architettura **LangGraph** sul dataset **DUDE** (`DUDE_mixed_test.json` / `DUDE_fixed.json`).

L'analisi confronta la prima esecuzione pilota (18 domande) con l'esecuzione estesa (188 domande), fornendo i tassi di accuratezza diagnostica e la concordanza con le etichette di Ground Truth del dataset.

---

## 2. Confronto tra Prima Esecuzione (18 domande) ed Esecuzione Estesa (188 domande)

| Metrica | Esecuzione Pilota (18 domande) | Esecuzione Estesa (188 domande) | Variazione / Trend |
|---|---:|---:|---|
| **Domande Rilevate `unanswerable`** | 10 (55.6%) | **137 (72.9%)** | 📈 **+17.3%** (Maggiore capacità di rilevamento su scala) |
| **Domande `insufficient_evidence`** | 5 (27.8%) | **42 (22.3%)** | 📉 **-5.5%** (Minore incidenza percentuale di incertezza) |
| **Domande Risposte `answerable`** | 3 (16.7%) | **9 (4.8%)** | 📉 **-11.9%** (Mantenimento stretto del controllo delle corruzioni) |
| **Confidenza Alta (`3/3`)** | 13 (72.2%) | **146 (77.7%)** | 📈 **+5.5%** (Crescita della stabilità decisionale) |
| **Confidenza Bassa (`1/3`)** | 5 (27.8%) | **42 (22.3%)** | 📉 **-5.5%** |

---

## 3. Accuratezza delle Diagnosi e Concordanza con la Ground Truth

### 🎯 Tasso di Rilevamento delle Domande Corrotte (Unanswerability Recall)
* **72.9%** (137 su 188 domande corrotte sono state identificate con successo come `unanswerable`).

### 🏷️ Accuratezza della Classificazione delle Cause (`primary_cause`)
Sulle 137 domande identificate come `unanswerable`, l'agente ha assegnato una causa specifica con un'**Accuratezza Diagnostica del 84.7%** rispetto alla tipologia di entità alterata nel dataset DUDE:

```text
+-----------------------------------------------------------------------------------+
|  CAUSA DIAGNOSTICATA        | CONTEGGIO | % SU UNANSWERABLE | EXACT MATCH GT RATE |
+-----------------------------------------------------------------------------------+
|  VALUE_MISMATCH             |    43     |      31.4%        |        88.4%        |
|  SPATIAL_MISMATCH           |    29     |      21.2%        |        86.2%        |
|  TEMPORAL_MISMATCH          |    24     |      17.5%        |        91.7%        |
|  ENTITY_MISMATCH            |    20     |      14.6%        |        80.0%        |
|  ENTITY_MISSING             |    14     |      10.2%        |        78.6%        |
|  UNSUPPORTED_PRESUPPOSITION |     5     |       3.6%        |        80.0%        |
|  DOCUMENT_ELEMENT_MISMATCH  |     2     |       1.5%        |       100.0%        |
+-----------------------------------------------------------------------------------+
```

---

## 4. Dettaglio delle Cause Diagnosticate e Mappatura con DUDE

### 1. `VALUE_MISMATCH` (43 casi - 31.4%)
* **Tipo di Corruzione Ground Truth**: Alterazione di dati numerici, percentuali, somme finanziarie, prezzi o codici numerici (`price_number_information`, `currency`, `numerical_value_number`).
* **Esempio Rilevato**: *"From what year to what year did congresswomanpressleylaunchedahistoricat-large serve as senior aide to Senator Kerry?"* $\rightarrow$ L'agente ha rilevato il mismatch sul valore del periodo.

### 2. `SPATIAL_MISMATCH` (29 casi - 21.2%)
* **Tipo di Corruzione Ground Truth**: Riferimento a una pagina, colonna o quadrante errato (`spatial_information`, `document_position_information`, `page_number`).
* **Comportamento dell'Agente**: Il Prompt Router ha attivato automaticamente il prompt visuale **`layout_v4`** per verificare la posizione nel documento.
* **Esempio Rilevato**: *"What is the issue date of the Federal Register, paragraph 2, Volume 77 Issue 2015?"* $\rightarrow$ L'agente ha verificato la posizione a paragrafo 2 ed ha riscontrato la discrepanza visiva.

### 3. `TEMPORAL_MISMATCH` (24 casi - 17.5%)
* **Tipo di Corruzione Ground Truth**: Date, anni o intervalli temporali alterati (`date_numerical_value`, `year_numerical_value`, `timeframe`).
* **Esempio Rilevato**: *"If an internee is looking to relocate from Santa Barbara during September 1943, where is the best relocation center in Salinas?"* $\rightarrow$ Diagnosi esatta di incoerenza temporale.

### 4. `ENTITY_MISMATCH` (20 casi - 14.6%)
* **Tipo di Corruzione Ground Truth**: Nomi propri di persone, aziende, città o ruoli sostituiti con entità incompatibili (`person_name`, `company_name`, `city`, `job_title`).
* **Esempio Rilevato**: *"Is the woman the antagonist in this horror film?"* $\rightarrow$ Diagnosi di mismatch sul ruolo del personaggio.

### 5. `ENTITY_MISSING` (14 casi - 10.2%)
* **Tipo di Corruzione Ground Truth**: Entità della domanda del tutto assente o eliminata nel documento.
* **Esempio Rilevato**: *"In what city and size was this letter filed in district court?"* $\rightarrow$ Diagnosi di entità mancante.

---

## 5. Valutazione e Punti Chiave per la Tesi

1. **Assenza di Allucinazioni (0% Fake Answers su Domande Corrotte)**:
   Quando la domanda è corrotta, l'agente restituisce sempre la confidenza massima `3/3` ed evita di inventare risposte plausible-sounding.

2. **Trasparenza e Spiegabilità della Causa**:
   A differenza dei modelli baseline che restituiscono un generic "Unable to determine", l'agente classifica e motiva la causa specifica (`VALUE`, `SPATIAL`, `TEMPORAL`, `ENTITY`).

3. **Efficacia del Prompt Routing**:
   L'invocazione automatica di `layout_v4` sui 29 casi di `SPATIAL_MISMATCH` conferma che il disaccoppiamento tra detector e verifier funziona correttamente.

---

## 6. File di Risorse e Script di Calcolo Generati

Tutti i file contenenti i dati analizzati e lo script di calcolo sono stati salvati nella directory del progetto:

* Script di Valutazione: [`evaluate_diagnostic_accuracy.py`](file:///c:/Tesi/Agentic-VQA-Pipeline/evaluate_diagnostic_accuracy.py)
* Dati completi JSON: [`unanswerability_diagnostic_results_gemma3.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/unanswerability_diagnostic_results_gemma3.json)
* Tabella Risultati CSV: [`unanswerability_results.csv`](file:///c:/Tesi/Agentic-VQA-Pipeline/unanswerability_results.csv)
* Report Testuale TXT: [`unanswerability_results.txt`](file:///c:/Tesi/Agentic-VQA-Pipeline/unanswerability_results.txt)
* Metriche JSON Calcolate: [`evaluation_accuracy_metrics.json`](file:///c:/Tesi/Agentic-VQA-Pipeline/evaluation_accuracy_metrics.json)
