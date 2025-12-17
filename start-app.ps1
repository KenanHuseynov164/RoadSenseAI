# --------------------------------------------
# START ROADSENSEAI BACKEND + FRONTEND
# --------------------------------------------

# Set API KEY globally for all child PowerShell processes
$env:OPENAI_API_KEY = "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"

Write-Host "Starting RoadSenseAI..." -ForegroundColor Cyan

# -------- BACKEND --------
Write-Host "`n[1/2] Activating backend and starting FastAPI..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command",
@"
# pass API key inside child shell
\$env:OPENAI_API_KEY = '$env:OPENAI_API_KEY'

cd '$PSScriptRoot\roadsense-backend'
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
"@

# -------- FRONTEND --------
Write-Host "`n[2/2] Starting React frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command",
@"
cd '$PSScriptRoot\roadsense-frontend'
npm run dev
"@

Write-Host "`nRoadSenseAI is running!" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:5173"
