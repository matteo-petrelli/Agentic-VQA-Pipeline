import json
from collections import Counter
from pathlib import Path

new_path = Path(r"c:\Users\mpetr\Downloads\results(11)\unanswerability_diagnostic_results_qwen3vl8b.json")
old_path = Path(r"c:\Tesi\Agentic-VQA-Pipeline\Agentic_results\raw\unanswerability_diagnostic_results_qwen3vl8b.json")

def analyze_file(p):
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("corrupted_questions", [])
    ans_dist = Counter()
    causes_dist = Counter()
    expl_count = 0
    expl_lengths = []
    prompts_dist = Counter()
    coverage_sum = 0
    
    for it in items:
        res = it.get("agentic_result", {})
        ans = res.get("answerability", "unknown")
        cause = res.get("primary_cause") or "None"
        expl = res.get("cause_explanation") or ""
        cov = res.get("evidence_coverage", 0.0)
        prompts = res.get("prompts_used", [])
        
        ans_dist[ans] += 1
        causes_dist[cause] += 1
        coverage_sum += cov
        for pr in prompts:
            prompts_dist[pr] += 1
            
        if expl.strip():
            expl_count += 1
            expl_lengths.append(len(expl.strip()))
            
    return {
        "total": len(items),
        "ans_dist": ans_dist,
        "causes_dist": causes_dist,
        "expl_count": expl_count,
        "avg_expl_len": sum(expl_lengths) / len(expl_lengths) if expl_lengths else 0,
        "avg_cov": coverage_sum / len(items) if items else 0,
        "prompts_dist": prompts_dist,
        "items": items
    }

print("="*60)
print("ANALISI DETTAGLIATA NUOVO FILE QWEN3-VL 8B (results(11))")
print("="*60)

new_res = analyze_file(new_path)
print(f"Totale Domande Elaborate: {new_res['total']}")
print(f"Distribuzione Decisioni:")
for k, v in new_res['ans_dist'].items():
    print(f"  - {k:22s}: {v:3d} ({v/new_res['total']*100:.1f}%)")

print(f"\nDistribuzione Cause Diagnosticate:")
for k, v in sorted(new_res['causes_dist'].items(), key=lambda x: x[1], reverse=True):
    print(f"  - {k:30s}: {v:3d} ({v/new_res['total']*100:.1f}%)")

print(f"\nSpiegazioni delle Cause (cause_explanation):")
print(f"  - Domande con spiegazione presente: {new_res['expl_count']} / {new_res['total']} ({new_res['expl_count']/new_res['total']*100:.1f}%)")
print(f"  - Lunghezza media spiegazione: {new_res['avg_expl_len']:.1f} caratteri")
print(f"  - Copertura media evidenze (coverage): {new_res['avg_cov']*100:.1f}%")

print(f"\nPrompt Utilizzati:")
for k, v in sorted(new_res['prompts_dist'].items(), key=lambda x: x[1], reverse=True):
    print(f"  - {k:30s}: {v:3d}")

if old_path.exists():
    print("\n" + "="*60)
    print("CONFRONTO: VECCHIO RUN vs NUOVO RUN (POST-AUMENTO TOKEN)")
    print("="*60)
    old_res = analyze_file(old_path)
    
    print(f"{'Metrica':<35} | {'VECCHIO (pre-fix)':<18} | {'NUOVO (post-fix)':<18}")
    print("-" * 75)
    print(f"{'Totale Domande':<35} | {old_res['total']:<18} | {new_res['total']:<18}")
    print(f"{'Unanswerable (Diagnosi attiva)':<35} | {old_res['ans_dist']['unanswerable']:<18} | {new_res['ans_dist']['unanswerable']:<18}")
    print(f"{'Insufficient Evidence (Fallback)':<35} | {old_res['ans_dist']['insufficient_evidence']:<18} | {new_res['ans_dist']['insufficient_evidence']:<18}")
    print(f"{'Answerable (Allucinazioni / FN)':<35} | {old_res['ans_dist']['answerable']:<18} | {new_res['ans_dist']['answerable']:<18}")
    print(f"{'Spiegazioni Generate (>0 chars)':<35} | {old_res['expl_count']:<18} | {new_res['expl_count']:<18}")
    print(f"{'% Unanswerable Rilevati':<35} | {old_res['ans_dist']['unanswerable']/old_res['total']*100:.1f}%{'':<13} | {new_res['ans_dist']['unanswerable']/new_res['total']*100:.1f}%")
    print(f"{'% Insufficient Evidence':<35} | {old_res['ans_dist']['insufficient_evidence']/old_res['total']*100:.1f}%{'':<13} | {new_res['ans_dist']['insufficient_evidence']/new_res['total']*100:.1f}%")

# Sample 3 examples of explanations
print("\n" + "="*60)
print("ESEMPI DI SPIEGAZIONI GENERATE NEL NUOVO RUN:")
print("="*60)
sample_count = 0
for it in new_res['items']:
    res = it.get('agentic_result', {})
    if res.get('answerability') == 'unanswerable' and res.get('cause_explanation'):
        sample_count += 1
        print(f"\n[Esempio {sample_count}]")
        print(f"  Domanda: {it.get('corrupted_question')}")
        print(f"  Causa:   {res.get('primary_cause')}")
        print(f"  Spieg.:  {res.get('cause_explanation')}")
        if sample_count >= 3:
            break
