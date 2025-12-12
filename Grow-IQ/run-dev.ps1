# Glow-IQ Development Server Startup Script for PowerShell
# This script runs both frontend and backend in development mode

Write-Host "[GLOW-IQ] Starting Development Environment..." -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed. Please install Python 3.11+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[INFO] Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "[INFO] Activating Python virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Install Python dependencies
Write-Host "[INFO] Installing Python dependencies..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
if (-not (Test-Path "fronted\node_modules")) {
    Write-Host "[INFO] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location "fronted"
    npm install
    Set-Location ".."
}

# Set environment variables
$env:DEBUG = "true"
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "sqlite:///./dashboard.db"
$env:SECRET_KEY = "dev-secret-key-change-in-production"
$env:HOST = "0.0.0.0"
$env:PORT = "8000"

Write-Host "[INFO] Starting Backend Server..." -ForegroundColor Green
Write-Host "[INFO] Backend URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "[INFO] API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""

# Start backend in background
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "venv\Scripts\Activate.ps1"
    python start.py
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "[INFO] Starting Frontend Server..." -ForegroundColor Green
Write-Host "[INFO] Frontend URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Set-Location "fronted"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
}
Set-Location ".."

Write-Host ""
Write-Host "[SUCCESS] Glow-IQ is now running!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Yellow

try {
    # Wait for user to stop
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Cleanup
    Write-Host "[INFO] Stopping servers..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "[INFO] All servers stopped. Goodbye!" -ForegroundColor Green
}
