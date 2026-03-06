Set-Location -Path 'C:\Users\USER\Documents\trae_projects\VoxQuery'

$token = '1DBXGR4SQ1OVQ40WR9FQOCS5Y73TUQWV'
$cpanelHost = 'cloud771.thundercloud.uk'
$user = 'voxcoreo'

# Read file
$content = Get-Content -Path 'frontend\dist\landing.html' -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$b64 = [Convert]::ToBase64String($bytes)

# Build the API request URL
$url = "https://${cpanelHost}:2083/json-api/cpanel?cpanel_jsonapi_apiversion=2&cpanel_jsonapi_user=${user}&cpanel_jsonapi_func=fileman_save_file&filepath=/public_html/index.html"

# Prepare headers
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}

Write-Host "Uploading to cPanel..."
Write-Host "File: landing.html"
Write-Host "Size: $($bytes.Length) bytes"
Write-Host ""

Write-Host "Step 1: Encoding file content..."
Write-Host "Encoded size: $($b64.Length) bytes"
Write-Host ""

Write-Host "Step 2: Sending to cPanel..."

$payload = @{
    filepath = '/public_html/index.html'
    file_content = $b64
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body $payload -SkipCertificateCheck 2>&1
    Write-Host "Response Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Status: $($_.Exception.Response.StatusCode)"
}

Write-Host ""
Write-Host "DONE"
