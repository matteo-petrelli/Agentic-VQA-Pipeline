"""
Stratified sampling utility for human review of Agentic VQA Pipeline results.
Generates balanced, representative samples of question-answer-diagnosis pairs
for human evaluation across complexity levels, corruption types, and agent decisions.
"""

import argparse
import csv
import json
import os
import random
from collections import defaultdict
from pathlib import Path


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
    
    return {
        "sample_id": index + 1,
        "question_id": item.get("question_id", f"Q_{index+1}"),
        "corrupted_question": item.get("corrupted_question", ""),
        "original_question": item.get("original_question", ""),
        "complexity": item.get("complexity", "Unknown"),
        "entity_type": item.get("entity_type", "Unknown"),
        "answerability": agent_res.get("answerability", "unknown"),
        "primary_cause": agent_res.get("primary_cause") or "None",
        "final_answer": agent_res.get("final_answer", ""),
        "cause_explanation": explanation,
        "evidence_coverage": agent_res.get("evidence_coverage", 0.0),
        "prompts_used": ", ".join(agent_res.get("prompts_used", [])),
        "evidence_snippets": " | ".join(evidence_snippets[:2]),
        "image_paths": ", ".join([os.path.basename(p) for p in item.get("image_paths", [])]),
    }


def stratified_sample(items, sample_size=50, seed=42):
    """
    Select a representative stratified sample of items covering:
    - All complexities (C1, C2, C3)
    - All answerability outcomes (unanswerable, insufficient_evidence, answerable)
    - All diagnosed causes (SPATIAL, VALUE, TEMPORAL, ENTITY, etc.)
    """
    random.seed(seed)
    n_total = len(items)
    if n_total <= sample_size:
        return [extract_item_fields(item, i) for i, item in enumerate(items)]
    
    # Categorize items into strata: (complexity, answerability, primary_cause)
    strata = defaultdict(list)
    for i, item in enumerate(items):
        extracted = extract_item_fields(item, i)
        key = (extracted["complexity"], extracted["answerability"], extracted["primary_cause"])
        strata[key].append(extracted)
    
    sampled = []
    
    # 1. Guarantee inclusion of critical edge cases (all false negatives / answerable cases)
    for key, group in list(strata.items()):
        if key[1] == "answerable":  # Hallucination / False negative
            take = group  # include all for human review
            sampled.extend(take)
            strata[key] = []
    
    # 2. Proportional selection across remaining strata
    remaining_needed = sample_size - len(sampled)
    
    # Complexity targets roughly proportional: C1 ~ 60%, C2 ~ 30%, C3 ~ 10%
    comp_groups = defaultdict(list)
    for key, group in strata.items():
        comp_groups[key[0]].extend(group)
    
    # Shuffle within groups
    for comp in comp_groups:
        random.shuffle(comp_groups[comp])
    
    # Distribute remaining quota
    c3_quota = max(min(len(comp_groups["C3"]), int(remaining_needed * 0.12)), min(len(comp_groups["C3"]), 4))
    c2_quota = max(min(len(comp_groups["C2"]), int(remaining_needed * 0.32)), 12)
    c1_quota = remaining_needed - (c3_quota + c2_quota)
    
    quotas = {"C3": c3_quota, "C2": c2_quota, "C1": c1_quota}
    
    # Pick diverse causes within each complexity
    for comp, quota in quotas.items():
        pool = comp_groups[comp]
        # Group by cause to ensure cause diversity
        by_cause = defaultdict(list)
        for it in pool:
            by_cause[it["primary_cause"]].append(it)
        
        comp_sampled = []
        # Round-robin across causes
        cause_keys = list(by_cause.keys())
        while len(comp_sampled) < quota and any(by_cause.values()):
            for c_key in cause_keys:
                if by_cause[c_key] and len(comp_sampled) < quota:
                    comp_sampled.append(by_cause[c_key].pop(0))
        
        sampled.extend(comp_sampled)
    
    # If still short, backfill from any remaining
    if len(sampled) < sample_size:
        all_remaining = []
        sampled_ids = {it["sample_id"] for it in sampled}
        for i, item in enumerate(items):
            ext = extract_item_fields(item, i)
            if ext["sample_id"] not in sampled_ids:
                all_remaining.append(ext)
        random.shuffle(all_remaining)
        sampled.extend(all_remaining[: sample_size - len(sampled)])
    
    # Sort nicely by Complexity then Sample ID
    sampled.sort(key=lambda x: (x["complexity"], x["sample_id"]))
    # Re-index sample IDs 1..N
    for i, s in enumerate(sampled, 1):
        s["sample_id"] = i
    
    return sampled[:sample_size]


def export_markdown_review(samples, output_path, model_name=""):
    """Export human-readable Markdown review form with scoring rubrics."""
    md = []
    md.append(f"# 📋 Human Review Sample: {model_name or 'Agentic VQA Pipeline'}")
    md.append(f"\n**Total Sample Size:** {len(samples)} questions (Stratified across C1, C2, C3 and Failure Causes)")
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
    
    for item in samples:
        md.append(f"### Item #{item['sample_id']} — Complexity: `{item['complexity']}` | Decision: **`{item['answerability']}`** | Cause: `{item['primary_cause']}`")
        md.append(f"- **Corrupted Question**: *\"{item['corrupted_question']}\"*")
        if item.get("original_question"):
            md.append(f"- **Original Question**: *\"{item['original_question']}\"*")
        md.append(f"- **Agent Final Answer**: `{item['final_answer']}`")
        md.append(f"- **Agent Cause Explanation**:\n  > {item['cause_explanation'] or '*(Nessuna spiegazione fornita)*'}")
        if item.get("evidence_snippets"):
            md.append(f"- **Extracted Document Evidence**: `{item['evidence_snippets']}`")
        md.append(f"- **Prompts Used**: `{item['prompts_used']}`")
        md.append("")
        md.append("```")
        md.append("[ ] Answerability Correct (0/1): ___")
        md.append("[ ] Cause Diagnosis Correct (0/1/2): ___")
        md.append("[ ] Explanation Quality (0/1/2/3): ___")
        md.append("[ ] Overall Trustworthiness (1-5): ___")
        md.append("Reviewer Notes: __________________________________________________")
        md.append("```")
        md.append("\n---\n")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def export_csv_review(samples, output_path):
    """Export tabular CSV for filling in scores via Excel / Google Sheets."""
    fields = [
        "Sample_ID",
        "Complexity",
        "Corrupted_Question",
        "Original_Question",
        "Agent_Decision",
        "Primary_Cause",
        "Agent_Answer",
        "Agent_Explanation",
        "Evidence_Snippets",
        "Prompts_Used",
        "Human_Decision_Correct_0_1",
        "Human_Cause_Correct_0_1_2",
        "Human_Explanation_Quality_0_1_2_3",
        "Human_Trust_Score_1_5",
        "Human_Notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for s in samples:
            writer.writerow([
                s["sample_id"],
                s["complexity"],
                s["corrupted_question"],
                s["original_question"],
                s["answerability"],
                s["primary_cause"],
                s["final_answer"],
                s["cause_explanation"],
                s["evidence_snippets"],
                s["prompts_used"],
                "",  # Human Decision Score
                "",  # Human Cause Score
                "",  # Human Explanation Score
                "",  # Human Trust Score
                "",  # Notes
            ])


def process_file(json_path, sample_size=50, output_dir=None, seed=42):
    """Process a single JSON file and output Markdown + CSV review samples."""
    path = Path(json_path)
    if not path.is_file():
        raise FileNotFoundError(f"Result file not found: {json_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    items = data.get("corrupted_questions", [])
    if not items:
        print(f"Warning: No questions found in {path.name}")
        return
    
    model_name = path.stem.replace("unanswerability_diagnostic_results_", "")
    out_dir = Path(output_dir) if output_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    samples = stratified_sample(items, sample_size=sample_size, seed=seed)
    
    # Save files
    md_out = out_dir / f"human_review_sample_{model_name}.md"
    csv_out = out_dir / f"human_review_sample_{model_name}.csv"
    json_out = out_dir / f"human_review_sample_{model_name}.json"
    
    export_markdown_review(samples, md_out, model_name=model_name)
    export_csv_review(samples, csv_out)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump({"model": model_name, "sample_size": len(samples), "samples": samples}, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Generated {len(samples)} review samples for '{model_name}':")
    print(f"   - Markdown: {md_out.name}")
    print(f"   - CSV:      {csv_out.name}")
    print(f"   - JSON:     {json_out.name}")
    
    # Print distribution
    comp_dist = defaultdict(int)
    dec_dist = defaultdict(int)
    cause_dist = defaultdict(int)
    for s in samples:
        comp_dist[s["complexity"]] += 1
        dec_dist[s["answerability"]] += 1
        cause_dist[s["primary_cause"]] += 1
    
    print(f"   Distribution by Complexity: {dict(comp_dist)}")
    print(f"   Distribution by Decision:   {dict(dec_dist)}")
    print(f"   Distribution by Cause:      {dict(cause_dist)}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate stratified sample for human review of VQA agent results.")
    parser.add_argument("--input", "-i", default=None, help="Path to specific results JSON or directory")
    parser.add_argument("--sample-size", "-n", type=int, default=50, help="Number of questions to sample (default: 50)")
    parser.add_argument("--output-dir", "-o", default=None, help="Directory to save review files")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    
    target = args.input or r"c:\Tesi\Agentic-VQA-Pipeline\Agentic_results"
    target_path = Path(target)
    
    if target_path.is_file():
        process_file(target_path, sample_size=args.sample_size, output_dir=args.output_dir, seed=args.seed)
    elif target_path.is_dir():
        json_files = sorted(target_path.glob("unanswerability_diagnostic_results_*.json"))
        if not json_files:
            print(f"No result JSON files found in {target_path}")
            return
        for jf in json_files:
            process_file(jf, sample_size=args.sample_size, output_dir=args.output_dir, seed=args.seed)


if __name__ == "__main__":
    main()
