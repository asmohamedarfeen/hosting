@echo off
REM Glow-IQ Development Server Startup Script for Windows
REM This script runs both frontend and backend in development mode

echo [GLOW-IQ] Starting Development Environment...
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating Python virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install frontend dependencies
if not exist "fronted\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd fronted
    npm install
    cd ..
)

REM Set environment variables
set DEBUG=true
set ENVIRONMENT=development
set DATABASE_URL=sqlite:///./dashboard.db
set SECRET_KEY=dev-secret-key-change-in-production
set HOST=0.0.0.0
set PORT=8000

echo [INFO] Starting Backend Server...
echo [INFO] Backend URL: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/docs
echo [INFO] Health Check: http://localhost:8000/health
echo.

REM Start backend in background
start "Glow-IQ Backend" cmd /k "python start.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo [INFO] Starting Frontend Server...
echo [INFO] Frontend URL: http://localhost:5173
echo.

cd fronted
start "Glow-IQ Frontend" cmd /k "npm run dev"
cd ..

echo.
echo [SUCCESS] Glow-IQ is now running!
echo ================================================
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press any key to stop all servers...
pause >nul

REM Kill background processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo [INFO] All servers stopped. Goodbye!
pause
