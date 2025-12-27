# ===============================
# FraudNET Backend Runner Script
# ===============================

Write-Host "🔧 Starting FraudNET Backend..." -ForegroundColor Cyan

# Go to backend folder
Set-Location -Path "E:\Fraudnet\backend"

# Activate virtual environment
Write-Host "🟢 Activating virtual environment..."
& "E:\Fraudnet\backend\venv\Scripts\Activate.ps1"

# Start Uvicorn
Write-Host "🚀 Starting Uvicorn server on http://127.0.0.1:8000 ..." -ForegroundColor Green
uvicorn main:app --reload
