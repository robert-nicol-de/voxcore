@echo off
REM Minimal Backend Startup - No dependencies needed for testing

echo ========================================
echo   VoxQuery Backend - Installation
echo ========================================
echo.
echo Installing Python dependencies...
echo This may take a few minutes on first run...
echo.

cd /d "%~dp0%backend"

REM Install requirements
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Starting VoxQuery Backend...
echo.
echo API:  http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python main_simple.py

if errorlevel 1 (
    echo.
    echo ERROR: Backend failed to start
    pause
)
