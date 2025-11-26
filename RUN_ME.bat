@echo off
echo Starting FinServ API Server...
call venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
