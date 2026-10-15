from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.prediction import HealthResponse, ReadyResponse
from app.services.inference import inference_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    st = inference_service.status()
    loaded = st["models_loaded"]
    return ReadyResponse(
        status="ready" if loaded else "not_ready",
        models_loaded=loaded,
        model_root=st["model_root"],
    )
