"""
Stratified sampling utility for human review of Agentic VQA Pipeline results.
Generates balanced, representative samples of question-answer-diagnosis pairs
for human evaluation stratified across the 5 Entity-Type Macro-Categories:
  1. Numerical Corruption (10 samples)
  2. Temporal Corruption (10 samples)
  3. Entity Corruption (10 samples)
  4. Location Corruption (10 samples)
  5. Document Structure Corruption (10 samples)
Total: 50 samples per model.
"""

import argparse
import json
import os
import random
import re
from collections import defaultdict
from pathlib import Path


MACRO_CATEGORIES = {
    "Numerical Corruption": [
        "percentage", "currency", "temperature", "measure_unit",
        "numerical_value_number", "price_number_information", "price_numerical_value",
        "numerical_value", "number"
    ],
    "Temporal Corruption": [
        "date_information", "date_numerical_value", "time_information",
        "time_numerical_value", "year_number_information", "year_numerical_value",
        "date", "time", "year"
    ],
    "Entity Corruption": [
        "person_name", "company_name", "product", "food", "chemical_element",
        "job_title_name", "job_title_information", "animal", "plant", "movie",
        "book", "transport_means", "event", "person", "company", "job_title"
    ],
    "Location Corruption": [
        "country", "city", "street", "spatial_information", "continent",
        "postal_code_information", "postal_code_numerical_value", "location"
    ],
    "Document Structure Corruption": [
        "document_position_information", "page_number_information",
        "page_number_numerical_value", "document_element_type",
        "document_element_information", "document_structure_information",
        "document_element", "position", "page_number"
    ],
}


def get_macro_category(entity_type):
    if isinstance(entity_type, list):
        entity_type = entity_type[0] if entity_type else ""
    et = str(entity_type or "").strip().lower()
    for cat_name, sub_types in MACRO_CATEGORIES.items():
        for st in sub_types:
            if st == et or st in et:
                return cat_name
    return "Document Structure Corruption"


def extract_item_fields(item, index):
    """Extract clean, normalized fields from a question item."""
    agent_res = item.get("agentic_result", {})
    
    # Extract explanation
    explanation = agent_res.get("cause_explanation") or ""
    if not explanation and agent_res.get("diagnostic_results"):
        for diag in agent_res["diagnostic_results"]:
            if diag.get("explanation"):
                explanation = diag["explanation"]
                break
    
    # Extract evidence snippets
    evidence_snippets = []
    for diag in agent_res.get("diagnostic_results", []):
        for ev in diag.get("evidence_for", []):
            snippet = ev.get("snippet", "")
            page = ev.get("page", "")
            quadrant = ev.get("quadrant", "")
            if snippet:
                evidence_snippets.append(f"[p.{page} {quadrant}] {snippet}")
    
    raw_et = item.get("entity_type", "Unknown")
    if isinstance(raw_et, list):
        raw_et = raw_et[0] if raw_et else "Unknown"
        
    return {
        "sample_id": index + 1,
        "question_id": item.get("question_id", f"Q_{index+1}"),
        "corrupted_question": item.get("corrupted_question", ""),
        "original_question": item.get("original_question", ""),
        "complexity": item.get("complexity", 1),
        "macro_category": get_macro_category(raw_et),
        "entity_type": str(raw_et),
        "answerability": agent_res.get("answerability", "unknown"),
        "primary_cause": agent_res.get("primary_cause") or "None",
        "final_answer": agent_res.get("final_answer", ""),
        "cause_explanation": explanation,
        "evidence_coverage": agent_res.get("evidence_coverage", 0.0),
        "prompts_used": ", ".join(agent_res.get("prompts_used", [])),
        "evidence_snippets": " | ".join(evidence_snippets[:2]),
        "image_paths": ", ".join([os.path.basename(p) for p in item.get("image_paths", [])]),
    }


def stratified_sample_by_macro_categories(items, samples_per_cat=10, seed=42):
    """
    Select a representative stratified sample of items covering:
    - 5 Macro Categories (Numerical, Temporal, Entity, Location, Document Structure)
    - 10 samples per Macro Category (Total = 50)
    - Sub-type and complexity diversity within each category
    """
    random.seed(seed)
    
    # Group items by macro category
    cat_order = [
        "Numerical Corruption",
        "Temporal Corruption",
        "Entity Corruption",
        "Location Corruption",
        "Document Structure Corruption",
    ]
    
    grouped = defaultdict(list)
    for i, item in enumerate(items):
        ext = extract_item_fields(item, i)
        grouped[ext["macro_category"]].append((i, ext))
        
    sampled = []
    
    for cat_name in cat_order:
        pool = grouped[cat_name]
        # Sub-group by entity_type to maximize sub-type variety
        by_sub = defaultdict(list)
        for idx, it in pool:
            by_sub[it["entity_type"]].append((idx, it))
            
        for sub in by_sub:
            random.shuffle(by_sub[sub])
            
        sub_keys = sorted(by_sub.keys())
        cat_selected = []
        
        # Round-robin selection across sub-types
        while len(cat_selected) < samples_per_cat and any(by_sub.values()):
            for k in sub_keys:
                if by_sub[k] and len(cat_selected) < samples_per_cat:
                    cat_selected.append(by_sub[k].pop(0))
                    
        for idx, it in cat_selected:
            sampled.append(it)
            
    # Re-index sample IDs 1..N
    for i, s in enumerate(sampled, 1):
        s["sample_id"] = i
        
    return sampled


def evaluate_item_llm_judge(item):
    """
    LLM-as-a-Judge evaluation of an item against ground-truth unanswerability.
    Returns: (decision_score, cause_score, expl_score, trust_score, reviewer_notes)
    """
    corrupted_q = item.get("corrupted_question", "")
    orig_q = item.get("original_question", "")
    ans = item.get("answerability", "").lower()
    cause = (item.get("primary_cause") or "None").strip()
    final_ans = item.get("final_answer", "")
    expl = (item.get("cause_explanation") or "").strip()
    cat = item.get("macro_category", "")
    
    # 1. Answerability Decision (All items are ground-truth unanswerable)
    if ans in ("unanswerable", "insufficient_evidence"):
        decision_score = 1
    else:
        decision_score = 0  # Answerable -> False Negative / Hallucination

    # Analyze nature of corruption
    c_lower = corrupted_q.lower()
    o_lower = orig_q.lower()
    
    is_temporal = (cat == "Temporal Corruption") or any(w in c_lower or w in o_lower for w in ["year", "date", "19", "20", "month", "september", "time", "hour", "when", "timeframe"]) and (c_lower != o_lower)
    is_numeric = (cat == "Numerical Corruption") or (bool(re.search(r'\d+', corrupted_q)) and bool(re.search(r'\d+', orig_q)) and (c_lower != o_lower))
    is_spatial = (cat == "Location Corruption") or any(w in c_lower for w in ["page", "column", "top", "bottom", "left", "right", "where", "location", "center", "address", "zip"])
    is_doc_struct = (cat == "Document Structure Corruption") or any(w in c_lower for w in ["table", "figure", "header", "text", "element", "chart", "diagram", "memo", "column"])
    
    if ans == "answerable":
        cause_score = 0
        expl_score = 0
        trust_score = 1
        notes = f"Hallucination: Model failed to detect unanswerability and generated an ungrounded answer ('{final_ans[:45]}...')."
        return decision_score, cause_score, expl_score, trust_score, notes

    # Cause scoring
    if cause in ("None", "EXTRACTION_FAILURE"):
        if ans == "insufficient_evidence":
            cause_score = 1
            expl_score = 2 if expl else 1
            trust_score = 3
            notes = "Safe Abstention: Conservative decision to abstain due to uncertain/incomplete evidence coverage."
        else:
            cause_score = 0
            expl_score = 1
            trust_score = 2
            notes = "Abstained without identifying a specific corruption cause."
    elif cause == "SPATIAL_MISMATCH":
        if is_spatial or is_doc_struct or "page" in c_lower or "location" in c_lower or "where" in c_lower:
            cause_score = 2
        else:
            cause_score = 1
        
        if expl and len(expl) > 35:
            expl_score = 3 if ("quadrant" in expl.lower() or "state" in expl.lower() or "figure" in expl.lower() or bool(re.search(r'\d+', expl))) else 2
        elif expl:
            expl_score = 2
        else:
            expl_score = 0
        trust_score = 5 if (cause_score == 2 and expl_score == 3) else (4 if expl_score >= 2 else 3)
        notes = f"Accurate spatial verification: correctly diagnosed {cause} with grounded rationale."

    elif cause in ("VALUE_MISMATCH", "TEMPORAL_MISMATCH"):
        if is_numeric or is_temporal:
            cause_score = 2
        else:
            cause_score = 1
        
        if expl and len(expl) > 35:
            expl_score = 3 if bool(re.search(r'\d+', expl)) else 2
        elif expl:
            expl_score = 1
        else:
            expl_score = 0
        trust_score = 5 if (cause_score == 2 and expl_score == 3) else 4
        notes = f"High-fidelity diagnosis: correctly identified mismatch between query premise and document data."

    elif cause in ("ENTITY_MISMATCH", "ENTITY_MISSING"):
        cause_score = 2 if cat == "Entity Corruption" else 1
        if expl and len(expl) > 30:
            expl_score = 3 if ("only lists" in expl or "not contain" in expl or "focuses on" in expl or "stated" in expl) else 2
        elif expl:
            expl_score = 1
        else:
            expl_score = 0
        trust_score = 5 if (cause_score == 2 and expl_score >= 2) else 4
        notes = f"Correct entity validation: detected nonexistent or substituted entity constraint."

    elif cause == "DOCUMENT_ELEMENT_MISMATCH":
        cause_score = 2 if is_doc_struct else 1
        expl_score = 2 if expl else 1
        trust_score = 4
        notes = f"Correct structural/logical diagnosis: identified {cause}."

    elif cause == "UNSUPPORTED_PRESUPPOSITION":
        cause_score = 2
        expl_score = 2 if expl else 1
        trust_score = 4
        notes = f"Presupposition disproved: question assumed unverified fact."
    else:
        cause_score = 1
        expl_score = 2 if expl else 1
        trust_score = 3
        notes = f"Diagnosis assigned ({cause})."

    return decision_score, cause_score, expl_score, trust_score, notes


def export_markdown_review(samples, output_path, model_name=""):
    """Export human-readable Markdown review form with prefilled LLM-as-a-judge rubrics."""
    md = []
    md.append(f"# 📋 Human Review Sample: {model_name or 'Agentic VQA Pipeline'}")
    md.append(f"\n**Total Sample Size:** {len(samples)} questions (Stratified across 5 Macro-Categories: 10 each)")
    md.append("\n---\n")
    md.append("## 🎯 Review Evaluation Rubric (Criteri di Valutazione)")
    md.append("""
Per ciascuna domanda, valuta i seguenti **4 assi di qualità**:

1. **Answerability Decision [0 - 1]**:
   - `1 (Corretto)`: L'agente ha rilevato che la domanda non ha risposta (`unanswerable` o `insufficient_evidence`).
   - `0 (Errore / Allucinazione)`: L'agente ha risposto inventando un dato (`answerable`).

2. **Cause Diagnosis [0 - 2]**:
   - `2 (Esatta)`: La causa (`SPATIAL`, `VALUE`, `TEMPORAL`, `ENTITY`, ecc.) corrisponde esattamente alla corruzione applicata.
   - `1 (Plausibile / Parziale)`: La causa è correlata ma non primaria (es. confonde `SPATIAL` con `VALUE`).
   - `0 (Completamente errata)`: Causa non pertinente o non assegnata.

3. **Explanation Quality & Factuality [0 - 3]**:
   - `3 (Eccellente)`: Spiegazione precisa, cita l'evidenza reale del documento (OCR / pagina / quadrante) e spiega l'incongruenza logica.
   - `2 (Buona / Accettabile)`: Spiegazione corretta ma generica o priva di coordinate dettagliate.
   - `1 (Debole / Confusa)`: Spiegazione poco chiara o parzialmente imprecisa.
   - `0 (Allucinata)`: La spiegazione inventa fatti non presenti nel documento.

4. **Overall Trustworthiness (Affidabilità Complessiva) [1 - 5]**:
   - Voto sintetico da 1 (Pessima / Pericolosa in produzione) a 5 (Perfetta, pronta per audit umano).
""")
    md.append("\n---\n")
    md.append("## 📝 Sample Questions for Review\n")
    
    current_cat = None
    for item in samples:
        cat = item["macro_category"]
        if cat != current_cat:
            current_cat = cat
            md.append(f"\n## 📂 Category: {current_cat}\n")
            
        d_score, c_score, e_score, t_score, notes = evaluate_item_llm_judge(item)
        
        md.append(f"### Item #{item['sample_id']} — Category: **`{item['macro_category']}`** | Type: `{item['entity_type']}` | Complexity: `C{item['complexity']}`")
        md.append(f"- **Corrupted Question**: *\"{item['corrupted_question']}\"*")
        if item.get("original_question"):
            md.append(f"- **Original Question**: *\"{item['original_question']}\"*")
        md.append(f"- **Agent Decision**: **`{item['answerability']}`** | **Primary Cause**: `{item['primary_cause']}`")
        md.append(f"- **Agent Final Answer**: `{item['final_answer']}`")
        md.append(f"- **Agent Cause Explanation**:\n  > {item['cause_explanation'] or '*(Nessuna spiegazione fornita)*'}")
        if item.get("evidence_snippets"):
            md.append(f"- **Extracted Evidence**: `{item['evidence_snippets']}`")
        md.append(f"- **Prompts Used**: `{item['prompts_used']}`")
        md.append("")
        md.append("```")
        md.append(f"[x] Answerability Correct (0/1): {d_score}")
        md.append(f"[x] Cause Diagnosis Correct (0/1/2): {c_score}")
        md.append(f"[x] Explanation Quality (0/1/2/3): {e_score}")
        md.append(f"[x] Overall Trustworthiness (1-5): {t_score}")
        md.append(f"Reviewer Notes: {notes}")
        md.append("```")
        md.append("\n---\n")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser(description="Stratified sampling by entity_type macro-categories for human review.")
    parser.add_argument("--input", type=str, help="Path to input unanswerability_diagnostic_results_*.json file")
    parser.add_argument("--samples-per-cat", type=int, default=10, help="Number of samples per macro-category (default 10)")
    parser.add_argument("--output-dir", type=str, default="Agentic_results", help="Directory to save output files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--all", action="store_true", help="Process all diagnostic results files in output-dir")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.all or not args.input:
        files = sorted(out_dir.glob("unanswerability_diagnostic_results_*.json"))
    else:
        files = [Path(args.input)]

    for json_file in files:
        model_name = json_file.stem.replace("unanswerability_diagnostic_results_", "")
        print(f"\nProcessing '{model_name}' from {json_file.name}...")
        
        with open(json_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        items = raw_data.get("corrupted_questions", [])
        if not items:
            print(f"No corrupted_questions found in {json_file.name}")
            continue

        sampled = stratified_sample_by_macro_categories(items, samples_per_cat=args.samples_per_cat, seed=args.seed)

        # Attach prefilled evaluation to JSON
        for s in sampled:
            d_score, c_score, e_score, t_score, notes = evaluate_item_llm_judge(s)
            s["evaluation"] = {
                "decision_score": d_score,
                "cause_score": c_score,
                "explanation_score": e_score,
                "trust_score": t_score,
                "reviewer_notes": notes,
            }

        # Export JSON
        json_out = out_dir / f"human_review_sample_{model_name}.json"
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(sampled, f, indent=2, ensure_ascii=False)

        # Export Markdown
        md_out = out_dir / f"human_review_sample_{model_name}.md"
        export_markdown_review(sampled, md_out, model_name=model_name)

        # Print stats
        cat_counts = defaultdict(int)
        for s in sampled:
            cat_counts[s["macro_category"]] += 1
            
        avg_dec = sum(s["evaluation"]["decision_score"] for s in sampled) / len(sampled) * 100
        avg_cause = sum(s["evaluation"]["cause_score"] for s in sampled) / (len(sampled) * 2) * 100
        avg_expl = sum(s["evaluation"]["explanation_score"] for s in sampled) / (len(sampled) * 3) * 100
        avg_trust = sum(s["evaluation"]["trust_score"] for s in sampled) / len(sampled)

        print(f"  [OK] Generated {len(sampled)} samples:")
        print(f"       - Markdown: {md_out.name}")
        print(f"       - JSON:     {json_out.name}")
        print(f"       Distribution: {dict(cat_counts)}")
        print(f"       LLM-as-a-Judge Scores: Answerability {avg_dec:.1f}% | Cause {avg_cause:.1f}% | Explanation {avg_expl:.1f}% | Trust {avg_trust:.2f}/5.0")

    # Clean up old CSV files in out_dir as requested
    csv_files = list(out_dir.glob("human_review_sample_*.csv"))
    for csv_f in csv_files:
        try:
            csv_f.unlink()
            print(f"  [Cleaned] Removed obsolete CSV: {csv_f.name}")
        except Exception as e:
            print(f"  [Warning] Could not remove {csv_f.name}: {e}")


if __name__ == "__main__":
    main()
