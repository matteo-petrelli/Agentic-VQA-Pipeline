import json
import argparse
import numpy as np

def is_unable(answer: str) -> bool:
    ans_lower = str(answer).strip().lower()
    for kw in ["unable to determine", "unable", "cannot determine", "unanswerable"]:
        if kw in ans_lower:
            return True
    return False

def evaluate_results(result_file):
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    questions = data.get("corrupted_questions", [])
    if not questions:
        print("No questions found in the result file.")
        return

    # Metrics
    metrics = {
        "corrupted": {"total": 0, "unable": 0, "c1_tot": 0, "c1_un": 0, "c2_tot": 0, "c2_un": 0, "c3_tot": 0, "c3_un": 0},
        "original":  {"total": 0, "unable": 0, "c1_tot": 0, "c1_un": 0, "c2_tot": 0, "c2_un": 0, "c3_tot": 0, "c3_un": 0}
    }
    
    pass1_exits = 0
    pass2_exits = 0

    for q in questions:
        agent_res = q.get("agentic_result", {})
        final_ans = agent_res.get("final_answer", "Error")
        is_un = is_unable(final_ans)
        
        pass_reached = agent_res.get("pass_reached", 0)
        if pass_reached == 1: pass1_exits += 1
        elif pass_reached == 2: pass2_exits += 1
        
        is_corr = q.get("is_corrupted", True)
        comp = q.get("complexity", 1)
        
        group = "corrupted" if is_corr else "original"
        
        metrics[group]["total"] += 1
        if is_un:
            metrics[group]["unable"] += 1
            
        if comp == 1:
            metrics[group]["c1_tot"] += 1
            if is_un: metrics[group]["c1_un"] += 1
        elif comp == 2:
            metrics[group]["c2_tot"] += 1
            if is_un: metrics[group]["c2_un"] += 1
        elif comp == 3:
            metrics[group]["c3_tot"] += 1
            if is_un: metrics[group]["c3_un"] += 1

    # --- Calculations ---
    # QUR: True Positive Rate (corrupted questions classified as unable)
    tot_corr = metrics["corrupted"]["total"]
    qur = metrics["corrupted"]["unable"] / tot_corr if tot_corr else 0
    qur_c1 = metrics["corrupted"]["c1_un"] / metrics["corrupted"]["c1_tot"] if metrics["corrupted"]["c1_tot"] else 0
    qur_c2 = metrics["corrupted"]["c2_un"] / metrics["corrupted"]["c2_tot"] if metrics["corrupted"]["c2_tot"] else 0
    qur_c3 = metrics["corrupted"]["c3_un"] / metrics["corrupted"]["c3_tot"] if metrics["corrupted"]["c3_tot"] else 0

    # FUR: False Positive Rate (original questions classified as unable)
    tot_orig = metrics["original"]["total"]
    fur = metrics["original"]["unable"] / tot_orig if tot_orig else 0
    fur_c1 = metrics["original"]["c1_un"] / metrics["original"]["c1_tot"] if metrics["original"]["c1_tot"] else 0
    fur_c2 = metrics["original"]["c2_un"] / metrics["original"]["c2_tot"] if metrics["original"]["c2_tot"] else 0
    fur_c3 = metrics["original"]["c3_un"] / metrics["original"]["c3_tot"] if metrics["original"]["c3_tot"] else 0

    # F1 Score
    true_positives = metrics["corrupted"]["unable"]
    false_positives = metrics["original"]["unable"]
    false_negatives = metrics["corrupted"]["total"] - true_positives
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
    recall = qur # same as TPR
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

    # --- Reporting ---
    print("\n" + "="*50)
    print(" AGENTIC PIPELINE EVALUATION RESULTS")
    print("="*50)
    
    print("\n--- Pipeline Efficiency ---")
    print(f"Total questions processed : {len(questions)}")
    print(f"Early Exits (Pass 1 only) : {pass1_exits} ({pass1_exits/len(questions)*100:.1f}%)")
    print(f"Full Escalations (Pass 2) : {pass2_exits} ({pass2_exits/len(questions)*100:.1f}%)")
    
    print("\n--- QUR (Corrupted Detection Rate) ---")
    print(f"QUR Total : {qur*100:.1f}%  ({metrics['corrupted']['unable']}/{tot_corr})")
    print(f"  QUR C1  : {qur_c1*100:.1f}%")
    print(f"  QUR C2  : {qur_c2*100:.1f}%")
    print(f"  QUR C3  : {qur_c3*100:.1f}%")

    print("\n--- FUR (False Unable Rate) ---")
    print(f"FUR Total : {fur*100:.1f}%  ({metrics['original']['unable']}/{tot_orig})")
    print(f"  FUR C1  : {fur_c1*100:.1f}%")
    print(f"  FUR C2  : {fur_c2*100:.1f}%")
    print(f"  FUR C3  : {fur_c3*100:.1f}%")

    print("\n--- Overall Metrics ---")
    print(f"Precision : {precision:.3f}")
    print(f"F1 Score  : {f1:.3f}")

    print("\n--- Confusion Matrix ---")
    print("                     | Agent: 'Unable' | Agent: 'Answer' |")
    print(f"  Actual: Corrupted  | TP: {true_positives:<11} | FN: {false_negatives:<13} |")
    print(f"  Actual: Original   | FP: {false_positives:<11} | TN: {tot_orig - false_positives:<13} |")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="agentic_pipeline_results.json", help="Path to the JSON result file")
    args = parser.parse_args()
    evaluate_results(args.file)
