import os
import statistics
import sys

import torch
import torch.nn.functional as F

from profiling.audio import create_audio_windows

MODEL_ID = os.getenv("MODEL_ID", "tiantiaf/wavlm-large-age-sex")
DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
VOX_PROFILE_PATH = os.getenv("VOX_PROFILE_PATH", "/opt/vox-profile-release")
sys.path.insert(0, VOX_PROFILE_PATH)
sys.path.insert(0, f"{VOX_PROFILE_PATH}/src/model/age_sex")

from wavlm_demographics import WavLMWrapper


class VoxProfileAgeGenderModel:
    def __init__(self):
        self.device = torch.device(DEVICE)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("DEVICE=cuda requested but CUDA is unavailable.")
        print(f"Loading {MODEL_ID} on {self.device}")
        self.model = WavLMWrapper.from_pretrained(MODEL_ID).to(self.device)
        self.model.eval()
        print("Age/Gender model loaded.")

    @torch.inference_mode()
    def _predict_window(self, waveform: torch.Tensor) -> dict:
        age_output, sex_output = self.model(waveform.unsqueeze(0).to(self.device))
        age = age_output.detach().float().cpu().reshape(-1)[0].item() * 100.0
        probabilities = F.softmax(sex_output, dim=-1).detach().cpu().reshape(-1)
        return {"age": age, "female": probabilities[0].item(), "male": probabilities[1].item()}

    @torch.inference_mode()
    def predict(self, waveform: torch.Tensor) -> dict:
        windows = [self._predict_window(window) for window in create_audio_windows(waveform)]
        return {
            "age": statistics.median(result["age"] for result in windows),
            "female": sum(result["female"] for result in windows) / len(windows),
            "male": sum(result["male"] for result in windows) / len(windows),
        }


age_gender_model = VoxProfileAgeGenderModel()