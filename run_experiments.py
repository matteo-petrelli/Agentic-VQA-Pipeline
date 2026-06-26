import json
import os
import config
from preprocessing import PreprocessingEngine
from agentic_pipeline import AgenticPipeline
import traceback
from tqdm import tqdm

def load_checkpoint(output_path):
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"corrupted_questions": []}
    return {"corrupted_questions": []}

def save_checkpoint(output_path, data):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    print("=== Agentic VQA Pipeline ===")
    
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
    engine = PreprocessingEngine()
    pipeline = AgenticPipeline(engine)
    
    # 5. Process Loop
    for i in tqdm(range(processed_count, len(questions)), desc="Processing"):
        item = questions[i]
        q_text = item.get("corrupted_question", "")
        
        # Extract image paths from the DUDE_fixed.json structure.
        # Images are derived from `patch_entities` keys (page filenames)
        # or `original_entity[].page_id` as fallback.
        image_paths = []
        
        # Primary: patch_entities keys contain all page filenames
        patch_entities = item.get("patch_entities", {})
        if patch_entities:
            for page_filename in patch_entities.keys():
                full_path = os.path.join(config.IMAGE_DIR, page_filename)
                image_paths.append(full_path)
        
        # Fallback: extract page_ids from original_entity or corrupted_entities
        if not image_paths:
            for ent_list_key in ["original_entity", "corrupted_entities"]:
                for ent in item.get(ent_list_key, []):
                    page_id = ent.get("page_id", "")
                    if page_id:
                        full_path = os.path.join(config.IMAGE_DIR, page_id)
                        if full_path not in image_paths:
                            image_paths.append(full_path)
        
        # Ensure unique paths and sort by page number for consistent ordering
        image_paths = sorted(set(image_paths))
        
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
                "final_answer": f"Error: {e}",
                "pass_reached": 0
            }
            
        # Save Checkpoint
        checkpoint_data["corrupted_questions"].append(item)
        save_checkpoint(config.OUTPUT_JSON_PATH, checkpoint_data)
        
    print(f"\n=== Finished processing {len(questions)} questions ===")
    print(f"Results saved to {config.OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()
