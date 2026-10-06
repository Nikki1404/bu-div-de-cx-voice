# Voice IQ API

One FastAPI service combines voice biometrics and age/gender profiling. The UI is served from the same origin, so the browser sends each selected recording to the same API host.

## Run with Docker

Requirements: Docker, an NVIDIA GPU with compatible drivers, and Docker's NVIDIA Container Toolkit. The image builds `voice-detect.cpp`, downloads its speaker model, installs the VoxProfile model code, and runs one Uvicorn worker.

```powershell
docker build -t voice-iq .
docker run --rm --gpus all -p 8000:8000 -v voice-iq-data:/data voice-iq
```

Open `http://localhost:8000/demo` for the guided UI or `http://localhost:8000/docs` for the API. Check `http://localhost:8000/health` for service health.

To run without an NVIDIA GPU, set `DEVICE=cpu` when starting the container. The biometrics engine runs on CPU. Profiling inference will be slower.

## Test the complete flow

Open `http://localhost:8000/demo` and enter a speaker/customer ID.

1. For a new speaker, record three enrollment clips. The UI enrolls each clip immediately.
2. After enrollment, record a separate biometric-test clip. For an existing speaker, proceed directly to this test.
3. Review the 1:1 verification and 1:N identification results.
4. Select any enrollment or test recordings still available in the current session, then click **Profile selected**. Each selected clip is sent to `/age-gender/predict` and gets an individual age/gender result.

For API testing from PowerShell, replace the example file paths with recordings at least 3 seconds long. Use distinct enrollment recordings and a held-out test recording:

```powershell
curl.exe -X POST `
	-F "files=@C:\audio\enroll-1.wav" `
	-F "files=@C:\audio\enroll-2.wav" `
	-F "files=@C:\audio\enroll-3.wav" `
	http://localhost:8000/biometrics/speakers/alex/enroll

curl.exe -X POST `
	-F "speaker_id=alex" `
	-F "file=@C:\audio\biometric-test.wav" `
	http://localhost:8000/biometrics/verify

curl.exe -X POST `
	-F "file=@C:\audio\biometric-test.wav" `
	http://localhost:8000/biometrics/identify

curl.exe -X POST `
	-F "file=@C:\audio\biometric-test.wav" `
	http://localhost:8000/age-gender/predict
```

The last request uses the same held-out recording for age/gender profiling after the biometric test.

The speaker registry stores voice embeddings, not recordings. Session audio is not persisted by the server and disappears when the browser page is closed or refreshed. The `/data` volume stores the registry across container restarts.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/biometrics/health` | Biometrics engine status |
| GET | `/biometrics/speakers` | List enrolled speakers |
| POST | `/biometrics/speakers/{speaker_id}/enroll` | Enroll several recordings |
| POST | `/biometrics/speakers/{speaker_id}/enroll-one` | Enroll one recording |
| DELETE | `/biometrics/speakers/{speaker_id}` | Delete a voiceprint |
| POST | `/biometrics/verify` | 1:1 speaker verification |
| POST | `/biometrics/identify` | 1:N speaker identification |
| POST | `/biometrics/call` | Enrollment/authentication call flow |
| POST | `/biometrics/compare` | Compare two recordings |
| GET | `/age-gender/health` | Profiling model status |
| POST | `/age-gender/predict` | Age and gender prediction |
| WS | `/age-gender/ws` | Age and gender prediction over WebSocket |

## Configuration

The speaker engine and model paths can be overridden with `VD_LIB` and `VD_MODEL`. Other biometrics settings use the `VD_` variables defined in `biometrics/config.py`. Set `MODEL_ID` or `DEVICE` to change the profiling model or device. `VD_REGISTRY` defaults to `/data/registry.json` in Docker.

This demo has no authentication. Put it behind an authenticated HTTPS gateway before exposing it publicly; voiceprints and profiling results are sensitive data.