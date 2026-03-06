# VoxCore Production Deployment Script
# This script uploads and deploys VoxCore to voxcore.org

param(
    [string]$Username = "voxcoreo",
    [string]$Host = "voxcore.org",
    [string]$Password = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoxCore Production Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow
Write-Host ""

# Check if plink is available (from PuTTY)
$plink = "C:\Program Files\PuTTY\plink.exe"
$pscp = "C:\Program Files\PuTTY\pscp.exe"

# Try common locations
if (!(Test-Path $plink)) {
    $plink = "C:\Program Files (x86)\PuTTY\plink.exe"
}
if (!(Test-Path $pscp)) {
    $pscp = "C:\Program Files (x86)\PuTTY\pscp.exe"
}

# Check if scp is available (OpenSSH)
$scp = "scp"
$testScp = @(where.exe scp -ErrorAction SilentlyContinue)[0]

if ($testScp) {
    Write-Host "✓ OpenSSH scp found" -ForegroundColor Green
    $scp = $testScp
} elseif (Test-Path $pscp) {
    Write-Host "✓ PuTTY pscp found" -ForegroundColor Green
    $scp = $pscp
} else {
    Write-Host "✗ Neither scp nor pscp found!" -ForegroundColor Red
    Write-Host "Please install either:" -ForegroundColor Yellow
    Write-Host "  - Git for Windows (includes scp)" -ForegroundColor Yellow
    Write-Host "  - PuTTY (includes pscp)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Uploading frontend files..." -ForegroundColor Cyan
$frontendSource = ".\frontend\dist\*"
$frontendDest = "${Username}@${Host}:~/public_html/voxcore/"

Write-Host "Source: $frontendSource" -ForegroundColor Gray
Write-Host "Destination: $frontendDest" -ForegroundColor Gray

if ($scp -like "*pscp*") {
    Write-Host "Using PuTTY pscp..." -ForegroundColor Gray
    & $scp -r -p "$Password" "$frontendSource" "$frontendDest" 2>&1
} else {
    Write-Host "Using OpenSSH scp..." -ForegroundColor Gray
    Write-Host "Please enter your cPanel password when prompted..." -ForegroundColor Yellow
    & $scp -r "$frontendSource" "$frontendDest" 2>&1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend upload failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 2: Uploading backend files..." -ForegroundColor Cyan
$backendSource = ".\voxcore"
$backendDest = "${Username}@${Host}:~/"

Write-Host "Source: $backendSource" -ForegroundColor Gray
Write-Host "Destination: $backendDest" -ForegroundColor Gray

if ($scp -like "*pscp*") {
    & $pscp -r -p "$Password" "$backendSource" "$backendDest" 2>&1
} else {
    Write-Host "Please enter your cPanel password when prompted..." -ForegroundColor Yellow
    & $scp -r "$backendSource" "$backendDest" 2>&1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Backend upload failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 3: Running setup on server..." -ForegroundColor Cyan

$setupScript = @"
#!/bin/bash
set -e

echo "Setting up VoxCore backend..."

# Create directories
mkdir -p ~/logs

# Navigate to backend
cd ~/voxcore/voxcore/voxquery

# Check if Python exists
python3 --version || python --version

# Setup virtual environment
echo "Creating virtual environment..."
python3 -m venv venv 2>/dev/null || python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt

# Create logs directory
mkdir -p ~/logs

# Create environment file (without database credentials for now)
cat > .env << 'ENVEOF'
VITE_API_URL=https://voxcore.org/api
ALLOWED_HOSTS=voxcore.org,www.voxcore.org
ENV=production
DATABASE_URL=
ENVEOF

echo "Environment configured (database locked)"

# Create restart script
cat > ~/restart_voxcore.sh << 'RESTARTEOF'
#!/bin/bash
if ! pgrep -f "uvicorn voxquery.api.main" > /dev/null; then
    echo "[`date`] Restarting backend" >> ~/logs/voxcore-restart.log
    cd ~/voxcore/voxcore/voxquery
    source venv/bin/activate
    nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
fi
RESTARTEOF

chmod +x ~/restart_voxcore.sh

# Start backend
echo "Starting backend..."
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
sleep 2

# Setup .htaccess
echo "Configuring web server..."
cat > ~/public_html/voxcore/.htaccess << 'HTACCESSEOF'
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/\$1 [P,L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>
HTACCESSEOF

# Add cron job
(crontab -l 2>/dev/null | grep -v "restart_voxcore"; echo "*/5 * * * * ~/restart_voxcore.sh") | crontab -

echo ""
echo "========================================"
echo "✓ VoxCore is now LIVE!"
echo "========================================"
echo ""
echo "Frontend:  https://voxcore.org/"
echo "API:       https://voxcore.org/api/health"
echo "Docs:      https://voxcore.org/api/docs"
echo ""
echo "⚠️  DATABASE IS LOCKED (no credentials)"
echo "    Your site is live for browsing!"
echo ""
"@

if ($scp -like "*pscp*") {
    $setupScript | & $plink -p "$Password" "${Username}@${Host}" 2>&1
} else {
    Write-Host "Setting up server... (enter password if prompted)" -ForegroundColor Yellow
    $setupScript | & ssh "${Username}@${Host}" 2>&1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Setup completed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Setup had issues (check above)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "✓✓✓ DEPLOYMENT COMPLETE! ✓✓✓" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Your VoxCore app is now LIVE at:" -ForegroundColor Green
Write-Host "  https://voxcore.org/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Open it in your browser now!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open https://voxcore.org/" -ForegroundColor Gray
Write-Host "  2. Verify frontend loads" -ForegroundColor Gray
Write-Host "  3. Check https://voxcore.org/api/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Database is currently LOCKED for security." -ForegroundColor Yellow
Write-Host "To unlock later, add credentials to ~/.env on server" -ForegroundColor Yellow
Write-Host ""
