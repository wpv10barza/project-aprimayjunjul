# Fix V4 - Ruta fija de Transcriptor2

Esta version corrige la ruta base para que el agente trabaje en:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

Aunque el ZIP haya quedado por error en:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\Transcriptor2
```

los scripts usan por defecto la ruta correcta externa:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

## Correcciones incluidas

1. `setup_command_agent.ps1` ya no usa como salida la carpeta interna `Transcriptor2\Transcriptor2`.
2. `run_command_agent_exe.ps1` usa `mp3`, `salidas_doc_xls`, `acciones_grabadas`, `librery` y `dist_exe` en la ruta correcta.
3. `start_command_agent_api.ps1` levanta el API usando la ruta correcta.
4. Se corrigio el bug real de PowerShell donde `Resolve-PythonExe` imprimia texto al pipeline y `$Py` dejaba de ser un objeto con propiedad `.Exe`.

## Instalacion recomendada

Abre PowerShell y ejecuta:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
Set-ExecutionPolicy -Scope Process Bypass -Force
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

Si todavia estas dentro de la carpeta interna, tambien funciona:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2\Transcriptor2"
Set-ExecutionPolicy -Scope Process Bypass -Force
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

En ambos casos, el venv y los EXE se crean en:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\librery\venv_command_agent
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\dist_exe
```

## Prueba rapida

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear documento excel y crear archivo en disco c"
```

Salidas esperadas:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\salidas_doc_xls
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\acciones_grabadas
C:\Transcriptor2_Agent_Output
```

## API local para n8n

```powershell
.\scripts\start_command_agent_api.ps1
```

Endpoint:

```text
http://127.0.0.1:53320/agent/execute
```
