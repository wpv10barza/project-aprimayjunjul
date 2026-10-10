param(
  [string]$BaseDir = "",
  [string]$HostIp = "127.0.0.1",
  [int]$Port = 53320
)
$ErrorActionPreference = "Stop"
$PreferredBaseDir = 'D:\118102025\Downloads\Nueva carpeta\Transcriptor2'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
if ([string]::IsNullOrWhiteSpace($BaseDir)) {
  if (Test-Path -LiteralPath $PreferredBaseDir) { $BaseDir = $PreferredBaseDir } else { $BaseDir = $PackageRoot }
}

$VenvPython = Join-Path $BaseDir "librery\venv_command_agent\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPython)) { throw "No existe venv. Ejecuta .\scripts\setup_command_agent.ps1 -RecreateVenv" }
$env:TRANSCRIPTOR2_BASE_DIR = $BaseDir
$env:VOICE_INPUT_DIR = Join-Path $BaseDir "mp3"
$env:OUTPUT_DIR = Join-Path $BaseDir "salidas_doc_xls"
$env:ACTIONS_DIR = Join-Path $BaseDir "acciones_grabadas"
$env:COMMAND_AGENT_HOST = $HostIp
$env:COMMAND_AGENT_PORT = [string]$Port
$env:PYTHONPATH = Join-Path $PackageRoot "services"
Write-Host "[INFO] BaseDir: $BaseDir"
Write-Host "[INFO] API: http://${HostIp}:$Port/agent/execute"
Set-Location (Join-Path $PackageRoot "services")
& $VenvPython "command_agent_api.py"
