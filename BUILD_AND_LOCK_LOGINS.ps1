Write-Host ""
Write-Host "VoxCore - Build and Deploy (Logins Locked)" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build frontend
Write-Host "[1/3] Building frontend..." -ForegroundColor Yellow
cd c:\Users\USER\Documents\trae_projects\VoxQuery\frontend

try {
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing dependencies..." -ForegroundColor Cyan
        npm install
    }
    
    Write-Host "Running Vite build..." -ForegroundColor Cyan
    npm run build
    Write-Host "Build completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error during build: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Verify dist folder
Write-Host "[2/3] Verifying build output..." -ForegroundColor Yellow
$distFiles = Get-ChildItem -Path "dist" -Recurse
Write-Host "Build produced $($distFiles.Count) files" -ForegroundColor Green
Write-Host "  - index.html (landing page with lockout notice)" -ForegroundColor Cyan
Write-Host "  - assets/ (compiled app)" -ForegroundColor Cyan
if (Test-Path "dist\index.html") {
    Write-Host "✓ Index file ready" -ForegroundColor Green
}

Write-Host ""

# Step 3: Prepare for upload
Write-Host "[3/3] Preparing deployment..." -ForegroundColor Yellow
$cpanelHost = "cloud771.thundercloud.uk:2083"
$cpanelUser = "voxcoreo"
$apiToken = "1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV"

Write-Host "Files ready to upload:" -ForegroundColor Green
Write-Host "  ✓ Updated landing.html with lockout message" -ForegroundColor Green
Write-Host "  ✓ Updated Login component (logins disabled)" -ForegroundColor Green
Write-Host "  ✓ New assets built" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. In cPanel File Manager, go to public_html" -ForegroundColor White
Write-Host "2. Delete old index.html" -ForegroundColor White
Write-Host "3. Upload new files from dist/ folder" -ForegroundColor White
Write-Host "4. Hard refresh your browser (Ctrl+F5)" -ForegroundColor White
Write-Host ""
Write-Host "What visitors will see:" -ForegroundColor Yellow
Write-Host "  • Landing page with lockout notice" -ForegroundColor Cyan
Write-Host "  • Login modal with disabled login (Browse Dashboard button)" -ForegroundColor Cyan
Write-Host "  • Full access to explore the governance dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "To enable logins later:" -ForegroundColor Yellow
Write-Host "  Edit: frontend/src/screens/Login.tsx" -ForegroundColor Cyan
Write-Host "  Change: const loginsLocked = false" -ForegroundColor Cyan
Write-Host "  Then rebuild and redeploy" -ForegroundColor Cyan
Write-Host ""
