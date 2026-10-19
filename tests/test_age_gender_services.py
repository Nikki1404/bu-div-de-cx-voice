import asyncio
import importlib.util
import unittest
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import patch

from profiling.age.service import format_age_result, get_age_bucket
from profiling.gender.service import format_gender_result


class AgeGenderServiceTests(unittest.TestCase):
    def test_age_bucket_boundaries(self):
        self.assertEqual(get_age_bucket(19.9), "Under 20")
        self.assertEqual(get_age_bucket(20), "20-30")
        self.assertEqual(get_age_bucket(30), "30-40")
        self.assertEqual(get_age_bucket(100), "100+")

    def test_age_prediction_uses_rounded_estimate_for_bucket(self):
        self.assertEqual(
            format_age_result({"age": 29.96}),
            {"age_bucket": "30-40", "estimated_age": 30.0},
        )

    def test_gender_prediction_formats_class_and_probabilities(self):
        result = format_gender_result({"female": 0.8, "male": 0.2})
        self.assertEqual(result["gender"], "Female")
        self.assertEqual(result["gender_confidence"], 0.8)
        self.assertEqual(
            result["gender_probabilities"], {"female": 0.8, "male": 0.2}
        )


class ProfilingConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_inference_does_not_block_event_loop(self):
        started = Event()
        release = Event()

        def predict(waveform):
            started.set()
            if not release.wait(timeout=5):
                raise RuntimeError("event loop blocked during inference")
            return {"age": 30.0, "female": 0.8, "male": 0.2}

        modules = {
            "models.age_gender_model": SimpleNamespace(
                DEVICE="cpu", MODEL_ID="test", age_gender_model=SimpleNamespace(predict=predict)
            ),
            "profiling.audio": SimpleNamespace(
                load_audio=lambda data: SimpleNamespace(shape=(16000,))
            ),
        }
        route_path = Path(__file__).resolve().parents[1] / "api" / "routes" / "age_gender.py"
        with patch.dict("sys.modules", modules):
            spec = importlib.util.spec_from_file_location("profiling_route_test", route_path)
            route = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(route)

        async def read():
            return b"audio"

        upload = SimpleNamespace(read=read, filename="test.wav")
        task = asyncio.create_task(route.predict(upload))
        try:
            self.assertTrue(await asyncio.to_thread(started.wait, 3))
        finally:
            release.set()
        result = await task
        self.assertEqual(result["audio_duration_seconds"], 1.0)
        self.assertEqual(result["estimated_age"], 30.0)
        self.assertEqual(result["filename"], "test.wav")


if __name__ == "__main__":
    unittest.main()