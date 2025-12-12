# ===============================
# FraudNET Dashboard Runner Script
# ===============================

Write-Host "🎨 Starting FraudNET Dashboard..." -ForegroundColor Cyan

# Go to dashboard folder
Set-Location -Path "E:\Fraudnet\fraudnet-dashboard"

# Start Vite dev server
Write-Host "🚀 Opening dashboard on http://localhost:5173 ..." -ForegroundColor Green
npm run dev
