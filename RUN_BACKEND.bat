@echo off
TITLE PDF Cortex Backend
COLOR 0A

echo ==================================================
echo      GENESIS ARCHITECT - NEURAL BACKEND LAUNCHER
echo ==================================================
echo.

echo [1/3] Checking for existing process on Port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo [!] Killing old process PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo [2/3] Cleaning up temporary files...
if exist "data\temp" del /q "data\temp\*"

echo [3/3] Igniting Neural Core...
echo.
echo ⚡ SYSTEM READY. LISTENING ON PORT 8000.
echo ⚡ MODE: LOCAL / CLOUD (Controlled by .env)
echo.

python -m app.main

pause
