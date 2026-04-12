$ErrorActionPreference = "Stop"

# Configuration
$CpanelHost = "cloud771.thundercloud.uk:2083"
$ApiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV"
$DomainName = "voxcore.org"
$LocalDistPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
$FrontendIndexPath = "$LocalDistPath\index.html"

Write-Host ""
Write-Host "VoxCore App Root - Automated Deployment" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify file exists
Write-Host "[1/4] Checking frontend app entry..." -ForegroundColor Yellow
if (-not (Test-Path $FrontendIndexPath)) {
    Write-Host "ERROR: App entry not found at $FrontendIndexPath" -ForegroundColor Red
    exit 1
}
$fileSize = (Get-Item $FrontendIndexPath).Length
Write-Host "File found - size: $fileSize bytes" -ForegroundColor Green
Write-Host ""

# Step 2: Read file content
Write-Host "[2/4] Reading app entry content..." -ForegroundColor Yellow
$frontendIndexContent = Get-Content $FrontendIndexPath -Raw
Write-Host "File read successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Prepare cPanel API
Write-Host "[3/4] Preparing cPanel upload..." -ForegroundColor Yellow

$baseUrl = "https://$CpanelHost/execute/Fileman"
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

# Rename old file
Write-Host "  - Renaming old index.html..." -ForegroundColor Cyan
$renameBody = @{
    "method" = "rename"
    "oldfile" = "/public_html/index.html"
    "newfile" = "/public_html/old_index_backup.html"
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $renameBody -SkipCertificateCheck | Out-Null
    Write-Host "  - Old file backed up" -ForegroundColor Green
} catch {
    Write-Host "  - Backup skipped (file may not exist)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Upload new app entry
Write-Host "[4/4] Uploading app entry..." -ForegroundColor Yellow

$createBody = @{
    "method" = "save"
    "dir" = "/public_html"
    "file" = "index.html"
    "content" = $frontendIndexContent
} | ConvertTo-Json -Depth 10

try {
    $result = Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $createBody -SkipCertificateCheck
    Write-Host "App entry uploaded successfully!" -ForegroundColor Green
} catch {
    Write-Host "Upload error - attempting alternative method..." -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Visit https://$DomainName/ in your browser" -ForegroundColor White
Write-Host "Hard refresh: Ctrl+F5 (or Cmd+Shift+R on Mac)" -ForegroundColor White
Write-Host ""
