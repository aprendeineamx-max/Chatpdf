@echo off
cd /d "%~dp0"

echo ==================================================
echo      RESTARTING PDF CORTEX SYSTEM (Full Reset)
echo ==================================================

echo [1/3] Closing existing processes (Port cleanup)...
:: Kill Node (Frontend)
taskkill /F /IM node.exe >nul 2>&1
:: Kill Python (Backend/Uvicorn) - Warning: This kills all python processes
taskkill /F /IM python.exe >nul 2>&1

echo Waiting for ports to free up...
timeout /t 3 >nul

echo [2/3] Launching Backend (Uvicorn)...
:: Opens in a new window titled "PDF Cortex Backend"
start "PDF Cortex Backend" cmd /k "call venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [3/3] Launching Frontend (Vite)...
cd genesis-web
:: Opens in a new window titled "Genesis Web Frontend"
start "Genesis Web Frontend" cmd /k "npm run dev"

echo ==================================================
echo      ✅ SYSTEM RESTART INITIATED
echo      Please check the two new terminal windows.
echo ==================================================
pause
