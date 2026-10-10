# Fix V5 - setup_command_agent.ps1

Esta version corrige definitivamente el error de PowerShell:

```text
No se encuentra la propiedad 'Exe' en este objeto.
```

## Causa

El instalador anterior guardaba el ejecutable Python en un objeto y luego lo llamaba con:

```powershell
$Py.Exe
```

En algunos entornos de PowerShell con `Set-StrictMode -Version Latest`, ese objeto no conserva la propiedad como se esperaba y el instalador se detiene antes de crear el entorno virtual.

## Correccion V5

El script ya no usa `$Py.Exe`. Ahora guarda Python en variables internas simples:

```powershell
$script:PythonExe
$script:PythonArgs
```

La ruta base queda fija en:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

## Uso recomendado

Extrae el ZIP V5 directamente en:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

Luego ejecuta:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
Set-ExecutionPolicy -Scope Process Bypass -Force
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

La primera linea del instalador debe mostrar:

```text
[INFO] Fix V5 activo: ruta fija + Python sin propiedad .Exe
```

## Prueba despues de instalar

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear documento excel y crear archivo en disco c"
```
