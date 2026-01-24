@echo off
REM VoxQuery Launcher - Just double-click this file!

title VoxQuery Launcher
color 0A
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   VoxQuery - Natural Language SQL
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if Python is installed
echo Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
cd backend
pip show langchain >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
cd ..

REM Check if Node.js is installed
echo Checking Node.js...
node --version 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: Node.js not found!
    echo Install from https://nodejs.org
    echo.
    pause
)

REM Run the launcher
echo.
echo Launching VoxQuery...
echo.
python launcher.py

if errorlevel 1 (
    echo.
    echo ERROR occurred. Press any key to see details...
    pause
)
