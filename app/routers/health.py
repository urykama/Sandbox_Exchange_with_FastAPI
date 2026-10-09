# app/routers/health.py
"""GET /health — проверка живости."""

from fastapi import APIRouter

from config import PROJECT_NAME, VERSION, MODE
from app.models.responses import HealthResponse


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        project=PROJECT_NAME,
        version=VERSION,
        mode=MODE,
    )