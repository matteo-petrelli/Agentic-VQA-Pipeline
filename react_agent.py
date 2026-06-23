"""
ReAct Agent for Document VQA.

Implements a Thought → Action → Observation loop where the VLM autonomously
decides which tools to invoke to answer questions about document images.

Reference: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", 2023.
"""
import re
import config
from prompt_library import (
    build_react_system_prompt,
    build_react_user_prompt,
    build_react_observation,
    build_layout_prompt,
)


def parse_react_response(response: str):
    """
    Parses a ReAct-formatted VLM response to extract Thought and Action.
    
    Expected format:
        Thought: ...
        Action: tool_name
    
    Returns:
        (thought: str, action: str)
    """
    thought = ""
    action = ""
    
    # Extract Thought (everything after "Thought:" until "Action:")
    thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", response, re.DOTALL | re.IGNORECASE)
    if thought_match:
        thought = thought_match.group(1).strip()
    
    # Extract Action
    action_match = re.search(r"Action:\s*(\S+)", response, re.IGNORECASE)
    if action_match:
        action = action_match.group(1).strip().lower()
    
    return thought, action


def parse_final_answer(response: str):
    """
    Parses the final_answer action to extract Answer and Confidence.
    
    Expected format:
        Thought: ...
        Action: final_answer
        Answer: ...
        Confidence: High / Medium / Low
    
    Returns:
        (answer: str, confidence: int)  where confidence is 1-3
    """
    answer = "Unable to determine"
    confidence = 1  # Default: Low
    
    # Extract Answer
    ans_match = re.search(r"Answer:\s*(.+?)(?=\nConfidence:|\Z)", response, re.DOTALL | re.IGNORECASE)
    if ans_match:
        answer = ans_match.group(1).strip()
    
    # Extract Confidence
    conf_match = re.search(r"Confidence:\s*(\S+)", response, re.IGNORECASE)
    if conf_match:
        c = conf_match.group(1).strip().lower()
        if "high" in c:
            confidence = 3
        elif "medium" in c:
            confidence = 2
        else:
            confidence = 1
    
    return answer, confidence


class ReActAgent:
    """
    ReAct-style agent that autonomously decides which tools to use
    for answering document VQA questions.
    
    Available tools:
        - visual_inspect: Spatial/layout analysis of the document image
        - ocr_extract: DOTS.OCR text extraction with layout structure
        - entity_tag: GLiNER semantic entity tagging on OCR text
        - final_answer: Terminates the loop with an answer
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.tool_handlers = {
            "visual_inspect": self._tool_visual_inspect,
            "ocr_extract": self._tool_ocr_extract,
            "entity_tag": self._tool_entity_tag,
        }
    
    def process_question(self, question: str, image_paths: list) -> dict:
        """
        Main ReAct loop for processing a single question.
        
        Args:
            question: The question to answer.
            image_paths: List of document page image paths.
            
        Returns:
            dict with final_answer, confidence, steps, tools_used, trace.
        """
        num_pages = len(image_paths)
        primary_image = image_paths[0]  # Use first page for VLM calls
        
        # Build initial conversation
        conversation = [
            {"role": "system", "content": build_react_system_prompt()},
            {"role": "user", "content": build_react_user_prompt(question, num_pages)},
        ]
        
        trace = []          # Full step-by-step log
        tools_used = set()  # Track which tools have been called
        ocr_cache = {}      # Cache OCR results across tools
        
        print(f"--- [ReAct] Processing: {question}")
        
        for step in range(1, config.MAX_ITERATIONS + 1):
            # 1. Call VLM with full conversation history + image
            response = self.engine.call_vlm_chat(conversation, primary_image)
            
            # 2. Parse Thought + Action from response
            thought, action = parse_react_response(response)
            
            step_log = {
                "step": step,
                "thought": thought,
                "action": action,
                "raw_response": response,
            }
            
            print(f"  Step {step} | Thought: {thought[:80]}...")
            print(f"         | Action: {action}")
            
            # 3. Handle final_answer → terminate loop
            if action == "final_answer":
                answer, confidence = parse_final_answer(response)
                step_log["answer"] = answer
                step_log["confidence"] = confidence
                trace.append(step_log)
                
                print(f"  ✓ Final Answer: {answer} (Confidence: {confidence})")
                
                return {
                    "final_answer": answer,
                    "final_confidence": confidence,
                    "steps": len(trace),
                    "tools_used": list(tools_used),
                    "trace": trace,
                }
            
            # 4. Execute tool if valid and not already used
            if action in self.tool_handlers:
                if action in tools_used:
                    observation = f"Error: Tool '{action}' has already been used. Choose a different tool or call final_answer."
                    print(f"         | ⚠ Tool already used")
                else:
                    tools_used.add(action)
                    observation = self.tool_handlers[action](
                        question=question,
                        image_paths=image_paths,
                        ocr_cache=ocr_cache,
                    )
                    print(f"         | Observation: {observation[:100]}...")
            else:
                observation = (
                    f"Error: Unknown tool '{action}'. "
                    f"Available tools: {', '.join(list(self.tool_handlers.keys()) + ['final_answer'])}"
                )
                print(f"         | ⚠ Unknown tool")
            
            step_log["observation"] = observation[:1000]  # Truncate for logging
            trace.append(step_log)
            
            # 5. Append assistant response + observation to conversation
            conversation.append({"role": "assistant", "content": response})
            conversation.append({
                "role": "user",
                "content": build_react_observation(action, observation),
            })
        
        # Forced exit: MAX_ITERATIONS reached without final_answer
        print(f"  ⚠ Forced exit after {config.MAX_ITERATIONS} steps")
        
        # Try to extract an answer from the last response as fallback
        last_response = trace[-1]["raw_response"] if trace else ""
        fallback_answer, fallback_conf = parse_final_answer(last_response)
        
        return {
            "final_answer": fallback_answer if fallback_answer != "Unable to determine" else "Unable to determine",
            "final_confidence": fallback_conf,
            "steps": len(trace),
            "tools_used": list(tools_used),
            "trace": trace,
            "forced_exit": True,
        }
    
    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================
    
    def _tool_visual_inspect(self, question: str, image_paths: list, ocr_cache: dict) -> str:
        """
        Tool: visual_inspect
        Sends the document image to the VLM with a layout/spatial analysis prompt.
        Returns the VLM's visual assessment of the document.
        """
        prompt = build_layout_prompt(question)
        results = []
        
        for i, img_path in enumerate(image_paths):
            result = self.engine.call_vlm(prompt, img_path)
            results.append(f"--- Page {i+1} ---\n{result}")
        
        return "\n\n".join(results)
    
    def _tool_ocr_extract(self, question: str, image_paths: list, ocr_cache: dict) -> str:
        """
        Tool: ocr_extract
        Runs DOTS.OCR on each page to extract structured text blocks.
        Caches results for use by entity_tag.
        """
        all_blocks = []
        
        for i, img_path in enumerate(image_paths):
            layout_objs = self.engine.get_layout(img_path)
            
            structured_blocks = []
            for obj in layout_objs:
                cat = obj.get("category", "Text")
                txt = obj.get("text_content", "")
                structured_blocks.append(f"[{cat}]: {txt}")
            
            page_text = "\n".join(structured_blocks)
            ocr_cache[f"page_{i+1}"] = page_text  # Cache for entity_tag
            all_blocks.append(f"--- Page {i+1} ---\n{page_text}")
        
        return "\n\n".join(all_blocks)
    
    def _tool_entity_tag(self, question: str, image_paths: list, ocr_cache: dict) -> str:
        """
        Tool: entity_tag
        Runs GLiNER on cached OCR text to tag semantic entities.
        If OCR hasn't been run yet, returns an error.
        """
        if not ocr_cache:
            return (
                "Error: No OCR text available. You must call ocr_extract first "
                "before using entity_tag."
            )
        
        results = []
        
        # Tag each page's OCR text
        for page_key in sorted(ocr_cache.keys()):
            raw_text = ocr_cache[page_key]
            tagged_text, entities = self.engine.tag_text_with_gliner(raw_text)
            results.append(
                f"--- {page_key} (tagged) ---\n"
                f"{tagged_text}\n"
                f"Entities found: {entities}"
            )
        
        # Also tag the question itself
        annotated_q, q_entities = self.engine.tag_text_with_gliner(question)
        results.append(
            f"--- Question (tagged) ---\n"
            f"{annotated_q}\n"
            f"Question entities: {q_entities}"
        )
        
        return "\n\n".join(results)
