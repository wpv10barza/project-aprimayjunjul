<#
setup_windows.ps1 - Setup Python virtual environment and install Transcriptor dependencies on Windows
Usage: Run from repository root in PowerShell: .\setup_windows.ps1
#>
Param(
    [switch]$SkipFFmpegCheck
)

# Exit on error
$ErrorActionPreference = 'Stop'

# Check Python availability
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Install from https://python.org and check 'Add Python to PATH'."
    exit 1
}

# Create venv if missing
if (-not (Test-Path -Path .\.venv)) {
    python -m venv .venv
    Write-Host "Created virtual environment at ./.venv"
} else {
    Write-Host "Virtual environment ./.venv already exists"
}

$py = Join-Path -Path $PWD -ChildPath ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error "Could not find Python executable in .venv. Ensure the venv was created successfully."
    exit 1
}

# Upgrade pip and install requirements
& $py -m pip install --upgrade pip
if (Test-Path .\requirements.txt) {
    & $py -m pip install -r .\requirements.txt
} else {
    & $py -m pip install git+https://github.com/openai/whisper.git pandas tqdm
}

# ffmpeg check
if (-not $SkipFFmpegCheck) {
    if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
        $ff = Get-Command ffmpeg
        Write-Host "ffmpeg detected: $($ff.Path)"
    } else {
        Write-Warning "ffmpeg not found. Install via 'conda install -c conda-forge ffmpeg', 'choco install ffmpeg' or download from https://ffmpeg.org/download.html and add to PATH."
    }
}

Write-Host "Setup complete. To activate the venv in PowerShell run: .\.venv\Scripts\Activate.ps1"
Write-Host "If Activate.ps1 is blocked by policy, run (as admin): Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
