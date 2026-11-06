@echo off
title PaperTrail Backend
echo ========================================================
echo   Starting PaperTrail Backend (FastAPI + Uvicorn)
echo ========================================================
cd /d "%~dp0backend"
python main.py
if errorlevel 1 (
    echo.
    echo Backend exited with an error. Running fallback via python module...
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
)
pause

