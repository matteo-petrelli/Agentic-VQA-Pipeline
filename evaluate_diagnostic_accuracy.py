"""
Diagnostic Accuracy Evaluation Script for Agentic VQA Pipeline.

Evaluates unanswerability detection rate, diagnostic cause accuracy,
and per-cause precision/recall against DUDE dataset ground truth.
"""

import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path


def map_gt_entity_to_cause(entity_type: str) -> str:
    et = entity_type.lower()
    if any(term in et for term in ["date", "year", "time"]):
        return "TEMPORAL_MISMATCH"
    if any(term in et for term in ["spatial", "page", "position", "quadrant", "location"]):
        return "SPATIAL_MISMATCH"
    if any(term in et for term in ["price", "currency", "number", "percentage", "numerical", "amount", "count"]):
        return "VALUE_MISMATCH"
    if any(term in et for term in ["person", "company", "city", "country", "job", "organization", "name"]):
        return "ENTITY_MISMATCH"
    if "missing" in et or "deleted" in et:
        return "ENTITY_MISSING"
    return "VALUE_MISMATCH"


def evaluate_pipeline_results(results_json_path: str, dude_gt_path: str) -> dict:
    if not os.path.exists(results_json_path):
        raise FileNotFoundError(f"Results file not found: {results_json_path}")
    if not os.path.exists(dude_gt_path):
        raise FileNotFoundError(f"DUDE dataset not found: {dude_gt_path}")

    with open(results_json_path, "r", encoding="utf-8") as f:
        results_data = json.load(f)

    with open(dude_gt_path, "r", encoding="utf-8") as f:
        dude_data = json.load(f)

    gt_map = {}
    for item in dude_data.get("corrupted_questions", []):
        q = item.get("corrupted_question", "").strip()
        if q:
            gt_map[q] = item

    processed_items = results_data.get("corrupted_questions", [])
    total_items = len(processed_items)

    detection_hits = 0
    cause_exact_matches = 0
    cause_evaluations = 0

    per_cause_gt = Counter()
    per_cause_pred = Counter()
    per_cause_correct = Counter()

    evaluation_details = []

    for item in processed_items:
        q_text = item.get("corrupted_question", "").strip()
        res = item.get("agentic_result", {})
        pred_ans = res.get("answerability")
        pred_cause = res.get("primary_cause") or "NONE"

        gt_item = gt_map.get(q_text)
        if not gt_item:
            # Fallback substring match
            for k, v in gt_map.items():
                if q_text in k or k in q_text:
                    gt_item = v
                    break

        corrupted_ents = gt_item.get("corrupted_entities", []) if gt_item else []
        ent_types = [e.get("entity_type", "") for e in corrupted_ents if isinstance(e, dict)]

        gt_expected_cause = "UNKNOWN"
        if ent_types:
            gt_expected_cause = map_gt_entity_to_cause(ent_types[0])

        is_unanswerable_detected = (pred_ans == "unanswerable")
        is_cause_matched = (pred_cause == gt_expected_cause)

        if is_unanswerable_detected:
            detection_hits += 1

        if gt_expected_cause != "UNKNOWN":
            cause_evaluations += 1
            per_cause_gt[gt_expected_cause] += 1
            per_cause_pred[pred_cause] += 1
            if is_cause_matched:
                cause_exact_matches += 1
                per_cause_correct[gt_expected_cause] += 1

        evaluation_details.append({
            "question": q_text,
            "predicted_answerability": pred_ans,
            "predicted_cause": pred_cause,
            "gt_expected_cause": gt_expected_cause,
            "gt_entity_types": ent_types,
            "detection_success": is_unanswerable_detected,
            "cause_match_success": is_cause_matched,
        })

    detection_rate = (detection_hits / max(1, total_items)) * 100.0
    cause_accuracy = (cause_exact_matches / max(1, cause_evaluations)) * 100.0

    per_cause_metrics = {}
    for cause in sorted(set(list(per_cause_gt.keys()) + list(per_cause_pred.keys()))):
        gt_count = per_cause_gt[cause]
        pred_count = per_cause_pred[cause]
        correct = per_cause_correct[cause]

        precision = (correct / pred_count * 100.0) if pred_count > 0 else 0.0
        recall = (correct / gt_count * 100.0) if gt_count > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_cause_metrics[cause] = {
            "ground_truth_count": gt_count,
            "predicted_count": pred_count,
            "correct_count": correct,
            "precision_pct": round(precision, 2),
            "recall_pct": round(recall, 2),
            "f1_score": round(f1 / 100.0, 4),
        }

    metrics = {
        "total_questions_processed": total_items,
        "unanswerability_detection_rate_pct": round(detection_rate, 2),
        "cause_classification_accuracy_pct": round(cause_accuracy, 2),
        "cause_evaluations_count": cause_evaluations,
        "cause_exact_matches_count": cause_exact_matches,
        "per_cause_metrics": per_cause_metrics,
        "evaluation_details": evaluation_details,
    }
    return metrics


def main():
    results_path = os.path.join("c:\\Tesi\\Agentic-VQA-Pipeline", "unanswerability_diagnostic_results_gemma3.json")
    dude_gt_path = os.path.join("c:\\Tesi", "DUDE_mixed_test.json")
    if not os.path.exists(dude_gt_path):
        dude_gt_path = os.path.join("c:\\Tesi", "DUDE_fixed.json")

    print(f"Loading results from: {results_path}")
    print(f"Loading GT dataset from: {dude_gt_path}")

    metrics = evaluate_pipeline_results(results_path, dude_gt_path)

    out_json = os.path.join("c:\\Tesi\\Agentic-VQA-Pipeline", "evaluation_accuracy_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"\n================ EVALUATION METRICS SUMMARY ================")
    print(f"Total Questions Processed : {metrics['total_questions_processed']}")
    print(f"Unanswerability Detection Rate: {metrics['unanswerability_detection_rate_pct']}%")
    print(f"Cause Classification Accuracy : {metrics['cause_classification_accuracy_pct']}%")
    print(f"Metrics saved to: {out_json}")


if __name__ == "__main__":
    main()
