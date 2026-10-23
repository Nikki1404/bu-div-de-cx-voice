FROM nvidia/cuda:13.0.1-cudnn-runtime-ubuntu24.04

ARG http_proxy
ARG https_proxy

ARG VD_REPO=https://github.com/localai-org/voice-detect.cpp.git
ARG VD_REF=1db1759572c90faef6f3a78c36b5941a096a9f89
ARG VD_MODEL_URL=https://huggingface.co/mudler/voice-detect-gguf/resolve/main/ecapa-tdnn-voxceleb.gguf
ARG VD_MODEL_SHA256=68046a1fdfb7843f460962db4739fbd381cc5c3ab93d1505e75e2f4c0dc19b8f
ARG VOX_PROFILE_REPO=https://github.com/tiantiaf0627/vox-profile-release.git

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface \
    MODEL_ID=tiantiaf/wavlm-large-age-sex \
    DEVICE=cuda \
    VOX_PROFILE_PATH=/opt/vox-profile-release \
    CUDA_MODULE_LOADING=LAZY \
    TOKENIZERS_PARALLELISM=false \
    VD_LIB=/opt/voicedetect/lib/libvoicedetect.so \
    VD_MODEL=/opt/voicedetect/models/ecapa-tdnn-voxceleb.gguf \
    VD_REGISTRY=/data/registry.json

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-dev python3-venv python3-pip \
        build-essential cmake git curl ca-certificates ffmpeg \
        libsndfile1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 "${VOX_PROFILE_REPO}" /opt/vox-profile-release \
    && git clone "${VD_REPO}" /tmp/voice-detect.cpp \
    && cd /tmp/voice-detect.cpp \
    && git checkout -q "${VD_REF}" \
    && git submodule update --init --recursive --depth 1 \
    && cmake -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DGGML_NATIVE=OFF \
        -DVOICEDETECT_SHARED=ON \
        -DVOICEDETECT_BUILD_CLI=OFF \
        -DVOICEDETECT_BUILD_TESTS=OFF \
    && cmake --build build -j"$(nproc)" \
    && mkdir -p /opt/voicedetect/lib /opt/voicedetect/models \
    && find build -name '*.so*' -exec cp -a {} /opt/voicedetect/lib/ \; \
    && curl -fL --retry 3 -o /opt/voicedetect/models/ecapa-tdnn-voxceleb.gguf "${VD_MODEL_URL}" \
    && echo "${VD_MODEL_SHA256}  /opt/voicedetect/models/ecapa-tdnn-voxceleb.gguf" | sha256sum -c - \
    && echo /opt/voicedetect/lib > /etc/ld.so.conf.d/voicedetect.conf \
    && ldconfig \
    && rm -rf /tmp/voice-detect.cpp

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu130

WORKDIR /app
COPY requirements.txt .
RUN uv pip install -r requirements.txt

RUN python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="tiantiaf/wavlm-large-age-sex",
    cache_dir="/opt/huggingface/hub",
)
snapshot_download(
    repo_id="microsoft/wavlm-large",
    cache_dir="/opt/huggingface/hub",
)
PY

ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

RUN python - <<'PY'
from transformers import Wav2Vec2FeatureExtractor, WavLMConfig

Wav2Vec2FeatureExtractor.from_pretrained("microsoft/wavlm-large")
WavLMConfig.from_pretrained("microsoft/wavlm-large")
print("WavLM backbone files are cached for offline startup")
PY

RUN python - <<'PY'
from pathlib import Path

path = Path("/opt/venv/lib/python3.12/site-packages/speechbrain/utils/torch_audio_backend.py")
if path.exists():
    content = path.read_text()
    old = "available_backends = torchaudio.list_audio_backends()"
    new = "available_backends = torchaudio.list_audio_backends() if hasattr(torchaudio, 'list_audio_backends') else []"
    if old in content:
        path.write_text(content.replace(old, new))
PY

COPY api ./api
COPY biometrics ./biometrics
COPY models ./models
COPY profiling ./profiling
COPY demo.html ./demo.html

RUN python - <<'PY'
import sys
sys.path.insert(0, "/opt/vox-profile-release")
sys.path.insert(0, "/opt/vox-profile-release/src/model/age_sex")
from wavlm_demographics import WavLMWrapper
print("VoxProfile age/gender model code is available")
PY

RUN useradd --system --uid 10001 --home /app voiceiq \
    && mkdir -p /data && chown voiceiq /data
USER voiceiq

VOLUME ["/data"]
ENV PORT=8001
ENV APP_BASE_PATH=/app
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8001') + os.environ.get('APP_BASE_PATH', '/app').rstrip('/') + '/health', timeout=4)"

CMD ["sh", "-c", "exec python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1"]