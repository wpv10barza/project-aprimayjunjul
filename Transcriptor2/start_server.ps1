$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "No existe .venv. Ejecuta primero: .\install.ps1"
}

if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*#") { return }
        if ($_ -match "^\s*$") { return }
        $pair = $_ -split "=", 2
        if ($pair.Length -eq 2) { [Environment]::SetEnvironmentVariable($pair[0].Trim(), $pair[1].Trim(), "Process") }
    }
}

$hostIp = if ($env:LOCAL_API_HOST) { $env:LOCAL_API_HOST } else { "127.0.0.1" }
$port = if ($env:LOCAL_API_PORT) { $env:LOCAL_API_PORT } else { "8765" }

Write-Host "Iniciando Transcriptor API en http://$hostIp`:$port" -ForegroundColor Cyan
Write-Host "Health check: http://$hostIp`:$port/health" -ForegroundColor Yellow
& ".venv\Scripts\python.exe" -m uvicorn local_transcriptor_api:app --host $hostIp --port $port
