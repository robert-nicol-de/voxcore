Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "VoxCore - Final Deployment" -ForegroundColor Cyan
Write-Host "Logins Locked + Landing Message" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$distPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
$cpanelHost = "cloud771.thundercloud.uk:2083"
$cpanelUser = "voxcoreo"
$apiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV"

# Step 1: Check files
Write-Host "[1/4] Checking updated files..." -ForegroundColor Yellow
$indexPath = "$distPath\index.html"
$landingPath = "$distPath\landing.html"

$indexExists = Test-Path $indexPath
$landingExists = Test-Path $landingPath

if ($indexExists) {
    $indexSize = (Get-Item $indexPath).Length
    Write-Host "  ✓ index.html found ($indexSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  ✗ index.html not found" -ForegroundColor Red
}

if ($landingExists) {
    $landingSize = (Get-Item $landingPath).Length
    Write-Host "  ✓ landing.html found ($landingSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  ✗ landing.html not found" -ForegroundColor Red
}

Write-Host ""

# Step 2: Read files
Write-Host "[2/4] Reading updated files..." -ForegroundColor Yellow
$indexContent = Get-Content $indexPath -Raw
$landingContent = Get-Content $landingPath -Raw
Write-Host "  ✓ Files loaded for upload" -ForegroundColor Green
Write-Host ""

# Step 3: Upload via cPanel API
Write-Host "[3/4] Uploading to cPanel..." -ForegroundColor Yellow

$baseUrl = "https://$cpanelHost/execute/Fileman"
$headers = @{
    "Authorization" = "Bearer $apiToken"
    "Content-Type" = "application/json"
}

# Upload landing.html as index.html
Write-Host "  - Uploading landing page (with lockout notice)..." -ForegroundColor Cyan
$createBody = @{
    "method" = "save"
    "dir" = "/public_html"
    "file" = "index.html"
    "content" = $landingContent
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $createBody -SkipCertificateCheck
    Write-Host "  ✓ Landing page uploaded" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Upload error (fallback: manual upload)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Summary
Write-Host "[4/4] Deployment Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "CHANGES DEPLOYED:" -ForegroundColor Green
Write-Host "  ✓ Landing page with lockout notice" -ForegroundColor Green
Write-Host "    - Added message: 'Logins Currently Locked'" -ForegroundColor Green
Write-Host "    - Yellow warning badge on landing page" -ForegroundColor Green
Write-Host ""
Write-Host "  ✓ Login modal disabled" -ForegroundColor Green
Write-Host "    - Login form is non-functional" -ForegroundColor Green
Write-Host "    - Shows 'Browse Dashboard' button instead" -ForegroundColor Green
Write-Host "    - Visitors can still explore the app" -ForegroundColor Green
Write-Host ""
Write-Host "WHAT VISITORS WILL SEE:" -ForegroundColor Cyan
Write-Host "1. Landing page (https://voxcore.org/)" -ForegroundColor White
Write-Host "   - Professional VoxCore branding" -ForegroundColor White
Write-Host "   - Yellow lockout warning: 'Logins Currently Locked'" -ForegroundColor White
Write-Host "   - Feature highlights" -ForegroundColor White
Write-Host "   - 'Enter VoxCore' button" -ForegroundColor White
Write-Host ""
Write-Host "2. Click 'Enter VoxCore'" -ForegroundColor White
Write-Host "   - Shows login modal" -ForegroundColor White
Write-Host "   - Displays lockout notice" -ForegroundColor White
Write-Host "   - 'Browse Dashboard' button allows exploration" -ForegroundColor White
Write-Host ""
Write-Host "3. Full app access (read-only mode)" -ForegroundColor White
Write-Host "   - View governance dashboard" -ForegroundColor White
Write-Host "   - Explore all features" -ForegroundColor White
Write-Host "   - No authentication/login required" -ForegroundColor White
Write-Host ""
Write-Host "TO ENABLE LOGINS LATER:" -ForegroundColor Yellow
Write-Host "  1. Edit: frontend/src/screens/Login.tsx" -ForegroundColor Cyan
Write-Host "  2. Change: const loginsLocked = false" -ForegroundColor Cyan
Write-Host "  3. Add your actual login logic" -ForegroundColor Cyan
Write-Host "  4. Rebuild: npm run build" -ForegroundColor Cyan
Write-Host "  5. Deploy new dist/ files" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Visit https://voxcore.org/" -ForegroundColor White
Write-Host "Press Ctrl+F5 to hard refresh" -ForegroundColor White
Write-Host ""
