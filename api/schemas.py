from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model: str
    device: str


class GenderProbabilities(BaseModel):
    female: float
    male: float


class AgeGenderPrediction(BaseModel):
    status: str
    filename: str | None = None
    audio_duration_seconds: float
    age_bucket: str
    estimated_age: float
    gender: str
    gender_confidence: float
    gender_probabilities: GenderProbabilities
    processing_time_seconds: float