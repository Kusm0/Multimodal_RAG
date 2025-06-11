import os
from dotenv import load_dotenv

load_dotenv()


# --- Налаштування Шляхів ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_CACHE_DIR_PATH = os.path.join(BASE_DIR, "app", "data", "cached_html")
EMBEDDINGS_CACHE_DIR_PATH = os.path.join(BASE_DIR, "app", "data", "embedding_cache")
JSONL_DATASET_PATH = os.path.join(BASE_DIR, "app", "data", "dataset_the_batch.jsonl")
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "app", "system_prompt.txt")


# --- Налаштування логування ---
LOGS_DIR = os.path.join(BASE_DIR, "app", "data", "logs")
LOG_FILE_NAME = "system.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"


# --- Налаштування для Веб-парсингу ---
HEADERS_TYPE = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
BASE_URL_BATCH = "https://www.deeplearning.ai/the-batch/"
TAG_NAMES_ARRAY = [
    "letters", "data-points", "research", "business",
    "science", "culture", "hardware", "ai-careers"
]


# Інші константи або налаштування
QDRANT_IP_ADDRESS = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = "batch_articles_embeddings"


OPENAI_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
OPENAI_LLM_NAME = "gpt-4o"
