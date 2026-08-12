import argparse
import json
from collections import Counter


VALID_STATES = {"answerable", "unanswerable", "insufficient_evidence"}


def evaluate_results(result_file):
    """Evaluate structured answerability decisions and diagnostic behavior."""
    with open(result_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    questions = data.get("corrupted_questions", [])
    if not questions:
        print("No questions found in the result file.")
        return

    metrics = {
        group: {
            "total": 0,
            "unanswerable": 0,
            "insufficient": 0,
            "complexity_total": Counter(),
            "complexity_unanswerable": Counter(),
        }
        for group in ("corrupted", "original")
    }

    state_counts = Counter()
    cause_counts = Counter()
    prompt_counts = Counter()
    profile_counts = Counter()
    answerability_confidence = Counter()
    cause_confidence = Counter()
    test_counts = []
    coverages = []
    malformed_results = 0

    for q in questions:
        agent_res = q.get("agentic_result", {})
        state = agent_res.get("answerability", "insufficient_evidence")
        if state not in VALID_STATES:
            malformed_results += 1
            state = "insufficient_evidence"

        is_corr = q.get("is_corrupted", True)
        comp = q.get("complexity", 1)
        group = "corrupted" if is_corr else "original"

        metrics[group]["total"] += 1
        metrics[group]["complexity_total"][comp] += 1
        if state == "unanswerable":
            metrics[group]["unanswerable"] += 1
            metrics[group]["complexity_unanswerable"][comp] += 1
        elif state == "insufficient_evidence":
            metrics[group]["insufficient"] += 1

        state_counts[state] += 1
        cause_counts[agent_res.get("primary_cause") or "NONE"] += 1
        for prompt in agent_res.get("prompts_used", []):
            prompt_counts[prompt] += 1
        profile_counts[agent_res.get("prompt_profile", "unknown")] += 1
        answerability_confidence[agent_res.get("answerability_confidence", 1)] += 1
        cause_confidence[agent_res.get("cause_confidence", 1)] += 1
        test_counts.append(agent_res.get("tests_run", 0))
        coverages.append(float(agent_res.get("evidence_coverage", 0.0)))

    total = len(questions)
    tot_corr = metrics["corrupted"]["total"]
    tot_orig = metrics["original"]["total"]
    true_positives = metrics["corrupted"]["unanswerable"]
    false_positives = metrics["original"]["unanswerable"]
    false_negatives = metrics["corrupted"]["total"] - true_positives
    true_negatives = metrics["original"]["total"] - false_positives

    qur = true_positives / tot_corr if tot_corr else 0.0
    fur = false_positives / tot_orig if tot_orig else 0.0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
    f1 = 2 * precision * qur / (precision + qur) if (precision + qur) else 0.0

    print("\n" + "=" * 64)
    print(" UNANSWERABILITY DIAGNOSTIC AGENT RESULTS")
    print("=" * 64)
    print(f"Questions: {total} | malformed states: {malformed_results}")

    print("\n--- Answerability States ---")
    for state in ("answerable", "unanswerable", "insufficient_evidence"):
        count = state_counts[state]
        print(f"{state:<24}: {count:>5} ({count / total * 100:5.1f}%)")

    print("\n--- Core Detection Metrics ---")
    print(f"QUR / Recall: {qur:.3f} ({true_positives}/{tot_corr})")
    print(f"FUR         : {fur:.3f} ({false_positives}/{tot_orig})")
    print(f"Precision   : {precision:.3f}")
    print(f"F1          : {f1:.3f}")
    for complexity in (1, 2, 3):
        denominator = metrics["corrupted"]["complexity_total"][complexity]
        numerator = metrics["corrupted"]["complexity_unanswerable"][complexity]
        score = numerator / denominator if denominator else 0.0
        print(f"QUR C{complexity}      : {score:.3f} ({numerator}/{denominator})")

    print("\n--- Insufficient Evidence ---")
    for group in ("corrupted", "original"):
        count = metrics[group]["insufficient"]
        denominator = metrics[group]["total"]
        rate = count / denominator if denominator else 0.0
        print(f"{group:<10}: {count:>5} ({rate * 100:5.1f}%)")

    print("\n--- Diagnostic Efficiency ---")
    print(f"Average tests   : {sum(test_counts) / total:.2f}")
    print(f"Average coverage: {sum(coverages) / total:.3f}")
    print("Prompt profiles : " + ", ".join(f"{key}={value}" for key, value in profile_counts.most_common()))

    print("\n--- Primary Causes ---")
    for cause, count in cause_counts.most_common():
        print(f"{cause:<30}: {count:>5} ({count / total * 100:5.1f}%)")

    print("\n--- Prompt Usage ---")
    for prompt, count in prompt_counts.most_common():
        print(f"{prompt:<30}: {count:>5} ({count / total * 100:5.1f}%)")

    print("\n--- Confidence Distributions ---")
    print("Answerability: " + ", ".join(f"{key}={value}" for key, value in sorted(answerability_confidence.items())))
    print("Cause       : " + ", ".join(f"{key}={value}" for key, value in sorted(cause_confidence.items())))

    print("\n--- Binary Confusion Matrix ---")
    print("                     | Pred. Unanswerable | Pred. Other |")
    print(f"Actual Corrupted     | TP: {true_positives:<14} | FN: {false_negatives:<10} |")
    print(f"Actual Original      | FP: {false_positives:<14} | TN: {true_negatives:<10} |")
    print("=" * 64)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="agentic_pipeline_results.json", help="Path to the JSON result file")
    args = parser.parse_args()
    evaluate_results(args.file)
