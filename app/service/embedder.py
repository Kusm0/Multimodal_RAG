import app.config as config

import openai
import os
import hashlib
import json


openai.api_key = config.OPENAI_KEY
CACHE_DIR = config.EMBEDDINGS_CACHE_DIR_PATH
EMBEDDING_MODEL = config.EMBEDDING_MODEL_NAME


os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(text: str) -> str:
    key = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.json")

def get_embedding_cache(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    path = get_cache_path(text)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    response = openai.embeddings.create(model=model, input=text.strip())
    embedding = response.data[0].embedding

    with open(path, "w", encoding="utf-8") as f:
        json.dump(embedding, f)

    return embedding

def get_query_embedding(query: str, model: str = EMBEDDING_MODEL) -> list[float]:
    response = openai.embeddings.create(model=model, input=query)
    return response.data[0].embedding