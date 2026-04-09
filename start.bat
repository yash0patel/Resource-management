@echo off
echo.
echo ========================================
echo Inventory Management System - React+FastAPI
echo ========================================
echo.
echo Starting backend and frontend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from nodejs.org
    pause
    exit /b 1
)

REM Install Python dependencies if needed
echo.
echo Checking Python dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing Python dependencies
        pause
        exit /b 1
    )
)

REM Install Node dependencies if needed
echo.
echo Checking Node dependencies...
if not exist "frontend\node_modules" (
    echo Installing Node dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo Error installing Node dependencies
        pause
        exit /b 1
    )
    cd ..
)

REM Start backend
echo.
echo Starting FastAPI backend on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
start cmd /k python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo.
echo Starting React frontend on http://localhost:3000
echo.
cd frontend
call npm run dev
