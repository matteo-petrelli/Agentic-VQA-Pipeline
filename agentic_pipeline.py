"""
Agentic Pipeline - Thin wrapper around the ReAct Agent.

This module provides the AgenticPipeline class which delegates all processing
to the ReActAgent. It serves as the stable interface used by run_experiments.py.
"""
import config
from react_agent import ReActAgent


def is_unable(answer: str) -> bool:
    """Check if an answer indicates the question is unanswerable."""
    ans_lower = str(answer).strip().lower()
    for kw in config.UNABLE_KEYWORDS:
        if kw in ans_lower:
            return True
    return False


class AgenticPipeline:
    """
    Main pipeline interface for document VQA.
    
    Delegates processing to the ReActAgent, which autonomously decides
    which tools to use in a Thought → Action → Observation loop.
    """
    
    def __init__(self, engine):
        self.agent = ReActAgent(engine)
    
    def process_question(self, question: str, image_paths: list) -> dict:
        """
        Process a single question using the ReAct agent.
        
        Args:
            question: The question to answer.
            image_paths: List of document page image paths.
            
        Returns:
            dict with final_answer, final_confidence, steps, tools_used, trace.
        """
        return self.agent.process_question(question, image_paths)
