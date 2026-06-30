import json

with open(r"c:\Tesi\Agentic_Pipeline\agentic_pipeline_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data.get("corrupted_questions", [])
print(f"Totale domande nel file: {len(questions)}")

with_result = [q for q in questions if "agentic_result" in q]
without_result = [q for q in questions if "agentic_result" not in q]
print(f"Con risultato agentic: {len(with_result)}")
print(f"Senza risultato: {len(without_result)}")

if not with_result:
    print("Nessun risultato trovato!")
    exit()

# Confidence distribution
conf_counts = {}
for q in with_result:
    c = q["agentic_result"].get("final_confidence", "N/A")
    conf_counts[c] = conf_counts.get(c, 0) + 1

print(f"\n--- Distribuzione Confidence ---")
for c in sorted(conf_counts.keys()):
    label = {1: "Low", 2: "Medium", 3: "High"}.get(c, str(c))
    print(f"  {label} ({c}): {conf_counts[c]}")

# Steps distribution
steps_counts = {}
for q in with_result:
    s = q["agentic_result"].get("steps", "N/A")
    steps_counts[s] = steps_counts.get(s, 0) + 1

print(f"\n--- Distribuzione Steps ---")
for s in sorted(steps_counts.keys()):
    print(f"  {s} steps: {steps_counts[s]}")

# Tools used
all_tools = {}
for q in with_result:
    for t in q["agentic_result"].get("tools_used", []):
        all_tools[t] = all_tools.get(t, 0) + 1

print(f"\n--- Tools utilizzati ---")
for t, count in sorted(all_tools.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")

# Answers summary
print(f"\n--- Dettaglio risposte ---")
for i, q in enumerate(with_result):
    ar = q["agentic_result"]
    corrupted_q = q.get("corrupted_question", "")[:100]
    original_q = q.get("original_question", "")[:100]
    answer = ar.get("final_answer", "N/A")
    conf = ar.get("final_confidence", "N/A")
    conf_label = {1: "Low", 2: "Medium", 3: "High"}.get(conf, str(conf))
    steps = ar.get("steps", "N/A")
    is_corrupted = q.get("is_corrupted", False)
    
    # Check if verification_result exists
    vr = q.get("verification_result", {})
    vr_result = vr.get("verification_result", "N/A")
    
    print(f"\n[{i+1}] {'CORRUPTED' if is_corrupted else 'ORIGINAL'} | Conf: {conf_label} | Steps: {steps}")
    print(f"  Corrupted Q: {corrupted_q}")
    print(f"  Original Q:  {original_q}")
    print(f"  Agent Answer: {answer[:150]}")
    print(f"  Ground Truth Verification: {vr_result}")

# Quick accuracy estimate: count how many "unable" vs actual answers
unable_count = 0
actual_answers = 0
for q in with_result:
    ans = q["agentic_result"].get("final_answer", "").lower()
    if any(kw in ans for kw in ["unable", "cannot determine", "unanswerable", "not found"]):
        unable_count += 1
    else:
        actual_answers += 1

print(f"\n--- Riepilogo ---")
print(f"  Risposte concrete: {actual_answers}/{len(with_result)} ({actual_answers/len(with_result)*100:.1f}%)")
print(f"  Unable/Unanswerable: {unable_count}/{len(with_result)} ({unable_count/len(with_result)*100:.1f}%)")
