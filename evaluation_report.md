# 📊 Resoconto Risultati — Agentic VQA Pipeline (ReAct)

> Valutazione su **374 domande** (187 corrupted + 187 original) dal dataset DUDE.

---

## Metriche Principali

| Metrica | Valore |
|---|---|
| **F1 Score** | **0.613** |
| Precision | 0.582 |
| Recall (QUR) | 0.647 |

---

## Matrice di Confusione

|  | Agent: "Unable" | Agent: "Answer" |
|---|:---:|:---:|
| **Corrupted (reale)** | TP: **121** | FN: 66 |
| **Original (reale)** | FP: 87 | TN: **100** |

---

## QUR — Corrupted Detection Rate (Recall)

Il QUR misura la capacità dell'agente di **riconoscere le domande corrotte** e rispondere "Unable to determine".

| Complessità | QUR |
|---|---|
| **Totale** | **64.7%** (121/187) |
| C1 (semplice) | 67.5% |
| C2 (media) | 65.5% |
| C3 (complessa) | 40.0% |

> [!NOTE]
> L'agente rileva bene le corruzioni semplici (C1) e medie (C2), ma **perde efficacia sulle domande complesse (C3: 40%)**.
> Questo suggerisce che quando la corruzione è più sottile o multi-step, il modello tende a provare comunque a rispondere.

---

## FUR — False Unable Rate (Falsi Positivi)

Il FUR misura quanto spesso l'agente dichiara **"Unable"** su domande che in realtà sono **valide** (original).

| Complessità | FUR |
|---|---|
| **Totale** | **46.5%** (87/187) |
| C1 (semplice) | 52.6% |
| C2 (media) | 32.8% |
| C3 (complessa) | 53.3% |

> [!WARNING]
> **Questo è il punto più critico.** Quasi la metà delle domande originali (46.5%) viene erroneamente classificata come "unable".
> L'agente è **troppo conservativo**: preferisce dire "non so" piuttosto che rischiare una risposta su domande legittime.
> La FUR C2 (32.8%) è il dato migliore, mentre C1 e C3 sono oltre il 50%.

---

## Efficienza dell'Agente ReAct

| Metrica | Valore |
|---|---|
| Media step per domanda | **2.42** |
| Forced exits (max iterazioni) | **92 (24.6%)** |

### Distribuzione degli Step

```
1 step:   62 (16.6%) ████
2 steps: 192 (51.3%) ███████████████
3 steps:  22 ( 5.9%) █
4 steps:  98 (26.2%) ███████
```

> [!NOTE]
> - La maggioranza (51.3%) si risolve in **2 step** (tipico pattern: Thought → Tool → Answer).
> - Il 26.2% usa **4 step** (max), di cui molti sono **forced exits** (92/374 = 24.6%).
> - Il 16.6% in **1 solo step** indica domande dove l'agente risponde immediatamente senza usare tool.

### Uso dei Tool

| Tool | Utilizzi | % |
|---|---|---|
| `ocr_extract` | 191 | 51.1% |
| `visual_inspect` | 152 | 40.6% |
| `entity_tag` | 8 | 2.1% |

> [!NOTE]
> - `ocr_extract` e `visual_inspect` sono usati in modo bilanciato, come atteso.
> - `entity_tag` è raramente chiamato (solo 8 volte su 374): l'agente non lo sfrutta quasi mai, probabilmente perché le informazioni OCR/visual sono sufficienti nella maggior parte dei casi.

---

## Analisi Complessiva

### Punti di Forza ✅
1. **QUR discreto (64.7%)**: l'agente riesce a individuare ~2/3 delle domande corrotte.
2. **Recall C1-C2 sopra il 65%**: buona capacità di rilevare corruzioni evidenti.
3. **Efficienza ragionevole**: media 2.42 step, il che significa che l'agente non "gira a vuoto" troppo.

### Criticità ❌
1. **FUR troppo alto (46.5%)**: il problema principale. L'agente è **eccessivamente cauto** e rifiuta troppe domande valide. Questo penalizza pesantemente la Precision (0.582).
2. **QUR C3 basso (40%)**: sulle domande complesse la corruzione non viene individuata.
3. **Forced exits elevate (24.6%)**: quasi 1/4 delle domande raggiunge il limite massimo di iterazioni senza convergere a una risposta chiara.
4. **Entity_tag sottoutilizzato**: il tool di tagging delle entità potrebbe fornire informazioni utili per il cross-referencing ma viene quasi ignorato.

### Possibili Miglioramenti 🔧
1. **Ridurre la FUR**: il prompt potrebbe essere calibrato per essere meno conservativo, ad esempio istruendo l'agente a rispondere "Unable" **solo** quando ci sono evidenze positive di corruzione, non per default.
2. **Aumentare max iterazioni**: passare da 4 a 5-6 potrebbe ridurre i forced exits.
3. **Incentivare l'uso di `entity_tag`**: aggiungere nel prompt un passo esplicito di verifica entità prima di concludere.
4. **Migliorare il QUR C3**: potrebbe servire un prompt più specifico per le corruzioni complesse (multi-entity, cross-page).

---

## Confronto con Baseline (se applicabile)

| Metrica | Agentic Pipeline (ReAct) |
|---|---|
| F1 Score | 0.613 |
| QUR | 64.7% |
| FUR | 46.5% |
| Precision | 0.582 |
| Recall | 0.647 |

> [!TIP]
> Per contestualizzare questi risultati, confrontali con le baseline della tesi (se disponibili).
> Un F1 di 0.613 è un punto di partenza solido ma migliorabile, soprattutto lavorando sulla FUR.
