@echo off
REM DBT Core Installation Script for Windows
REM Installs dbt Core to C:\dbt-core

setlocal enabledelayedexpansion

set INSTALL_PATH=C:\dbt-core
set VENV_PATH=%INSTALL_PATH%\venv

echo.
echo ========================================
echo DBT Core Installation Script
echo ========================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python found: %PYTHON_VERSION%
echo.

REM Step 2: Create directory
echo [2/5] Creating installation directory...
if exist "%INSTALL_PATH%" (
    echo Directory already exists: %INSTALL_PATH%
) else (
    mkdir "%INSTALL_PATH%"
    echo ✓ Created directory: %INSTALL_PATH%
)
echo.

REM Step 3: Create virtual environment
echo [3/5] Creating Python virtual environment...
if exist "%VENV_PATH%" (
    echo Virtual environment already exists
) else (
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
)
echo.

REM Step 4: Install dbt
echo [4/5] Installing dbt Core...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

python -m pip install --upgrade pip >nul 2>&1
pip install dbt-core
if errorlevel 1 (
    echo ERROR: Failed to install dbt Core
    pause
    exit /b 1
)
echo ✓ dbt Core installed successfully
echo.

REM Step 5: Verify
echo [5/5] Verifying installation...
dbt --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not verify dbt installation
) else (
    echo ✓ Installation verified!
    echo.
    echo dbt version info:
    dbt --version
)
echo.

REM Summary
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installation Location: %INSTALL_PATH%
echo Virtual Environment: %VENV_PATH%
echo.
echo To use dbt in the future, activate the virtual environment:
echo   %VENV_PATH%\Scripts\activate.bat
echo.
echo Or run dbt directly:
echo   dbt --version
echo.
pause
