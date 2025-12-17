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
