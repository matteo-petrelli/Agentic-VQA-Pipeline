import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
file_path = Path(r"c:\Users\mpetr\Downloads\results\unanswerability_diagnostic_results_qwen3vl8b.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("corrupted_questions", [])
print(f"Totale items: {len(items)}\n")

for i, it in enumerate(items, 1):
    res = it.get("agentic_result", {})
    final_ans = res.get("final_answer", "")
    ans = res.get("answerability")
    cause = res.get("primary_cause")
    trace = res.get("trace", [])
    
    print(f"Item #{i:2d}: {it.get('corrupted_question')[:60]}...")
    print(f"   Answerability: {ans} | Cause: {cause}")
    print(f"   Final Answer:  {final_ans}")
    for t in trace:
        node = t.get("node")
        res_obj = t.get("result")
        if isinstance(res_obj, dict):
            raw = res_obj.get("raw_response")
            print(f"     -> Node: {node:25s} | raw_response: {repr(raw)[:80]}")
    print("-" * 60)
