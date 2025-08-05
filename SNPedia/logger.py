import logging
import os

logging.basicConfig(
    level=logging.NOTSET,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger("app")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logger.setLevel(LOG_LEVEL)
