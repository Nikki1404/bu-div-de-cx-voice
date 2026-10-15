"""Load MAM Keras models and run age/gender inference."""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Any

import numpy as np
from keras.models import load_model

from app.core.config import ClsTask, Settings, get_settings
from app.services.spectrogram import AudioMeta, audio_bytes_to_spectrogram, suffix_from_filename

logger = logging.getLogger(__name__)

LABELS: dict[ClsTask, dict[int, str]] = {
    "gender_age": {
        0: "female-teens",
        1: "female-twenties",
        2: "female-thirties",
        3: "female-fourties",
        4: "female-fifties",
        5: "female-sixties",
        6: "male-teens",
        7: "male-twenties",
        8: "male-thirties",
        9: "male-fourties",
        10: "male-fifties",
        11: "male-sixties",
    },
    "gender": {0: "male", 1: "female"},
    "age": {
        0: "teens",
        1: "twenties",
        2: "thirties",
        3: "fourties",
        4: "fifties",
        5: "sixties",
    },
}


@dataclass(frozen=True)
class TaskResult:
    task: ClsTask
    label: str
    confidence: float
    probabilities: dict[str, float]


class MamInferenceService:
    """Thread-safe loader for MAM CNN weights (age / gender / gender_age)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._models: dict[ClsTask, Any] = {}
        self._settings: Settings | None = None

    @property
    def is_ready(self) -> bool:
        return bool(self._models)

    @property
    def loaded_tasks(self) -> list[str]:
        return sorted(self._models.keys())

    def load(self, settings: Settings | None = None) -> None:
        with self._lock:
            if self._models:
                return

            os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
            settings = settings or get_settings()
            self._settings = settings

            root = settings.model_root
            if not root.is_dir():
                raise FileNotFoundError(f"Model root not found: {root}")

            for task in settings.tasks_to_load:
                path = settings.model_path_for(task)
                if not path.is_file() or path.stat().st_size == 0:
                    logger.warning("Skipping missing model for task=%s path=%s", task, path)
                    continue
                logger.info("Loading MAM model task=%s path=%s", task, path)
                self._models[task] = load_model(path)

            if not self._models:
                raise RuntimeError(
                    f"No MAM models loaded from {root}. "
                    "Expected best_model_<task>.h5 under age/, gender/, gender_age/."
                )
            logger.info("Loaded tasks: %s", ", ".join(self.loaded_tasks))

    def unload(self) -> None:
        with self._lock:
            self._models.clear()
            self._settings = None

    def predict_bytes(
        self,
        data: bytes,
        *,
        filename: str | None = None,
        tasks: list[ClsTask] | None = None,
    ) -> tuple[dict[str, TaskResult], AudioMeta]:
        if not self.is_ready:
            raise RuntimeError("Models are not loaded")

        selected = tasks or list(self._models.keys())  # type: ignore[arg-type]
        for t in selected:
            if t not in self._models:
                raise ValueError(f"Model for task '{t}' is not loaded")

        spec, meta = audio_bytes_to_spectrogram(data, suffix=suffix_from_filename(filename))
        batch = np.expand_dims(spec / 255.0, axis=0).reshape(-1, 64, 64, 3)

        results: dict[str, TaskResult] = {}
        for task in selected:
            model = self._models[task]
            probs = model.predict(batch, verbose=0)[0]
            idx = int(np.argmax(probs))
            label_map = LABELS[task]
            label = label_map[idx]
            prob_dict = {label_map[i]: float(p) for i, p in enumerate(probs)}
            results[task] = TaskResult(
                task=task,
                label=label,
                confidence=float(probs[idx]),
                probabilities=prob_dict,
            )
        return results, meta

    def status(self) -> dict[str, Any]:
        settings = self._settings or get_settings()
        return {
            "models_loaded": self.loaded_tasks,
            "model_root": str(settings.model_root),
        }


inference_service = MamInferenceService()
