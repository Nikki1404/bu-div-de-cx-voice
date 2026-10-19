import logging
import threading
import time

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from api.schemas import AgeGenderPrediction, HealthResponse
from models.age_gender_model import DEVICE, MODEL_ID, age_gender_model
from profiling.age.service import format_age_result
from profiling.audio import load_audio
from profiling.config import SAMPLE_RATE
from profiling.gender.service import format_gender_result

logger = logging.getLogger("age-gender")
router = APIRouter(prefix="/age-gender", tags=["Age & Gender"])
_prediction_lock = threading.Lock()


def make_prediction(waveform):
    with _prediction_lock:
        model_result = age_gender_model.predict(waveform)
    return {**format_age_result(model_result), **format_gender_result(model_result)}


def predict_audio(data):
    waveform = load_audio(data)
    return {
        "audio_duration_seconds": round(waveform.shape[0] / SAMPLE_RATE, 2),
        **make_prediction(waveform),
    }


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "healthy", "model": MODEL_ID, "device": DEVICE}


@router.post("/predict", response_model=AgeGenderPrediction)
async def predict(file: UploadFile = File(...)):
    try:
        start = time.perf_counter()
        result = await run_in_threadpool(predict_audio, await file.read())
        return {
            "status": "success",
            "filename": file.filename,
            **result,
            "processing_time_seconds": round(time.perf_counter() - start, 3),
        }
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(500, "Prediction failed. Check server logs.") from exc


@router.websocket("/ws")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected", "message": "Send audio as binary data."})
    try:
        while True:
            start = time.perf_counter()
            try:
                data = await websocket.receive_bytes()
                result = await run_in_threadpool(predict_audio, data)
                await websocket.send_json({
                    "status": "success",
                    **result,
                    "processing_time_seconds": round(time.perf_counter() - start, 3),
                })
            except Exception as exc:
                logger.exception("WebSocket prediction failed")
                await websocket.send_json({"status": "error", "message": str(exc)})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")