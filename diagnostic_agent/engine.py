"""Production engine for Ollama VLM, DOTS.OCR, and GLiNER."""

import base64
import io
import json
import os
import re
from typing import Any

import PIL.Image
import requests

import config


def _resize_image(image_path: str, max_size: int = 768) -> PIL.Image.Image:
    image = PIL.Image.open(image_path).convert("RGB")
    width, height = image.size
    if max(width, height) > max_size:
        scale = max_size / max(width, height)
        image = image.resize(
            (int(width * scale), int(height * scale)),
            PIL.Image.Resampling.LANCZOS,
        )
    return image


def _image_to_base64(image: PIL.Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _repair_layout_json(response: str) -> list[dict[str, Any]]:
    cleaned = re.sub(r"```(?:json)?|```", "", response).strip()
    candidates = (cleaned, cleaned + "]", cleaned + "}]")
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return [value]
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        except json.JSONDecodeError:
            continue
    last_object = cleaned.rfind("}")
    if last_object >= 0:
        try:
            value = json.loads(cleaned[: last_object + 1] + "]")
            return [item for item in value if isinstance(item, dict)]
        except json.JSONDecodeError:
            pass
    return []


class DocumentEngine:
    def __init__(self):
        import torch
        from gliner import GLiNER
        from transformers import AutoModelForCausalLM, AutoProcessor, BitsAndBytesConfig

        self.torch = torch
        quantization = (
            BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
            if config.USE_4BIT_DOTS
            else BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True)
        )
        self.dots_model = AutoModelForCausalLM.from_pretrained(
            config.DOTS_MODEL_PATH,
            device_map={"": config.EVIDENCE_DEVICE},
            quantization_config=quantization,
            trust_remote_code=True,
            torch_dtype=torch.float16,
        ).eval()
        self.dots_processor = AutoProcessor.from_pretrained(
            config.DOTS_MODEL_PATH, trust_remote_code=True
        )
        self.gliner_model = GLiNER.from_pretrained(config.GLINER_MODEL_PATH).to(
            config.EVIDENCE_DEVICE
        )

    def _resolve_image(self, image_path: str) -> str:
        if os.path.exists(image_path):
            return image_path
        candidate = os.path.join(config.IMAGE_DIR, image_path)
        if os.path.exists(candidate):
            return candidate
        raise FileNotFoundError(image_path)

    def get_layout(self, image_path: str) -> list[dict[str, Any]]:
        image = _resize_image(self._resolve_image(image_path))
        prompt = (
            "Detect all layout elements and transcribe their text content exactly. "
            "Return a JSON list whose objects contain bbox [x1,y1,x2,y2], category, "
            "and text_content."
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        text = self.dots_processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.dots_processor(
            text=[text], images=[image], padding=True, return_tensors="pt"
        ).to(self.dots_model.device)
        inputs = {
            key: value.to(dtype=self.torch.float16)
            if isinstance(value, self.torch.Tensor) and self.torch.is_floating_point(value)
            else value
            for key, value in dict(inputs).items()
        }
        with self.torch.no_grad(), self.torch.autocast(
            device_type="cuda", dtype=self.torch.float16
        ):
            generated = self.dots_model.generate(**inputs, max_new_tokens=1024)
        trimmed = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(inputs["input_ids"], generated)
        ]
        response = self.dots_processor.batch_decode(trimmed, skip_special_tokens=True)[0]
        results = _repair_layout_json(response)
        results.sort(
            key=lambda item: (
                item.get("bbox", [0, 0, 0, 0])[1],
                item.get("bbox", [0, 0, 0, 0])[0],
            )
        )
        self.torch.cuda.empty_cache()
        return results

    def tag_text_with_gliner(self, text: str) -> tuple[str, list[str]]:
        if not text or len(text.strip()) < 2:
            return text, []
        labels = config.GLINER_LABELS
        entities = self.gliner_model.predict_entities(text[: config.MAX_GLINER_CHARS], labels)
        valid = []
        for entity in entities:
            threshold = config.GLINER_THRESHOLDS.get(
                entity.get("label"), config.GLINER_THRESHOLDS["default"]
            )
            if entity.get("score", 0) > threshold:
                valid.append(entity)

        tagged = text
        entity_labels = []
        for entity in sorted(valid, key=lambda item: item["start"], reverse=True):
            label = entity["label"]
            value = entity["text"]
            tagged = (
                tagged[: entity["start"]]
                + f"<{label}>{value}</{label}>"
                + tagged[entity["end"] :]
            )
            entity_labels.append(f"{label}: {value.strip().lower()}")
        return tagged, sorted(set(entity_labels))

    def infer(
        self,
        prompt: str,
        image_paths: list[str] | None = None,
        *,
        json_mode: bool = True,
        temperature: float | None = None,
    ) -> str:
        message: dict[str, Any] = {"role": "user", "content": prompt}
        if image_paths:
            message["images"] = [
                _image_to_base64(_resize_image(self._resolve_image(path)))
                for path in image_paths
            ]
        payload: dict[str, Any] = {
            "model": config.OLLAMA_VLM,
            "messages": [message],
            "stream": False,
            "options": {
                "temperature": (
                    config.AGENT_TEMPERATURE if temperature is None else temperature
                ),
                "num_predict": config.VLM_MAX_TOKENS,
            },
        }
        if json_mode:
            payload["format"] = "json"
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=config.OLLAMA_TIMEOUT)
        response.raise_for_status()
        return response.json()["message"]["content"]