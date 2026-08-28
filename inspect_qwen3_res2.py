import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
file_path = Path(r"c:\Users\mpetr\Downloads\results(2)\unanswerability_diagnostic_results_qwen3vl8b.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("corrupted_questions", [])
print(f"Totale items nel file: {len(items)}\n")

for i in [0, 2, 3, 6, 10, 13]:
    if i < len(items):
        it = items[i]
        res = it.get("agentic_result", {})
        print(f"=== ITEM #{i+1} ===")
        print("Domanda:      ", it.get("corrupted_question"))
        print("Answerability:", res.get("answerability"))
        print("Primary Cause:", res.get("primary_cause"))
        print("Final Answer: ", res.get("final_answer"))
        trace = res.get("trace", [])
        for step in trace:
            node = step.get("node")
            prompt = step.get("prompt")
            res_obj = step.get("result")
            print(f"  -> Node: {node} (prompt: {prompt})")
            if isinstance(res_obj, dict):
                raw = res_obj.get("raw_response")
                print(f"     raw_response: {repr(raw)[:140]}")
                if "explanation" in res_obj:
                    print(f"     explanation:  {repr(res_obj.get('explanation'))[:140]}")
        print("-" * 60)
