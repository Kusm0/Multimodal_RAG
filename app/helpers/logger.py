import app.config as config

import logging
import os


LOG_FILE_PATH = os.path.join(config.LOGS_DIR, config.LOG_FILE_NAME)


os.makedirs(config.LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MRAG")