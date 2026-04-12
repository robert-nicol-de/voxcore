# VoxCore frontend deployment helper.
# Deploy the built SPA to root while preserving the /app entrypoint.

param(
    [string]$CpanelHost = "cloud771.thundercloud.uk:2083",
    [string]$CpanelUser = "voxcoreo",
    [string]$ApiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV",
    [string]$DomainName = "voxcore.org",
    [string]$LocalDistPath = "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist"
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "VoxCore App Root Deployment" -ForegroundColor Cyan
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

# Step 2: Check the built SPA exists
Write-Host "[2/5] Checking frontend build files..." -ForegroundColor Yellow
$frontendIndexPath = "$LocalDistPath\index.html"
if (Test-Path $frontendIndexPath) {
    Write-Host "✓ Frontend entry found: $frontendIndexPath" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend entry not found at: $frontendIndexPath" -ForegroundColor Red
    Write-Host "Make sure index.html is in your frontend\dist folder" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Copy the same SPA shell to both root and /app
Write-Host "[3/5] Reorganizing files..." -ForegroundColor Yellow
Write-Host "  → Will upload index.html as /public_html/index.html" -ForegroundColor Cyan
Write-Host "  → Will copy the same SPA shell to /public_html/app/index.html" -ForegroundColor Cyan
Write-Host "  → Will keep shared assets under /public_html/assets/" -ForegroundColor Cyan
Write-Host ""

# Step 4: Upload SPA entrypoint
Write-Host "[4/5] Frontend app ready for upload..." -ForegroundColor Yellow
$frontendIndexContent = Get-Content $frontendIndexPath -Raw
Write-Host "✓ Frontend index loaded ($(($frontendIndexContent.Length / 1KB).ToString('N1')) KB)" -ForegroundColor Green
Write-Host ""

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files ready for upload:" -ForegroundColor White
Write-Host "  • From: $LocalDistPath\index.html" -ForegroundColor Cyan
Write-Host "  • To:   /public_html/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Folder structure after deployment:" -ForegroundColor White
Write-Host "  public_html/" -ForegroundColor Cyan
Write-Host "  ├── index.html (real VoxCore app)" -ForegroundColor Cyan
Write-Host "  ├── assets/" -ForegroundColor Cyan
Write-Host "  └── app/" -ForegroundColor Cyan
Write-Host "      └── index.html (same SPA shell)" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. In cPanel File Manager, navigate to public_html" -ForegroundColor White
Write-Host "2. Delete the current index.html" -ForegroundColor White
Write-Host "3. Upload index.html from: $LocalDistPath" -ForegroundColor White
Write-Host "4. Copy the same file to app/index.html" -ForegroundColor White
Write-Host "5. Refresh https://$DomainName/" -ForegroundColor White
Write-Host ""
Write-Host "The deployed site will now have:" -ForegroundColor Green
Write-Host "  ✓ The real VoxCore app at /" -ForegroundColor Green
Write-Host "  ✓ The same app shell preserved at /app" -ForegroundColor Green
Write-Host "  ✓ Shared assets served from /assets" -ForegroundColor Green
Write-Host ""
Write-Host "Questions? Check frontend/dist/index.html" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
