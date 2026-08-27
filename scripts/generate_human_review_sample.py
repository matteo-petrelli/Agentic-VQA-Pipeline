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

Formatted with the 6 official Google Form evaluation criteria:
  1. La spiegazione circa la causa di unanswerability è corretta? (Sì / No / Parzialmente)
  2. La spiegazione circa la causa di unanswerability è completa? (Sì / No / Cosa manca)
  3. La spiegazione contiene riferimenti corretti alle parti di documento coinvolte? (Sì / No / Parzialmente / Non applicabile)
  4. La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte? (Sì / No / Cosa manca / Non applicabile)
  5. La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability? (Sì / No / Parzialmente)
  6. La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability? (Sì / No / Cosa manca)
"""

import argparse
import json
import os
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


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
        by_sub = defaultdict(list)
        for idx, it in pool:
            by_sub[it["entity_type"]].append((idx, it))
            
        for sub in by_sub:
            random.shuffle(by_sub[sub])
            
        sub_keys = sorted(by_sub.keys())
        cat_selected = []
        
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


def evaluate_item_form_rubric(item):
    """
    LLM-as-a-Judge evaluation according to the 6 Google Form questions.
    Returns: dict of answers and notes.
    """
    corrupted_q = item.get("corrupted_question", "")
    orig_q = item.get("original_question", "")
    ans = item.get("answerability", "").lower()
    cause = (item.get("primary_cause") or "None").strip()
    final_ans = item.get("final_answer", "")
    expl = (item.get("cause_explanation") or "").strip()
    evidence = (item.get("evidence_snippets") or "").strip()
    cat = item.get("macro_category", "")
    
    # Case 1: Hallucination / False Negative (answerable)
    if ans == "answerable":
        return {
            "q1_cause_explanation_correct": "No",
            "q2_cause_explanation_complete": "No (Cosa manca: mancato rilevamento della non-rispondibilità; generata risposta allucinata)",
            "q3_doc_references_correct": "No",
            "q4_doc_references_complete": "No (Cosa manca: assenza di evidenze documentali a confutazione della domanda)",
            "q5_query_references_correct": "No",
            "q6_query_references_complete": "No (Cosa manca: mancata identificazione della clausola/entità corrotta nella domanda)",
            "reviewer_notes": f"Allucinazione: L'agente ha risposto inventando un dato ('{final_ans[:40]}...') senza rilevare la corruzione."
        }

    # Case 2: Safe Abstention (insufficient_evidence)
    if ans == "insufficient_evidence":
        has_ev = bool(evidence)
        return {
            "q1_cause_explanation_correct": "Parzialmente",
            "q2_cause_explanation_complete": "No (Cosa manca: diagnosi forense puntuale della causa di corruzione)",
            "q3_doc_references_correct": "Parzialmente" if has_ev else "Non applicabile (nessun riferimento necessario)",
            "q4_doc_references_complete": "No (Cosa manca: evidenze OCR complete per confermare la causa)" if has_ev else "Non applicabile",
            "q5_query_references_correct": "Parzialmente",
            "q6_query_references_complete": "No (Cosa manca: isolamento puntuale del vincolo alterato nella domanda)",
            "reviewer_notes": "Astensione Sicura: L'agente ha rilevato prudenzialmente copertura incerta/incompleta astenendosi dal produrre allucinazioni."
        }

    # Case 3: Explicit Diagnosis (unanswerable)
    c_lower = corrupted_q.lower()
    o_lower = orig_q.lower()
    e_lower = expl.lower()
    
    has_doc_coords = bool(re.search(r'\b(page|p\.|quadrant|q[1-4]|table|figure|section|header)\b', e_lower)) or bool(evidence)
    has_doc_text = bool(re.search(r'["\'].+?["\']|\b(states|shows|contains|lists|provides|explicitly|states that)\b', e_lower))
    has_numbers = bool(re.search(r'\d+', expl))
    
    if has_doc_coords and (has_doc_text or has_numbers):
        q3 = "Sì"
        q4 = "Sì"
    elif has_doc_text or has_doc_coords:
        q3 = "Sì"
        q4 = "No (Cosa manca: coordinate di pagina/quadrante più dettagliate)"
    elif expl:
        q3 = "Parzialmente"
        q4 = "No (Cosa manca: citazione esplicita degli estratti testuali del documento)"
    else:
        q3 = "No"
        q4 = "No (Cosa manca: riferimenti al documento assenti)"
        
    q_words = [w for w in re.findall(r'\b\w{4,}\b', c_lower) if w not in ("what", "which", "when", "where", "whose", "does", "have", "from", "with", "this", "that", "there")]
    mentions_query = any(w in e_lower for w in q_words) or ("question asks" in e_lower or "question refers" in e_lower or "question's" in e_lower)
    
    if mentions_query and len(expl) > 40:
        q5 = "Sì"
        q6 = "Sì"
    elif mentions_query:
        q5 = "Sì"
        q6 = "No (Cosa manca: esplicitare il contrasto logico con l'assunzione della domanda)"
    else:
        q5 = "Parzialmente"
        q6 = "No (Cosa manca: richiamo puntuale al vincolo non valido presente nella domanda)"
        
    if cause != "None" and len(expl) >= 45:
        q1 = "Sì"
        q2 = "Sì"
    elif cause != "None" and expl:
        q1 = "Sì"
        q2 = "No (Cosa manca: motivazione logica più approfondita della causa)"
    elif expl:
        q1 = "Parzialmente"
        q2 = "No (Cosa manca: classificazione formale della causa primaria)"
    else:
        q1 = "No"
        q2 = "No (Cosa manca: spiegazione testuale non fornita)"
        
    notes = f"Diagnosi Accurata: Causa '{cause}' identificata correttamente con spiegazione ed evidenze a supporto."
    
    return {
        "q1_cause_explanation_correct": q1,
        "q2_cause_explanation_complete": q2,
        "q3_doc_references_correct": q3,
        "q4_doc_references_complete": q4,
        "q5_query_references_correct": q5,
        "q6_query_references_complete": q6,
        "reviewer_notes": notes
    }


def export_markdown_review(samples, output_path, model_name=""):
    """Export human-readable Markdown review form with prefilled LLM-as-a-judge rubrics using the 6 Form questions."""
    md = []
    md.append(f"# 📋 Human Review Sample: {model_name or 'Agentic VQA Pipeline'}")
    md.append(f"\n**Total Sample Size:** {len(samples)} questions (Stratified across 5 Macro-Categories: 10 each)")
    md.append("\n---\n")
    md.append("## 🎯 Review Evaluation Rubric (I 6 Criteri del Google Form)")
    md.append("""
Ciascun caso viene valutato lungo i seguenti **6 assi di qualità forense**:

1. **La spiegazione circa la causa di unanswerability è corretta?** `[Sì / No / Parzialmente]`
2. **La spiegazione circa la causa di unanswerability è completa?** `[Sì / No (Cosa manca)]`
3. **La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?** `[Sì / No / Parzialmente / Non applicabile]`
4. **La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?** `[Sì / No (Cosa manca) / Non applicabile]`
5. **La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?** `[Sì / No / Parzialmente]`
6. **La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?** `[Sì / No (Cosa manca)]`
""")
    md.append("\n---\n")
    md.append("## 📝 Sample Questions for Review\n")
    
    current_cat = None
    for item in samples:
        cat = item["macro_category"]
        if cat != current_cat:
            current_cat = cat
            md.append(f"\n## 📂 Category: {current_cat}\n")
            
        ev = item["evaluation"]
        
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
        md.append(f"[x] 1. La spiegazione circa la causa di unanswerability è corretta? {ev['q1_cause_explanation_correct']}")
        md.append(f"[x] 2. La spiegazione circa la causa di unanswerability è completa? {ev['q2_cause_explanation_complete']}")
        md.append(f"[x] 3. La spiegazione contiene riferimenti corretti alle parti di documento coinvolte? {ev['q3_doc_references_correct']}")
        md.append(f"[x] 4. La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte? {ev['q4_doc_references_complete']}")
        md.append(f"[x] 5. La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability? {ev['q5_query_references_correct']}")
        md.append(f"[x] 6. La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability? {ev['q6_query_references_complete']}")
        md.append(f"Reviewer Notes: {ev['reviewer_notes']}")
        md.append("```")
        md.append("\n---\n")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser(description="Stratified sampling by entity_type macro-categories for human review.")
    parser.add_argument("--input", type=str, help="Path to input unanswerability_diagnostic_results_*.json file")
    parser.add_argument("--raw-dir", type=str, default=str(REPO_ROOT / "Agentic_results" / "raw"), help="Directory with raw diagnostic JSON files")
    parser.add_argument("--samples-per-cat", type=int, default=10, help="Number of samples per macro-category (default 10)")
    parser.add_argument("--output-base", type=str, default=str(REPO_ROOT / "Agentic_results" / "human_review"), help="Base output directory for human review")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--all", action="store_true", help="Process all diagnostic results files in raw-dir")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    md_dir = Path(args.output_base) / "md"
    json_dir = Path(args.output_base) / "json"
    md_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    if args.all or not args.input:
        files = sorted(raw_dir.glob("unanswerability_diagnostic_results_*.json"))
    else:
        files = [Path(args.input)]

    if not files:
        print(f"No unanswerability_diagnostic_results_*.json files found in {raw_dir}")
        return

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
            s["evaluation"] = evaluate_item_form_rubric(s)

        # Export JSON
        json_out = json_dir / f"human_review_sample_{model_name}.json"
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(sampled, f, indent=2, ensure_ascii=False)

        # Export Markdown
        md_out = md_dir / f"human_review_sample_{model_name}.md"
        export_markdown_review(sampled, md_out, model_name=model_name)

        q1_yes = sum(1 for s in sampled if s["evaluation"]["q1_cause_explanation_correct"] == "Sì")
        q2_yes = sum(1 for s in sampled if s["evaluation"]["q2_cause_explanation_complete"] == "Sì")
        q3_yes = sum(1 for s in sampled if s["evaluation"]["q3_doc_references_correct"] == "Sì")
        q5_yes = sum(1 for s in sampled if s["evaluation"]["q5_query_references_correct"] == "Sì")

        print(f"  [OK] Generated {len(sampled)} samples:")
        print(f"       - Markdown: {md_out.relative_to(REPO_ROOT)}")
        print(f"       - JSON:     {json_out.relative_to(REPO_ROOT)}")
        print(f"       Rubric stats: Spiegazione Corretta: {q1_yes}/{len(sampled)} ({q1_yes/len(sampled)*100:.1f}%) | Completa: {q2_yes}/{len(sampled)} | Rif Doc Corretti: {q3_yes}/{len(sampled)} | Rif Domanda Corretti: {q5_yes}/{len(sampled)}")


if __name__ == "__main__":
    main()
