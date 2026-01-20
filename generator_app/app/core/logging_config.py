import logging

logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
