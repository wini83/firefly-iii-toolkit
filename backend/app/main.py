import tomllib

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.auth import router as auth_router
from app.api.file import router as file_router
from app.api.upload import router as upload_router
from app.routers.file import router as file_ui_router
from app.routers.login import router as login_router
from app.routers.upload import router as upload__ui_router
from app.utils.logger import setup_logging

setup_logging()


def get_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


APP_VERSION = get_version()

app = FastAPI(title="Firefly III Alior BLIK Tool", version=APP_VERSION)

router = APIRouter()
templates = Jinja2Templates("templates")

app.include_router(login_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(file_router)
app.include_router(file_ui_router)
app.include_router(upload__ui_router)


app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/match/{file_id}")
# def match_view(file_id: str):
#     """
#     Serves the frontend match page.
#     The HTML uses HTMX to fetch /api/match/{id}.
#     """
#     try:
#         with open("static/match.html", "r", encoding="utf-8") as f:
#             html = f.read()
#     except FileNotFoundError:
#         return HTMLResponse("<h1>match.html not found</h1>", status_code=500)
#     return HTMLResponse(html)


@app.get("/demo")
def demo_view():
    """
    Serves the frontend match page.
    The HTML uses HTMX to fetch /api/match/{id}.
    """
    try:
        with open("static/demo.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>file not found</h1>", status_code=500)
    return HTMLResponse(html)


app.get("/health")


async def health_check():
    return {"status": "ok"}
