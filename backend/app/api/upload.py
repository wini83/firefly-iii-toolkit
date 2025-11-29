import os
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile

from app.services.auth import get_current_user
from app.services.csv_reader import BankCSVReader
from app.utils.encoding import encode_base64url

router = APIRouter(prefix="/api/upload-csv", tags=["upload"])


@router.post("", dependencies=[Depends(get_current_user)])
async def upload_csv(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    records = BankCSVReader(tmp_path).parse()

    filename = os.path.basename(tmp_path)
    file_id = os.path.splitext(filename)[0]  # tmpXXXX
    encoded = encode_base64url(file_id)

    return {
        "message": "Plik poprawnie wczytany",
        "count": len(records),
        "id": encoded,
    }
