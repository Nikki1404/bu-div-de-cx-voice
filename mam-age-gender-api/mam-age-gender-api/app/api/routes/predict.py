import logging
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import get_inference_service
from app.core.config import ClsTask, get_settings
from app.schemas.prediction import PredictResponse, TaskPrediction
from app.services.inference import MamInferenceService
from app.services.spectrogram import AudioValidationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict")


async def _read_upload(file: UploadFile) -> tuple[bytes, str | None]:
    settings = get_settings()
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    name = (file.filename or "").lower()

    if content_type and content_type not in settings.allowed_content_type_list:
        if not any(name.endswith(ext) for ext in (".wav", ".mp3", ".flac", ".ogg", ".m4a")):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type: {content_type}",
            )

    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds max size of {settings.max_upload_bytes} bytes",
        )
    return data, file.filename


@router.post(
    "",
    response_model=PredictResponse,
    summary="Predict age/gender with MAM CNN models",
)
async def predict(
    file: UploadFile = File(..., description="Audio file (wav/mp3/flac/ogg)"),
    task: Literal["age", "gender", "gender_age", "all"] = Query(
        "all",
        description="Which MAM head to run (all = every loaded model)",
    ),
    service: MamInferenceService = Depends(get_inference_service),
) -> PredictResponse:
    data, filename = await _read_upload(file)
    tasks: list[ClsTask] | None
    if task == "all":
        tasks = None
    else:
        tasks = [task]  # type: ignore[list-item]

    try:
        results, meta = service.predict_bytes(data, filename=filename, tasks=tasks)
    except AudioValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        logger.exception("MAM inference failed for %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed",
        ) from None

    return PredictResponse(
        filename=filename,
        duration_seconds=round(meta.duration_seconds, 3),
        sampling_rate=meta.sampling_rate,
        predictions={
            name: TaskPrediction(
                task=r.task,
                label=r.label,
                confidence=round(r.confidence, 6),
                probabilities={k: round(v, 6) for k, v in r.probabilities.items()},
            )
            for name, r in results.items()
        },
    )
