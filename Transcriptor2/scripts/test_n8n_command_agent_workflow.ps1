param(
  [string]$WebhookUrl = "https://carlospolo-n8n.duckdns.org/webhook-test/voice-office/gemma-command",
  [string]$ServiceUrl = "http://127.0.0.1:53320/agent/execute",
  [string]$Command = "crear documento excel y crear archivo en disco c"
)
$body = @{
  command = $Command
  service_url = $ServiceUrl
  use_latest_voice = $false
  use_gemma = $true
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri $WebhookUrl -Method POST -ContentType "application/json" -Body $body
