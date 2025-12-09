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
