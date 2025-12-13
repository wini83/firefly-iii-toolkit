# app/api/auth.py
from datetime import datetime, timedelta
from typing import Optional

import jwt  # pip install PyJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def load_users() -> dict:
    users = {}
    if settings.USERS:
        for part in settings.USERS.split(","):
            if ":" in part:
                u, p = part.split(":", 1)
                users[u.strip()] = p.strip()
    return users


USERS = load_users()


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
    to_encode: dict[str, object] = {"sub": subject}
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
