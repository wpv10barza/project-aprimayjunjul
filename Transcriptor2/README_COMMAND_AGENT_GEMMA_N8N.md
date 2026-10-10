# Transcriptor2 - n8n + Function Gemma + Command Agent Office/Disco C

## Objetivo corregido

Este paquete agrega un flujo estable para que n8n reciba una orden como:

```text
crear documento excel
crear archivo en disco c
agente transcribe ultimo audio de ruta D:\118102025\Downloads\Nueva carpeta\Transcriptor2\mp3
```

y la ejecute mediante un agente Python local controlado por Function Gemma 270M.

El flujo final queda así:

```text
n8n Webhook
  -> normaliza comando JSON
  -> llama al CommandAgent Python local
  -> CommandAgent consulta Function Gemma 270M local para seleccionar herramienta
  -> valida whitelist de herramientas
  -> ejecuta OpenPyXL / python-docx / creación segura de archivo o carpeta
  -> graba action_plan JSON
  -> devuelve rutas generadas a n8n
```

## Corrección principal

El ZIP anterior estaba orientado a Pocket AI/cámara/detección de objetos. Esta actualización agrega un módulo específico para Office/Disco C:

```text
services/command_agent_core.py
services/command_agent_api.py
services/command_agent_cli.py
requirements_command_agent.txt
.env.command_agent.example
n8n/workflow_transcriptor2_gemma_command_agent_fixed.json
n8n/command_agent_tools.functiongemma.json
scripts/setup_command_agent.ps1
scripts/build_command_agent_exe.ps1
scripts/start_command_agent_api.ps1
scripts/run_command_agent_exe.ps1
scripts/test_command_agent_local.ps1
scripts/test_command_agent_api.ps1
scripts/test_n8n_command_agent_workflow.ps1
scripts/start_command_agent_cloudflare_tunnel.ps1
```

## Rutas usadas

Ruta hardcodeada para último audio/TXT:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\mp3
```

Salidas de Excel/Word:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\salidas_doc_xls
```

Planes de acción grabados:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\acciones_grabadas
```

Archivo/carpeta en Disco C, por seguridad:

```text
C:\Transcriptor2_Agent_Output
```

> Importante: el agente no escribe libremente en cualquier parte de `C:\`. Para evitar daños, todo lo de Disco C se redirige a `C:\Transcriptor2_Agent_Output`.

## Instalación limpia en Windows

Extrae el ZIP en:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

Abre PowerShell dentro de esa carpeta:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
Get-ChildItem -Recurse -File | Unblock-File
```

Crea carpetas, venv aislado en `librery`, instala librerías y compila EXE:

```powershell
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

Esto debe generar:

```text
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\librery\venv_command_agent
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\dist_exe\CommandAgent.exe
D:\118102025\Downloads\Nueva carpeta\Transcriptor2\dist_exe\CommandAgentAPI.exe
```

## Prueba local sin n8n

Crear Excel:

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear documento excel"
```

Crear archivo en Disco C seguro:

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear archivo en disco c"
```

Crear ambas cosas:

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear documento excel y crear archivo en disco c"
```

Usar el último TXT/audio de la carpeta `mp3`:

```powershell
.\scripts\run_command_agent_exe.ps1 -Latest -Command "agente transcribe ultimo audio de ruta D:\118102025\Downloads\Nueva carpeta\Transcriptor2\mp3"
```

Si el último archivo es `.txt`, lo lee directamente. Si es audio real `.mp3/.wav/.m4a`, intentará usar `local_whisper_cli.py`. Si Whisper no está instalado, coloca un `.txt` con la transcripción en la carpeta `mp3` para probar el flujo Office/Disco C.

## Activar API local para n8n

En una ventana de PowerShell:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
.\scripts\start_command_agent_api.ps1
```

Endpoint local:

```text
http://127.0.0.1:53320/agent/execute
```

Prueba API:

```powershell
.\scripts\test_command_agent_api.ps1
```

## Activar Function Gemma

El CommandAgent intenta llamar a:

```text
http://127.0.0.1:8090/tool-call
```

con el modelo:

```text
google/functiongemma-270m-it
```

Si Function Gemma no responde, el agente no se bloquea: usa un fallback determinístico local para seguir creando Excel, Word, archivo o carpeta. En el `action_plan` queda registrado el motivo.

## Importar workflow n8n

Importa:

```text
n8n/workflow_transcriptor2_gemma_command_agent_fixed.json
```

Webhook de prueba:

```text
https://carlospolo-n8n.duckdns.org/webhook-test/voice-office/gemma-command
```

Webhook de producción:

```text
https://carlospolo-n8n.duckdns.org/webhook/voice-office/gemma-command
```

Payload mínimo:

```json
{
  "command": "crear documento excel y crear archivo en disco c",
  "service_url": "http://127.0.0.1:53320/agent/execute",
  "use_latest_voice": false,
  "use_gemma": true
}
```

## Si n8n corre en Oracle

Oracle no puede llamar directamente a `127.0.0.1` de tu PC Windows. En ese caso:

1. Inicia el API local:

```powershell
.\scripts\start_command_agent_api.ps1
```

2. En otra ventana abre tunnel:

```powershell
.\scripts\start_command_agent_cloudflare_tunnel.ps1
```

3. Copia la URL `https://xxxx.trycloudflare.com` y úsala como:

```text
https://xxxx.trycloudflare.com/agent/execute
```

4. Envía a n8n:

```powershell
$WebhookUrl = "https://carlospolo-n8n.duckdns.org/webhook-test/voice-office/gemma-command"
$body = @{
  command = "crear documento excel y crear archivo en disco c"
  service_url = "https://xxxx.trycloudflare.com/agent/execute"
  use_latest_voice = $false
  use_gemma = $true
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri $WebhookUrl -Method POST -ContentType "application/json" -Body $body
```

## Herramientas permitidas

Function Gemma solo puede seleccionar estas herramientas:

```text
office.create_xlsx
office.create_docx
office.create_docx_xlsx_bundle
disk.create_file
disk.create_folder
agent.execute_plan
system.health
```

No hay ejecución arbitraria de `cmd`, `powershell`, `bash` ni scripts externos. Esto evita que una orden de voz pueda dañar tu sistema.

## Diferencia frente al ZIP anterior

El ZIP anterior tenía el flujo Pocket AI post-routing para cámara/detección:

```text
camera_stream.py
object_detection.py
system_status.py
file_storage.py
```

Este ZIP conserva ese módulo, pero agrega un segundo flujo específico para Office/Disco C:

```text
n8n -> CommandAgent Python -> Function Gemma -> OpenPyXL / DOCX / archivo seguro en C
```

También corrige la ejecución inicial para evitar falsos `[OK]` cuando `pip` o PyInstaller fallan. El instalador se detiene si ocurre un error real.

## Fix anti-bloqueo en n8n

El nodo HTTP `Ejecutar agente local Office/DiscoC` tiene `continueOnFail=true`. Si el API local no responde, el workflow no queda colgado sin respuesta: devuelve un JSON con `ok=false`, `error` y una pista para revisar `service_url`, tunnel Cloudflare o estado de `CommandAgentAPI`.

---

## Fix V4 - Ruta fija corregida

La ruta base corregida del paquete es:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

Los scripts `setup_command_agent.ps1`, `run_command_agent_exe.ps1`, `start_command_agent_api.ps1`, `build_command_agent_exe.ps1`, `create_empty_folders.ps1` y `test_command_agent_local.ps1` usan esa ruta por defecto. Esto evita que el entorno se cree en `Transcriptor2\Transcriptor2` cuando el ZIP queda anidado por error.

Tambien se corrigio el bug de PowerShell donde `Resolve-PythonExe` mandaba texto al pipeline y despues `$Py.Exe` fallaba con:

```text
No se encuentra la propiedad 'Exe' en este objeto.
```
