from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import BLIK_PAGE_TITLE

router = APIRouter()
templates = Jinja2Templates("templates")


@router.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "title": "Upload CSV",
            "step": "upload",
            "page_title": BLIK_PAGE_TITLE,
        },
    )
