param(
    [string]$CompanyId = "1",
    [string]$WorkspaceId = "1",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$connectionDir = Join-Path $repoRoot "data/companies/$CompanyId/workspaces/$WorkspaceId/connections"
$sqliteDir = Join-Path $repoRoot "data/sqlite"
$sqliteDbPath = Join-Path $sqliteDir "sqlserver_default.db"
$iniPath = Join-Path $connectionDir "sqlserver-default.ini"

New-Item -ItemType Directory -Force -Path $connectionDir | Out-Null
New-Item -ItemType Directory -Force -Path $sqliteDir | Out-Null

if ($Force -or -not (Test-Path $iniPath)) {
    @"
[database]
type = sqlite
database = data/sqlite/sqlserver_default.db
"@ | Set-Content -Path $iniPath -Encoding UTF8
}

$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) {
    throw "Python virtual environment not found at .venv/Scripts/python.exe"
}

$py = @"
import sqlite3
conn = sqlite3.connect(r'$sqliteDbPath')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL)')
conn.commit()
conn.close()
print('VALIDATION_SCHEMA_READY')
"@

& $python -c $py
Write-Output "WROTE: $iniPath"
Write-Output "WROTE: $sqliteDbPath"
