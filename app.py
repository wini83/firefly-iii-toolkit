import os
import base64
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import tempfile

from dotenv import load_dotenv

from csv_reader import BankCSVReader
from tx_processor import TransactionProcessor
from fireflyiii_enricher_core.firefly_client import FireflyClient

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

app = FastAPI(title="Firefly Transaction Tool API")

def encode_base64url(s: str) -> str:
    encoded = base64.urlsafe_b64encode(s.encode()).decode()
    return encoded.rstrip("=")

def decode_base64url(s: str) -> str:
    # usuwamy przypadkowe whitespace, bo curl lubi dokleić
    s = s.strip()

    # padding
    missing = len(s) % 4
    if missing:
        s += "=" * (4 - missing)

    return base64.urlsafe_b64decode(s).decode()

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # zapisujemy CSV do temporary
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    records = BankCSVReader(tmp_path).parse()
    filename = os.path.basename(tmp_path)     # "tmp94pv4q6h.csv"
    file_id = os.path.splitext(filename)[0]   # "tmp94pv4q6h"
    file_id_encoded = encode_base64url(file_id)
    print(tmp_path, file_id, file_id_encoded)
    return {
        "message": "Plik poprawnie wczytany",
        "count": len(records),
        "id": file_id_encoded
    }

@app.get("/")
def root():
    return {"status": "OK", "message": "API działa 🚀"}


@app.get("/file/{encoded_id}")
async def get_tempfile(encoded_id: str):
    try:
        # 1. Dekodujemy ID → oryginalna nazwa tempfile (np. tmp94pv4q6h.csv)
        decoded_name = decode_base64url(encoded_id)
        print(decoded_name)
        # 2. Zabezpieczamy się przed path traversal
        if "/" in decoded_name or ".." in decoded_name:
            raise HTTPException(status_code=400, detail="Invalid file id")

        # 4. Walidacja istnienia
        tempdir = tempfile.gettempdir()
        full_path = os.path.join(tempdir, decoded_name+".csv")
        print(full_path)
        if not os.path.exists(full_path):
            print("File does not exist")
            raise HTTPException(status_code=404, detail="File not found")
        print("File exists")

        # 5. Wczytujemy
        csv_data = BankCSVReader(full_path).parse()
        print(f"Wczytano {len(csv_data)} rekordów z CSV")
        if not FIREFLY_URL or not TOKEN:
            logger.error("FIREFLY_URL and FIREFLY_TOKEN environment variables must be set")
            raise HTTPException(status_code=500, detail="Server configuration error")
        firefly = FireflyClient(FIREFLY_URL, TOKEN)  
        processor = TransactionProcessor(firefly, csv_data)
        report = processor.preview(DESCRIPTION_FILTER, exact_match=False)
        
        return {
            "file_id": encoded_id,
            "decoded_name": decoded_name,
            "size": len(csv_data),
            "content": report
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Invalid or corrupted id")
