from fastapi import FastAPI

from app.api.file import router as file_router
from app.api.upload import router as upload_router
from app.utils.logger import setup_logging

setup_logging()

app = FastAPI(title="Firefly Transaction Tool API")

app.include_router(upload_router)
app.include_router(file_router)


@app.get("/")
def root():
    return {"status": "OK", "message": "API działa 🚀"}
