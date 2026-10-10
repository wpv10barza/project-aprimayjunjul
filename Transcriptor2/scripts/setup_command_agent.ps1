param(
  [switch]$RecreateVenv,
  [switch]$BuildExe,
  [string]$BaseDir = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$PreferredBaseDir = 'D:\118102025\Downloads\Nueva carpeta\Transcriptor2'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
if (-not (Test-Path -LiteralPath $PackageRoot)) { throw "No se encontro PackageRoot" }

if ([string]::IsNullOrWhiteSpace($BaseDir)) {
  if (Test-Path -LiteralPath $PreferredBaseDir) {
    $BaseDir = $PreferredBaseDir
  } else {
    $BaseDir = $PackageRoot
  }
}

function Invoke-Checked {
  param(
    [Parameter(Mandatory=$true)][string]$Exe,
    [Parameter(Mandatory=$true)][string[]]$ArgumentList
  )
  Write-Host "> $Exe $($ArgumentList -join ' ')"
  $global:LASTEXITCODE = 0
  & $Exe @ArgumentList
  if ($LASTEXITCODE -ne 0) {
    throw "Fallo comando: $Exe $($ArgumentList -join ' ')"
  }
}

# V5: no devolvemos Hashtable/PSCustomObject para evitar el error:
# "No se encuentra la propiedad 'Exe' en este objeto" con Set-StrictMode.
$script:PythonExe = $null
$script:PythonArgs = @()

function Select-PythonExe {
  $candidates = @(
    @('py', @('-3.12')),
    @('py', @('-3.11')),
    @('py', @('-3')),
    @('python', @())
  )

  foreach ($candidate in $candidates) {
    $exe = [string]$candidate[0]
    $args = @($candidate[1])
    try {
      $global:LASTEXITCODE = 0
      $probeArgs = @($args + @('-c', 'import sys; print(sys.executable); print(sys.version)'))
      $probe = & $exe @probeArgs 2>$null
      if ($LASTEXITCODE -eq 0) {
        $script:PythonExe = $exe
        $script:PythonArgs = $args
        Write-Host "[INFO] Python seleccionado: $script:PythonExe $($script:PythonArgs -join ' ')"
        if ($probe) { Write-Host ($probe -join "`n") }
        return
      }
    } catch {
      # Probar siguiente candidato.
    }
  }

  throw "No se encontro Python. Instala Python 3.11/3.12/3.13/3.14 y habilita py.exe o python.exe en PATH."
}

Write-Host "[INFO] Fix V5 activo: ruta fija + Python sin propiedad .Exe"
Write-Host "[INFO] PackageRoot: $PackageRoot"
Write-Host "[INFO] BaseDir fijo: $BaseDir"
Write-Host "[1/6] Verificando carpetas..."
$global:LASTEXITCODE = 0
& (Join-Path $ScriptRoot "create_empty_folders.ps1") -BaseDir $BaseDir
if (-not $?) { throw "No se pudieron crear/verificar carpetas base." }
$global:LASTEXITCODE = 0

$VenvDir = Join-Path $BaseDir "librery\venv_command_agent"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if ($RecreateVenv -and (Test-Path -LiteralPath $VenvDir)) {
  Write-Host "[2/6] Eliminando venv anterior: $VenvDir"
  Remove-Item -LiteralPath $VenvDir -Recurse -Force
}

Select-PythonExe
if (-not (Test-Path -LiteralPath $VenvPython)) {
  Write-Host "[2/6] Creando venv aislado en librery..."
  $global:LASTEXITCODE = 0
  $venvArgs = @($script:PythonArgs + @('-m', 'venv', $VenvDir))
  Write-Host "> $script:PythonExe $($venvArgs -join ' ')"
  & $script:PythonExe @venvArgs
  if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
} else {
  Write-Host "[2/6] venv ya existe: $VenvDir"
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
  throw "El venv se creo, pero no aparece python.exe en: $VenvPython"
}

Write-Host "[3/6] Actualizando pip/setuptools/wheel..."
Invoke-Checked $VenvPython @('-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel')

$ReqFile = Join-Path $PackageRoot "requirements_command_agent.txt"
if (-not (Test-Path -LiteralPath $ReqFile)) {
  throw "No se encontro requirements_command_agent.txt en: $ReqFile"
}

Write-Host "[4/6] Instalando librerias CommandAgent, OpenPyXL, DOCX y API..."
Invoke-Checked $VenvPython @('-m', 'pip', 'install', '-r', $ReqFile)

Write-Host "[5/6] Verificando imports principales..."
Invoke-Checked $VenvPython @('-c', "import fastapi, uvicorn, requests, openpyxl, docx; import PyInstaller; print('imports OK')")

if ($BuildExe) {
  Write-Host "[6/6] Compilando EXE..."
  $global:LASTEXITCODE = 0
  & (Join-Path $ScriptRoot "build_command_agent_exe.ps1") -BaseDir $BaseDir -PackageRoot $PackageRoot
  if (-not $?) { throw "Compilacion EXE fallo." }
  if ($LASTEXITCODE -ne 0) { throw "Compilacion EXE fallo con codigo $LASTEXITCODE." }
} else {
  Write-Host "[6/6] BuildExe omitido. Para compilar: .\scripts\build_command_agent_exe.ps1"
}

Write-Host "[OK] Instalacion CommandAgent lista."
Write-Host "BaseDir: $BaseDir"
Write-Host "VENV:    $VenvDir"
Write-Host "EXE:     $(Join-Path $BaseDir 'dist_exe\CommandAgent.exe')"
Write-Host "API:     http://127.0.0.1:53320/agent/execute"
