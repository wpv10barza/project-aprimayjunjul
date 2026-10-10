# Transcriptor Local + n8n Oracle + Function Gemma Pocket AI

Paquete actualizado para dos usos:

1. Transcripcion local con Whisper conectada a n8n Oracle.
2. Flujo post-Routing de Pocket AI con Tool Calling local usando exclusivamente `google/functiongemma-270m-it`.

## Parte 1 - Transcripcion local

Copia esta carpeta a:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor
```

Instala:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1
```

Enviar resultado ya transcrito a n8n:

```powershell
.\send_transcription_to_n8n.ps1 `
  -TextPath "D:\118102025\Downloads\Nueva carpeta\Transcriptor\transcripcion_resumen.txt" `
  -WebhookUrl "https://carlospolo-n8n.duckdns.org/webhook-test/transcripcion-local"
```

## Parte 2 - Pocket AI post-Routing con Function Gemma

Archivo principal:

```text
README_FUNCTION_GEMMA_POCKET_AI.md
```

Workflow n8n para importar:

```text
n8n/workflow_function_gemma_pocket_ai_post_routing.json
```

Servicios agregados:

```text
services/function_gemma_agent.py
services/pocket_ai_executor_api.py
```

Docker Compose:

```bash
cd docker
docker compose -f docker-compose.functiongemma.yml up -d --build
```

Endpoint de prueba n8n:

```text
https://carlospolo-n8n.duckdns.org/webhook-test/pocket-ai/post-routing
```

Endpoint de produccion n8n:

```text
https://carlospolo-n8n.duckdns.org/webhook/pocket-ai/post-routing
```

## Notas clave

- La URL `/workflow/...` es solo para editar el workflow, no para recibir datos.
- Para recibir datos se usa un nodo Webhook.
- En pruebas usa `/webhook-test/...` con `Listen for test event`.
- En produccion activa el workflow y usa `/webhook/...`.
- El Tool Calling de Pocket AI no usa modelos cloud: solo Function Gemma local.

---

## Actualizacion agregada: Command Agent Office/Disco C

Para crear Excel, Word, archivos o carpetas desde n8n + Function Gemma, lee:

```text
README_COMMAND_AGENT_GEMMA_N8N.md
```

Workflow principal nuevo:

```text
n8n/workflow_transcriptor2_gemma_command_agent_fixed.json
```

Instalacion recomendada:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```


## Inventario de Google Drive

- Nombre: Transcriptor2.
- Propósito documentado: Transcriptor Local + n8n Oracle + Function Gemma Pocket AI.
- Periodo de archivos: 2026-06-10 a 2026-06-10.
- Tecnologías y formatos: .conf, .html, .json, .md, .ps1, .py, .sh, .txt, .yml.
- Estructura: CHANGELOG_COMMAND_AGENT.md, MANIFEST_COMMAND_AGENT_FIXED.txt, README.md, README_COMMAND_AGENT_GEMMA_N8N.md, README_FIX_V3_POWER_SHELL.md, README_FIX_V4_RUTA_TRANSCRIPTOR2.md, README_FIX_V5_EXE_PROPERTY.md, README_FUNCTION_GEMMA_POCKET_AI.md, docker, install.ps1, librery, local_transcriptor_api.py, local_whisper_cli.py, n8n, nginx, requirements.txt, requirements_command_agent.txt, requirements_function_gemma.txt, scripts, send_transcription_to_n8n.ps1, services, start_cloudflare_tunnel.ps1, start_server.ps1, test_local.ps1.
- Módulos principales: services/command_agent_api.py, services/function_gemma_agent.py, services/command_agent_core.py, services/pocket_ai_executor_api.py, services/command_agent_cli.py, local_whisper_cli.py, local_transcriptor_api.py.
- Origen: carpeta Drive `12G311dc0cFaVNEmZTT-9ZcCuJ9b5sHNE`.
- Archivos originales seleccionados: 47.
- Observaciones: se conserva el original de Drive cuando existen archivos excluidos o insumos no copiados. Se conserva cada proyecto por separado.
