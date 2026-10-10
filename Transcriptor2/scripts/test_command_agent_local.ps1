param(
  [string]$BaseDir = ""
)
$ErrorActionPreference = "Stop"
$PreferredBaseDir = 'D:\118102025\Downloads\Nueva carpeta\Transcriptor2'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
if ([string]::IsNullOrWhiteSpace($BaseDir)) {
  if (Test-Path -LiteralPath $PreferredBaseDir) { $BaseDir = $PreferredBaseDir } else { $BaseDir = $PackageRoot }
}
Write-Host "[TEST 1] Crear Excel sin Gemma, fallback local"
& (Join-Path $ScriptRoot "run_command_agent_exe.ps1") -BaseDir $BaseDir -NoGemma -Command "crear documento excel"
Write-Host "[TEST 2] Crear archivo en Disco C seguro sin Gemma"
& (Join-Path $ScriptRoot "run_command_agent_exe.ps1") -BaseDir $BaseDir -NoGemma -Command "crear archivo en disco c"
