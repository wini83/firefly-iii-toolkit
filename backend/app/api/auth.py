# app/api/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt  # pip install PyJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
USERS_RAW = os.getenv("USERS", "")  # e.g. "alice:pass,bob:pass"


def load_users() -> dict:
    users = {}
    if USERS_RAW:
        for part in USERS_RAW.split(","):
            if ":" in part:
                u, p = part.split(":", 1)
                users[u.strip()] = p.strip()
    return users


USERS = load_users()


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": subject}
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(USERS)
    # OAuth2PasswordRequestForm expects fields: username, password (x-www-form-urlencoded)
    username = form_data.username
    password = form_data.password
    real = USERS.get(username)
    if not real or real != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(subject=username)
    return {"access_token": access_token, "token_type": "bearer"}
