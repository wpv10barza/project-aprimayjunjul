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
$folders = @(
  $BaseDir,
  (Join-Path $BaseDir "mp3"),
  (Join-Path $BaseDir "librery"),
  (Join-Path $BaseDir "acciones_grabadas"),
  (Join-Path $BaseDir "salidas_doc_xls"),
  (Join-Path $BaseDir "dist_exe"),
  (Join-Path $BaseDir "logs"),
  'C:\Transcriptor2_Agent_Output'
)
foreach ($dir in $folders) {
  if (-not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "[OK] Carpeta creada: $dir"
  } else {
    Write-Host "[OK] Carpeta ya existe: $dir"
  }
}
$global:LASTEXITCODE = 0
Write-Host "[OK] Carpetas base verificadas en: $BaseDir"
