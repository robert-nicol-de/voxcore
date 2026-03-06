# Download and install Microsoft C++ Build Tools
# Run this script as Administrator

Write-Host "Downloading Microsoft C++ Build Tools..." -ForegroundColor Green

$downloadUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
$installerPath = "$env:TEMP\vs_BuildTools.exe"

# Download the installer
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    exit 1
}

# Install with required components
Write-Host "Installing C++ Build Tools..." -ForegroundColor Green
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow

$arguments = @(
    "--quiet",
    "--norestart",
    "--wait",
    "--add", "Microsoft.VisualStudio.Workload.VCTools",
    "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
    "--add", "Microsoft.VisualStudio.Component.Windows10SDK.19041"
)

& $installerPath $arguments

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "You may need to restart your computer for changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host "Installation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}

# Clean up
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
