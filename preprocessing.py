import os
import torch
import gc
import json
import re
import PIL.Image
import io
import base64
import requests
from typing import List, Dict, Any
from transformers import AutoModelForCausalLM, AutoProcessor, BitsAndBytesConfig
from gliner import GLiNER
from nltk.tokenize import sent_tokenize
import config

def repair_json(json_str):
    """Attempts to repair truncated or malformed JSON strings."""
    json_str = json_str.strip()
    json_str = re.sub(r"```json|```", "", json_str).strip()
    try: return json.loads(json_str)
    except: pass
    
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    try: return json.loads(json_str + "]")
    except: pass
    try: return json.loads(json_str + "}]")
    except: pass
    try:
        last_obj_end = json_str.rfind("}")
        if last_obj_end != -1:
            return json.loads(json_str[:last_obj_end+1] + "]")
    except: pass
    return []

def resize_image_for_model(image_path, max_size=768):
    if isinstance(image_path, str):
        img = PIL.Image.open(image_path).convert("RGB")
    else:
        img = image_path.convert("RGB")
    w, h = img.size
    scale = 1.0
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), PIL.Image.Resampling.LANCZOS)
    return img, scale

def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def clean_inputs_for_quantized(inputs_obj, dtype=torch.float16):
    new_inputs = {}
    inputs_dict = dict(inputs_obj)
    for k, v in inputs_dict.items():
        if isinstance(v, torch.Tensor) and torch.is_floating_point(v):
            new_inputs[k] = v.to(dtype=dtype)
        else:
            new_inputs[k] = v
    return new_inputs

class PreprocessingEngine:
    """Singleton Engine for DOTS.OCR and GLiNER"""
    def __init__(self):
        print("[Engine] Initializing Preprocessing Engine...")
        
        # 1. DOTS.OCR (4-bit or 8-bit)
        print(f"   - Loading DOTS (Layout/OCR) {'4-bit' if config.USE_4BIT_DOTS else '8-bit'}...")
        if config.USE_4BIT_DOTS:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_enable_fp32_cpu_offload=True
            )
            
        self.dots_model = AutoModelForCausalLM.from_pretrained(
            config.DOTS_MODEL_PATH, device_map="cuda", quantization_config=bnb_config, 
            trust_remote_code=True, torch_dtype=torch.float16
        ).eval()
        self.dots_processor = AutoProcessor.from_pretrained(config.DOTS_MODEL_PATH, trust_remote_code=True)

        # 2. GLiNER
        print(f"   - Loading GLiNER...")
        self.gliner_model = GLiNER.from_pretrained(config.GLINER_MODEL_PATH).to("cuda")
        
        print("[Engine] Ready.")

    def get_layout(self, image_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(image_path):
            potential = os.path.join(config.IMAGE_DIR, image_path)
            if os.path.exists(potential):
                image_path = potential
                
        prompt = (
            "Detect all layout elements and transcribe their text content exactly. "
            "Output MUST be a valid JSON list of objects. "
            "Each object must have exactly three keys: 'bbox' [x1,y1,x2,y2], 'category', and 'text_content'."
        )        
        resized_img, scale_factor = resize_image_for_model(image_path, max_size=768)
        messages = [{"role": "user", "content": [{"type": "image", "image": resized_img}, {"type": "text", "text": prompt}]}]
        text_input = self.dots_processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.dots_processor(text=[text_input], images=[resized_img], padding=True, return_tensors="pt").to(self.dots_model.device)
        inputs = clean_inputs_for_quantized(inputs)
        
        with torch.no_grad():
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                generated_ids = self.dots_model.generate(**inputs, max_new_tokens=1024)
        
        generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs['input_ids'], generated_ids)]
        out = self.dots_processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]

        del inputs, generated_ids
        torch.cuda.empty_cache()

        results = repair_json(out)
        if isinstance(results, dict): results = [results]
        
        # Sort top-to-bottom
        results.sort(key=lambda x: (x.get('bbox', [0,0,0,0])[1], x.get('bbox', [0,0,0,0])[0]))
        return results

    def tag_text_with_gliner(self, text: str):
        if not text or len(text.strip()) < 5:
            return text, []
        
        flat_labels = [
            "percentage", "currency", "temperature", "measure_unit", "numerical_value_number", 
            "price_number_information", "price_numerical_value", "date_information", 
            "date_numerical_value", "time_information", "time_numerical_value", 
            "year_number_information", "year_numerical_value", "person_name", "company_name", 
            "product", "food", "chemical_element", "job_title_name", "job_title_information", 
            "animal", "plant", "movie", "book", "transport_means", "event", "country", "city", 
            "street", "spatial_information", "continent", "postal_code_information", 
            "postal_code_numerical_value", "document_position_information", 
            "page_number_information", "page_number_numerical_value", "document_element_type", 
            "document_element_information", "document_structure_information"
        ]

        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
                nltk.download('punkt_tab')
                
            sentences = sent_tokenize(text)
            final_tagged_parts = []
            all_entity_list = []

            for sentence in sentences:
                if len(sentence) > 350:
                    sub_sentences = [sentence[i : i + 350] for i in range(0, len(sentence), 350)]
                else:
                    sub_sentences = [sentence]

                for sub_sentence in sub_sentences:
                    entities = self.gliner_model.predict_entities(sub_sentence, flat_labels)
                    valid_entities = []
                    for ent in entities:
                        score = ent.get("score", 0)
                        label = ent.get("label")
                        thr = config.GLINER_THRESHOLDS.get(label, config.GLINER_THRESHOLDS["default"])
                        if score > thr:
                            valid_entities.append(ent)
                    
                    valid_entities.sort(key=lambda x: x['start'], reverse=True)
                    tagged_sub = sub_sentence
                    
                    for ent in valid_entities:
                        lbl = ent['label']
                        original_text = ent['text']
                        start = ent['start']
                        end = ent['end']
                        
                        replacement = f"<{lbl}>{original_text}</{lbl}>"
                        tagged_sub = tagged_sub[:start] + replacement + tagged_sub[end:]
                        
                        cleaned_text = re.sub(r"\s+", " ", original_text)
                        cleaned_text = re.sub(r"[^\w\s.-]", "", cleaned_text).strip(" -").lower()
                        all_entity_list.append(f"{lbl}: {cleaned_text}")
                    
                    final_tagged_parts.append(tagged_sub)

            full_tagged_text = " ".join(final_tagged_parts)
            return full_tagged_text, list(set(all_entity_list))

        except Exception as e:
            print(f"[GLiNER Tagging Error] {e}")
            return text, []

    def call_vlm(self, prompt, image_path=None):
        payload = {
            "model": config.OLLAMA_VLM,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 1024}
        }
        if image_path:
            potential = os.path.join(config.IMAGE_DIR, image_path) if not os.path.exists(image_path) else image_path
            img, _ = resize_image_for_model(potential)
            payload["messages"][0]["images"] = [image_to_base64(img)]

        response = requests.post(config.OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
