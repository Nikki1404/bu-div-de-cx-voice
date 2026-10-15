"""Audio → 64x64 RGB spectrogram (same pipeline as Age-Gender-Classification)."""

from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass
from pathlib import Path

import librosa
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from keras.utils import img_to_array, load_img

from app.core.config import get_settings


class AudioValidationError(ValueError):
    """Raised when audio cannot be processed."""


@dataclass(frozen=True)
class AudioMeta:
    duration_seconds: float
    sampling_rate: int


def scale_minmax(x: np.ndarray, min_v: float = 0.0, max_v: float = 255.0) -> np.ndarray:
    x_min, x_max = float(x.min()), float(x.max())
    if x_max - x_min < 1e-12:
        return np.zeros_like(x, dtype=np.float32)
    x_std = (x - x_min) / (x_max - x_min)
    return x_std * (max_v - min_v) + min_v


def _save_spectrogram_png(data: np.ndarray, path: Path) -> None:
    """Match repo: matplotlib imshow → PNG (colormap applied)."""
    plt.axis("off")
    fig = plt.imshow(data, aspect="auto", origin="lower", interpolation="none")
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", pad_inches=0)
    plt.close()


def audio_bytes_to_spectrogram(
    data: bytes,
    suffix: str = ".wav",
) -> tuple[np.ndarray, AudioMeta]:
    """
    Load audio bytes, build STFT spectrogram image, return float array (64,64,3).

    Uses a temp file because librosa needs a path/file-like with format support.
    """
    settings = get_settings()
    if not data:
        raise AudioValidationError("Empty audio payload")
    if len(data) > settings.max_upload_bytes:
        raise AudioValidationError(
            f"File exceeds max size of {settings.max_upload_bytes} bytes"
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(data)
        tmp.flush()
        try:
            y, sr = librosa.load(tmp.name, sr=settings.target_sampling_rate)
        except Exception as exc:  # noqa: BLE001
            raise AudioValidationError(f"Could not decode audio: {exc}") from exc

    duration = float(len(y) / sr) if sr else 0.0
    if duration < 0.1:
        raise AudioValidationError("Audio too short (minimum 0.1s)")
    if duration > settings.max_audio_seconds:
        raise AudioValidationError(
            f"Audio duration {duration:.2f}s exceeds limit of {settings.max_audio_seconds}s"
        )

    spec = librosa.stft(y, n_fft=settings.n_fft, hop_length=settings.hop_length)
    spec_db = librosa.amplitude_to_db(np.abs(spec))
    img = scale_minmax(spec_db).astype(np.uint8)

    size = (settings.spectrogram_size, settings.spectrogram_size)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as png_tmp:
        png_path = Path(png_tmp.name)
        _save_spectrogram_png(img, png_path)
        inp_spec = img_to_array(load_img(png_path, target_size=size))

    return inp_spec, AudioMeta(duration_seconds=duration, sampling_rate=sr)


def suffix_from_filename(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ".wav"
    return "." + filename.rsplit(".", 1)[-1].lower()
