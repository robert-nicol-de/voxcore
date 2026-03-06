# VoxQuery - Unified Startup Script (PowerShell)
# Starts both backend and frontend together

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    VOXQUERY - STARTING FULL STACK" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ and add it to your PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and add it to your PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting Backend (Python)..." -ForegroundColor Yellow
Write-Host ""

# Start backend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python backend/main.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend (React)..." -ForegroundColor Yellow
Write-Host ""

# Start frontend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

# Wait for frontend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                    VOXQUERY STARTED SUCCESSFULLY" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the application:" -ForegroundColor Yellow
Write-Host "1. Close the Backend window (VoxQuery Backend)" -ForegroundColor Yellow
Write-Host "2. Close the Frontend window (VoxQuery Frontend)" -ForegroundColor Yellow
Write-Host ""
