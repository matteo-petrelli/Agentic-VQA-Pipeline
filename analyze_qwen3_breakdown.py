import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

file_path = Path(r"c:\Users\mpetr\Downloads\results(11)\unanswerability_diagnostic_results_qwen3vl8b.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("corrupted_questions", [])
print(f"Totale items nel file: {len(items)}\n")

for i, it in enumerate(items, 1):
    res = it.get("agentic_result", {})
    ans = res.get("answerability", "")
    cause = res.get("primary_cause")
    final_ans = res.get("final_answer", "")
    trace = res.get("trace", [])
    
    empty_nodes = []
    for step in trace:
        step_res = step.get("result", {})
        if isinstance(step_res, dict) and step_res.get("raw_response") == "":
            empty_nodes.append(step.get("node"))
            
    is_400 = "400 Client Error" in final_ans
    
    status_str = "❌ 400 Bad Request" if is_400 else ("⚠️ Risposte Vuote" if empty_nodes else "❓ Altro")
    print(f"Item #{i:2d}: {status_str} | Ans: {ans} | Cause: {cause}")
    print(f"   Domanda: {it.get('corrupted_question')[:70]}...")
    if is_400:
        print(f"   Errore:  {final_ans}")
    if empty_nodes:
        print(f"   Nodi con risposta vuota da Ollama: {empty_nodes}")
    print()
