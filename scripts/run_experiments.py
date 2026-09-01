import argparse
import json
import os
import sys
import traceback
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    output_p = Path(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
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


def _image_paths(item: dict) -> list[str]:
    """Retrieve absolute image paths for a question item."""
    image_paths = item.get("image_paths", [])
    if not image_paths:
        doc_id = item.get("docId", "") or item.get("document_id", "") or item.get("doc_id", "")
        if not doc_id:
            # Fallback: the output JSON doesn't retain docId at root, extract from inner fields
            vr_img = item.get("verification_result", {}).get("image_path", "")
            if vr_img:
                doc_id = os.path.basename(vr_img).split("_")[0]
            elif item.get("original_entity") and isinstance(item["original_entity"], list):
                page_id = item["original_entity"][0].get("page_id", "")
                if page_id:
                    doc_id = page_id.split("_")[0]

        if doc_id:
            img_dir = Path(config.IMAGE_DIR)
            image_paths = [str(p) for p in sorted(img_dir.glob(f"{doc_id}*"))]
            if not image_paths:
                image_paths = [str(p) for p in sorted(img_dir.glob(f"*{doc_id}*"))]
    return image_paths


def is_failed_result(result: dict | None) -> bool:
    """Check if an item's agentic result is a failed/crashed execution."""
    if not isinstance(result, dict):
        return True
    final_ans = str(result.get("final_answer", ""))
    primary_cause = str(result.get("primary_cause", ""))
    trace = result.get("trace", [])
    return (
        "Error" in final_ans
        or "400" in final_ans
        or (primary_cause == "EXTRACTION_FAILURE" and len(trace) == 0)
    )


def main(
    model_name=None,
    profile_name=None,
    prompt_overrides=None,
    engine=None,
    retry_failed=False,
):
    selected_model = model_name or config.OLLAMA_VLM
    active_profile = profile_name or config.PROMPT_PROFILE
    print("=== Unanswerability Diagnostic VQA Pipeline ===")
    print(f"Model: {selected_model}")
    print(f"Prompt profile: {active_profile}")
    print(f"Mode: {'RETRY FAILED QUESTIONS ONLY' if retry_failed else 'STANDARD / RESUME'}")

    # 1. Initialize Engine & Pipeline
    # Use the Ollama model name from config (start_ollama may have created a
    # custom model variant with baked-in num_ctx for reliable context sizing).
    ollama_model = config.OLLAMA_VLM
    if ollama_model != selected_model:
        print(f"  (using Ollama model: {ollama_model})")
    config.OLLAMA_VLM = ollama_model
    engine = engine or DocumentEngine()
    pipeline = AgenticPipeline(
        engine,
        model_name=selected_model,
        profile_name=active_profile,
        prompt_overrides=prompt_overrides,
    )

    # 2. Check Checkpoint
    checkpoint_data = load_checkpoint(config.OUTPUT_JSON_PATH)
    processed_questions = checkpoint_data.get("corrupted_questions", [])

    # -----------------------------------------------------------------------
    # MODE A: Retry ONLY failed questions from existing checkpoint
    # -----------------------------------------------------------------------
    if retry_failed:
        if not processed_questions:
            print(f"[Warning] No checkpoint questions found in {config.OUTPUT_JSON_PATH} to retry.")
            return

        failed_indices = [
            idx for idx, it in enumerate(processed_questions)
            if is_failed_result(it.get("agentic_result"))
        ]

        if not failed_indices:
            print(f"✅ All {len(processed_questions)} questions in checkpoint are already successful! Nothing to retry.")
            return

        print(f"\n🔄 Found {len(failed_indices)} failed questions out of {len(processed_questions)} total.")
        print("Starting targeted re-execution of failed questions...\n")

        recovered_count = 0
        for idx in tqdm(failed_indices, desc="Retrying Failed"):
            item = processed_questions[idx]
            q_text = item.get("corrupted_question", "")
            image_paths = _image_paths(item)

            if not image_paths:
                print(f"  [Warning] No images found for question #{idx+1}: {q_text[:50]}")
                continue

            try:
                result = pipeline.process_question(q_text, image_paths)
                item["agentic_result"] = result
                recovered_count += 1
            except Exception as e:
                print(f"  [Error] Retry failed on question #{idx+1}: {e}")
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

            # Save updated checkpoint in-place
            save_checkpoint(config.OUTPUT_JSON_PATH, checkpoint_data)

        print(f"\n=== Finished retrying: {recovered_count}/{len(failed_indices)} questions updated ===")
        print(f"Updated results saved to {config.OUTPUT_JSON_PATH}")
        return

    # -----------------------------------------------------------------------
    # MODE B: Standard processing / resume from last index
    # -----------------------------------------------------------------------
    if not os.path.exists(config.INPUT_JSON_PATH):
        print(f"[Error] Input file not found: {config.INPUT_JSON_PATH}")
        return

    with open(config.INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    questions = input_data.get("corrupted_questions", [])

    if config.SAMPLING_PERCENTAGE < 1.0:
        limit = max(1, int(len(questions) * config.SAMPLING_PERCENTAGE))
        questions = questions[:limit]
        print(f"Sampling enabled: using {len(questions)} questions ({config.SAMPLING_PERCENTAGE*100}% of total).")
    else:
        print(f"Loaded {len(questions)} questions from {config.INPUT_JSON_PATH}")

    processed_count = len(processed_questions)
    print(f"Found {processed_count} already processed questions. Resuming...")

    if processed_count >= len(questions):
        print("All questions have been processed! Exiting.")
        return

    for i in tqdm(range(processed_count, len(questions)), desc="Processing"):
        item = questions[i]
        q_text = item.get("corrupted_question", "")
        image_paths = _image_paths(item)

        if not image_paths:
            print(f"  [Warning] No images found for question: {q_text[:50]}")
            continue

        try:
            result = pipeline.process_question(q_text, image_paths)
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
        help="Prompt profile (default, gemma3_focused, gemma4_focused, qwen25_focused, qwen3vl_focused, phi35_focused)",
    )
    parser.add_argument(
        "--prompt-overrides",
        default=None,
        help="JSON file overriding analyzer, verifier, answerer, or per-cause prompts",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Only re-execute questions from existing checkpoint that encountered errors",
    )
    arguments = parser.parse_args()
    main(
        model_name=arguments.model,
        profile_name=arguments.prompt_profile,
        prompt_overrides=_load_prompt_overrides(arguments.prompt_overrides),
        retry_failed=arguments.retry_failed,
    )
