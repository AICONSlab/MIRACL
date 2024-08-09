import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("debug.log")
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# INFO: Use %(name)s instead of %(filename)s to get logger script name
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
