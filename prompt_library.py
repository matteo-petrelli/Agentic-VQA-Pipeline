def get_confidence_instructions():
    return (
        "### RESPONSE FORMAT ###\n"
        "You MUST respond exactly in the following format (two lines):\n"
        "Answer: [your concise answer or 'Unable to determine']\n"
        "Confidence: [High / Medium / Low]\n\n"
        "Rate your confidence as:\n"
        "- High: The evidence is clear and unambiguous.\n"
        "- Medium: Evidence exists but there is some ambiguity.\n"
        "- Low: You are guessing or there is a strong contradiction.\n\n"
    )

def build_layout_prompt(question: str) -> str:
    prompt = (
        "You are a highly precise AI assistant for document layout analysis.\n"
        "Your task is to reason spatially about the structure and layout of document pages to answer the question.\n"
        "Do not infer from text meaning — focus only on visual and positional reasoning.\n\n"
        "### LAYOUT REASONING STEPS ###\n"
        "1. **Identify Key Entities:** Extract the main entities or visual cues implied by the question.\n"
        f"   Question: '{question}'\n\n"
        "2. **In-Page Spatial Analysis:**\n"
        "   - Divide each page into four regions:\n"
        "     [Q1] Top-Left | [Q2] Top-Right | [Q3] Bottom-Left | [Q4] Bottom-Right\n"
        "   - Locate where each relevant entity or element appears within its page.\n"
        "   - Assess spatial coherence: does the entity consistently appear in a specific region (top, bottom, etc.)?\n\n"
        "3. **Cross-Page Verification:**\n"
        "   - If multiple pages exist, compare spatial zones across them.\n"
        "   - Confirm consistent positioning of similar entities across pages (e.g., always near top-left).\n"
        "   - Treat inconsistent spatial locations as unreliable evidence.\n\n"
        "4. **Layout Heuristics (for reasoning support):**\n"
        "   - Titles and headers usually appear in the upper regions.\n"
        "   - Tables and core facts often appear mid or bottom-left.\n"
        "   - References and footnotes are typically bottom-right.\n\n"
        "5. **Formulate Spatially-Consistent Answer:**\n"
        "   - If entities appear consistently in the expected regions, provide a concise factual answer.\n"
        "   - If layout evidence is ambiguous, inconsistent, or unsupported, respond 'Unable to determine'.\n\n"
        f"{get_confidence_instructions()}"
        f"Question: {question}\n"
    )
    return prompt

def build_unified_prompt(question: str, annotated_question: str, structured_tag_text: str, question_entities: list, doc_entities: list, page_info: str) -> str:
    prompt = (
        "You are a highly precise AI assistant for document analysis.\n"
        "Your task is to answer questions about the document image content precisely.\n\n"
        "The OCR text has been enriched with NLP entity tags (e.g., <year_numerical_value>, <time_information>, <event>), "
        "so that important elements are explicitly marked and it is divided into the specific object elements from which the OCR was retrieved.\n\n"
        "DOCUMENT CONTENT\n"
        f"{structured_tag_text}\n\n"
        "We provide the list of annotated entities in the question and in the document:\n"
        f"- Entities in the question: {question_entities}\n"
        f"- Entities in the document: {doc_entities}\n\n"
        "GUIDELINES\n"
        "Analyze the user's question by following these steps:\n"
        f"1. Understand the Question: Break down the question: '{annotated_question}' into its key elements.\n"
        "2. In-Page Spatial Analysis:\n"
        "   - Divide each page into four regions: [Q1] Top-Left | [Q2] Top-Right | [Q3] Bottom-Left | [Q4] Bottom-Right\n"
        "   - Locate where each relevant entity or element appears within its page.\n"
        "   - Assess spatial coherence: does the entity consistently appear in a specific region.\n\n"        
        "3. Cross-Page Verification:\n"
        "   - If multiple pages exist, compare spatial zones across them.\n"
        f"   - **Consider document length: {page_info}** Only provide an answer after checking all pages.\n\n"
        "4. Identify and Categorize Document Elements: Examine the document content to identify the distinct elements present (e.g., [Title], [Text], [Table]).\n"
        "5. Check for Key Question Entities in Each Document Element: Look for matches between identified question entities (<...>...</...>) inside document elements.\n"
        "6. Check for Consistency Between Document Elements and Question Context: Evaluate whether the element containing the match aligns with the question’s intent.\n"
        "7. Verify Context: Check if the context around the entities is consistent with what the question is asking.\n"
        "8. Resolve Ambiguities: If multiple matches exist, choose the one that best fits the context implied by the question.\n"        
        "9. Check for Contradictions: Examine whether any document element or entities contains information that directly contradicts the question. If any element presents a clear contradiction, respond 'Unable to determine'.\n"
        "10. Formulate the Answer: If a valid and consistent match exists, provide a concise factual answer. If entities are missing, contexts are mismatched, or any contradiction is detected, respond 'Unable to determine'.\n\n"
        f"{get_confidence_instructions()}"
        f"Question: {question}\n"
    )
    return prompt

# =============================================================================
# REACT AGENT PROMPTS
# =============================================================================

def build_react_system_prompt():
    """System prompt that defines the ReAct agent's role, tools, and format."""
    return (
        "You are a document analysis agent specialized in answering questions about document images.\n"
        "You must determine if a question can be answered from the document, or if it is unanswerable.\n\n"
        "## AVAILABLE TOOLS\n"
        "You can use the following tools by specifying them in your response:\n\n"
        "1. visual_inspect: Look at the document image to analyze its layout, structure, and visible content.\n"
        "   Use this FIRST to get an overview of the document type and spatial layout.\n\n"
        "2. ocr_extract: Extract all text content from the document with layout structure (titles, tables, text blocks).\n"
        "   Use this when you need precise text that is hard to read visually.\n\n"
        "3. entity_tag: Tag the extracted text with semantic entities (dates, names, numbers, positions, etc.).\n"
        "   Use this AFTER ocr_extract when you need to identify and match specific entities from the question.\n\n"
        "4. final_answer: Provide your final answer after gathering enough evidence.\n"
        "   You MUST call this tool to complete your analysis.\n\n"
        "## RESPONSE FORMAT\n"
        "At each step, you MUST respond in this exact format:\n\n"
        "Thought: [your reasoning about what you know so far and what information you still need]\n"
        "Action: [tool_name]\n\n"
        "When using final_answer, use this extended format:\n\n"
        "Thought: [your final reasoning summarizing all evidence]\n"
        "Action: final_answer\n"
        "Answer: [your concise answer or 'Unable to determine']\n"
        "Confidence: [High / Medium / Low]\n\n"
        "## CONFIDENCE LEVELS\n"
        "- High: The evidence from the document is clear and directly supports the answer.\n"
        "- Medium: Evidence exists but there is some ambiguity or partial match.\n"
        "- Low: You are guessing, evidence is weak, or there is a contradiction.\n\n"
        "## RULES\n"
        "- Always start with visual_inspect to understand the document structure.\n"
        "- You can call each tool AT MOST ONCE.\n"
        "- After each tool call, you will receive an Observation with the tool's output.\n"
        "- If the question asks about information that contradicts or is absent from the document, "
        "answer 'Unable to determine' with High confidence.\n"
        "- Be concise in your thoughts. Focus on evidence.\n"
        "- You MUST eventually call final_answer to provide your response.\n"
    )

def build_react_user_prompt(question, num_pages):
    """Builds the initial user message for the ReAct agent."""
    return (
        f"Question: {question}\n\n"
        f"The document has {num_pages} page(s). The document image is attached.\n"
        "Analyze the document to answer the question. Start by inspecting the document visually."
    )

def build_react_observation(tool_name, result):
    """Formats a tool output as an Observation message for the conversation."""
    return f"Observation from [{tool_name}]:\n{result}"

