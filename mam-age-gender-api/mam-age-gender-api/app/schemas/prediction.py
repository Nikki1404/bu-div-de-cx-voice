from typing import Literal

from pydantic import BaseModel, Field

ClsTask = Literal["age", "gender", "gender_age"]


class TaskPrediction(BaseModel):
    task: ClsTask
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: dict[str, float]


class PredictResponse(BaseModel):
    filename: str | None = None
    duration_seconds: float
    sampling_rate: int
    predictions: dict[str, TaskPrediction]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
    environment: str


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    models_loaded: list[str]
    model_root: str
