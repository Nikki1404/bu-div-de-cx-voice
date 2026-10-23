# Voice IQ API

One FastAPI service combines voice biometrics and age/gender profiling. The UI is served from the same origin, so the browser sends each selected recording to the same API host.

## Run with Docker

Requirements: Docker with direct access to the build dependencies and Hugging Face. The image builds `voice-detect.cpp`, downloads both model assets, installs the VoxProfile model code, and runs one Uvicorn worker. No proxy is configured for either build or runtime.

```bash
docker build -t voice-iq .
docker run --rm -p 8001:8001 -v voice-iq-data:/data -e DEVICE=cpu voice-iq
```

Hugging Face model files are cached in the image, and runtime is configured for offline model loading. The run command uses normal bridge networking and publishes port `8001`. Omit `-e DEVICE=cpu` and add `--gpus all` when running on a GPU host.

Open `http://localhost:8001/app/demo` for the guided UI or `http://localhost:8001/app/docs` for the API. Check `http://localhost:8001/app/health` for service health.

## Deploy behind an AWS Application Load Balancer

The container serves the entire application beneath `/app` by default. Configure an HTTPS listener rule for `/app` and `/app/*` to forward to a target group using HTTP on port `8001`; the ALB forwards the path unchanged. Set the target group's health check path to `/app/health`. Allow inbound port `8001` on the EC2 security group only from the ALB security group, and expose HTTPS on the ALB. The resulting public URLs are `https://<your-domain>/app/demo`, `https://<your-domain>/app/docs`, and `https://<your-domain>/app/health`.

To use a different URL prefix, set `APP_BASE_PATH` to that path on the container, such as `/voice-iq`, and use the same prefix in the listener rule and target health check.

## Push and deploy to Cloud Run

Run these after building the image on EC2. Use the same image tag through push and deploy:

```bash
IMAGE=us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-voice-biometric-profile-classification/voice-iq:cloudrun
docker tag voice-iq "$IMAGE"
docker push "$IMAGE"
gcloud run deploy voice-iq --image "$IMAGE" --region us-central1 --port 8001
```

CPU mode is used in the example above. The biometrics engine also runs on CPU; profiling inference will be slower.

## Test the complete flow

Open `http://localhost:8001/app/demo` and enter a speaker/customer ID.

1. For a new speaker, record three enrollment clips. The UI keeps them in the current browser page and submits all three together after the last recording. A failed request does not create a partial voiceprint.
2. After enrollment, record a separate biometric-test clip. For an existing speaker, proceed directly to this test.
3. Review the 1:1 verification and 1:N identification results.
4. Select one or more enrollment or verification recordings, then click **Profile selected**. Each selected clip is sent individually to `/age-gender/predict`.
5. The recording picker shows each selected recording's age bucket, gender, and profiling status. **Profile results** shows the estimated age and gender for each selected clip. Selecting the same clip and clicking **Profile selected** again runs a fresh prediction. Profile results are not persisted by the service.

For API testing from PowerShell, replace the example file paths with recordings at least 3 seconds long. Use distinct enrollment recordings and a held-out test recording:

```powershell
curl.exe -X POST `
	-F "files=@C:\audio\enroll-1.wav" `
	-F "files=@C:\audio\enroll-2.wav" `
	-F "files=@C:\audio\enroll-3.wav" `
		http://localhost:8001/app/biometrics/speakers/alex/enroll

curl.exe -X POST `
	-F "speaker_id=alex" `
	-F "file=@C:\audio\biometric-test.wav" `
		http://localhost:8001/app/biometrics/verify

curl.exe -X POST `
	-F "file=@C:\audio\biometric-test.wav" `
		http://localhost:8001/app/biometrics/identify

curl.exe -X POST `
	-F "file=@C:\audio\biometric-test.wav" `
		http://localhost:8001/app/age-gender/predict
```

The last request uses the same held-out recording for age/gender profiling after the biometric test.

The speaker registry stores voice embeddings, not recordings. Session audio is not persisted by the server and disappears when the browser page is closed or refreshed. The `/data` volume stores the registry across container restarts.

Profiling runs on demand for each selected enrollment or verification recording. Recordings and profile results remain in the current browser page only; the service does not persist audio or age/gender predictions.

### Concurrent demo users

Different browser pages can enroll different speaker IDs concurrently. Each page keeps its own recordings and profiling results. The same voice is not rejected merely for appearing under a different ID in this demo flow; IDs are the registration conflict boundary. If two pages submit the same ID, only one enrollment succeeds and the other receives HTTP 409 without overwriting the stored voiceprint. Existing IDs go to verification rather than being enrolled again.

**Reset** clears only the current page's recordings and results, not other users' voiceprints. To intentionally delete a stored voiceprint, use the DELETE speaker endpoint.

Biometric inference and profiling inference each serialize access to their shared model, so requests may queue while other users are processing audio. Profiling runs off the async event loop, allowing the server to handle other requests while inference runs. Keep one Uvicorn worker and one service instance when using the JSON registry: its lock does not protect multiple processes or replicas. Multi-instance deployments require a shared transactional registry; session affinity alone does not fix registry consistency.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/app/biometrics/health` | Biometrics engine status |
| GET | `/app/biometrics/speakers` | List enrolled speakers |
| POST | `/app/biometrics/speakers/{speaker_id}/enroll` | Enroll several recordings |
| POST | `/app/biometrics/speakers/{speaker_id}/enroll-one` | Enroll one recording |
| DELETE | `/app/biometrics/speakers/{speaker_id}` | Delete a voiceprint |
| POST | `/app/biometrics/verify` | 1:1 speaker verification |
| POST | `/app/biometrics/identify` | 1:N speaker identification |
| POST | `/app/biometrics/call` | Enrollment/authentication call flow |
| POST | `/app/biometrics/compare` | Compare two recordings |
| GET | `/app/age-gender/health` | Profiling model status |
| POST | `/app/age-gender/predict` | Age and gender prediction |
| WS | `/app/age-gender/ws` | Age and gender prediction over WebSocket |

Speaker IDs are trimmed and compared case-insensitively. `/biometrics/speakers/{speaker_id}/enroll` returns HTTP 409 if the ID already exists. `/enroll-one` only allows adding clips to an incomplete enrollment when the new clip matches that ID's existing voiceprint; completed IDs and mismatched voices return HTTP 409. Use a new ID for a different speaker.

## Configuration

The speaker engine and model paths can be overridden with `VD_LIB` and `VD_MODEL`. Other biometrics settings use the `VD_` variables defined in `biometrics/config.py`. Set `MODEL_ID` or `DEVICE` to change the profiling model or device. `VD_REGISTRY` defaults to `/data/registry.json` in Docker.

This demo has no authentication. Put it behind an authenticated HTTPS gateway before exposing it publicly; voiceprints and profiling results are sensitive data.