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
    print(f"Loaded {len(questions)} questions from {config.INPUT_JSON_PATH}")
    
    # 2. Check Checkpoint
    checkpoint_data = load_checkpoint(config.OUTPUT_JSON_PATH)
    processed_count = len(checkpoint_data.get("corrupted_questions", []))
    print(f"Found {processed_count} already processed questions. Resuming...")
    
    if processed_count >= len(questions):
        print("All questions have been processed! Exiting.")
        return
        
    # 3. Initialize Engine
    engine = PreprocessingEngine()
    pipeline = AgenticPipeline(engine)
    
    # 4. Process Loop
    for i in tqdm(range(processed_count, len(questions)), desc="Processing"):
        item = questions[i]
        q_text = item.get("corrupted_question", "")
        
        # Extract images
        vr = item.get("verification_result", {})
        vqa_res = vr.get("vqa_results", [{}])[0]
        images = vqa_res.get("image_paths", vqa_res.get("answer", []))
        
        image_paths = []
        if isinstance(images, list):
            for img in images:
                if isinstance(img, dict) and "pages" in img:
                    image_paths.extend(img["pages"])
                elif isinstance(img, str):
                    image_paths.append(img)
                    
        # Ensure unique paths
        image_paths = list(set(image_paths))
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
