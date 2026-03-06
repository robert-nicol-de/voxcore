# Automated Python 3.12 Installation Script
# This script will:
# 1. Download Python 3.12
# 2. Uninstall Python 3.14
# 3. Install Python 3.12
# 4. Reinstall all VoxQuery packages

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoxQuery - Python 3.12 Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download Python 3.12
Write-Host "[1/4] Downloading Python 3.12..." -ForegroundColor Green
$pythonUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
$installerPath = "$env:TEMP\python-3.12.7-amd64.exe"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Host "Downloading from: $pythonUrl"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "OK - Download complete!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR - Download failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Uninstall Python 3.14
Write-Host ""
Write-Host "[2/4] Uninstalling Python 3.14..." -ForegroundColor Green
try {
    $python314 = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Python 3.14*" }
    if ($python314) {
        Write-Host "Found Python 3.14, uninstalling..."
        $python314.Uninstall() | Out-Null
        Start-Sleep -Seconds 5
        Write-Host "OK - Python 3.14 uninstalled!" -ForegroundColor Green
    }
    else {
        Write-Host "Python 3.14 not found (already uninstalled)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Warning: Could not uninstall Python 3.14: $_" -ForegroundColor Yellow
}

# Step 3: Install Python 3.12
Write-Host ""
Write-Host "[3/4] Installing Python 3.12..." -ForegroundColor Green
Write-Host "This may take 2-3 minutes..."

$arguments = @(
    "/quiet",
    "InstallAllUsers=1",
    "PrependPath=1",
    "Include_test=0"
)

& $installerPath $arguments
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "OK - Python 3.12 installed successfully!" -ForegroundColor Green
    Start-Sleep -Seconds 3
}
else {
    Write-Host "ERROR - Installation failed with exit code: $exitCode" -ForegroundColor Red
    exit 1
}

# Step 4: Reinstall packages
Write-Host ""
Write-Host "[4/4] Reinstalling VoxQuery packages..." -ForegroundColor Green
Write-Host "This may take 5-10 minutes..."

# Verify Python 3.12 is available
$python312 = Get-Command python -ErrorAction SilentlyContinue
if ($python312) {
    Write-Host "Python found at: $($python312.Source)"
    & python --version
}
else {
    Write-Host "Warning: Python not found in PATH, trying full path..." -ForegroundColor Yellow
    $python312Path = "C:\Program Files\Python312\python.exe"
    if (Test-Path $python312Path) {
        Write-Host "Found Python at: $python312Path"
        & $python312Path --version
    }
    else {
        Write-Host "ERROR - Python 3.12 not found!" -ForegroundColor Red
        exit 1
    }
}

# Upgrade pip
Write-Host "Upgrading pip..."
& python -m pip install --upgrade pip --quiet

# Install requirements
Write-Host "Installing VoxQuery requirements..."
& python -m pip install -r backend/requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - All packages installed successfully!" -ForegroundColor Green
}
else {
    Write-Host "ERROR - Package installation failed" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up..."
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OK - Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now use Snowflake connectivity!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal/PowerShell" -ForegroundColor Yellow
Write-Host "2. Run: python backend/main.py" -ForegroundColor Yellow
Write-Host "3. Connect to Snowflake in VoxQuery" -ForegroundColor Yellow
Write-Host ""
