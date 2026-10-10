param(
    [Parameter(Mandatory=$true)]
    [string]$AudioPath,
    [string]$Model = "medium"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path $AudioPath)) { throw "No existe el archivo: $AudioPath" }
if (-not (Test-Path ".venv\Scripts\python.exe")) { throw "Ejecuta primero .\install.ps1" }

& ".venv\Scripts\python.exe" ".\local_whisper_cli.py" --audio $AudioPath --modelo $Model --language es
