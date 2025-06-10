import json
import os
from app.helpers.logger import logger


def append_to_jsonl(records: list[dict], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.info(f"Ensured directory exists for JSONL: {os.path.dirname(output_path)}")

    try:
        with open(output_path, "a", encoding="utf-8") as f:
            for record in records:
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")
        logger.info(f"Successfully wrote {len(records)} records to {output_path}.")
    except IOError as e:
        logger.error(f"Error writing records to {output_path}: {e}")
        raise