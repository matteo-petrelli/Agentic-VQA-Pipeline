import base64
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import PIL.Image
import requests

from diagnostic_agent.agent import UnanswerabilityDiagnosticAgent
from diagnostic_agent.engine import DocumentEngine
from diagnostic_agent.profiles import resolve_prompt_profile
from diagnostic_agent.schemas import CauseCode


class FakeEngine:
    def __init__(self, scenario):
        self.scenario = scenario
        self.prompts = []

    def get_layout(self, image_path):
        if self.scenario == "extraction_failure":
            raise RuntimeError("simulated OCR failure")
        return [
            {
                "bbox": [0, 0, 100, 30],
                "category": "Title",
                "text_content": "Annual report 2012",
            },
            {
                "bbox": [0, 40, 100, 100],
                "category": "Table",
                "text_content": "Revenue: 42",
            },
        ]

    def tag_text_with_gliner(self, text):
        entities = []
        if "2012" in text:
            entities.append("year_numerical_value: 2012")
        if "2015" in text:
            entities.append("year_numerical_value: 2015")
        return text, entities

    def infer(
        self,
        prompt,
        image_paths=None,
        *,
        json_mode=True,
        temperature=None,
    ):
        self.prompts.append(prompt)
        if "Decompose the question" in prompt:
            return json.dumps(
                {
                    "answer_type": "date",
                    "entities": [{"text": "2015", "type": "year"}],
                    "relations": [],
                    "constraints": ["year=2015"],
                    "spatial_references": [],
                    "document_element_references": [],
                    "presuppositions": ["the report is from 2015"],
                }
            )

        if "### ANSWERING TASK" in prompt:
            return json.dumps(
                {
                    "status": "supported",
                    "answer": "42",
                    "evidence": [{"page": 1, "snippet": "Revenue: 42"}],
                    "confidence": "high",
                }
            )

        cause = prompt.split("Test this candidate cause only: ", 1)[1].split(".", 1)[0]
        if self.scenario == "value_mismatch" and cause == CauseCode.VALUE_MISMATCH.value:
            status = "confirmed"
            evidence_for = [{"page": 1, "snippet": "Annual report 2012"}]
        elif self.scenario == "extraction_failure" and cause in {
            CauseCode.EVIDENCE_MISSING.value,
            CauseCode.EXTRACTION_FAILURE.value,
        }:
            status = "confirmed"
            evidence_for = [{"page": 1, "snippet": "simulated OCR failure"}]
        else:
            status = "rejected"
            evidence_for = []

        return json.dumps(
            {
                "cause": cause,
                "status": status,
                "expected": "2015",
                "observed": ["2012"],
                "evidence_for": evidence_for,
                "evidence_against": [],
                "confidence": "high",
                "next_test": None,
            }
        )


class DiagnosticAgentTests(unittest.TestCase):
    def build_agent(self, scenario, max_tests=4):
        engine = FakeEngine(scenario)
        agent = UnanswerabilityDiagnosticAgent(
            engine,
            model_name="test-model",
            max_diagnostic_tests=max_tests,
            min_evidence_coverage=1.0,
        )
        return agent, engine

    def test_confirmed_value_mismatch_is_unanswerable(self):
        agent, _ = self.build_agent("value_mismatch")
        result = agent.process_question("What was the revenue in 2015?", ["page1.png"])

        self.assertEqual(result["answerability"], "unanswerable")
        self.assertEqual(result["primary_cause"], CauseCode.VALUE_MISMATCH.value)
        self.assertEqual(result["final_answer"], "Unable to determine")
        self.assertIn("nlp_tag_cot", result["prompts_used"])

    def test_rejected_hypotheses_reach_answerer(self):
        agent, _ = self.build_agent("answerable", max_tests=2)
        result = agent.process_question("What was the revenue?", ["page1.png"])

        self.assertEqual(result["answerability"], "answerable")
        self.assertEqual(result["final_answer"], "42")
        self.assertEqual(result["answer_confidence"], 3)
        self.assertIn("docel_cot_v4", result["prompts_used"])

    def test_extraction_failure_is_not_semantic_unanswerability(self):
        agent, _ = self.build_agent("extraction_failure")
        result = agent.process_question("What was the revenue in 2015?", ["page1.png"])

        self.assertEqual(result["answerability"], "insufficient_evidence")
        self.assertIn(
            result["primary_cause"],
            {CauseCode.EVIDENCE_MISSING.value, CauseCode.EXTRACTION_FAILURE.value},
        )
        self.assertEqual(result["evidence_coverage"], 0.0)

    def test_model_prompt_override_is_applied(self):
        profile = resolve_prompt_profile(
            "custom-model",
            overrides={
                "answerer_prompt": "docel",
                "cause_prompts": {CauseCode.VALUE_MISMATCH.value: "nlp_list_ocr_cot"},
            },
        )

        self.assertEqual(profile.answerer_prompt, "docel")
        self.assertEqual(
            profile.cause_prompts[CauseCode.VALUE_MISMATCH], "nlp_list_ocr_cot"
        )


class OllamaEngineTests(unittest.TestCase):
    # Generated by GitHub Copilot - Aug-31-2026
    def test_vision_payload_resizes_and_normalizes_image(self):
        """Send bounded JPEG data instead of an unmodified source image."""
        engine = DocumentEngine.__new__(DocumentEngine)
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"message": {"content": "ok"}}

        with tempfile.TemporaryDirectory() as temporary_dir:
            image_path = Path(temporary_dir) / "large.png"
            PIL.Image.new("RGB", (1600, 800), "white").save(image_path)

            with patch("diagnostic_agent.engine.requests.post", return_value=response) as post:
                result = engine._infer_ollama("Describe the page", [str(image_path)])

        payload = post.call_args.kwargs["json"]
        image_bytes = base64.b64decode(payload["messages"][0]["images"][0])
        with PIL.Image.open(io.BytesIO(image_bytes)) as sent_image:
            self.assertEqual(sent_image.format, "JPEG")
            self.assertLessEqual(max(sent_image.size), 768)
        self.assertEqual(result, "ok")

    # Generated by GitHub Copilot - Aug-31-2026
    def test_ollama_http_error_includes_response_detail(self):
        """Expose Ollama's error body when a chat request is rejected."""
        engine = DocumentEngine.__new__(DocumentEngine)
        response = Mock()
        response.text = '{"error":"model does not support images"}'
        response.raise_for_status.side_effect = requests.HTTPError(
            "400 Client Error", response=response
        )

        with patch("diagnostic_agent.engine.requests.post", return_value=response):
            with self.assertRaisesRegex(
                requests.HTTPError, "model does not support images"
            ):
                engine._infer_ollama("Describe the page")


if __name__ == "__main__":
    unittest.main()