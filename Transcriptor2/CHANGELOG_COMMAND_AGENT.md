# Cambios aplicados sobre el comprimido original

## Agregado

- Nuevo agente local Python para comandos Office/Disco C:
  - `services/command_agent_core.py`
  - `services/command_agent_api.py`
  - `services/command_agent_cli.py`
- Nuevo workflow n8n:
  - `n8n/workflow_transcriptor2_gemma_command_agent_fixed.json`
- Nueva whitelist de herramientas para Function Gemma:
  - `n8n/command_agent_tools.functiongemma.json`
- Nuevo instalador PowerShell con validación estricta:
  - `scripts/setup_command_agent.ps1`
  - `scripts/build_command_agent_exe.ps1`
  - `scripts/start_command_agent_api.ps1`
  - `scripts/run_command_agent_exe.ps1`
  - `scripts/test_command_agent_local.ps1`
  - `scripts/test_command_agent_api.ps1`
  - `scripts/test_n8n_command_agent_workflow.ps1`
- Carpetas base:
  - `mp3/`
  - `librery/`
  - `acciones_grabadas/`
  - `salidas_doc_xls/`
  - `dist_exe/`
  - `logs/`
- README técnico:
  - `README_COMMAND_AGENT_GEMMA_N8N.md`

## Corregido

- Se evita depender de `$LASTEXITCODE` viejo después de crear carpetas.
- Se usa `pyinstaller>=6.15,<7` para evitar el fallo de `pyinstaller==6.11.1` en Python reciente.
- Se agrega fallback local si Function Gemma no responde, para que n8n no se quede sin resultado funcional.
- Se separa el flujo Pocket AI/cámara del nuevo flujo Office/Disco C.
- Se evita ejecución arbitraria de comandos del sistema.

## Seguridad

- `disk.create_file` y `disk.create_folder` solo escriben en `C:\Transcriptor2_Agent_Output`.
- El modelo no puede elegir herramientas fuera de la whitelist.
- El agente no expone ejecución de `cmd`, `powershell`, `bash` ni rutas arbitrarias.

## V3 - Correccion PowerShell StrictMode y carpeta interna

- Corregido error: `No se encuentra la propiedad 'Exe' en este objeto`.
- Causa: `Resolve-PythonExe` devolvia un Hashtable y `Set-StrictMode -Version Latest` no permitia acceder con `$Py.Exe`.
- Solucion: ahora devuelve `[pscustomobject]` y el setup puede crear el venv sin fallar.
- Mejora: los scripts ya no dependen de una ruta hardcodeada si se ejecutan desde otra carpeta. Si no pasas `-BaseDir`, usan automaticamente la raiz real del paquete donde esta la carpeta `scripts`.
