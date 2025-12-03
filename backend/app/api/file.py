import logging
import os
import tempfile
from typing import Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fireflyiii_enricher_core.firefly_client import FireflyClient
from pydantic import BaseModel

from app.config import (DESCRIPTION_FILTER, FIREFLY_TOKEN, FIREFLY_URL,
                        TAG_BLIK_DONE)
from app.services.auth import get_current_user
from app.services.csv_reader import BankCSVReader
from app.services.tx_processor import (MatchResult, SimplifiedRecord,
                                       TransactionProcessor)
from app.utils.encoding import decode_base64url, encode_base64url

router = APIRouter(prefix="/api/file", tags=["files"])
logger = logging.getLogger(__name__)

MEM_MATCHES: Dict[str, List[MatchResult]] = {}


class UploadResponse(BaseModel):
    message: str
    count: int
    id: str


class ApplyPayload(BaseModel):
    csv_indexes: list[int]


class FilePreviewResponse(BaseModel):
    file_id: str
    decoded_name: str
    size: int
    content: List[SimplifiedRecord]


class FileMatchResponse(BaseModel):
    file_id: str
    decoded_name: str
    records_in_file: int
    transactions_found: int
    transactions_not_matched: int
    transactions_with_one_match: int
    transactions_with_many_matches: int
    content: List[MatchResult]


class FileApplyResponse(BaseModel):
    file_id: str
    updated: int
    errors: List[str]


@router.post("", dependencies=[Depends(get_current_user)])
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    records = BankCSVReader(tmp_path).parse()

    filename = os.path.basename(tmp_path)
    file_id = os.path.splitext(filename)[0]  # tmpXXXX
    encoded = encode_base64url(file_id)

    return UploadResponse(
        message="File uploaded successfully",
        count=len(records),
        id=encoded,
    )


@router.get("/{encoded_id}", dependencies=[Depends(get_current_user)])
async def get_tempfile(encoded_id: str) -> FilePreviewResponse:
    try:
        print(f"cache items before: {len(MEM_MATCHES)}")
        decoded = decode_base64url(encoded_id)

        if "/" in decoded or ".." in decoded:
            raise HTTPException(status_code=400, detail="Invalid file id")

        tempdir = tempfile.gettempdir()
        full_path = os.path.join(tempdir, decoded + ".csv")

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        csv_data = BankCSVReader(full_path).parse()

        return FilePreviewResponse(
            file_id=encoded_id,
            decoded_name=decoded,
            size=len(csv_data),
            content=csv_data,
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Invalid or corrupted id")


@router.get("/do-match/{encoded_id}", dependencies=[Depends(get_current_user)])
async def do_match(encoded_id: str) -> FileMatchResponse:
    print(f"cache items before: {len(MEM_MATCHES)}")
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
    processor = TransactionProcessor(firefly)
    report = processor.match(
        csv_data, DESCRIPTION_FILTER, exact_match=False, tag=TAG_BLIK_DONE
    )
    not_matched = len([r for r in report if not r.matches])
    with_one_match = len([r for r in report if len(r.matches) == 1])
    with_many_matches = len([r for r in report if len(r.matches) > 1])

    MEM_MATCHES[encoded_id] = report

    return FileMatchResponse(
        file_id=encoded_id,
        decoded_name=decoded,
        records_in_file=len(csv_data),
        transactions_found=len(report),
        transactions_not_matched=not_matched,
        transactions_with_one_match=with_one_match,
        transactions_with_many_matches=with_many_matches,
        content=report,
    )


@router.post("/apply_match/{encoded_id}", dependencies=[Depends(get_current_user)])
async def apply_matches(encoded_id: str, payload: ApplyPayload)->FileApplyResponse:
    if encoded_id not in MEM_MATCHES:
        raise HTTPException(status_code=400, detail="No match data found")
    data = MEM_MATCHES[encoded_id]

    index = {int(item.tx.id): item for item in data}

    to_update: List[MatchResult] = []

    for req_id in payload.csv_indexes:
        item = index.get(req_id)
        if not item:
            raise HTTPException(
                status_code=400, detail=f"Transaction id {req_id} not found"
            )
        to_update.append(item)

    for match in to_update:
        if len(match.matches) != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Transaction id {match.tx.id} does not have exactly one match",
            )
    if not FIREFLY_URL or not FIREFLY_TOKEN:
        logger.error("Missing FIREFLY_URL or FIREFLY_TOKEN")
        raise HTTPException(status_code=500, detail="Config error")

    firefly = FireflyClient(FIREFLY_URL, FIREFLY_TOKEN)
    processor = TransactionProcessor(firefly)
    updated = 0
    errors = []
    for match in to_update:
        try:
            processor.apply_match(match.tx, match.matches[0])
            updated += 1
        except RuntimeError as e:
            errors.append(f"Error updating transaction id {match.tx.id}: {str(e)}")
    return FileApplyResponse(file_id=encoded_id, updated=updated, errors=errors)
