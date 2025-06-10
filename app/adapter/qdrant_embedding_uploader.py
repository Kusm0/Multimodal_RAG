import app.config as config
import json
from app.service.embedder import get_embedding_cache
from app.adapter.qdrant_client_connect import create_collection_if_not_exists, add_point_to_qdrant
from app.helpers.processing_helpers import load_jsonl, extract_text_for_embedding
from app.helpers.logger import logger

INPUT_JSONL = config.JSONL_DATASET_PATH


def qdrant_load_embedding_entry_point():
    logger.info("Starting Qdrant embedding and loading process.")

    try:
        create_collection_if_not_exists()
        logger.info("Qdrant collection checked/created.")
    except Exception as e:
        logger.critical(f"Failed to create/check Qdrant collection: {e}")
        return  # Завершуємо, якщо не можемо працювати з Qdrant

    data = load_jsonl(INPUT_JSONL)
    if not data:
        logger.warning(f"No data found in {INPUT_JSONL}. Skipping Qdrant embedding.")
        return

    logger.info(f"Loaded {len(data)} records from {INPUT_JSONL} for embedding.")

    successful_embeddings = 0
    total_items = len(data)
    for i, item in enumerate(data):
        if (i + 1) % 100 == 0 or (i + 1) == total_items:  # Логуємо кожні 100 елементів або на останньому
            logger.info(f"Processing item {i + 1}/{total_items}...")

        content = extract_text_for_embedding(item)
        if not content:
            logger.debug(f"Skipping item ID {item.get('id', 'N/A')} due to empty content.")
            continue

        try:
            embedding = get_embedding_cache(content)
            payload = {
                "type": item["type"],
                "title": item.get("title"),
                "subtitle": item.get("subtitle"),
                "image_caption": item.get("image_caption"),
                "text": content,
                "metadata": item["metadata"]
            }
            add_point_to_qdrant(point_id=item["id"], vector=embedding, payload=payload)
            successful_embeddings += 1
        except Exception as e:
            logger.error(f"Error processing item ID {item.get('id', 'N/A')} for Qdrant: {e}")

    logger.info(f"Finished Qdrant embedding and loading process. Successfully embedded {successful_embeddings} points.")


if __name__ == "__main__":
    qdrant_load_embedding_entry_point()