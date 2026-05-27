import os
import config
from prompt_library import build_layout_prompt, build_unified_prompt

def is_unable(answer: str) -> bool:
    ans_lower = str(answer).strip().lower()
    for kw in config.UNABLE_KEYWORDS:
        if kw in ans_lower:
            return True
    return False

def parse_response(response: str):
    """
    Parses the 2-line structured output:
    Answer: [ans]
    Confidence: [High/Medium/Low]
    Returns (answer_string, numeric_confidence_1_to_3)
    """
    ans = "Unable to determine"
    conf_val = 1 # Default to Low
    
    lines = str(response).strip().split('\n')
    found_ans = False
    
    for line in lines:
        line_lower = line.lower()
        if line_lower.startswith("answer:"):
            ans = line[len("answer:"):].strip()
            found_ans = True
        elif line_lower.startswith("confidence:"):
            c = line[len("confidence:"):].strip().lower()
            if "high" in c: conf_val = 3
            elif "medium" in c: conf_val = 2
            else: conf_val = 1
            
    # Fallback if VLM ignores format
    if not found_ans and lines:
        ans = lines[0].replace("Final Answer:", "").strip()
        
    return ans, conf_val

def aggregate_page_answers(answers_data):
    """
    Given a list of {"answer": str, "confidence": int},
    finds the consensus answer across pages.
    """
    best_ans = "Unable to determine"
    best_conf = 0
    
    for item in answers_data:
        ans = item["answer"]
        conf = item["confidence"]
        
        if conf > best_conf:
            best_ans = ans
            best_conf = conf
        elif conf == best_conf:
            # If tied, prefer a concrete answer over 'Unable'
            if not is_unable(ans) and is_unable(best_ans):
                best_ans = ans
                
    return best_ans, best_conf

class AgenticPipeline:
    def __init__(self, engine):
        self.engine = engine

    def process_question(self, question: str, image_paths: list) -> dict:
        page_info = f"Document has {len(image_paths)} page(s)."
        
        all_pass1_answers = []
        all_pass2_answers = []
        
        print(f"--- Processing: {question}")
        
        # =====================================================================
        # PASS 1: Layout Prompt (Purely Visual, No OCR)
        # =====================================================================
        print("  -> Running Pass 1 (Layout)...")
        for img_path in image_paths:
            prompt1 = build_layout_prompt(question)
            ans_raw = self.engine.call_vlm(prompt1, img_path)
            ans, conf = parse_response(ans_raw)
            all_pass1_answers.append({"answer": ans, "confidence": conf, "raw": ans_raw})
            
        pass1_ans, pass1_conf = aggregate_page_answers(all_pass1_answers)
            
        # Early Exit: If the best visual guess is "Unable" AND confidence is High
        if is_unable(pass1_ans) and pass1_conf == 3:
            print("  ✓ Early Exit: Pass 1 is UNABLE with HIGH confidence.")
            return {
                "final_answer": "Unable to determine",
                "pass_reached": 1,
                "pass1_answers": all_pass1_answers,
                "pass2_answers": []
            }

        # =====================================================================
        # PASS 2: Unified Prompt (DOTS.OCR + GLiNER tags)
        # =====================================================================
        print(f"  -> Escalarion needed (P1={pass1_ans}, Conf={pass1_conf}). Running Pass 2...")
        for i, img_path in enumerate(image_paths):
            print(f"     [+] Processing OCR for page {i+1}...")
            layout_objs = self.engine.get_layout(img_path)
            
            structured_blocks = []
            for obj in layout_objs:
                cat = obj.get("category", "Text")
                txt = obj.get("text_content", "")
                structured_blocks.append(f"[{cat}]: {txt}")
            raw_ocr_text = "\n".join(structured_blocks)
            
            tagged_text, doc_entities = self.engine.tag_text_with_gliner(raw_ocr_text)
            annotated_question, question_entities = self.engine.tag_text_with_gliner(question)
            
            prompt2 = build_unified_prompt(
                question=question,
                annotated_question=annotated_question,
                structured_tag_text=f"--- Page {i+1} ---\n{tagged_text}",
                question_entities=question_entities,
                doc_entities=doc_entities,
                page_info=page_info
            )
            ans_raw = self.engine.call_vlm(prompt2, img_path)
            ans, conf = parse_response(ans_raw)
            all_pass2_answers.append({"answer": ans, "confidence": conf, "raw": ans_raw})

        pass2_ans, pass2_conf = aggregate_page_answers(all_pass2_answers)
        
        # =====================================================================
        # DECISION LOGIC (Confidence Based Routing)
        # =====================================================================
        # 1. Consensus
        if pass1_ans.lower() == pass2_ans.lower():
            final_ans = pass1_ans
            print(f"  ✓ Consensus Reached: {final_ans} (P1 Conf: {pass1_conf}, P2 Conf: {pass2_conf})")
            
        # 2. Disagreement - Confidence Tiebreaker
        else:
            if pass1_conf > pass2_conf:
                final_ans = pass1_ans
                print(f"  ✓ Disagreement. P1 wins by Confidence ({pass1_conf} > {pass2_conf}) -> {final_ans}")
            elif pass2_conf > pass1_conf:
                final_ans = pass2_ans
                print(f"  ✓ Disagreement. P2 wins by Confidence ({pass2_conf} > {pass1_conf}) -> {final_ans}")
            else:
                # Tie
                final_ans = pass2_ans
                print(f"  ✓ Disagreement. Tie ({pass1_conf}=={pass2_conf}). P2 wins by Authority -> {final_ans}")

        return {
            "final_answer": final_ans,
            "pass_reached": 2,
            "pass1_answers": all_pass1_answers,
            "pass2_answers": all_pass2_answers,
            "final_confidence": max(pass1_conf, pass2_conf)
        }
