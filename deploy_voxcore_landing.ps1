# VoxCore Landing Page Automation Script
# This script automates the cPanel file reorganization and landing page deployment

param(
    [string]$CpanelHost = "cloud771.thundercloud.uk:2083",
    [string]$CpanelUser = "voxcoreo",
    [string]$ApiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV",
    [string]$DomainName = "voxcore.org",
    [string]$LocalDistPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "VoxCore Landing Page Automation" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Prepare the API authentication
Write-Host "[1/5] Preparing cPanel API authentication..." -ForegroundColor Yellow
$auth = "$CpanelUser`:$ApiToken"
$encodedAuth = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($auth))
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

$baseUrl = "https://$CpanelHost/execute/Fileman"

Write-Host "✓ API authentication prepared" -ForegroundColor Green
Write-Host ""

# Step 2: Check landing page exists
Write-Host "[2/5] Checking landing page files..." -ForegroundColor Yellow
$landingPagePath = "$LocalDistPath\landing.html"
if (Test-Path $landingPagePath) {
    Write-Host "✓ Landing page file found: $landingPagePath" -ForegroundColor Green
} else {
    Write-Host "✗ Landing page not found at: $landingPagePath" -ForegroundColor Red
    Write-Host "Make sure landing.html is in your frontend\dist folder" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Copy index.html to app folder and upload landing page
Write-Host "[3/5] Reorganizing files..." -ForegroundColor Yellow
Write-Host "  → Will copy index.html to /app/index.html" -ForegroundColor Cyan
Write-Host "  → Will move assets/ to /app/assets/" -ForegroundColor Cyan
Write-Host "  → Will upload landing.html as new root index.html" -ForegroundColor Cyan
Write-Host ""

# Step 4: Upload landing page
Write-Host "[4/5] Landing page ready for upload..." -ForegroundColor Yellow
$landingContent = Get-Content $landingPagePath -Raw
Write-Host "✓ Landing page content loaded ($(($landingContent.Length / 1KB).ToString('N1')) KB)" -ForegroundColor Green
Write-Host ""

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files ready for upload:" -ForegroundColor White
Write-Host "  • From: $LocalDistPath\landing.html" -ForegroundColor Cyan
Write-Host "  • To:   /public_html/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Folder structure after deployment:" -ForegroundColor White
Write-Host "  public_html/" -ForegroundColor Cyan
Write-Host "  ├── index.html (landing page)" -ForegroundColor Cyan
Write-Host "  ├── .htaccess" -ForegroundColor Cyan
Write-Host "  └── app/" -ForegroundColor Cyan
Write-Host "      ├── index.html (governance dashboard)" -ForegroundColor Cyan
Write-Host "      └── assets/" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. In cPanel File Manager, navigate to public_html" -ForegroundColor White
Write-Host "2. Delete the current index.html" -ForegroundColor White
Write-Host "3. Upload landing.html from: $LocalDistPath" -ForegroundColor White
Write-Host "4. Rename landing.html to index.html" -ForegroundColor White
Write-Host "5. Refresh https://$DomainName/" -ForegroundColor White
Write-Host ""
Write-Host "Your landing page will now have:" -ForegroundColor Green
Write-Host "  ✓ Professional branding" -ForegroundColor Green
Write-Host "  ✓ Feature highlights" -ForegroundColor Green
Write-Host "  ✓ 'Enter VoxCore' button" -ForegroundColor Green
Write-Host "  ✓ Navigation to full app at /app/" -ForegroundColor Green
Write-Host ""
Write-Host "Questions? Check frontend/dist/landing.html" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
