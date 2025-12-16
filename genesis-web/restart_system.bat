@echo off
echo ===================================================
echo   GENESIS ARCHITECT - EMERGENCY RESTART SYSTEM
echo ===================================================
echo.
echo [1/3] Stopping Zombie Processes...
powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"
powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"

echo.
echo [2/3] Starting Backend (Port 8000)...
cd ..\app
start /MIN "Genesis Backend" cmd /k "uvicorn app.main:app --reload --port 8000"

echo.
echo [3/3] Starting Frontend (Port 5173)...
cd ..\genesis-web
start /MIN "Genesis Frontend" cmd /k "npm run dev"

echo.
echo ===================================================
echo   SYSTEM REBOOTED. OPENING BROWSER IN 5 SECONDS...
echo ===================================================
timeout /t 5 >nul
start http://localhost:5173
exit
