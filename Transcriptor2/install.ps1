param(
    [ValidateSet("auto", "cpu", "cuda")]
    [string]$TorchMode = "auto"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "[1/6] Buscando Python compatible..." -ForegroundColor Cyan
$candidates = @(
    @{Cmd="py"; Args=@("-3.11")},
    @{Cmd="py"; Args=@("-3.12")},
    @{Cmd="python"; Args=@()}
)

$pythonCmd = $null
$pythonArgs = @()
foreach ($c in $candidates) {
    try {
        $out = & $c.Cmd @($c.Args + @("-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")) 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) {
            $ver = [version]$out.Trim()
            if ($ver.Major -eq 3 -and $ver.Minor -ge 10 -and $ver.Minor -le 12) {
                $pythonCmd = $c.Cmd
                $pythonArgs = $c.Args
                break
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    throw "No encontre Python 3.10, 3.11 o 3.12. Recomendado: instala Python 3.11 x64. Python 3.14 suele fallar con torch/whisper."
}

Write-Host "[OK] Usando: $pythonCmd $($pythonArgs -join ' ')" -ForegroundColor Green

Write-Host "[2/6] Creando entorno .venv limpio..." -ForegroundColor Cyan
if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force }
& $pythonCmd @($pythonArgs + @("-m", "venv", ".venv"))

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip setuptools wheel

Write-Host "[3/6] Instalando PyTorch..." -ForegroundColor Cyan
$hasNvidia = $false
try {
    $null = & nvidia-smi 2>$null
    if ($LASTEXITCODE -eq 0) { $hasNvidia = $true }
} catch {}

if ($TorchMode -eq "cuda" -or ($TorchMode -eq "auto" -and $hasNvidia)) {
    Write-Host "[INFO] NVIDIA detectada. Instalando torch CUDA 12.1." -ForegroundColor Yellow
    & $venvPython -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
} else {
    Write-Host "[INFO] Instalando torch CPU." -ForegroundColor Yellow
    & $venvPython -m pip install torch torchvision torchaudio
}

Write-Host "[4/6] Instalando dependencias del Transcriptor..." -ForegroundColor Cyan
& $venvPython -m pip install -r requirements.txt

Write-Host "[5/6] Revisando FFmpeg..." -ForegroundColor Cyan
$ffmpegOk = $false
try {
    $null = & ffmpeg -version 2>$null
    if ($LASTEXITCODE -eq 0) { $ffmpegOk = $true }
} catch {}

if (-not $ffmpegOk) {
    Write-Host "[AVISO] FFmpeg no esta en PATH. Intentando instalar con winget..." -ForegroundColor Yellow
    try {
        winget install --id Gyan.FFmpeg -e --source winget
        Write-Host "[INFO] Reinicia PowerShell despues de instalar FFmpeg si el comando ffmpeg aun no aparece." -ForegroundColor Yellow
    } catch {
        Write-Host "[AVISO] No pude instalar FFmpeg automaticamente. Instalalo manualmente: winget install --id Gyan.FFmpeg -e" -ForegroundColor Yellow
    }
}

Write-Host "[6/6] Preparando .env..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[INFO] Se creo .env. Edita TRANSCRIPTOR_API_KEY y N8N_WEBHOOK_URL." -ForegroundColor Yellow
}

Write-Host "[LISTO] Instalacion terminada." -ForegroundColor Green
Write-Host "Ejecuta: .\start_server.ps1" -ForegroundColor Green
