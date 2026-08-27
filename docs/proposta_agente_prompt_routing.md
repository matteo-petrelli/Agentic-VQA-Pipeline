# Proposta di Unanswerability Diagnostic Agent per VQA

## Obiettivo

L'obiettivo e' integrare il lavoro precedente sui prompt per il riconoscimento delle `corrupted_question` in un agente focalizzato prima di tutto sulla **diagnosi di answerability**. L'agente non deve limitarsi a scegliere tra una risposta e `Unable to determine`: deve stabilire se la domanda e' supportata dal documento, individuare la possibile causa di unanswerability e raccogliere evidenza sufficiente per confermarla o smentirla.

L'output principale diventa quindi una decisione a tre stati:

| Stato | Significato |
|---|---|
| `answerable` | Il documento contiene evidenza diretta e coerente per rispondere |
| `unanswerable` | Una premessa o un vincolo della domanda e' incompatibile con il documento |
| `insufficient_evidence` | L'evidenza non basta per decidere, per esempio per OCR incompleto o pagina mancante |

La distinzione e' essenziale: `unanswerable` descrive una proprieta' della domanda rispetto al documento; `insufficient_evidence` descrive un limite dell'osservazione o della pipeline. Solo il primo stato deve essere considerato rilevamento certo di una `corrupted_question`.

## Evidenze dagli esperimenti precedenti

Gli esperimenti in `VQA_Experiments` hanno testato diverse famiglie di prompt:

| Famiglia | Evidenza usata | Ruolo nell'agente |
|---|---|---|
| `docel`, `docel_cot_*` | OCR strutturato con document elements | Answering e controllo del contesto |
| `nlp_tag`, `nlp_tag_cot` | OCR con entity tags inline | Rilevamento di entita' mancanti o incoerenti |
| `nlp_list`, `nlp_list_ocr_cot` | Liste di entita' domanda/documento | Verifica di mismatch tra entita' |
| `layout_v*` | Informazione visuale e quadranti | Controllo spaziale e strutturale |
| `baseline`, `baseline_ocr` | Immagine o OCR semplice | Baseline di confronto |

Dai risultati emerge una distinzione utile tra prompt "detector" e prompt "answerer":

| Prompt | QUR | UR | Lettura |
|---|---:|---:|---|
| Qwen2.5 `NLP_tag_cot` | 0.8235 | 0.9554 | Ottimo detector, troppo astensivo come risposta finale |
| Qwen2.5 `DocEl_cot_v4` | 0.3262 | 0.3397 | Piu' bilanciato, adatto come answerer/verifier |
| Qwen2.5 `DocEl` | 0.2032 | 0.2550 | Poco astensivo, utile come fallback |
| Phi `Layout_v1` | 0.8503 | 0.9576 | Forte detector spaziale, ma molto conservativo |

Nota: `UR` misura la percentuale complessiva di risposte `Unable`, non la FUR sulle sole domande originali. Va quindi letto come indice di astensione.

## Tassonomia delle cause di unanswerability

L'agente deve produrre una o piu' cause candidate, ciascuna accompagnata da evidenza. Una tassonomia iniziale puo' essere:

| Codice | Causa | Esempio diagnostico | Evidenza principale |
|---|---|---|---|
| `ENTITY_MISSING` | Un'entita' richiesta non compare nel documento | La persona citata non e' presente | Entity tags/list + OCR |
| `ENTITY_MISMATCH` | L'entita' presente e' diversa da quella richiesta | Nome o organizzazione sostituiti | Entity tags/list |
| `VALUE_MISMATCH` | Numero, data, anno, importo o percentuale non coincidono | La domanda cita 2015, il documento 2012 | OCR + entity tags |
| `RELATION_MISMATCH` | Le entita' esistono ma non hanno la relazione richiesta | La persona compare, ma non con quel ruolo | Document elements + contesto OCR |
| `ANSWER_TYPE_MISMATCH` | Il documento non contiene il tipo di risposta richiesto | Si chiede una data, ma e' riportato solo un luogo | Question analysis + OCR |
| `DOCUMENT_ELEMENT_MISMATCH` | La domanda rimanda all'elemento sbagliato | Informazione attribuita a una tabella inesistente | Document elements |
| `SPATIAL_MISMATCH` | Pagina, quadrante o posizione non sono coerenti | La domanda cita page 6, il documento ne ha 4 | Layout + metadati pagina |
| `TEMPORAL_MISMATCH` | Il periodo richiesto e' incompatibile con il documento | Evento o valore associato a un altro anno | OCR + entity tags |
| `UNSUPPORTED_PRESUPPOSITION` | Una premessa della domanda non e' supportata | "the two new hires" quando ne compare uno solo | Question decomposition + OCR |
| `AMBIGUOUS_TARGET` | Esistono piu' candidati e il documento non consente di scegliere | Due valori ugualmente compatibili | OCR + contesto |
| `EVIDENCE_MISSING` | La parte necessaria del documento non e' disponibile | Pagina o sezione richiesta assente | Coverage check |
| `EXTRACTION_FAILURE` | OCR, layout o tagging non sono affidabili | Testo illeggibile o tool in errore | Tool diagnostics |

Le ultime due cause devono normalmente portare a `insufficient_evidence`, non a `unanswerable`. Anche l'assenza di un'entita' puo' confermare `ENTITY_MISSING` solo dopo avere verificato una copertura adeguata di tutte le pagine rilevanti.

Ogni ipotesi di causa attraversa un ciclo esplicito:

| Stato causa | Significato |
|---|---|
| `suspected` | La domanda contiene segnali compatibili con la causa, ma non e' ancora stata verificata |
| `confirmed` | Esiste evidenza positiva del mismatch e la copertura e' sufficiente |
| `rejected` | E' stata trovata evidenza documentale che smentisce la causa |
| `undetermined` | Il test non e' conclusivo o la copertura e' insufficiente |

Il risultato di ogni test diagnostico deve quindi contenere `evidence_for`, `evidence_against`, `coverage` e `next_test`. Questo obbliga l'agente a cercare anche elementi che possano falsificare la propria ipotesi, riducendo la tendenza a confermare prematuramente un `Unable`.

## Idea dell'agente

L'agente proposto puo' essere descritto come un **Unanswerability Diagnostic Agent**. La scelta centrale e' separare quattro funzioni:

| Funzione | Prompt candidati | Scopo |
|---|---|---|
| Question analyzer | Prompt dedicato strutturato | Scomporre domanda, entita', vincoli e presupposizioni |
| Cause diagnoser | `nlp_tag_cot`, `layout_v4`, `nlp_list_ocr_cot` | Generare e testare cause candidate di unanswerability |
| Answerability verifier | `docel_cot_v4`, prompt dedicato | Decidere tra `answerable`, `unanswerable` e `insufficient_evidence` |
| Answerer | `docel_cot_v4`, `docel`, `nlp_tag` | Rispondere solo dopo un verdetto `answerable` |

In questo modo un prompt molto conservativo non decide da solo la risposta finale. Produce invece un'ipotesi diagnostica, per esempio `VALUE_MISMATCH`, che deve essere verificata contro OCR, contesto, document elements e copertura delle pagine.

## Flusso logico

```text
Domanda + immagini documento
    -> analisi della domanda
       entita', answer type, relazioni, vincoli, presupposizioni
    -> estrazione iniziale dell'evidenza
       OCR, document elements, entity tags, pagine e quadranti
    -> generazione delle cause candidate
       mismatch semantico, numerico, temporale, spaziale o strutturale
    -> routing diagnostico
       scelta del prompt piu' adatto a testare ogni causa
    -> verifica della copertura
       tutte le pagine/regioni rilevanti sono state osservate?
    -> verdetto di answerability
       answerable / unanswerable / insufficient_evidence
    -> answering condizionale
       eseguito solo se answerable
    -> output diagnostico
       stato + cause + evidenze + confidence + trace
```

## Scelte principali dell'agente

### Separare diagnosi e answering

I prompt con QUR alto sono spesso anche quelli con UR alto. Per questo non conviene usare `NLP_tag_cot` o `layout_v4` come prompt finali universali. Devono formulare affermazioni verificabili, per esempio: "l'anno richiesto non compare nelle pagine analizzate" oppure "la pagina citata non esiste". L'answerer non viene eseguito finche' il verifier non ha escluso una causa confermata di unanswerability.

### Scomporre la domanda prima di osservare il documento

Il question analyzer estrae una rappresentazione strutturata:

```json
{
   "answer_type": "job_title",
   "entities": ["James Casey"],
   "relations": ["new_hire", "has_job_title"],
   "constraints": ["count=2"],
   "spatial_references": [],
   "presuppositions": ["there are two new hires named James Casey"]
}
```

Questa scomposizione permette di riconoscere non solo entita' corrotte, ma anche relazioni, cardinalita', tipo di risposta e presupposizioni incompatibili.

### Usare `DocEl_cot_v4` come verifier e answerer principale

`DocEl_cot_v4` sfrutta OCR strutturato e document elements, quindi puo' controllare se l'informazione viene da una parte coerente del documento. Prima verifica le cause proposte; solo in assenza di mismatch confermati produce una risposta candidata.

### Usare `NLP_tag_cot` per cause entity/value based

`NLP_tag_cot` e' adatto quando la domanda contiene entita' esplicite: date, nomi, numeri, luoghi, organizzazioni. Il suo output deve indicare `expected`, `observed`, pagine e frammenti di evidenza per supportare cause come `ENTITY_MISMATCH`, `VALUE_MISMATCH` o `TEMPORAL_MISMATCH`.

### Usare `Layout_v4` per cause spaziali e strutturali

I prompt layout vanno usati quando la domanda contiene segnali come pagina, quadrante, posizione, header, footer, table, figure, chart, first/last page. Devono verificare `SPATIAL_MISMATCH` o `DOCUMENT_ELEMENT_MISMATCH`, senza interpretare la mancata lettura del testo come prova di corruzione.

### Usare `NLP_list_ocr_cot` per falsificare le cause candidate

`NLP_list_ocr_cot` controlla in modo esplicito il matching tra entita' della domanda, entita' del documento e OCR. Una causa viene confermata solo se il verifier trova evidenza positiva del mismatch e non trova un match valido in un'altra pagina o sezione.

## Router diagnostico proposto

La prima versione puo' essere rule-based e spiegabile. Il router non sceglie direttamente quale prompt dara' la risposta: sceglie quale test eseguire su ciascuna possibile causa.

| Feature della domanda/documento | Cause candidate | Prompt diagnostico | Verifica finale |
|---|---|---|---|
| Date, anni, numeri, percentuali | `VALUE_MISMATCH`, `TEMPORAL_MISMATCH` | `NLP_tag_cot` | `NLP_list_ocr_cot` |
| Persone, aziende, luoghi | `ENTITY_MISSING`, `ENTITY_MISMATCH` | `NLP_tag_cot` | `NLP_list_ocr_cot` |
| Ruoli, eventi e relazioni | `RELATION_MISMATCH`, `UNSUPPORTED_PRESUPPOSITION` | `DocEl_cot_v4` | Prompt verifier dedicato |
| Tabelle | `DOCUMENT_ELEMENT_MISMATCH`, `VALUE_MISMATCH` | `DocEl_cot_v4` | `Layout_v4` se conta la posizione |
| Figure o contenuto visuale | `DOCUMENT_ELEMENT_MISMATCH`, `EVIDENCE_MISSING` | `Layout_v4` | Controllo visuale multi-page |
| Pagina, quadrante, posizione | `SPATIAL_MISMATCH` | `Layout_v4` | Coverage check |
| Piu' candidati compatibili | `AMBIGUOUS_TARGET` | `DocEl_cot_v4` | `NLP_list_ocr_cot` |
| OCR incompleto o tool error | `EXTRACTION_FAILURE` | Retry/fallback | `insufficient_evidence` |

Una versione successiva puo' essere data-driven e basata sui risultati precedenti. Il punteggio deve premiare non solo il rilevamento di `Unable`, ma anche la precisione della causa:

```text
score(prompt, causa, segmento) = cause_F1 - alpha * FUR - beta * cost
```

Il segmento puo' essere tipo di domanda, document element, quadrante o complessita'. Per stimare `cause_F1` serve annotare le cause o derivarle dai metadati di corruzione. I campi `original_entity`, `corrupted_entities` e `patch_entities` possono essere usati offline per costruire etichette, ma non devono essere esposti all'agente durante l'inferenza.

## Decisione finale

Il verifier finale applica regole esplicite e richiede evidenza positiva:

```text
1. Causa confermata + copertura sufficiente -> unanswerable.
2. Causa sospetta ma copertura insufficiente -> insufficient_evidence.
3. Nessuna causa confermata + evidenza diretta per la risposta -> answerable.
4. Risposta candidata da contesto, entita' o document element errati -> unanswerable.
5. Piu' risposte candidate senza criterio di disambiguazione -> unanswerable con AMBIGUOUS_TARGET.
6. OCR/tool failure senza evidenza semantica di mismatch -> insufficient_evidence.
7. Il solo disaccordo tra prompt non basta per dichiarare unanswerable.
```

Per ogni causa confermata vanno salvati almeno: valore atteso dalla domanda, valore osservato, pagina/document element, frammento di evidenza e test diagnostico usato.

## Confidence e stato della diagnosi

Non conviene usare una sola confidence. La sicurezza sulla diagnosi e quella sulla risposta misurano aspetti diversi:

| Campo | Significato |
|---|---|
| `answerability_confidence` | Sicurezza del verdetto a tre stati |
| `cause_confidence` | Sicurezza della causa primaria identificata |
| `answer_confidence` | Sicurezza della risposta, valorizzata solo se `answerable` |
| `evidence_coverage` | Quota di pagine/regioni rilevanti effettivamente verificate |

Esempi:

| Caso | Confidence |
|---|---|
| Mismatch esplicito, verificato su tutte le pagine rilevanti | Answerability High, cause High |
| Nessun mismatch e risposta supportata da OCR + document element | Answerability High, answer High |
| Entita' non trovata ma OCR parziale | Answerability Low, coverage Low, `insufficient_evidence` |
| Tool error o pagina mancante | Answerability Low, `insufficient_evidence` |
| Due cause plausibili ma non separabili | Answerability Medium, cause Low/Medium |

La confidence dichiarata dal VLM puo' essere conservata come segnale ausiliario, ma non deve determinare da sola il verdetto.

## Output strutturato

Un risultato dovrebbe avere una forma simile:

```json
{
   "answerability": "unanswerable",
   "primary_cause": "VALUE_MISMATCH",
   "secondary_causes": [],
   "cause_status": "confirmed",
   "expected": "2015",
   "observed": ["2012"],
   "evidence": [
      {
         "page": 2,
         "document_element": "Table",
         "snippet": "Volume 77, Issue 2012"
      }
   ],
   "evidence_coverage": 1.0,
   "final_answer": "Unable to determine",
   "answerability_confidence": 3,
   "cause_confidence": 3,
   "answer_confidence": null,
   "prompts_used": ["NLP_tag_cot", "NLP_list_ocr_cot"],
   "trace": []
}
```

## Implementazione possibile con LangGraph

LangGraph permette di implementare un ciclo ipotesi-test: l'agente genera una causa candidata, sceglie il test piu' informativo e aggiorna lo stato finche' la causa viene confermata, smentita o resta non decidibile.

| Nodo | Funzione |
|---|---|
| `analyze_question` | Estrae answer type, entita', relazioni, vincoli e presupposizioni |
| `extract_base_evidence` | Estrae OCR, document elements, tag, pagine e quadranti |
| `generate_cause_hypotheses` | Produce cause candidate ordinate per plausibilita' |
| `select_diagnostic_test` | Sceglie il prompt/tool adatto alla causa corrente |
| `run_diagnostic_test` | Cerca evidenza pro e contro la causa |
| `check_evidence_coverage` | Verifica pagine, regioni e qualita' dell'estrazione |
| `assess_answerability` | Decide i tre stati e se servono altri test |
| `run_answerer` | Produce la risposta solo nello stato `answerable` |
| `finalize_diagnosis` | Produce cause, evidenze, confidence e trace |

State essenziale:

```python
class AgentState(TypedDict):
    question: str
    image_paths: list[str]
   question_analysis: dict
    structured_ocr: str
    tagged_ocr: str
    question_entities: list[str]
    document_entities: list[str]
    document_elements: list[str]
    quadrants: list[str]
   cause_hypotheses: list[dict]
   current_cause: str | None
   diagnostic_results: list[dict]
   evidence_coverage: float
   answerability: str | None
   primary_cause: str | None
   final_answer: str | None
   answerability_confidence: int
   cause_confidence: int
   answer_confidence: int | None
    trace: list[dict]
```

Routing essenziale:

```text
generate hypotheses -> select test -> run test -> check coverage
   -> causa non risolta e budget disponibile: select test
   -> evidenza insufficiente: insufficient_evidence
   -> causa confermata: unanswerable
   -> cause smentite + answer evidence: answerable -> run answerer
```

## Piano sperimentale

1. **Prompt statici precedenti**: usare i risultati gia' disponibili come baseline.
2. **Agente ReAct legacy**: usare i risultati gia' prodotti come baseline storica, senza mantenerlo nel runtime corrente.
3. **Prompt Routing Agent**: valutare la selezione dinamica dei prompt senza diagnosi esplicita.
4. **Unanswerability Diagnostic Agent**: valutare verdetto a tre stati e riconoscimento delle cause.

Metriche principali:

- QUR;
- FUR sulle original questions;
- F1;
- UR come misura di astensione;
- accuratezza e macro-F1 delle cause;
- accuratezza del verdetto a tre stati;
- tasso di `insufficient_evidence`;
- coverage medio prima di dichiarare `unanswerable`;
- frequenza di selezione dei test diagnostici;
- numero medio di test per domanda;
- calibration error di answerability e cause confidence;
- percentuale di falsi `Unable` evitati distinguendo failure da corruzione.

Per valutare le cause serve un piccolo gold standard. Puo' essere ottenuto annotando un sottoinsieme o derivando etichette iniziali dalle trasformazioni che hanno generato le corrupted questions, con revisione manuale dei casi ambigui.

## Contributo metodologico

Il contributo e' trasformare i prompt precedenti in **test diagnostici specializzati**. Gli esperimenti non vengono abbandonati: diventano la base empirica per decidere quale evidenza cercare per verificare una specifica causa di unanswerability.

```text
Gli esperimenti precedenti mostrano che ogni prompt cattura un diverso tipo di evidenza.
L'agente usa questa conoscenza per generare e verificare ipotesi sulle cause di unanswerability,
distinguendo le contraddizioni del documento dai limiti di estrazione e rispondendo solo dopo
avere escluso mismatch confermati.
```

## Riassunto

La strategia finale e':

```text
1. Usare i risultati dei prompt experiments come base empirica.
2. Scomporre domanda, vincoli e presupposizioni.
3. Generare cause candidate di unanswerability.
4. Usare `NLP_tag_cot`, `Layout_v4` e `DocEl_cot_v4` come test specializzati.
5. Verificare sia evidenza a favore sia evidenza contro ogni causa.
6. Distinguere answerable, unanswerable e insufficient_evidence.
7. Eseguire l'answerer solo dopo un verdetto answerable.
8. Salvare causa, stato, expected/observed, evidence span, coverage e confidence separate.
```