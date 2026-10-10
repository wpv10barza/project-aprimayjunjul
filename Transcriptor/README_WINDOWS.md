README — Windows quick fixes 🔧

Purpose: Short, copy-paste commands and notes to get this repo running on a Windows machine.

1) Verificar Python y pip
- `python --version`  # comprobar versión
- `python -m pip --version`  # evita usar `pip` si no está en PATH

2) Instalar dependencias (recomendado: dentro de un venv)
- Crear venv: `python -m venv .venv`
- Activar en PowerShell: `. .\.venv\Scripts\Activate.ps1`
- Actualizar pip e instalar deps:
  - `python -m pip install --upgrade pip`
  - `python -m pip install -r requirements.txt`

3) Si `pip` no es reconocido
- Usa `python -m pip ...` siempre (funciona sin tocar PATH).
- Alternativa: añadir la carpeta `Scripts` de tu Python a la variable PATH (ej.: `C:\Users\<usuario>\AppData\Local\Programs\Python\Python3xx\Scripts`).

4) ffmpeg (necesario para Whisper/Transcriptor)
- Con Conda: `conda install -c conda-forge ffmpeg`
- Con Chocolatey: `choco install ffmpeg` (PowerShell en modo administrador)
- O descargar desde https://ffmpeg.org/download.html y añadir la carpeta `bin` a PATH
- Verificar: `ffmpeg -version` o `Get-Command ffmpeg` (PowerShell)

5) PowerShell y políticas de ejecución (si `Activate.ps1` está bloqueado)
- Como administrador: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Luego: `. .\.venv\Scripts\Activate.ps1`

6) `sudo` / `apt` en el notebook
- El notebook fue hecho para Colab/Linux; en Windows no uses `sudo`/`apt`.
- Opciones: ejecutar en Google Colab (más sencillo) o usar WSL (Ubuntu) para comandos `sudo apt`.

7) Script de setup incluido
- Ejecuta desde la raíz del repo: `.\setup_windows.ps1`
- El script crea `.venv`, actualiza `pip`, instala `requirements.txt` (o Whisper+pandas si faltan) y valida `ffmpeg`.

8) Verificación rápida
- `python -c "import pandas; import whisper; print('OK')"`  # smoke test (si instalaste Whisper)

Si quieres, puedo:
- Añadir un enlace a este archivo en el `README.md` principal, o
- Integrar estas instrucciones dentro de `.github/copilot-instructions.md`.

¿Deseas que haga alguna de esas dos cosas ahora? ✅