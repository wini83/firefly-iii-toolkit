from fastapi import APIRouter

from api.models.system import HealthResponse, VersionResponse

router = APIRouter(prefix="/api/system", tags=["system"])

APP_VERSION: str | None = None


def init_system_router(version: str):
    """Call this function from main to inject version."""
    global APP_VERSION
    APP_VERSION = version


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


@router.get("/version", response_model=VersionResponse)
async def version_check():
    return VersionResponse(version=APP_VERSION or "unknown")
