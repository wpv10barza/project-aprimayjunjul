param(
  [string]$BaseDir = "",
  [string]$PackageRoot = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$PreferredBaseDir = 'D:\118102025\Downloads\Nueva carpeta\Transcriptor2'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
  $PackageRoot = Split-Path -Parent $ScriptRoot
}
if ([string]::IsNullOrWhiteSpace($BaseDir)) {
  if (Test-Path -LiteralPath $PreferredBaseDir) { $BaseDir = $PreferredBaseDir } else { $BaseDir = $PackageRoot }
}

$VenvPython = Join-Path $BaseDir "librery\venv_command_agent\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPython)) {
  throw "No existe venv en $VenvPython. Ejecuta primero: .\scripts\setup_command_agent.ps1 -RecreateVenv"
}
$Dist = Join-Path $BaseDir "dist_exe"
$Build = Join-Path $BaseDir "librery\build_command_agent"
$Spec = Join-Path $BaseDir "librery\spec_command_agent"
New-Item -ItemType Directory -Force -Path $Dist, $Build, $Spec | Out-Null

function Invoke-Checked {
  param([string[]]$ArgumentList)
  Write-Host "> $VenvPython $($ArgumentList -join ' ')"
  $global:LASTEXITCODE = 0
  & $VenvPython @ArgumentList
  if ($LASTEXITCODE -ne 0) { throw "Fallo PyInstaller" }
}

$Services = Join-Path $PackageRoot "services"
Invoke-Checked @("-m", "PyInstaller", "--onefile", "--clean", "--name", "CommandAgent", "--paths", $Services, "--distpath", $Dist, "--workpath", $Build, "--specpath", $Spec, (Join-Path $Services "command_agent_cli.py"))
Invoke-Checked @("-m", "PyInstaller", "--onefile", "--clean", "--name", "CommandAgentAPI", "--paths", $Services, "--hidden-import", "multipart", "--distpath", $Dist, "--workpath", $Build, "--specpath", $Spec, (Join-Path $Services "command_agent_api.py"))

Write-Host "[OK] Ejecutables generados en BaseDir fijo: $BaseDir"
Write-Host (Join-Path $Dist "CommandAgent.exe")
Write-Host (Join-Path $Dist "CommandAgentAPI.exe")
