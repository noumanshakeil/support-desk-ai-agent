from fastapi import APIRouter
from backend import __version__
from backend.config import settings
from backend.schemas import HealthOut
router = APIRouter()

@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    return HealthOut(status="ok", service=settings.app_name, version=__version__, llm_mode=settings.llm_mode)
