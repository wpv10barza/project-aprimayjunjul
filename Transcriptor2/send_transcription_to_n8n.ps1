param(
    [Parameter(Mandatory=$true)]
    [string]$AudioPath,
    [string]$Model = "medium",
    [string]$WebhookUrl = $env:N8N_WEBHOOK_URL,
    [string]$WebhookApiKey = $env:N8N_WEBHOOK_API_KEY
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path $AudioPath)) { throw "No existe el archivo: $AudioPath" }
if (-not $WebhookUrl) { throw "Falta WebhookUrl. Usa -WebhookUrl o configura N8N_WEBHOOK_URL en .env" }
if (-not (Test-Path ".venv\Scripts\python.exe")) { throw "Ejecuta primero .\install.ps1" }

# Cargar .env si existe
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*#") { return }
        if ($_ -match "^\s*$") { return }
        $pair = $_ -split "=", 2
        if ($pair.Length -eq 2) { [Environment]::SetEnvironmentVariable($pair[0].Trim(), $pair[1].Trim(), "Process") }
    }
    if (-not $WebhookUrl) { $WebhookUrl = $env:N8N_WEBHOOK_URL }
    if (-not $WebhookApiKey) { $WebhookApiKey = $env:N8N_WEBHOOK_API_KEY }
}

$tmpJson = Join-Path $env:TEMP ("transcripcion_" + [guid]::NewGuid().ToString() + ".json")
& ".venv\Scripts\python.exe" ".\local_whisper_cli.py" --audio $AudioPath --modelo $Model --language es --json-output $tmpJson
if ($LASTEXITCODE -ne 0) { throw "Fallo la transcripcion local" }

$body = Get-Content $tmpJson -Raw
$headers = @{}
if ($WebhookApiKey) { $headers["x-api-key"] = $WebhookApiKey }

Write-Host "Enviando resultado a n8n: $WebhookUrl" -ForegroundColor Cyan
$response = Invoke-RestMethod -Method Post -Uri $WebhookUrl -Headers $headers -ContentType "application/json; charset=utf-8" -Body $body
$response | ConvertTo-Json -Depth 20
Remove-Item $tmpJson -Force -ErrorAction SilentlyContinue
