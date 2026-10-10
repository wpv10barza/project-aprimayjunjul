<#
.SYNOPSIS
    Script profesional para depurar dependencias y ejecutar el motor Whisper local.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$false)]
    [string]$AudioPath = "C:\Users\ASUS\GESTIONA ACTIVOS S.A.C\TGA_PEN - 2501_EVAL SGM - 03.00 EJECUCION\03.02 Fase 2 Recolección\03.02.02 Entrevistas\01. 02.02 - Plan & Prog\Lun Pla y Pro 1.mp4",
    
    [Parameter(Mandatory=$false)]
    [string]$Modelo = "turbo"
)

# Configuracion de variables
$DirectorioBase = $PSScriptRoot
$PythonExe      = Join-Path -Path $DirectorioBase -ChildPath "venv\Scripts\python.exe"
$ScriptPython   = Join-Path -Path $DirectorioBase -ChildPath "local_whisper.py"
$Requirements   = Join-Path -Path $DirectorioBase -ChildPath "requirements.txt"

# Forzar que los errores detengan el script
$ErrorActionPreference = "Stop"

try {
    Clear-Host
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host " INICIANDO ENTORNO DE TRANSCRIPCION (POWERSHELL)" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan

    # 1. VALIDAR ENTORNO VIRTUAL
    if (-not (Test-Path $PythonExe)) {
        Write-Host "[ALERTA] Entorno virtual (venv) no detectado. Creando uno nuevo..." -ForegroundColor Yellow
        python -m venv venv
        Write-Host "[OK] Entorno virtual creado." -ForegroundColor Green
    } else {
        Write-Host "[OK] Entorno virtual detectado." -ForegroundColor Green
    }

    # 2. DEPURACION DE REQUERIMIENTOS
    if (Test-Path $Requirements) {
        Write-Host "[INFO] Validando dependencias desde requirements.txt..." -ForegroundColor DarkGray
        & $PythonExe -m pip install -r $Requirements --upgrade --quiet
        Write-Host "[OK] Dependencias alineadas." -ForegroundColor Green
    } else {
        Write-Host "[ALERTA] No se encontro el archivo requirements.txt" -ForegroundColor Yellow
    }

    # 3. VALIDAR EXISTENCIA DEL AUDIO
    if (-not (Test-Path $AudioPath)) {
        throw "El archivo de audio no existe en la ruta especificada: $AudioPath"
    }

    # 4. EJECUTAR EL SCRIPT DE PYTHON
    Write-Host "`n[INFO] Lanzando motor Whisper en GPU..." -ForegroundColor Magenta
    Write-Host "Audio objetivo: $AudioPath" -ForegroundColor DarkGray
    Write-Host "Modelo: $Modelo`n" -ForegroundColor DarkGray

    & $PythonExe $ScriptPython --audio "`"$AudioPath`"" --modelo $Modelo

    # 5. MANEJO DE CODIGOS DE SALIDA
    if ($LASTEXITCODE -ne 0) {
        throw "Python finalizo con un error (Codigo de salida: $LASTEXITCODE). Revisa la consola."
    }

    Write-Host "`n[OK] Proceso finalizado con exito." -ForegroundColor Green

} catch {
    # 6. CAPTURA PROFESIONAL DE ERRORES
    Write-Host "`n==================================================" -ForegroundColor Red
    Write-Host " ERROR CRITICO DETECTADO EN EL PIPELINE" -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Exit 1
}