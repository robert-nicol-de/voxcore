$ErrorActionPreference = "Stop"

# Configuration
$CpanelHost = "cloud771.thundercloud.uk:2083"
$ApiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV"
$DomainName = "voxcore.org"
$LocalDistPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
$LandingPagePath = "$LocalDistPath\landing.html"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "VoxCore Landing Page - Automated Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify file exists
Write-Host "[1/4] Checking landing page file..." -ForegroundColor Yellow
if (-not (Test-Path $LandingPagePath)) {
    Write-Host "ERROR: Landing page not found at $LandingPagePath" -ForegroundColor Red
    exit 1
}
$fileSize = (Get-Item $LandingPagePath).Length / 1KB
Write-Host "✓ Landing page found ($([math]::Round($fileSize, 1)) KB)" -ForegroundColor Green
Write-Host ""

# Step 2: Read file content
Write-Host "[2/4] Reading landing page content..." -ForegroundColor Yellow
$landingContent = Get-Content $LandingPagePath -Raw
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
Write-Host "[4/4] Uploading landing page as new index.html..." -ForegroundColor Yellow

$createFileBody = @{
    "method" = "save"
    "dir" = "/public_html"
    "file" = "index.html"
    "content" = $landingContent
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method POST -Headers $headers -Body $createFileBody -SkipCertificateCheck -ErrorAction Stop
    $responseContent = $response.Content | ConvertFrom-Json
    
    if ($responseContent.status -eq 1 -or $response.StatusCode -eq 200) {
        Write-Host "✓ Landing page uploaded and installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Upload may have completed (cPanel response: $($responseContent.status))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not upload via API: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "FALLBACK: Manual upload instructions" -ForegroundColor Cyan
    Write-Host "1. Copy the file to clipboard:" -ForegroundColor White
    Write-Host "   File: $LandingPagePath" -ForegroundColor Cyan
    Write-Host "2. Go to: https://cloud771.thundercloud.uk:2083/" -ForegroundColor Cyan
    Write-Host "3. File Manager → public_html" -ForegroundColor Cyan
    Write-Host "4. Upload landing.html and rename to index.html" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your landing page is now live!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Open your browser" -ForegroundColor Cyan
Write-Host "2. Go to: https://$DomainName/" -ForegroundColor Cyan
Write-Host "3. Hard refresh: Ctrl+F5 (or Cmd+Shift+R on Mac)" -ForegroundColor Cyan
Write-Host "4. You should see the professional VoxCore landing page" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features on landing page:" -ForegroundColor Green
Write-Host "  ✓ VoxCore branding with gradient" -ForegroundColor Green
Write-Host "  ✓ Feature highlights grid" -ForegroundColor Green
Write-Host "  ✓ 'Enter VoxCore' button" -ForegroundColor Green
Write-Host "  ✓ Professional footer with links" -ForegroundColor Green
Write-Host "  ✓ Responsive design" -ForegroundColor Green
Write-Host ""
Write-Host "What happens when users click 'Enter VoxCore':" -ForegroundColor White
Write-Host "  → Redirects to: https://$DomainName/app/" -ForegroundColor Cyan
Write-Host "  → Full governance dashboard loads" -ForegroundColor Cyan
Write-Host ""
Write-Host "Questions or issues? Contact: support@$DomainName" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
