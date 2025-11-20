import logging
import os
import tempfile

from fastapi import APIRouter, HTTPException,Depends
from fireflyiii_enricher_core.firefly_client import FireflyClient

from app.config import DESCRIPTION_FILTER, FIREFLY_TOKEN, FIREFLY_URL
from app.services.csv_reader import BankCSVReader
from app.services.tx_processor import TransactionProcessor
from app.utils.encoding import decode_base64url

from app.services.auth import verify_token

router = APIRouter(prefix="/file", tags=["files"])
logger = logging.getLogger(__name__)


@router.get("start-process/{encoded_id}",dependencies=[Depends(verify_token)])
async def proces_tempfile(encoded_id: str):
    try:
        decoded = decode_base64url(encoded_id)

        if "/" in decoded or ".." in decoded:
            raise HTTPException(status_code=400, detail="Invalid file id")

        tempdir = tempfile.gettempdir()
        full_path = os.path.join(tempdir, decoded + ".csv")

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        csv_data = BankCSVReader(full_path).parse()

        if not FIREFLY_URL or not FIREFLY_TOKEN:
            logger.error("Missing FIREFLY_URL or FIREFLY_TOKEN")
            raise HTTPException(status_code=500, detail="Config error")

        firefly = FireflyClient(FIREFLY_URL, FIREFLY_TOKEN)
        processor = TransactionProcessor(firefly, csv_data)
        report = processor.preview(DESCRIPTION_FILTER, exact_match=False)

        return {
            "file_id": encoded_id,
            "decoded_name": decoded,
            "size": len(csv_data),
            "content": report,
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Invalid or corrupted id")



@router.get("/{encoded_id}",dependencies=[Depends(verify_token)])
async def get_tempfile(encoded_id: str):
    try:
        decoded = decode_base64url(encoded_id)

        if "/" in decoded or ".." in decoded:
            raise HTTPException(status_code=400, detail="Invalid file id")

        tempdir = tempfile.gettempdir()
        full_path = os.path.join(tempdir, decoded + ".csv")

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        csv_data = BankCSVReader(full_path).parse()

        return {
            "file_id": encoded_id,
            "decoded_name": decoded,
            "size": len(csv_data),
            "content": csv_data,
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Invalid or corrupted id")
