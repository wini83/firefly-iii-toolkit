import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("blik_sync.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
