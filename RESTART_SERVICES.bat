@echo off
REM VoxQuery Services Restart Script (Batch version)
REM Automatically stops and restarts all services

echo.
echo ========================================
echo   VoxQuery Services Restart Script
echo ========================================
echo.

REM Kill any existing processes on ports 3000 and 8000
echo Stopping existing services...

REM Stop Node processes (frontend)
taskkill /F /IM node.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Frontend stopped
) else (
    echo   [INFO] No frontend process found
)

REM Stop Python processes (backend)
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Backend stopped
) else (
    echo   [INFO] No backend process found
)

timeout /t 2 /nobreak >nul

echo.
echo Starting services...
echo.

REM Start backend
echo Starting Backend API (port 8000)...
start "VoxQuery Backend" python backend/main.py
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting Frontend (port 3000)...
cd frontend
start "VoxQuery Frontend" npm run dev
cd ..

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All services restarted successfully!
echo ========================================
echo.
echo Service URLs:
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo.
echo Tip: Hard refresh browser with Ctrl+Shift+R
echo.
pause
