import logging
import os

from dotenv import load_dotenv
from fireflyiii_enricher_core.firefly_client import FireflyClient
from tx_processor import TransactionProcessor
from txt_parser import TxtParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("blik_sync.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

FIREFLY_URL = os.getenv("FIREFLY_URL")
TOKEN = os.getenv("FIREFLY_TOKEN")
DESCRIPTION_FILTER = "BLIK - płatność w internecie"




if __name__ == "__main__":
    logger.info("Start programu Firefly Transaction Tool")

    firefly = FireflyClient(FIREFLY_URL, TOKEN)
    txt_data = TxtParser("alior29072025.txt").parse()
    processor = TransactionProcessor(firefly, txt_data)
    processor.process(DESCRIPTION_FILTER, exact_match=False)

    logger.info("Zakończono działanie programu")
