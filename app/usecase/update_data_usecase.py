import asyncio

from app.helpers.logger import logger
from app.data_pipeline.crawler.crawler_pipeline import crawler_entry_point
from app.adapter.qdrant_embedding_uploader import qdrant_load_embedding_entry_point


async def pipeline_entry_point():
    logger.info("--- Starting full data processing pipeline ---")

    try:
        logger.info("Step 1: Running web crawling and HTML parsing.")
        await crawler_entry_point()
        logger.info("Step 1: Web crawling and HTML parsing completed.")
    except Exception as e:
        logger.critical(f"Pipeline interrupted: An error occurred during crawler_entry_point: {e}", exc_info=True)
        return

    try:
        logger.info("Step 2: Running Qdrant embedding and loading.")
        qdrant_load_embedding_entry_point()
        logger.info("Step 2: Qdrant embedding and loading completed.")
    except Exception as e:
        logger.critical(f"Pipeline interrupted: An error occurred during qdrant_load_embedding_entry_point: {e}", exc_info=True)
        return

    logger.info("--- Full data processing pipeline finished successfully ---")

if __name__ == "__main__":
    asyncio.run(pipeline_entry_point())