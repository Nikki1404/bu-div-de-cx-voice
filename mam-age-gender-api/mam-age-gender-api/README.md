# MAM Age / Gender Speech API

Small production-shaped FastAPI app wrapping the **Multi-Attention Module (MAM)** CNN from:

[`/data/Age-Gender-Classification`](../Age-Gender-Classification)  
Paper: *Age and Gender Recognition Using a CNN with a Specially Designed Multi-Attention Module through Speech Spectrograms*.

> There is **no MCM** codebase in this workspace. The second age/gender stack is **MAM** (this app).  
> The audeering Wav2Vec2 API lives separately at `/data/age-gender-api`.

---

## How the two APIs differ

| | `age-gender-api` | `mam-age-gender-api` (this) |
|--|------------------|----------------------------|
| Model | audeering Wav2Vec2 (PyTorch) | Anvarjon MAM CNN (TensorFlow/Keras) |
| Input | raw waveform | STFT spectrogram → 64×64 RGB |
| Age output | continuous years | buckets (teens…sixties) |
| Gender | female / male / child | male / female |
| Weights | Hugging Face hub | `.h5` under `Age-Gender-Classification/models/` |

---

## Layout

```
mam-age-gender-api/
├── app/
│   ├── main.py
│   ├── api/routes/          # health, ready, predict
│   ├── core/                # settings + logging
│   ├── schemas/
│   └── services/            # spectrogram + Keras inference
├── scripts/run_dev.sh
├── requirements.txt
├── .env.example
└── README.md
```

Weights are **not** bundled — set `MODEL_ROOT` to the MAM repo’s `models/` folder.

---

## Setup

```bash
cd /data/mam-age-gender-api

# Option A: use the existing MAM venv (already has TensorFlow)
export PATH="/data/Age-Gender-Classification/venv/bin:$PATH"
pip install fastapi "uvicorn[standard]" python-multipart pydantic-settings

# Option B: fresh venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit MODEL_ROOT if needed
```

---

## Run

```bash
cd /data/mam-age-gender-api
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
# default: http://127.0.0.1:8001
```

Or:

```bash
export PYTHONPATH=/data/mam-age-gender-api
/data/Age-Gender-Classification/venv/bin/python -m uvicorn app.main:app \
  --host 0.0.0.0 --port 8001
```

Docs: http://127.0.0.1:8001/docs

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/ready` | Which `.h5` models are loaded |
| POST | `/api/v1/predict?task=all` | Run age / gender / gender_age |
| POST | `/api/v1/predict?task=gender_age` | Single task |

`task` ∈ `age` | `gender` | `gender_age` | `all`

### Example

```bash
curl -s -X POST "http://127.0.0.1:8001/api/v1/predict?task=all" \
  -F "file=@/data/test-audio.wav" | python -m json.tool
```

Example shape:

```json
{
  "filename": "test-audio.wav",
  "duration_seconds": 6.574,
  "sampling_rate": 16000,
  "predictions": {
    "age": {
      "task": "age",
      "label": "twenties",
      "confidence": 0.81,
      "probabilities": { "teens": 0.05, "twenties": 0.81, "...": 0.0 }
    },
    "gender": { "task": "gender", "label": "male", "confidence": 0.96, "probabilities": {} },
    "gender_age": { "task": "gender_age", "label": "male-twenties", "confidence": 0.7, "probabilities": {} }
  }
}
```

---

## Config

| Variable | Default | Meaning |
|----------|---------|---------|
| `MODEL_ROOT` | `/data/Age-Gender-Classification/models` | Folder with `age/`, `gender/`, `gender_age/` |
| `LOAD_TASKS` | `age,gender,gender_age` | Which heads to load at startup |
| `MAX_AUDIO_SECONDS` | `60` | Max clip length |
| `API_PREFIX` | `/api/v1` | Route prefix |

Expected weight files:

```
MODEL_ROOT/age/best_model_age.h5
MODEL_ROOT/gender/best_model_gender.h5
MODEL_ROOT/gender_age/best_model_gender_age.h5
```
