@echo off
REM VoxQuery - Unified Startup Script
REM Starts both backend and frontend together

echo.
echo ================================================================================
echo                    VOXQUERY - STARTING FULL STACK
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and add it to your PATH
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version

echo ✓ Node.js found: 
node --version

echo.
echo Starting Backend (Python)...
echo.

REM Start backend in a new window (use uvicorn to serve the FastAPI app)
start "VoxQuery Backend" cmd /k "cd voxcore\voxquery && python -m uvicorn voxquery.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 3 /nobreak

echo.
echo Starting Frontend (React)...
echo.

REM Start frontend in a new window
start "VoxQuery Frontend" cmd /k "cd frontend && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

echo.
echo ================================================================================
echo                    VOXQUERY STARTED SUCCESSFULLY
echo ================================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to continue...
pause

echo.
echo To stop the application:
echo 1. Close the Backend window (VoxQuery Backend)
echo 2. Close the Frontend window (VoxQuery Frontend)
echo.
