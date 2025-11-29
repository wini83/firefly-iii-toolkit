from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates("templates")


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "Logowanie", "step": None}
    )


def ensure_token(request: Request):
    # token = request.cookies.get("access_token") or None
    # ALE TY używasz localStorage, więc bierzemy nagłówek Authorization
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401)
