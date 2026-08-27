import json
from pathlib import Path

def generate_google_apps_script(json_path: Path, output_script_path: Path, model_title: str = "Gemma 3 (4B)"):
    with open(json_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    js_lines = []
    js_lines.append("/**")
    js_lines.append(f" * Google Apps Script per la creazione automatica del Google Form di Human Review ({model_title})")
    js_lines.append(" * Istruzioni:")
    js_lines.append(" * 1. Vai su https://script.google.com/ e crea un 'Nuovo progetto'.")
    js_lines.append(" * 2. Incolla questo codice nel file 'Codice.gs' sostituendo tutto.")
    js_lines.append(" * 3. Clicca su 'Esegui' (Run). Autorizza l'accesso quando richiesto.")
    js_lines.append(" * 4. Controlla il log di esecuzione per ottenere il link al Form generato!")
    js_lines.append(" */")
    js_lines.append("")
    js_lines.append("function createHumanReviewForm() {")
    js_lines.append(f'  var formTitle = "📋 Human Review: Unanswerability Diagnostic Agent ({model_title})";')
    js_lines.append('  var form = FormApp.create(formTitle);')
    js_lines.append('  form.setDescription(')
    js_lines.append('    "Valutazione peritale delle risposte, cause diagnosticate e spiegazioni generate dall\'Agente di VQA sul benchmark DUDE.\\n\\n" +')
    js_lines.append('    "Per ciascuna delle 50 domande (stratificate in 5 macro-categorie), valuta la correttezza e la completezza della spiegazione fornita dall\'agente.");')
    js_lines.append('  form.setIsQuiz(false);')
    js_lines.append('  form.setProgressBar(true);')
    js_lines.append('  form.setRequireLogin(false);')
    js_lines.append('')

    # Reviewer name question
    js_lines.append('  // Dati Revisore')
    js_lines.append('  var nameItem = form.addTextItem();')
    js_lines.append('  nameItem.setTitle("Nome / ID del Revisore");')
    js_lines.append('  nameItem.setRequired(true);')
    js_lines.append('')

    for idx, item in enumerate(samples, 1):
        sample_id = item.get("sample_id", idx)
        cat = item.get("macro_category", "General")
        et = item.get("entity_type", "General")
        comp = item.get("complexity", 1)
        q_corr = item.get("corrupted_question", "").replace('"', '\\"').replace('\n', ' ')
        q_orig = item.get("original_question", "").replace('"', '\\"').replace('\n', ' ')
        decision = item.get("answerability", "").replace('"', '\\"')
        cause = item.get("primary_cause", "None").replace('"', '\\"')
        ans = str(item.get("final_answer", "")).replace('"', '\\"').replace('\n', ' ')
        expl = str(item.get("cause_explanation", "") or "(Nessuna spiegazione fornita)").replace('"', '\\"').replace('\n', ' ')
        evidence = str(item.get("evidence_snippets", "") or "(Nessuna evidenza estratta)").replace('"', '\\"').replace('\n', ' ')
        prompts = str(item.get("prompts_used", "")).replace('"', '\\"')

        section_title = f"Item #{sample_id} — [{cat}] ({et} - C{comp})"
        
        info_block = (
            f"❓ DOMANDA CORROTTA: \\\"{q_corr}\\\"\\n"
            f"📌 DOMANDA ORIGINALE: \\\"{q_orig}\\\"\\n\\n"
            f"⚖️ DECISIONE AGENTE: {decision.upper()} | CAUSA PRIMARIA: {cause}\\n"
            f"💬 RISPOSTA FINALE: \\\"{ans}\\\"\\n\\n"
            f"📝 SPIEGAZIONE DELLA CAUSA:\\n\\\"{expl}\\\"\\n\\n"
            f"🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: {evidence}\\n"
            f"⚙️ PROMPT USATI: {prompts}"
        )

        js_lines.append(f'  // ================= ITEM #{sample_id} =================')
        js_lines.append('  var pageBreak = form.addPageBreakItem();')
        js_lines.append(f'  pageBreak.setTitle("{section_title}");')
        js_lines.append(f'  pageBreak.setHelpText("{info_block}");')
        js_lines.append('')

        # 1. Spiegazione Causa - Correttezza
        js_lines.append(f'  var q1_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q1_{sample_id}.setTitle("#{sample_id}.1 - La spiegazione circa la causa di unanswerability è corretta?");')
        js_lines.append(f'  q1_{sample_id}.setChoiceValues(["Sì", "No", "Parzialmente"]);')
        js_lines.append(f'  q1_{sample_id}.setRequired(true);')
        js_lines.append('')

        # 2. Spiegazione Causa - Completezza
        js_lines.append(f'  var q2_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q2_{sample_id}.setTitle("#{sample_id}.2 - La spiegazione circa la causa di unanswerability è completa?");')
        js_lines.append(f'  q2_{sample_id}.setChoiceValues(["Sì", "No"]);')
        js_lines.append(f'  q2_{sample_id}.showOtherOption(true); // Permette di specificare cosa manca')
        js_lines.append(f'  q2_{sample_id}.setRequired(true);')
        js_lines.append('')

        # 3. Riferimenti Documento - Correttezza
        js_lines.append(f'  var q3_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q3_{sample_id}.setTitle("#{sample_id}.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");')
        js_lines.append(f'  q3_{sample_id}.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);')
        js_lines.append(f'  q3_{sample_id}.setRequired(true);')
        js_lines.append('')

        # 4. Riferimenti Documento - Completezza
        js_lines.append(f'  var q4_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q4_{sample_id}.setTitle("#{sample_id}.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");')
        js_lines.append(f'  q4_{sample_id}.setChoiceValues(["Sì", "No", "Non applicabile"]);')
        js_lines.append(f'  q4_{sample_id}.showOtherOption(true); // Permette di specificare cosa manca')
        js_lines.append(f'  q4_{sample_id}.setRequired(true);')
        js_lines.append('')

        # 5. Riferimenti Domanda - Correttezza
        js_lines.append(f'  var q5_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q5_{sample_id}.setTitle("#{sample_id}.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");')
        js_lines.append(f'  q5_{sample_id}.setChoiceValues(["Sì", "No", "Parzialmente"]);')
        js_lines.append(f'  q5_{sample_id}.setRequired(true);')
        js_lines.append('')

        # 6. Riferimenti Domanda - Completezza
        js_lines.append(f'  var q6_{sample_id} = form.addMultipleChoiceItem();')
        js_lines.append(f'  q6_{sample_id}.setTitle("#{sample_id}.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");')
        js_lines.append(f'  q6_{sample_id}.setChoiceValues(["Sì", "No"]);')
        js_lines.append(f'  q6_{sample_id}.showOtherOption(true); // Permette di specificare cosa manca')
        js_lines.append(f'  q6_{sample_id}.setRequired(true);')
        js_lines.append('')

    js_lines.append('  Logger.log("✅ Google Form creato con successo!");')
    js_lines.append('  Logger.log("🔗 Link per modificare il modulo: " + form.getEditUrl());')
    js_lines.append('  Logger.log("🔗 Link per compilare il modulo: " + form.getPublishedUrl());')
    js_lines.append('}')

    with open(output_script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(js_lines))
    print(f"Generated Apps Script: {output_script_path}")

if __name__ == "__main__":
    base_dir = Path(r"c:\Tesi\Agentic-VQA-Pipeline")
    results_dir = base_dir / "Agentic_results"
    
    # Generate for all 4 models
    models = {
        "gemma3": "Gemma 3 (4B)",
        "gemma4": "Gemma 4 (E4B)",
        "qwen2.5": "Qwen 2.5 (3B)",
        "qwen3vl8b": "Qwen3-VL (8B)",
    }
    
    for m_key, m_title in models.items():
        json_file = results_dir / f"human_review_sample_{m_key}.json"
        if json_file.exists():
            out_js = results_dir / f"google_form_script_{m_key}.js"
            generate_google_apps_script(json_file, out_js, model_title=m_title)
