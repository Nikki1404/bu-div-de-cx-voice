from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ClsTask = Literal["age", "gender", "gender_age"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MAM Age Gender Speech API"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Point at Age-Gender-Classification/models by default
    model_root: Path = Field(
        default=Path("/data/Age-Gender-Classification/models"),
        description="Directory containing age/, gender/, gender_age/ weight folders",
    )
    # Comma-separated subset of age,gender,gender_age
    load_tasks: str = "age,gender,gender_age"

    target_sampling_rate: int = 16000
    n_fft: int = 256
    hop_length: int = 128
    spectrogram_size: int = 64

    max_audio_seconds: float = 60.0
    max_upload_bytes: int = 25 * 1024 * 1024
    allowed_content_types: str = (
        "audio/wav,audio/x-wav,audio/wave,audio/mpeg,audio/mp3,"
        "audio/flac,audio/ogg,application/octet-stream"
    )

    api_prefix: str = "/api/v1"
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_content_type_list(self) -> list[str]:
        return [c.strip() for c in self.allowed_content_types.split(",") if c.strip()]

    @property
    def tasks_to_load(self) -> list[ClsTask]:
        allowed: set[str] = {"age", "gender", "gender_age"}
        tasks: list[ClsTask] = []
        for raw in self.load_tasks.split(","):
            t = raw.strip()
            if t in allowed:
                tasks.append(t)  # type: ignore[arg-type]
        return tasks or ["gender_age"]

    def model_path_for(self, task: ClsTask) -> Path:
        return self.model_root / task / f"best_model_{task}.h5"


@lru_cache
def get_settings() -> Settings:
    return Settings()
