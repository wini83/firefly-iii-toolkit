import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env immediately
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

print(f"Loaded .env from: {ENV_PATH}")


class Settings(BaseSettings):
    FIREFLY_URL: str | None = None
    FIREFLY_TOKEN: str | None = None
    USERS: str | None = None
    DEMO_MODE: bool = False

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ENV_PATH


settings = Settings()
