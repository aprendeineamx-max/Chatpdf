
# Kill existing processes on ports 5173 and 8000 to free them
Write-Host "Killing zombie processes..."
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

Write-Host "Starting Backend..."
Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload --port 8000" -WorkingDirectory "..\app" -WindowStyle Minimized

Write-Host "Starting Frontend..."
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "."
