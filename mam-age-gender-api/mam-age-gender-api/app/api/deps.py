from fastapi import HTTPException, status

from app.services.inference import MamInferenceService, inference_service


def get_inference_service() -> MamInferenceService:
    if not inference_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MAM models are not ready yet",
        )
    return inference_service
