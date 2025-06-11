#app/helpers/processing_helpers.py

import re
import hashlib
import unicodedata
import json

def url_to_filename(url: str) -> str:
    """
    Перетворює URL на безпечне ім’я файлу: видаляє домен, замінює / і - на _
    """
    clean_url = url.split("?")[0]
    if "the-batch/" in clean_url:
        clean_url = clean_url.split("the-batch/")[-1]
    filename = re.sub(r"[-/]+", "_", clean_url.strip("/"))
    return filename

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_numeric_id(article_slug: str, index: int) -> int:
    base_hash = int(hashlib.sha256(article_slug.encode()).hexdigest(), 16)
    numeric_id = (base_hash % 10**8) * 1000 + index
    return numeric_id

def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def extract_text_for_embedding(entry: dict) -> str:
    if entry["type"] == "news_chunk":
        return entry.get("content", "")
    return ""