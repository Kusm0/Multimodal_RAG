def load_system_prompt(filepath) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()

def parse_llm_response(content: str) -> dict:
    import json
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "answer": "Failed to parse response.",
            "best_image_caption": "",
            "best_image_url": ""
        }

def format_chunks_to_prompt(hits: list[dict]) -> list[str]:
    chunks = []

    for hit in hits:
        payload = hit.payload
        metadata = payload.get("metadata", {})

        title = payload.get("subtitle", "No Title").strip()
        content = payload.get("text", "").strip()
        image_url = metadata.get("image_url", "").strip()
        image_caption = payload.get("image_caption", "").strip()

        block_lines = [
            "-----------------",
            f"Title: {title}",
            f"Content: {content}",
            "\nImage to article:",
            f"- Caption to image: {image_caption}",
            f"- URL to image: {image_url}",
            "-----------------"
        ]

        chunks.append("\n".join(block_lines))

    return chunks

def extract_chunk_metadata(hits: list[dict]) -> list[dict]:
    chunks_info = []
    for hit in hits:
        payload = hit.payload
        metadata = hit.payload.get("metadata", {})

        title = payload.get("subtitle", "No Title").strip()
        source_url = metadata.get("source_url", "").strip()

        chunks_info.append({
            "title": title,
            "source_url": source_url
        })
    return chunks_info