from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import BLIK_PAGE_TITLE

router = APIRouter()
templates = Jinja2Templates("templates")


@router.get("/file/{file_id}")
def preview(request: Request, file_id: str):

    # ensure_token(request)

    return templates.TemplateResponse(
        "file.html",
        {
            "request": request,
            "file_id": file_id,
            "step": "preview",
            "page_title": BLIK_PAGE_TITLE,
        },
    )


@router.get("/match/{file_id}")
def match(request: Request, file_id: str):

    # ensure_token(request)

    return templates.TemplateResponse(
        "match.html",
        {
            "request": request,
            "file_id": file_id,
            "step": "match",
            "page_title": BLIK_PAGE_TITLE,
        },
    )
