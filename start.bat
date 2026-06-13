@echo off
set PORT=47375
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt -q
uvicorn app.main:app --host 0.0.0.0 --port 47375
