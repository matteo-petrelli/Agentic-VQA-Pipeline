import os
import config
from prompt_library import build_layout_prompt, build_unified_prompt

def is_unable(answer: str) -> bool:
    """Checks if the given answer means 'Unable to determine'."""
    ans_lower = str(answer).strip().lower()
    for kw in config.UNABLE_KEYWORDS:
        if kw in ans_lower:
            return True
    return False

def clean_answer(answer: str) -> str:
    ans = str(answer).strip()
    if ans.lower().startswith("final answer:"):
        ans = ans[len("final answer:"):].strip()
    return ans

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
            ans1 = self.engine.call_vlm(prompt1, img_path)
            all_pass1_answers.append(clean_answer(ans1))
            
        # If ALL pages in Pass 1 yield "Unable" and early exit is enabled
        if config.EARLY_EXIT_ON_UNABLE and all(is_unable(a) for a in all_pass1_answers):
            print("  ✓ Early Exit: Pass 1 is UNABLE")
            return {
                "final_answer": "Unable to determine",
                "pass_reached": 1,
                "pass1_answers": all_pass1_answers,
                "pass2_answers": []
            }
            
        # If we reach here, either Pass 1 gave an answer, or early exit is disabled
        pass1_consensus = next((a for a in all_pass1_answers if not is_unable(a)), all_pass1_answers[0])

        # =====================================================================
        # PASS 2: Unified Prompt (DOTS.OCR + GLiNER tags)
        # =====================================================================
        print("  -> Escalating to Pass 2 (Unified OCR) for deep analysis...")
        for i, img_path in enumerate(image_paths):
            print(f"     [+] Processing OCR for page {i+1}...")
            # 1. OCR structured extraction
            layout_objs = self.engine.get_layout(img_path)
            
            # 2. Format it into structured text like "[Title]: Text content"
            structured_blocks = []
            for obj in layout_objs:
                cat = obj.get("category", "Text")
                txt = obj.get("text_content", "")
                structured_blocks.append(f"[{cat}]: {txt}")
            raw_ocr_text = "\n".join(structured_blocks)
            
            # 3. Apply GLiNER to OCR text and Question
            tagged_text, doc_entities = self.engine.tag_text_with_gliner(raw_ocr_text)
            annotated_question, question_entities = self.engine.tag_text_with_gliner(question)
            
            # 4. Build & Call
            prompt2 = build_unified_prompt(
                question=question,
                annotated_question=annotated_question,
                structured_tag_text=f"--- Page {i+1} ---\n{tagged_text}",
                question_entities=question_entities,
                doc_entities=doc_entities,
                page_info=page_info
            )
            ans2 = self.engine.call_vlm(prompt2, img_path)
            all_pass2_answers.append(clean_answer(ans2))

        pass2_consensus = next((a for a in all_pass2_answers if not is_unable(a)), all_pass2_answers[0])
        
        # =====================================================================
        # DECISION LOGIC
        # =====================================================================
        is_p1_unable = is_unable(pass1_consensus)
        is_p2_unable = is_unable(pass2_consensus)
        
        # 1. Consensus
        if pass1_consensus.lower() == pass2_consensus.lower():
            final_ans = pass1_consensus
            print(f"  ✓ Consensus Reached: {final_ans}")
            
        # 2. Disagreement
        else:
            if config.DISAGREEMENT_RESOLUTION == "pass2_authority":
                # Pass 2 wins because it read the actual OCR text
                final_ans = pass2_consensus
                print(f"  ✓ Disagreement (P1: {pass1_consensus} vs P2: {pass2_consensus}). Trusting Pass 2 -> {final_ans}")
            else:
                # Strict consensus required, default to unable
                final_ans = "Unable to determine"
                print(f"  ✓ Disagreement (P1: {pass1_consensus} vs P2: {pass2_consensus}). Strict consensus failed -> UNABLE")

        return {
            "final_answer": final_ans,
            "pass_reached": 2,
            "pass1_answers": all_pass1_answers,
            "pass2_answers": all_pass2_answers
        }
