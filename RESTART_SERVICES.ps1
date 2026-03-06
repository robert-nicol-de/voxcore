# VoxQuery Services Restart Script
# Automatically stops and restarts all services

Write-Host "VoxQuery Services Restart Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$rootDir = Get-Location

Write-Host "Root Directory: $rootDir" -ForegroundColor Yellow
Write-Host ""

# Kill any existing processes on ports 3000 (frontend) and 8000 (backend)
Write-Host "Stopping existing services..." -ForegroundColor Yellow

# Stop frontend (port 3000)
$frontendProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*npm*dev*" }
if ($frontendProcess) {
    Write-Host "  Stopping frontend (npm run dev)..." -ForegroundColor Green
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Stop backend (port 8000)
$backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
if ($backendProcess) {
    Write-Host "  Stopping backend (python main.py)..." -ForegroundColor Green
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "All services stopped" -ForegroundColor Green
Write-Host ""

# Start backend first
Write-Host "Starting Backend API (port 8000)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "backend/main.py" -WorkingDirectory $rootDir
Write-Host "  Backend started" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Frontend (port 3000)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "$rootDir\frontend"
Write-Host "  Frontend started" -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "All services restarted successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Tip: Hard refresh browser with Ctrl+Shift+R to clear cache" -ForegroundColor Magenta
Write-Host ""
