import asyncio
import os
import app.config as config

from app.helpers.logger import logger
from app.data_pipeline.preprocessing.url_collector import collect_all_target_urls
from app.data_pipeline.preprocessing.html_downloader import download_and_cache_html
from app.data_pipeline.preprocessing.article_parser import parse_html
from app.data_pipeline.preprocessing.jsonl_writer import append_to_jsonl


HTML_DIR = config.HTML_CACHE_DIR_PATH
OUTPUT_JSONL = config.JSONL_DATASET_PATH

HEADERS = config.HEADERS_TYPE

BASE_URL = config.BASE_URL_BATCH
TAG_NAMES = config.TAG_NAMES_ARRAY


async def crawler_entry_point():
    os.makedirs(HTML_DIR, exist_ok=True)

    logger.info("Starting URL collection")
    urls = await collect_all_target_urls(HEADERS, BASE_URL, TAG_NAMES, OUTPUT_JSONL)
    logger.info(f"Collected {len(urls)} unique URLs")

    all_records = []

    for i, url in enumerate(sorted(urls)):
        logger.info(f"[{i+1}/{len(urls)}] Downloading HTML: {url}")
        html_path = await download_and_cache_html(url, HEADERS, HTML_DIR)
        if not html_path:
            logger.warning(f"Failed to download: {url}")
            continue

        try:
            logger.info(f"Parsing HTML: {html_path}")
            parsed_chunks = await parse_html(html_path, source_url=url)
            if parsed_chunks:
                all_records.extend(parsed_chunks)
        except Exception as e:
            logger.exception(f"Error parsing {url}: {e}")

    if all_records:
        logger.info(f"Writing {len(all_records)} records to JSONL")
        append_to_jsonl(all_records, OUTPUT_JSONL)
    else:
        logger.info("No records to write")

    logger.info("Pipeline finished")

if __name__ == "__main__":
    asyncio.run(crawler_entry_point())