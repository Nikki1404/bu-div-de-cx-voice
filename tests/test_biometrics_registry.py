import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from fastapi import HTTPException

from biometrics import routes
from biometrics.registry import DuplicateSpeakerError, SpeakerRegistry


class SpeakerRegistryEnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = SpeakerRegistry(
            f"{self.temp_dir.name}/registry.json",
            "test-model",
        )
        self.voice = np.array([1.0, 0.0], dtype=np.float32)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_duplicate_ids_are_case_and_whitespace_insensitive(self):
        result = self.registry.enroll("  Alice  ", [self.voice])

        self.assertEqual(result["speaker_id"], "alice")
        self.assertTrue(self.registry.has("ALICE"))
        with self.assertRaises(DuplicateSpeakerError):
            self.registry.enroll("ALICE", [self.voice])
        self.assertEqual(len(self.registry.list()), 1)

    def test_only_matching_voice_can_continue_incomplete_enrollment(self):
        self.registry.enroll("alice", [self.voice])

        result = self.registry.enroll(
            "alice",
            [self.voice],
            allow_incomplete_append=True,
            match_threshold=0.13,
            max_existing_utterances=3,
        )

        self.assertEqual(result["n_utterances"], 2)
        with self.assertRaises(DuplicateSpeakerError):
            self.registry.enroll(
                "alice",
                [np.array([0.0, 1.0], dtype=np.float32)],
                allow_incomplete_append=True,
                match_threshold=0.13,
                max_existing_utterances=3,
            )

    def test_completed_id_cannot_be_enrolled_again(self):
        self.registry.enroll("alice", [self.voice, self.voice, self.voice])

        with self.assertRaises(DuplicateSpeakerError):
            self.registry.enroll(
                "alice",
                [self.voice],
                allow_incomplete_append=True,
                match_threshold=0.13,
                max_existing_utterances=3,
            )

    def test_enroll_route_returns_409_for_existing_normalized_id(self):
        self.registry.enroll("alice", [self.voice])
        previous_registry = routes.STATE.get("registry")
        routes.STATE["registry"] = self.registry
        try:
            with self.assertRaises(HTTPException) as raised:
                routes.enroll(" ALICE ", [])
            self.assertEqual(raised.exception.status_code, 409)
        finally:
            if previous_registry is None:
                routes.STATE.pop("registry", None)
            else:
                routes.STATE["registry"] = previous_registry

    def test_concurrent_different_ids_keep_all_three_clips(self):
        barrier = Barrier(2)

        def embed(upload):
            barrier.wait(timeout=5)
            return self.voice, 3.0, 16000

        def enroll(speaker_id):
            uploads = [SimpleNamespace(filename=f"clip-{index}.wav") for index in range(3)]
            return routes.enroll(speaker_id, uploads)

        with patch.dict(routes.STATE, {"registry": self.registry}), patch.object(
            routes, "_embed_upload", side_effect=embed
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(enroll, ["alice", "bob"]))

        self.assertEqual([result["n_utterances"] for result in results], [3, 3])
        reloaded = SpeakerRegistry(self.registry.path, "test-model")
        self.assertEqual(
            [(entry["speaker_id"], entry["n_utterances"]) for entry in reloaded.list()],
            [("alice", 3), ("bob", 3)],
        )

    def test_concurrent_same_id_does_not_overwrite_enrollment(self):
        barrier = Barrier(2)

        def embed(upload):
            barrier.wait(timeout=5)
            return self.voice, 3.0, 16000

        def enroll(speaker_id):
            uploads = [SimpleNamespace(filename=f"clip-{index}.wav") for index in range(3)]
            try:
                return routes.enroll(speaker_id, uploads)["n_utterances"]
            except HTTPException as error:
                return error.status_code

        with patch.dict(routes.STATE, {"registry": self.registry}), patch.object(
            routes, "_embed_upload", side_effect=embed
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(enroll, ["alice", " ALICE "]))

        self.assertEqual(sorted(results), [3, 409])
        self.assertEqual(self.registry.list()[0]["n_utterances"], 3)


if __name__ == "__main__":
    unittest.main()