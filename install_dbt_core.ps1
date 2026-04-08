# DBT Core Installation Script for Windows
# Installs dbt Core to C:\dbt-core

$InstallPath = "C:\dbt-core"
$PythonVersion = "3.11"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DBT Core Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$PythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python found: $PythonCheck" -ForegroundColor Green
Write-Host ""

# Step 2: Create installation directory
Write-Host "[2/5] Creating installation directory..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Write-Host "Directory already exists: $InstallPath" -ForegroundColor Cyan
} else {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "✓ Created directory: $InstallPath" -ForegroundColor Green
}
Write-Host ""

# Step 3: Create virtual environment
Write-Host "[3/5] Creating Python virtual environment..." -ForegroundColor Yellow
$VenvPath = "$InstallPath\venv"
if (Test-Path $VenvPath) {
    Write-Host "Virtual environment already exists" -ForegroundColor Cyan
} else {
    python -m venv $VenvPath
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 4: Activate virtual environment and install dbt
Write-Host "[4/5] Installing dbt Core..." -ForegroundColor Yellow
$ActivateScript = "$VenvPath\Scripts\Activate.ps1"

# Run activation and installation in same process
& $ActivateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip first
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: pip upgrade had issues, continuing anyway..." -ForegroundColor Yellow
}

# Install dbt-core
pip install dbt-core
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ dbt Core installed successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dbt Core" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Verify installation
Write-Host "[5/5] Verifying installation..." -ForegroundColor Yellow
$DbtVersion = dbt --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "dbt version info:" -ForegroundColor Cyan
    Write-Host $DbtVersion -ForegroundColor White
} else {
    Write-Host "WARNING: Could not verify dbt installation" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation Location: $InstallPath" -ForegroundColor Cyan
Write-Host "Virtual Environment: $VenvPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use dbt in the future, activate the virtual environment:" -ForegroundColor Yellow
Write-Host "  $ActivateScript" -ForegroundColor White
Write-Host ""
Write-Host "Or run dbt directly:" -ForegroundColor Yellow
Write-Host "  dbt --version" -ForegroundColor White
Write-Host ""
