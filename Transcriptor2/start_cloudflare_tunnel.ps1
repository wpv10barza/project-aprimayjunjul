param(
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"

Write-Host "Revisando cloudflared..." -ForegroundColor Cyan
$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Host "cloudflared no esta instalado. Intentando instalar con winget..." -ForegroundColor Yellow
    winget install --id Cloudflare.cloudflared -e --source winget
}

Write-Host "Abriendo tunnel temporal hacia http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "Copia la URL https://....trycloudflare.com y usala en n8n como: https://....trycloudflare.com/transcribe" -ForegroundColor Green
cloudflared tunnel --url "http://127.0.0.1:$Port"
