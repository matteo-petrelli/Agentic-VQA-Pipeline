"""Extraction of reusable textual, semantic, and spatial evidence."""

import os
from typing import Any, Protocol


class EvidenceEngine(Protocol):
    def get_layout(self, image_path: str) -> list[dict[str, Any]]: ...

    def tag_text_with_gliner(self, text: str) -> tuple[str, list[str]]: ...


def _quadrant(bbox: list[float], width: float, height: float) -> str:
    if len(bbox) < 4 or width <= 0 or height <= 0:
        return "unknown"
    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2
    vertical = "top" if center_y < height / 2 else "bottom"
    horizontal = "left" if center_x < width / 2 else "right"
    return {
        ("top", "left"): "Q1",
        ("top", "right"): "Q2",
        ("bottom", "left"): "Q3",
        ("bottom", "right"): "Q4",
    }[(vertical, horizontal)]


class EvidenceExtractor:
    def __init__(self, engine: EvidenceEngine):
        self.engine = engine

    def extract(self, question: str, image_paths: list[str]) -> dict[str, Any]:
        pages = []
        structured_parts = []
        plain_parts = []
        tagged_parts = []
        document_entities: list[str] = []
        document_elements: set[str] = set()
        quadrants: set[str] = set()
        errors = []

        for page_number, image_path in enumerate(image_paths, start=1):
            try:
                layout = self.engine.get_layout(image_path)
                valid_objects = [obj for obj in layout if isinstance(obj, dict)]
                max_x = max(
                    (float(obj.get("bbox", [0, 0, 0, 0])[2]) for obj in valid_objects),
                    default=0.0,
                )
                max_y = max(
                    (float(obj.get("bbox", [0, 0, 0, 0])[3]) for obj in valid_objects),
                    default=0.0,
                )

                page_blocks = []
                page_plain = []
                for obj in valid_objects:
                    category = str(obj.get("category") or "Text")
                    text = str(obj.get("text_content") or "").strip()
                    bbox = obj.get("bbox", [0, 0, 0, 0])
                    block_quadrant = _quadrant(bbox, max_x, max_y)
                    document_elements.add(category)
                    quadrants.add(block_quadrant)
                    if text:
                        page_plain.append(text)
                        page_blocks.append(f"[{category}] [{block_quadrant}]: {text}")

                page_text = "\n".join(page_plain)
                tagged_text, page_entities = self.engine.tag_text_with_gliner(page_text)
                document_entities.extend(page_entities)
                page_header = f"--- Page {page_number}: {os.path.basename(image_path)} ---"
                plain_parts.append(f"{page_header}\n{page_text}")
                structured_parts.append(f"{page_header}\n" + "\n".join(page_blocks))
                tagged_parts.append(f"{page_header}\n{tagged_text}")
                pages.append(
                    {
                        "page": page_number,
                        "image_path": image_path,
                        "blocks": valid_objects,
                        "plain_text": page_text,
                    }
                )
            except Exception as exc:
                errors.append(f"Page {page_number} ({image_path}): {exc}")

        _, question_entities = self.engine.tag_text_with_gliner(question)
        total_pages = len(image_paths)
        coverage = len(pages) / total_pages if total_pages else 0.0
        return {
            "pages": pages,
            "plain_ocr": "\n\n".join(plain_parts),
            "structured_ocr": "\n\n".join(structured_parts),
            "tagged_ocr": "\n\n".join(tagged_parts),
            "question_entities": sorted(set(question_entities)),
            "document_entities": sorted(set(document_entities)),
            "document_elements": sorted(document_elements),
            "quadrants": sorted(q for q in quadrants if q != "unknown"),
            "extraction_errors": errors,
            "evidence_coverage": coverage,
        }