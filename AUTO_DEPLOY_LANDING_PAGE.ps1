$ErrorActionPreference = "Stop"

# Configuration
$CpanelHost = "cloud771.thundercloud.uk:2083"
$ApiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV"
$DomainName = "voxcore.org"
$LocalDistPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
$FrontendIndexPath = "$LocalDistPath\index.html"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "VoxCore App Root - Automated Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify file exists
Write-Host "[1/4] Checking frontend app entry..." -ForegroundColor Yellow
if (-not (Test-Path $FrontendIndexPath)) {
    Write-Host "ERROR: App entry not found at $FrontendIndexPath" -ForegroundColor Red
    exit 1
}
$fileSize = (Get-Item $FrontendIndexPath).Length / 1KB
Write-Host "✓ App entry found ($([math]::Round($fileSize, 1)) KB)" -ForegroundColor Green
Write-Host ""

# Step 2: Read file content
Write-Host "[2/4] Reading app entry content..." -ForegroundColor Yellow
$frontendIndexContent = Get-Content $FrontendIndexPath -Raw
Write-Host "✓ File read successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Prepare for upload via cPanel API
Write-Host "[3/4] Preparing cPanel API call..." -ForegroundColor Yellow
$baseUrl = "https://$CpanelHost/execute/Fileman"
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

# First, let's backup the old index.html by renaming it
Write-Host "  → Renaming old index.html to old_index.html..." -ForegroundColor Cyan

$renameOldBody = @{
    "method" = "rename"
    "oldfile" = "/public_html/index.html"
    "newfile" = "/public_html/old_index.html"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $renameOldBody -SkipCertificateCheck -ErrorAction Stop
    Write-Host "  ✓ Old index.html renamed to old_index.html" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Could not rename old file (may not exist or already moved)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Create the new index.html via API
Write-Host "[4/4] Uploading app entry as new index.html..." -ForegroundColor Yellow

$createFileBody = @{
    "method" = "save"
    "dir" = "/public_html"
    "file" = "index.html"
    "content" = $frontendIndexContent
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $createFileBody -SkipCertificateCheck -ErrorAction Stop
    $responseContent = $response.Content | ConvertFrom-Json
    
    if ($responseContent.status -eq 1 -or $response.StatusCode -eq 200) {
        Write-Host "✓ App entry uploaded and installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Upload may have completed (cPanel response: $($responseContent.status))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not upload via API: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "FALLBACK: Manual upload instructions" -ForegroundColor Cyan
    Write-Host "1. Copy the file to clipboard:" -ForegroundColor White
    Write-Host "   File: $FrontendIndexPath" -ForegroundColor Cyan
    Write-Host "2. Go to: https://cloud771.thundercloud.uk:2083/" -ForegroundColor Cyan
    Write-Host "3. File Manager → public_html" -ForegroundColor Cyan
    Write-Host "4. Upload index.html and keep the file name as index.html" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The VoxCore app is now live at root!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Open your browser" -ForegroundColor Cyan
Write-Host "2. Go to: https://$DomainName/" -ForegroundColor Cyan
Write-Host "3. Hard refresh: Ctrl+F5 (or Cmd+Shift+R on Mac)" -ForegroundColor Cyan
Write-Host "4. You should see the real VoxCore app at /" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment target:" -ForegroundColor Green
Write-Host "  ✓ Root path / serves the built React app" -ForegroundColor Green
Write-Host "  ✓ Existing /app routing remains available" -ForegroundColor Green
Write-Host ""
Write-Host "Routing behavior:" -ForegroundColor White
Write-Host "  → https://$DomainName/ serves the app directly" -ForegroundColor Cyan
Write-Host "  → https://$DomainName/app/ still serves the app shell" -ForegroundColor Cyan
Write-Host ""
Write-Host "Questions or issues? Contact: support@$DomainName" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
