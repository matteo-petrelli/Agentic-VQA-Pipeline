"""
Evaluation script for the Agentic VQA Pipeline.

Computes QUR, FUR, F1, confusion matrix, and ReAct-specific metrics
(average steps, tool usage frequency, forced exits).
"""
import json
import argparse
from collections import Counter


def is_unable(answer: str) -> bool:
    """Check if an answer indicates the question is unanswerable."""
    ans_lower = str(answer).strip().lower()
    for kw in ["unable to determine", "unable", "cannot determine", "unanswerable"]:
        if kw in ans_lower:
            return True
    return False


def evaluate_results(result_file):
    """Evaluate pipeline results and print metrics."""
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    questions = data.get("corrupted_questions", [])
    if not questions:
        print("No questions found in the result file.")
        return

    # Core Metrics
    metrics = {
        "corrupted": {"total": 0, "unable": 0, "c1_tot": 0, "c1_un": 0, "c2_tot": 0, "c2_un": 0, "c3_tot": 0, "c3_un": 0},
        "original":  {"total": 0, "unable": 0, "c1_tot": 0, "c1_un": 0, "c2_tot": 0, "c2_un": 0, "c3_tot": 0, "c3_un": 0}
    }
    
    # ReAct-specific metrics
    all_steps = []
    all_tools = Counter()
    forced_exits = 0
    step_distribution = Counter()

    for q in questions:
        agent_res = q.get("agentic_result", {})
        final_ans = agent_res.get("final_answer", "Error")
        is_un = is_unable(final_ans)
        
        # ReAct metrics
        steps = agent_res.get("steps", 0)
        all_steps.append(steps)
        step_distribution[steps] += 1
        
        tools = agent_res.get("tools_used", [])
        for tool in tools:
            all_tools[tool] += 1
        
        if agent_res.get("forced_exit", False):
            forced_exits += 1
        
        # Core classification metrics
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
    tot_corr = metrics["corrupted"]["total"]
    qur = metrics["corrupted"]["unable"] / tot_corr if tot_corr else 0
    qur_c1 = metrics["corrupted"]["c1_un"] / metrics["corrupted"]["c1_tot"] if metrics["corrupted"]["c1_tot"] else 0
    qur_c2 = metrics["corrupted"]["c2_un"] / metrics["corrupted"]["c2_tot"] if metrics["corrupted"]["c2_tot"] else 0
    qur_c3 = metrics["corrupted"]["c3_un"] / metrics["corrupted"]["c3_tot"] if metrics["corrupted"]["c3_tot"] else 0

    tot_orig = metrics["original"]["total"]
    fur = metrics["original"]["unable"] / tot_orig if tot_orig else 0
    fur_c1 = metrics["original"]["c1_un"] / metrics["original"]["c1_tot"] if metrics["original"]["c1_tot"] else 0
    fur_c2 = metrics["original"]["c2_un"] / metrics["original"]["c2_tot"] if metrics["original"]["c2_tot"] else 0
    fur_c3 = metrics["original"]["c3_un"] / metrics["original"]["c3_tot"] if metrics["original"]["c3_tot"] else 0

    true_positives = metrics["corrupted"]["unable"]
    false_positives = metrics["original"]["unable"]
    false_negatives = metrics["corrupted"]["total"] - true_positives
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
    recall = qur
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

    avg_steps = sum(all_steps) / len(all_steps) if all_steps else 0

    # --- Reporting ---
    print("\n" + "="*55)
    print(" AGENTIC PIPELINE (ReAct) EVALUATION RESULTS")
    print("="*55)
    
    print("\n--- ReAct Agent Efficiency ---")
    print(f"Total questions processed : {len(questions)}")
    print(f"Average steps per question: {avg_steps:.2f}")
    print(f"Forced exits (max iters)  : {forced_exits} ({forced_exits/len(questions)*100:.1f}%)")
    
    print("\n  Step distribution:")
    for step_count in sorted(step_distribution.keys()):
        count = step_distribution[step_count]
        bar = "█" * int(count / len(questions) * 30)
        print(f"    {step_count} steps: {count:>4} ({count/len(questions)*100:5.1f}%) {bar}")
    
    print("\n  Tool usage frequency:")
    for tool, count in all_tools.most_common():
        print(f"    {tool:<20}: {count:>4} ({count/len(questions)*100:5.1f}%)")
    
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
    print(f"Recall    : {recall:.3f}")
    print(f"F1 Score  : {f1:.3f}")

    print("\n--- Confusion Matrix ---")
    print("                     | Agent: 'Unable' | Agent: 'Answer' |")
    print(f"  Actual: Corrupted  | TP: {true_positives:<11} | FN: {false_negatives:<13} |")
    print(f"  Actual: Original   | FP: {false_positives:<11} | TN: {tot_orig - false_positives:<13} |")
    print("=" * 55)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="agentic_pipeline_results.json", help="Path to the JSON result file")
    args = parser.parse_args()
    evaluate_results(args.file)
