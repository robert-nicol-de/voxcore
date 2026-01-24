@echo off
REM VoxQuery Backend Startup
REM Simple batch file to start the backend API

cd /d "%~dp0"
echo Starting VoxQuery Backend...
echo.

REM Navigate to backend folder
cd backend

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt -q

echo.
echo ========================================
echo   VoxQuery Backend is Starting
echo ========================================
echo.
echo API will be available at: http://localhost:8000
echo Docs available at:        http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the backend
python main.py

pause
