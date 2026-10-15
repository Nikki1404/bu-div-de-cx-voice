#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer project venv, then Age-Gender-Classification venv (has TensorFlow)
if [[ -x "$ROOT/.venv/bin/uvicorn" ]]; then
  PY="$ROOT/.venv/bin/python"
  UVICORN="$ROOT/.venv/bin/uvicorn"
elif [[ -x /data/Age-Gender-Classification/venv/bin/python ]]; then
  PY=/data/Age-Gender-Classification/venv/bin/python
  UVICORN="$PY -m uvicorn"
else
  PY=python3
  UVICORN="uvicorn"
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"

if [[ "${RELOAD:-false}" == "true" ]]; then
  exec $UVICORN app.main:app --host "$HOST" --port "$PORT" --reload
else
  exec $UVICORN app.main:app --host "$HOST" --port "$PORT" --workers 1
fi
