
"""Configuration for the unanswerability diagnostic pipeline."""

# Model and inference
# Backend: "ollama" (Gemma, Qwen, etc.) or "transformers" (Phi-3.5-Vision, etc.)
VLM_BACKEND = "ollama"
OLLAMA_VLM = "qwen2.5vl:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_TIMEOUT = 300
VLM_NUM_CTX = 32768     # Context window size (input prompt + image patch tokens)
VLM_MAX_TOKENS = 4096   # Generation token limit (output response)
AGENT_TEMPERATURE = 0.0

# Whether to send format="json" to Ollama (GBNF-constrained output).
# Disable for models that conflict with strict JSON grammar (e.g. Qwen3-VL).
# When False, the pipeline relies on parse_json_object() to extract JSON from
# free-form text, which is more robust across model families.
OLLAMA_FORCE_JSON = False

# HuggingFace transformers backend (used when VLM_BACKEND = "transformers")
HF_VLM_MODEL_NAME = "microsoft/Phi-3.5-vision-instruct"
HF_VLM_DEVICE = "cuda:1"
HF_VLM_DTYPE = "float16"  # "float16", "bfloat16", or "float32"
HF_VLM_QUANTIZE = None     # None (FP16), "8bit", or "4bit"
HF_VLM_CACHE_DIR = "/tmp/hf_cache"
MAX_IMAGE_SIZE = 1024       # Max dimension for resizing images before passing to VLMs

# Evidence models
EVIDENCE_DEVICE = "cuda:0"
DOTS_MODEL_PATH = "strangervisionhf/dots.ocr-base-fix"
USE_4BIT_DOTS = True
GLINER_MODEL_PATH = "urchade/gliner_medium-v2.1"
MAX_GLINER_CHARS = 12000

GLINER_LABELS = [
    "percentage",
    "currency",
    "temperature",
    "measure_unit",
    "numerical_value_number",
    "price_number_information",
    "price_numerical_value",
    "date_information",
    "date_numerical_value",
    "time_information",
    "time_numerical_value",
    "year_number_information",
    "year_numerical_value",
    "person_name",
    "company_name",
    "product",
    "job_title_name",
    "job_title_information",
    "event",
    "country",
    "city",
    "street",
    "spatial_information",
    "postal_code_information",
    "postal_code_numerical_value",
    "document_position_information",
    "page_number_information",
    "page_number_numerical_value",
    "document_element_type",
    "document_element_information",
    "document_structure_information",
]

GLINER_THRESHOLDS = {
    "document_position_information": 0.75,
    "page_number_information": 0.75,
    "page_number_numerical_value": 0.8,
    "document_element_type": 0.8,
    "document_element_information": 0.8,
    "document_structure_information": 0.8,
    "postal_code_information": 0.8,
    "postal_code_numerical_value": 0.78,
    "date_information": 0.75,
    "year_numerical_value": 0.7,
    "job_title_information": 0.8,
    "job_title_name": 0.9,
    "default": 0.75,
}

# Prompt selection
# Initial configurations only. Replace them after evaluating prompt variants
# separately for each model and diagnostic cause.
PROMPT_PROFILE = "default"

MODEL_PROMPT_PROFILES = {
    # Exact names or lowercase substrings are accepted.
    # "gemma3": "gemma3_focused",
    # "gemma4": "gemma4_focused",
    # "qwen3-vl": "qwen3vl_focused",
}

MODEL_PROMPT_OVERRIDES = {
    # Example:
    # "qwen2.5vl": {
    #     "answerer_prompt": "docel_cot_v4",
    #     "verifier_prompt": "answerability_verifier_v1",
    #     "cause_prompts": {
    #         "VALUE_MISMATCH": "nlp_tag_cot",
    #         "SPATIAL_MISMATCH": "layout_v4",
    #     },
    # },
}

MAX_DIAGNOSTIC_TESTS = 4
MIN_EVIDENCE_COVERAGE = 1.0

# Dataset and output
INPUT_JSON_PATH = "/kaggle/input/datasets/matteopetrelli/dude-mixed/DUDE_mixed_test.json"
IMAGE_DIR = (
    "/kaggle/input/datasets/matteopetrelli/dude-train/"
    "content/DUDE_train-val-test_binaries/images/train"
)
OUTPUT_JSON_PATH = "/kaggle/working/unanswerability_diagnostic_results.json"
SAMPLING_PERCENTAGE = 0.1

try:
    from config_local import *
except ImportError:
    pass
