# Inventory Management System - Quick Start Script
# Save as: start.ps1
# Run with: powershell -ExecutionPolicy Bypass .\start.ps1

Clear-Host
Write-Host ""
Write-Host "========================================"
Write-Host "Inventory Management System - React+FastAPI"
Write-Host "========================================"
Write-Host ""
Write-Host "Starting backend and frontend..."
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Install Python dependencies if needed
Write-Host ""
Write-Host "Checking Python dependencies..."
try {
    pip show fastapi >$null 2>&1
    Write-Host "✓ Python dependencies already installed" -ForegroundColor Green
} catch {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Error installing Python dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
}

# Install Node dependencies if needed
Write-Host ""
Write-Host "Checking Node dependencies..."
if (-Not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Error installing Node dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
    Set-Location ..
    Write-Host "✓ Node dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Node dependencies already installed" -ForegroundColor Green
}

# Start backend
Write-Host ""
Write-Host "Starting FastAPI backend..." -ForegroundColor Cyan
Write-Host "Backend URL: http://localhost:8000"
Write-Host "API Documentation: http://localhost:8000/docs"
Write-Host ""

$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000" -PassThru
Write-Host "Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host ""
Write-Host "Starting React frontend..." -ForegroundColor Cyan
Write-Host "Frontend URL: http://localhost:3000"
Write-Host ""

Set-Location frontend
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -PassThru
Write-Host "Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "========================================"
Write-Host "Both servers are now running!"
Write-Host "========================================"
Write-Host ""
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend: http://localhost:8000"
Write-Host "API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop either server"
Write-Host ""

# Keep this window open
Read-Host "Press Enter to continue..."
