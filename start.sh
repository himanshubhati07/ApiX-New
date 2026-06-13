#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
PORT=47375
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -q
exec uvicorn app.main:app --host 0.0.0.0 --port 47375
