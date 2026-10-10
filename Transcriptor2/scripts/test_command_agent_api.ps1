param(
  [string]$Url = "http://127.0.0.1:53320/agent/execute",
  [string]$ApiKey = ""
)
$headers = @{}
if ($ApiKey) { $headers["x-api-key"] = $ApiKey }
$body = @{
  command = "crear documento excel y crear archivo en disco c"
  use_latest_voice = $false
  use_gemma = $true
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri $Url -Method POST -ContentType "application/json" -Headers $headers -Body $body
