import logging
import os

from dotenv import load_dotenv
from fireflyiii_enricher_core.firefly_client import FireflyClient
from txt_parser import TxtParser

from app.services.csv_reader import BankCSVReader
from app.services.tx_processor import TransactionProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("blik_sync.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()

FIREFLY_URL = os.getenv("FIREFLY_URL")
TOKEN = os.getenv("FIREFLY_TOKEN")
DESCRIPTION_FILTER = "BLIK - płatność w internecie"

TXT = False


if __name__ == "__main__":
    logger.info("Start programu Firefly Transaction Tool")
    if not FIREFLY_URL or not TOKEN:
        logger.error("FIREFLY_URL and FIREFLY_TOKEN environment variables must be set")
        exit(1)
    firefly = FireflyClient(FIREFLY_URL, TOKEN)
    if TXT:
        txt_data = TxtParser("alior29072025.txt").parse()

    else:
        csv_data = BankCSVReader("Historia_Operacji_2025-11-16_15-12-20.csv").parse()
        print("Wczytano %d rekordów z CSV" % len(csv_data))
        processor = TransactionProcessor(firefly, csv_data)
        report = processor.preview(DESCRIPTION_FILTER, exact_match=False)
        processor.process(DESCRIPTION_FILTER, exact_match=False)

    logger.info("Zakończono działanie programu")
