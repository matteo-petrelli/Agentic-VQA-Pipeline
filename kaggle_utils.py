"""
Kaggle-specific utilities for the Agentic VQA Pipeline.

Extracts document loading, GPU detection, Ollama management, text
processing, and result export into importable functions so the notebook
stays thin.
"""

import atexit
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

def find_project(
    project_source: str = "",
    git_url: str = "",
    git_ref: str = "main",
    working_dir: Path | None = None,
) -> Path:
    """Locate the project directory on Kaggle or clone it from Git."""
    working = working_dir or (Path("/kaggle/working") if Path("/kaggle").exists() else Path.cwd())
    clone_dir = working / "Agentic-VQA-Pipeline"

    explicit = Path(project_source).expanduser() if project_source else None
    for candidate in (explicit, clone_dir, Path.cwd()):
        if candidate and (candidate / "agentic_pipeline.py").is_file():
            return candidate.resolve()

    input_root = Path("/kaggle/input")
    if input_root.exists():
        matches = list(input_root.glob("**/agentic_pipeline.py"))
        if matches:
            return matches[0].parent.resolve()

    if git_url:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", git_ref, git_url, str(clone_dir)],
            check=True,
        )
        return clone_dir.resolve()

    raise FileNotFoundError(
        "Project not found. Set PROJECT_SOURCE, add it as a Kaggle Dataset, "
        "or set GIT_REPOSITORY_URL."
    )


def setup_environment(project_dir: Path) -> None:
    """Install dependencies and configure HF_TOKEN from Kaggle Secrets."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(project_dir / "requirements.txt")],
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "PyMuPDF", "python-docx", "pandas"],
        check=True,
    )

    if shutil.which("ollama") is None:
        subprocess.run(
            ["bash", "-lc", "curl -fsSL https://ollama.com/install.sh | sh"],
            check=True,
        )

    try:
        from kaggle_secrets import UserSecretsClient
        hf_token = UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        hf_token = None
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    os.chdir(project_dir)
    print(f"Project: {project_dir}")
    print("Environment ready.")


# ---------------------------------------------------------------------------
# GPU detection
# ---------------------------------------------------------------------------

def detect_gpus(
    evidence_gpu: int = 0,
    vlm_gpu: int = 1,
    allow_single_gpu: bool = True,
) -> tuple[str, int]:
    """
    Detect available GPUs and return (evidence_device, vlm_gpu_index).

    Prints nvidia-smi summary and validates the requested GPU assignment.
    """
    import torch

    subprocess.run(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free", "--format=csv"],
        check=True,
    )

    gpu_count = torch.cuda.device_count()
    if gpu_count == 0:
        raise RuntimeError("No CUDA GPU detected: enable a GPU accelerator in Kaggle.")

    if gpu_count >= 2:
        if evidence_gpu == vlm_gpu or max(evidence_gpu, vlm_gpu) >= gpu_count:
            raise ValueError("EVIDENCE_GPU and VLM_GPU must point to two distinct existing GPUs.")
    else:
        if not allow_single_gpu:
            raise RuntimeError("Two GPUs required; select GPU T4 x2 in Kaggle options.")
        evidence_gpu = vlm_gpu = 0
        print("WARNING: single GPU available; DOTS and VLM will share cuda:0.")

    for idx in range(gpu_count):
        print(f"cuda:{idx}: {torch.cuda.get_device_name(idx)}")
    if gpu_count >= 2 and not all(
        "T4" in torch.cuda.get_device_name(i) for i in (evidence_gpu, vlm_gpu)
    ):
        print("Note: the two GPUs are not both T4, but the split is still valid.")

    evidence_device = f"cuda:{evidence_gpu}"
    print(f"Document processing -> {evidence_device}")
    print(f"VLM Ollama -> physical GPU {vlm_gpu}")
    return evidence_device, vlm_gpu


# ---------------------------------------------------------------------------
# Ollama management
# ---------------------------------------------------------------------------

_ollama_process = None
_ollama_log_handle = None


def start_ollama(
    vlm_gpu: int,
    model_name: str,
    working_dir: Path | None = None,
    base_url: str = "http://127.0.0.1:11434",
) -> str:
    """
    Start Ollama server, pull the model, and run a warm-up call.

    Returns the full chat API URL.
    """
    global _ollama_process, _ollama_log_handle
    import requests as req

    working = working_dir or (Path("/kaggle/working") if Path("/kaggle").exists() else Path.cwd())

    # Check for existing server
    try:
        if req.get(f"{base_url}/api/tags", timeout=2).ok:
            raise RuntimeError(
                "An Ollama server is already running. Restart the Kaggle session "
                "and re-run the notebook from the beginning."
            )
    except req.RequestException:
        pass

    ollama_env = os.environ.copy()
    ollama_env.update({
        "CUDA_VISIBLE_DEVICES": str(vlm_gpu),
        "OLLAMA_HOST": "127.0.0.1:11434",
        "OLLAMA_KEEP_ALIVE": "-1",
        "OLLAMA_FLASH_ATTENTION": "1",
        "OLLAMA_MODELS": str(working / "ollama_models"),
    })
    _ollama_log_handle = open(working / "ollama.log", "w", encoding="utf-8")
    _ollama_process = subprocess.Popen(
        ["ollama", "serve"],
        env=ollama_env,
        stdout=_ollama_log_handle,
        stderr=subprocess.STDOUT,
    )
    atexit.register(stop_ollama)

    for _ in range(120):
        if _ollama_process.poll() is not None:
            _ollama_log_handle.flush()
            log_tail = (working / "ollama.log").read_text(encoding="utf-8", errors="replace")[-4000:]
            raise RuntimeError(f"Ollama crashed during startup:\n{log_tail}")
        try:
            if req.get(f"{base_url}/api/tags", timeout=2).ok:
                break
        except req.RequestException:
            pass
        time.sleep(1)
    else:
        stop_ollama()
        raise TimeoutError("Ollama did not become available within 120 seconds")

    subprocess.run(["ollama", "pull", model_name], env=ollama_env, check=True)

    api_url = f"{base_url}/api/chat"
    warmup = req.post(
        api_url,
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": 'Return only this JSON: {"ready": true}'}],
            "format": "json",
            "stream": False,
            "keep_alive": -1,
            "options": {"temperature": 0, "num_predict": 32},
        },
        timeout=600,
    )
    warmup.raise_for_status()
    print("Warm-up VLM:", warmup.json()["message"]["content"])

    subprocess.run(
        ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.free", "--format=csv"],
        check=True,
    )
    return api_url


def stop_ollama() -> None:
    """Terminate the Ollama server process."""
    global _ollama_process, _ollama_log_handle
    if _ollama_process is not None and _ollama_process.poll() is None:
        _ollama_process.terminate()
        try:
            _ollama_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _ollama_process.kill()
    if _ollama_log_handle is not None and not _ollama_log_handle.closed:
        _ollama_log_handle.close()


# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def render_text_pages(text: str, output_dir: Path) -> list[str]:
    """Render plain text into page images (A4-ish PNGs)."""
    from PIL import Image, ImageDraw, ImageFont

    output_dir.mkdir(parents=True, exist_ok=True)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 28) if Path(font_path).exists() else ImageFont.load_default()

    lines: list[str] = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=85) or [""])

    pages: list[str] = []
    for page_index, start in enumerate(range(0, len(lines), 45), start=1):
        image = Image.new("RGB", (1654, 2339), "white")
        draw = ImageDraw.Draw(image)
        draw.multiline_text(
            (100, 100), "\n".join(lines[start : start + 45]),
            fill="black", font=font, spacing=12,
        )
        path = output_dir / f"page_{page_index:04d}.png"
        image.save(path)
        pages.append(str(path))
    return pages


def prepare_document(
    document_path: str,
    working_dir: Path | None = None,
    max_mb: int = 100,
) -> list[str]:
    """
    Convert a PDF, DOCX, TXT, image, or image folder into a list of page
    image paths.  Returns an empty list when *document_path* is empty.
    """
    if not document_path:
        return []

    working = working_dir or (Path("/kaggle/working") if Path("/kaggle").exists() else Path.cwd())
    pages_dir = working / "prepared_document_pages"
    path = Path(document_path)

    if not path.exists():
        raise FileNotFoundError(path)

    if path.is_dir():
        files = sorted(item for item in path.iterdir() if item.suffix.lower() in SUPPORTED_IMAGES)
        total_bytes = sum(item.stat().st_size for item in files)
        if not files:
            raise ValueError(f"No supported images in {path}")
    else:
        files = [path]
        total_bytes = path.stat().st_size

    if total_bytes > max_mb * 1024 * 1024:
        raise ValueError(f"Document exceeds {max_mb} MB limit")

    suffix = path.suffix.lower()
    if path.is_dir() or suffix in SUPPORTED_IMAGES:
        return [str(item) for item in files]

    if suffix == ".pdf":
        import fitz

        pages_dir.mkdir(parents=True, exist_ok=True)
        pages: list[str] = []
        with fitz.open(path) as pdf:
            for page_index, page in enumerate(pdf, start=1):
                out = pages_dir / f"page_{page_index:04d}.png"
                page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(out)
                pages.append(str(out))
        return pages

    if suffix == ".docx":
        from docx import Document
        text = "\n".join(p.text for p in Document(path).paragraphs)
        return render_text_pages(text, pages_dir)

    if suffix == ".txt":
        return render_text_pages(
            path.read_text(encoding="utf-8", errors="replace"), pages_dir,
        )

    raise ValueError(f"Unsupported format: {suffix}")


# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Normalize whitespace and null bytes."""
    text = text.replace("\x00", " ").replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sliding_chunks(parts: list[str], max_chars: int, overlap: int = 0) -> list[str]:
    """Slide a window over concatenated text parts."""
    if max_chars <= 0 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Use max_chars > 0 and 0 <= overlap < max_chars")
    text = clean_text("\n".join(parts))
    step = max_chars - overlap
    return [text[s : s + max_chars] for s in range(0, len(text), step) if text[s : s + max_chars]]


def chunk_by_characters(text: str, size: int = 1800, overlap: int = 200) -> list[str]:
    return sliding_chunks([text], size, overlap)


def chunk_by_sentences(text: str, size: int = 1800) -> list[str]:
    return sliding_chunks(re.split(r"(?<=[.!?])\s+", clean_text(text)), size)


def chunk_by_paragraphs(text: str, size: int = 1800) -> list[str]:
    return sliding_chunks(re.split(r"\n\s*\n", clean_text(text)), size)


def chunk_by_tokens(text: str, tokenizer: Any, max_tokens: int = 512, overlap: int = 64) -> list[str]:
    token_ids = tokenizer.encode(clean_text(text), add_special_tokens=False)
    if max_tokens <= 0 or overlap < 0 or overlap >= max_tokens:
        raise ValueError("Invalid token range")
    step = max_tokens - overlap
    return [tokenizer.decode(token_ids[s : s + max_tokens]) for s in range(0, len(token_ids), step)]


# ---------------------------------------------------------------------------
# Result export
# ---------------------------------------------------------------------------

def export_results(
    output_json_path: str,
    smoke_result: dict[str, Any] | None = None,
    smoke_question: str = "",
    smoke_image_paths: list[str] | None = None,
    run_full: bool = False,
    working_dir: Path | None = None,
) -> None:
    """Export pipeline results to JSON, CSV, and TXT."""
    import json

    import pandas as pd
    from IPython.display import FileLink, display

    working = working_dir or (Path("/kaggle/working") if Path("/kaggle").exists() else Path.cwd())
    output_json = Path(output_json_path)

    if run_full and output_json.is_file():
        export_payload = json.loads(output_json.read_text(encoding="utf-8"))
        export_items = export_payload.get("corrupted_questions", [])
    elif smoke_result is not None:
        export_payload = {
            "corrupted_questions": [
                {
                    "corrupted_question": smoke_question,
                    "image_paths": smoke_image_paths or [],
                    "agentic_result": smoke_result,
                }
            ]
        }
        export_items = export_payload["corrupted_questions"]
        output_json = working / "smoke_result.json"
        output_json.write_text(
            json.dumps(export_payload, indent=2, ensure_ascii=False), encoding="utf-8",
        )
    else:
        export_payload = {"corrupted_questions": []}
        export_items = []

    rows = []
    for item in export_items:
        result = item.get("agentic_result", {})
        rows.append({
            "question": item.get("corrupted_question", ""),
            "answerability": result.get("answerability"),
            "primary_cause": result.get("primary_cause"),
            "final_answer": result.get("final_answer"),
            "evidence_coverage": result.get("evidence_coverage"),
            "answerability_confidence": result.get("answerability_confidence"),
            "prompts_used": ", ".join(result.get("prompts_used", [])),
        })

    output_csv = working / "unanswerability_results.csv"
    output_txt = working / "unanswerability_results.txt"
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    output_txt.write_text(
        "\n\n".join(
            f"Question: {row['question']}\nAnswerability: {row['answerability']}\n"
            f"Cause: {row['primary_cause']}\nAnswer: {row['final_answer']}"
            for row in rows
        ),
        encoding="utf-8",
    )

    print(f"Results exported: {len(rows)}")
    for path in (output_json, output_csv, output_txt):
        if path.is_file():
            display(FileLink(str(path)))
