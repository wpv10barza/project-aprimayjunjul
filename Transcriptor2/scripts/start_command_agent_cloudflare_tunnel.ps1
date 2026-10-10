param(
  [int]$Port = 53320
)
$ErrorActionPreference = "Stop"
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Host "cloudflared no esta instalado. Instalalo desde https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  throw "cloudflared no encontrado"
}
cloudflared tunnel --url "http://127.0.0.1:$Port"
