import os

# =============================================================================
# MODELS CONFIGURATION
# =============================================================================
# The primary Vision-Language Model to use for both Pass 1 and Pass 2
# Suggested options: "phi3.5-vision", "qwen3-vl:4b", "gemma3:4b"
OLLAMA_VLM = "qwen3-vl:4b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# DOTS.OCR configuration
DOTS_MODEL_PATH = "strangervisionhf/dots.ocr-base-fix"
# Set to True to use 4-bit quantization (NF4) for VRAM saving, False for 8-bit
USE_4BIT_DOTS = True 

# GLiNER configuration
GLINER_MODEL_PATH = "urchade/gliner_medium-v2.1"

# =============================================================================
# I/O PATHS (KAGGLE DEFAULTS)
# =============================================================================
INPUT_JSON_PATH = "/kaggle/input/dude-questions/DUDE_mixed_test.json"
IMAGE_DIR = "/kaggle/input/dude-train/content/DUDE_train-val-test_binaries/images/train"
OUTPUT_JSON_PATH = "/kaggle/working/agentic_pipeline_results.json"

# =============================================================================
# PIPELINE HYPERPARAMETERS
# =============================================================================
# List of keywords that indicate a VLM cannot answer
UNABLE_KEYWORDS = [
    "unable to determine",
    "unable",
    "cannot determine",
    "unanswerable"
]

# If set to a value < 1.0 (e.g. 0.1), only processes that percentage of the dataset.
# Extremely useful for testing the pipeline on a subset before committing to a 15h run.
SAMPLING_PERCENTAGE = 0.1

# Thresholds for GLiNER entity detection
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
