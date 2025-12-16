@echo off
setlocal
echo ===================================================
echo   GENESIS ARCHITECT - EMERGENCY RESTART SYSTEM
echo ===================================================

:: Ensure we are in the script directory
cd /d "%~dp0"

echo.
echo [1/3] Stopping Zombie Processes (Ignorable if none found)...
powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"
powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"

echo.
echo [2/3] Starting Backend (Port 8000)...
:: Go up to pdf-cortex root from genesis-web (..), then into app? No, app is sibling of genesis-web.
:: Script is in: ...\pdf-cortex\genesis-web
:: App is in:    ...\pdf-cortex\app
:: Venv is in:   ...\Universal Pdf\venv  (Two levels up from script is pdf-cortex, three levels up is Universal Pdf?)
:: user info: C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\genesis-web
:: So:
:: ".." -> pdf-cortex
:: "..\.." -> Universal Pdf
:: "..\..\venv" -> Universal Pdf\venv

cd ..\app
start "Genesis Backend" cmd /k "..\..\venv\Scripts\activate & uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

echo.
echo [3/3] Starting Frontend (Port 5173)...
cd ..\genesis-web
start "Genesis Frontend" cmd /k "npm run dev"

echo.
echo ===================================================
echo   SYSTEM REBOOTED. OPENING BROWSER IN 5 SECONDS...
echo ===================================================
timeout /t 5
start http://localhost:5173
exit
