@echo off
title PaperTrail - Launch All
echo ========================================================
echo   Starting PaperTrail (Backend + Frontend)
echo ========================================================
echo.
echo [1/2] Launching Backend on http://localhost:8000 ...
start "PaperTrail Backend" cmd /k "cd /d "%~dp0backend" && python main.py"

echo [2/2] Launching Frontend on http://localhost:5173 ...
start "PaperTrail Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================================
echo   PaperTrail is running!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   Docs:     http://localhost:8000/docs
echo ========================================================
echo.
pause
