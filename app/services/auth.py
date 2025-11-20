import os
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-Token", auto_error=False)

async def verify_token(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("APP_TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True
