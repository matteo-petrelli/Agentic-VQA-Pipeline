import argparse
import json
import os
import traceback

from tqdm import tqdm

import config
from agentic_pipeline import AgenticPipeline
from diagnostic_agent.engine import DocumentEngine


def load_checkpoint(output_path):
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"corrupted_questions": []}
    # Fallback: se siamo su Kaggle e il checkpoint è stato caricato come Input Dataset
    from pathlib import Path
    filename = os.path.basename(output_path)
    input_root = Path("/kaggle/input")
    if input_root.exists():
        matches = list(input_root.glob(f"**/{filename}"))
        if matches:
            try:
                with open(matches[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Checkpoint precedente trovato in Kaggle Input: {matches[0]}")
                    return data
            except json.JSONDecodeError:
                pass
    return {"corrupted_questions": []}

def save_checkpoint(output_path, data):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _load_prompt_overrides(path):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("Prompt overrides must be a JSON object.")
    return value


def _image_paths(item):
    paths = []
    for page_filename in item.get("patch_entities", {}):
        paths.append(os.path.join(config.IMAGE_DIR, os.path.basename(page_filename)))

    if not paths:
        for entity_list_key in ("original_entity", "corrupted_entities"):
            for entity in item.get(entity_list_key, []):
                page_id = entity.get("page_id")
                if page_id:
                    paths.append(os.path.join(config.IMAGE_DIR, os.path.basename(page_id)))
    return sorted(set(paths))


def main(model_name=None, profile_name=None, prompt_overrides=None, engine=None):
    selected_model = model_name or config.OLLAMA_VLM
    print("=== Unanswerability Diagnostic VQA Pipeline ===")
    print(f"Model: {selected_model}")
    print(f"Prompt profile: {profile_name or config.PROMPT_PROFILE}")
    
    # 1. Load Input Data
    if not os.path.exists(config.INPUT_JSON_PATH):
        print(f"[Error] Input file not found: {config.INPUT_JSON_PATH}")
        return
        
    with open(config.INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        input_data = json.load(f)
        
    questions = input_data.get("corrupted_questions", [])
    
    # 2. Apply Sampling
    if config.SAMPLING_PERCENTAGE < 1.0:
        limit = max(1, int(len(questions) * config.SAMPLING_PERCENTAGE))
        questions = questions[:limit]
        print(f"Sampling enabled: using {len(questions)} questions ({config.SAMPLING_PERCENTAGE*100}% of total).")
    else:
        print(f"Loaded {len(questions)} questions from {config.INPUT_JSON_PATH}")
    
    # 3. Check Checkpoint
    checkpoint_data = load_checkpoint(config.OUTPUT_JSON_PATH)
    processed_count = len(checkpoint_data.get("corrupted_questions", []))
    print(f"Found {processed_count} already processed questions. Resuming...")
    
    if processed_count >= len(questions):
        print("All questions have been processed! Exiting.")
        return
        
    # 4. Initialize Engine
    config.OLLAMA_VLM = selected_model
    engine = engine or DocumentEngine()
    pipeline = AgenticPipeline(
        engine,
        model_name=selected_model,
        profile_name=profile_name,
        prompt_overrides=prompt_overrides,
    )
    
    # 5. Process Loop
    for i in tqdm(range(processed_count, len(questions)), desc="Processing"):
        item = questions[i]
        q_text = item.get("corrupted_question", "")
        
        image_paths = _image_paths(item)
        
        if not image_paths:
            print(f"  [Warning] No images found for question: {q_text[:50]}")
            continue
            
        # Run Pipeline
        try:
            result = pipeline.process_question(q_text, image_paths)
            
            # Update item with agentic results
            item["agentic_result"] = result
            
        except Exception as e:
            print(f"  [Error] Processing failed: {e}")
            traceback.print_exc()
            item["agentic_result"] = {
                "answerability": "insufficient_evidence",
                "primary_cause": "EXTRACTION_FAILURE",
                "final_answer": f"Error: {e}",
                "answerability_confidence": 1,
                "cause_confidence": 2,
                "answer_confidence": None,
                "evidence_coverage": 0.0,
                "diagnostic_results": [],
                "prompts_used": [],
                "tests_run": 0,
                "steps": 0,
                "trace": [],
            }
            
        # Save Checkpoint
        checkpoint_data["corrupted_questions"].append(item)
        save_checkpoint(config.OUTPUT_JSON_PATH, checkpoint_data)
        
    print(f"\n=== Finished processing {len(questions)} questions ===")
    print(f"Results saved to {config.OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the diagnostic VQA agent.")
    parser.add_argument("--model", default=None, help="Ollama model name override")
    parser.add_argument(
        "--prompt-profile",
        default=None,
        help="Prompt profile (default, gemma3_focused, gemma4_focused, qwen3vl_focused)",
    )
    parser.add_argument(
        "--prompt-overrides",
        default=None,
        help="JSON file overriding analyzer, verifier, answerer, or per-cause prompts",
    )
    arguments = parser.parse_args()
    main(
        model_name=arguments.model,
        profile_name=arguments.prompt_profile,
        prompt_overrides=_load_prompt_overrides(arguments.prompt_overrides),
    )
