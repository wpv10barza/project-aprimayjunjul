param(
  [string]$Command = "crear documento excel",
  [switch]$Latest,
  [switch]$NoGemma,
  [string]$BaseDir = ""
)
$ErrorActionPreference = "Stop"
$PreferredBaseDir = 'D:\118102025\Downloads\Nueva carpeta\Transcriptor2'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
if ([string]::IsNullOrWhiteSpace($BaseDir)) {
  if (Test-Path -LiteralPath $PreferredBaseDir) { $BaseDir = $PreferredBaseDir } else { $BaseDir = $PackageRoot }
}

$env:TRANSCRIPTOR2_BASE_DIR = $BaseDir
$env:VOICE_INPUT_DIR = Join-Path $BaseDir "mp3"
$env:OUTPUT_DIR = Join-Path $BaseDir "salidas_doc_xls"
$env:ACTIONS_DIR = Join-Path $BaseDir "acciones_grabadas"
$Exe = Join-Path $BaseDir "dist_exe\CommandAgent.exe"
$ArgList = @("--command", $Command)
if ($Latest) { $ArgList += "--latest" }
if ($NoGemma) { $ArgList += "--no-gemma" }
Write-Host "[INFO] BaseDir: $BaseDir"
Write-Host "[INFO] VOICE_INPUT_DIR: $env:VOICE_INPUT_DIR"
if (Test-Path -LiteralPath $Exe) {
  & $Exe @ArgList
} else {
  $VenvPython = Join-Path $BaseDir "librery\venv_command_agent\Scripts\python.exe"
  if (-not (Test-Path -LiteralPath $VenvPython)) { throw "No existe EXE ni venv. Ejecuta setup_command_agent.ps1" }
  $env:PYTHONPATH = Join-Path $PackageRoot "services"
  & $VenvPython (Join-Path $PackageRoot "services\command_agent_cli.py") @ArgList
}
