@echo off
title NEXORA Launcher
echo ========================================================
echo               NEXORA Tourism AI Launcher
echo ========================================================
echo.
echo [1/2] Starting Backend Server (FastAPI on Port 8000)...
start "NEXORA Backend" cmd /k "python run_backend.py"

echo [2/2] Starting Frontend Server (Vite on Port 3000)...
start "NEXORA Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All servers started!
echo - Frontend UI:  http://127.0.0.1:3000
echo - Backend Docs: http://127.0.0.1:8000/docs
echo ========================================================

