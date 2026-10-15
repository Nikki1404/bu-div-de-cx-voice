import pytest

from app.services.spectrogram import AudioValidationError, audio_bytes_to_spectrogram


def test_empty_bytes_raises():
    with pytest.raises(AudioValidationError):
        audio_bytes_to_spectrogram(b"")
