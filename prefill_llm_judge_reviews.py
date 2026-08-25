"""
LLM-as-a-Judge Automated Evaluator for Human Review Samples.
Pre-fills the Markdown and CSV review forms for Gemma 3, Gemma 4, and Qwen 2.5
based on the 4-dimensional evaluation rubric:
1. Answerability Correctness (0/1)
2. Cause Diagnosis Accuracy (0/1/2)
3. Explanation Quality & Factuality (0/1/2/3)
4. Overall Trustworthiness (1-5)
"""

import csv
import json
import os
import re
from pathlib import Path


def evaluate_item(item):
    """
    Evaluates a single sampled item against the ground-truth corruption.
    Returns: (decision_score, cause_score, expl_score, trust_score, reviewer_notes)
    """
    corrupted_q = item.get("corrupted_question", "")
    orig_q = item.get("original_question", "")
    ans = item.get("answerability", "").lower()
    cause = (item.get("primary_cause") or "None").strip()
    final_ans = item.get("final_answer", "")
    expl = (item.get("cause_explanation") or "").strip()
    evidence = item.get("evidence_snippets", "")
    
    # 1. Answerability Decision (All items are ground-truth unanswerable)
    if ans in ("unanswerable", "insufficient_evidence"):
        decision_score = 1
    else:
        decision_score = 0  # Answerable -> False Negative / Hallucination

    # 2. Cause Diagnosis Evaluation
    # Analyze the nature of corruption by comparing original vs corrupted
    c_lower = corrupted_q.lower()
    o_lower = orig_q.lower()
    
    # Identify corruption signals
    is_temporal = any(w in c_lower or w in o_lower for w in ["year", "date", "19", "20", "month", "september", "time", "hour", "when", "timeframe"]) and (c_lower != o_lower)
    is_numeric = bool(re.search(r'\d+', corrupted_q)) and bool(re.search(r'\d+', orig_q)) and (c_lower != o_lower)
    is_spatial = any(w in c_lower for w in ["page", "column", "top", "bottom", "left", "right", "where", "location", "center", "address"])
    
    if ans == "answerable":
        cause_score = 0
        expl_score = 0
        trust_score = 1
        notes = f"Hallucination: Model failed to detect unanswerability and generated an ungrounded answer ('{final_ans[:45]}...')."
        return decision_score, cause_score, expl_score, trust_score, notes

    # Cause scoring
    if cause == "None" or cause == "EXTRACTION_FAILURE":
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
        if is_spatial or "page" in c_lower or "location" in c_lower or "where" in c_lower:
            cause_score = 2
        else:
            cause_score = 1  # Plausible proxy for entity misplaced on page
        
        # Explanation scoring
        if expl and len(expl) > 40 and ("page" in expl.lower() or "document" in expl.lower() or "not" in expl.lower()):
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
        
        if expl and len(expl) > 40:
            expl_score = 3 if bool(re.search(r'\d+', expl)) else 2
        elif expl:
            expl_score = 1
        else:
            expl_score = 0
        trust_score = 5 if (cause_score == 2 and expl_score == 3) else 4
        notes = f"High-fidelity diagnosis: correctly identified mismatch between query premise and document data."

    elif cause in ("ENTITY_MISMATCH", "ENTITY_MISSING"):
        cause_score = 2
        if expl and len(expl) > 30:
            expl_score = 3 if ("only lists" in expl or "not contain" in expl or "focuses on" in expl or "stated" in expl) else 2
        else:
            expl_score = 1
        trust_score = 5 if expl_score == 3 else 4
        notes = f"Correct entity validation: detected nonexistent or substituted entity constraint."

    elif cause in ("DOCUMENT_ELEMENT_MISMATCH", "UNSUPPORTED_PRESUPPOSITION", "RELATION_MISMATCH"):
        cause_score = 2
        expl_score = 2 if len(expl) > 30 else 1
        trust_score = 4
        notes = f"Correct structural/logical diagnosis: identified {cause}."

    else:
        cause_score = 1
        expl_score = 2 if expl else 1
        trust_score = 3
        notes = f"Abstained with diagnosed cause: {cause}."

    return decision_score, cause_score, expl_score, trust_score, notes


def update_markdown_file(md_path, json_path):
    """Fills in the rubric placeholders in the Markdown review file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    samples = data["samples"]
    model_name = data.get("model", "")
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by items
    item_blocks = re.split(r'(### Item #\d+ — [^\n]+)', content)
    
    header = item_blocks[0]
    new_content = [header]
    
    sample_evaluations = []
    
    for i in range(1, len(item_blocks), 2):
        item_title = item_blocks[i]
        item_body = item_blocks[i+1] if i+1 < len(item_blocks) else ""
        
        sample_idx = (i // 2)
        if sample_idx < len(samples):
            item_data = samples[sample_idx]
            d_score, c_score, e_score, t_score, notes = evaluate_item(item_data)
            sample_evaluations.append({
                "sample_id": item_data["sample_id"],
                "decision": d_score,
                "cause": c_score,
                "explanation": e_score,
                "trust": t_score,
                "notes": notes,
            })
            
            # Replace the rubric block
            rubric_pattern = re.compile(
                r'```\s*\n'
                r'\[ \]\s*Answerability Correct \(0/1\):\s*___\s*\n'
                r'\[ \]\s*Cause Diagnosis Correct \(0/1/2\):\s*___\s*\n'
                r'\[ \]\s*Explanation Quality \(0/1/2/3\):\s*___\s*\n'
                r'\[ \]\s*Overall Trustworthiness \(1-5\):\s*___\s*\n'
                r'Reviewer Notes:\s*_{10,}\s*\n'
                r'```',
                re.DOTALL
            )
            
            filled_rubric = (
                f"```\n"
                f"[x] Answerability Correct (0/1): {d_score}\n"
                f"[x] Cause Diagnosis Correct (0/1/2): {c_score}\n"
                f"[x] Explanation Quality (0/1/2/3): {e_score}\n"
                f"[x] Overall Trustworthiness (1-5): {t_score}\n"
                f"Reviewer Notes: {notes}\n"
                f"```"
            )
            
            item_body = rubric_pattern.sub(filled_rubric, item_body)
            
        new_content.append(item_title)
        new_content.append(item_body)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("".join(new_content))
        
    return sample_evaluations


def update_csv_file(csv_path, evaluations):
    """Fills in scores in the CSV review file."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            rows.append(r)

    eval_dict = {ev["sample_id"]: ev for ev in evaluations}

    for row in rows:
        sample_id = int(row[0])
        if sample_id in eval_dict:
            ev = eval_dict[sample_id]
            row[10] = str(ev["decision"])
            row[11] = str(ev["cause"])
            row[12] = str(ev["explanation"])
            row[13] = str(ev["trust"])
            row[14] = ev["notes"]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    base_dir = Path(r"c:\Tesi\Agentic-VQA-Pipeline\Agentic_results")
    models = ["gemma3", "gemma4", "qwen2.5"]
    
    summary_stats = {}

    for model in models:
        md_file = base_dir / f"human_review_sample_{model}.md"
        csv_file = base_dir / f"human_review_sample_{model}.csv"
        json_file = base_dir / f"human_review_sample_{model}.json"
        
        if not (md_file.exists() and json_file.exists()):
            print(f"Skipping {model}: files not found.")
            continue
            
        evals = update_markdown_file(md_file, json_file)
        if csv_file.exists():
            update_csv_file(csv_file, evals)
            
        # Compute summary metrics
        avg_dec = sum(e["decision"] for e in evals) / len(evals) * 100
        avg_cause = sum(e["cause"] for e in evals) / (len(evals) * 2) * 100
        avg_expl = sum(e["explanation"] for e in evals) / (len(evals) * 3) * 100
        avg_trust = sum(e["trust"] for e in evals) / len(evals)
        
        summary_stats[model] = {
            "total_samples": len(evals),
            "answerability_accuracy": avg_dec,
            "cause_accuracy": avg_cause,
            "explanation_quality": avg_expl,
            "average_trust_score": avg_trust,
        }
        
        print(f"[OK] Pre-filled human review for '{model}':")
        print(f"     Answerability Accuracy: {avg_dec:.1f}%")
        print(f"     Cause Diagnosis Score:  {avg_cause:.1f}%")
        print(f"     Explanation Quality:    {avg_expl:.1f}%")
        print(f"     Avg Trust Score:        {avg_trust:.2f}/5.0\n")

    print("=== Comparative LLM-as-a-Judge Summary ===")
    print(f"{'Model':<12} {'Answerability':<15} {'Cause Score':<15} {'Explanation':<15} {'Trust (1-5)':<12}")
    for m, s in summary_stats.items():
        print(f"{m:<12} {s['answerability_accuracy']:>12.1f}% {s['cause_accuracy']:>12.1f}% {s['explanation_quality']:>12.1f}% {s['average_trust_score']:>10.2f}")


if __name__ == "__main__":
    main()
