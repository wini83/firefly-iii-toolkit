import tomllib

from fastapi import FastAPI

from api.routers.auth import router as auth_router
from api.routers.blik_files import router as blik_router
from api.routers.system import init_system_router
from api.routers.system import router as system_router
from middleware import register_middlewares
from settings import settings
from utils.logger import setup_logging

setup_logging()


def get_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        init_system_router(data["project"]["version"])
    return data["project"]["version"]


APP_VERSION = get_version()

print(f"Settings loaded, DEMO_MODE={settings.DEMO_MODE}")

app = FastAPI(title="Firefly III Toolkit", version=APP_VERSION)

register_middlewares(app, settings)

print(f"Middlewares registered; allowed_origins={settings.allowed_origins}")


app.include_router(auth_router)
app.include_router(blik_router)
app.include_router(system_router)
