import io

import torch
import torchaudio

from profiling.config import (
    MAX_AUDIO_SECONDS,
    MIN_AUDIO_SECONDS,
    MIN_RMS,
    SAMPLE_RATE,
    WINDOW_SAMPLES,
)


def load_audio(audio_bytes: bytes) -> torch.Tensor:
    if not audio_bytes:
        raise ValueError("Empty audio file.")
    try:
        waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
    except Exception as exc:
        try:
            from biometrics.engine import decode_audio

            pcm, sample_rate = decode_audio(audio_bytes)
            waveform = torch.from_numpy(pcm).unsqueeze(0)
        except Exception as fallback_exc:
            raise ValueError(f"Unable to decode audio: {fallback_exc}") from exc
    if waveform.numel() == 0:
        raise ValueError("Decoded audio is empty.")
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sample_rate != SAMPLE_RATE:
        waveform = torchaudio.functional.resample(waveform, sample_rate, SAMPLE_RATE)
    waveform = waveform.squeeze(0).float()
    duration = waveform.shape[0] / SAMPLE_RATE
    if duration < MIN_AUDIO_SECONDS:
        raise ValueError(f"Audio must be at least {MIN_AUDIO_SECONDS} seconds.")
    return waveform[:SAMPLE_RATE * MAX_AUDIO_SECONDS]


def rms(waveform: torch.Tensor) -> float:
    return torch.sqrt(torch.mean(waveform ** 2)).item() if waveform.numel() else 0.0


def create_audio_windows(waveform: torch.Tensor) -> list[torch.Tensor]:
    windows = []
    for start in range(0, waveform.shape[0], WINDOW_SAMPLES):
        chunk = waveform[start:start + WINDOW_SAMPLES]
        if chunk.shape[0] / SAMPLE_RATE >= MIN_AUDIO_SECONDS and rms(chunk) >= MIN_RMS:
            windows.append(chunk)
    if not windows:
        if rms(waveform) < MIN_RMS:
            raise ValueError("Audio contains insufficient speech/audio energy.")
        windows.append(waveform)
    return windows