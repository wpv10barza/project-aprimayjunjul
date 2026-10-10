# README - Post-Routing Function Gemma 270M + Pocket AI + n8n

Este modulo actualiza el comprimido para ejecutar el flujo post-Routing de Pocket AI en n8n. El objetivo es que n8n sea el orquestador central y que la seleccion de herramientas se haga de forma estricta con el modelo local preentrenado `google/functiongemma-270m-it`.

## Politica estricta del flujo

- Tool Calling post-Routing usa solo `google/functiongemma-270m-it` local.
- No se llama a OpenAI, Gemini cloud, Claude, Groq ni otro LLM externo.
- Ollama/LLM queda fuera de este flujo de invocacion de herramientas. Si existe en tu servidor, usalo para resumen u otras tareas, no para decidir herramientas de Pocket AI.
- n8n solo normaliza datos, llama al agente local Function Gemma, valida el JSON y ejecuta una funcion interna del repositorio Pocket AI mediante un executor local.

## Archivos agregados

```text
n8n/workflow_function_gemma_pocket_ai_post_routing.json
n8n/pocket_ai_tools.functiongemma.json
services/function_gemma_agent.py
services/pocket_ai_executor_api.py
requirements_function_gemma.txt
docker/docker-compose.functiongemma.yml
docker/function-gemma-agent.Dockerfile
docker/pocket-ai-executor.Dockerfile
nginx/functiongemma_pocket_ai.conf
scripts/test_n8n_functiongemma_postrouting.ps1
scripts/test_n8n_functiongemma_postrouting.sh
docs/architecture_8gb.png
```

## Arquitectura logica

```text
Cliente / App / Web / Telegram
        |
        v
Router semantico previo
        |
        v
n8n Webhook post-routing
        |
        v
Normalizar payload + lista blanca de tools
        |
        v
Function Gemma 270M local
        |
        v
JSON estricto: { tool_name, arguments, confidence, reason }
        |
        v
n8n valida whitelist + argumentos
        |
        v
Pocket AI Executor API
        |
        v
camera_stream.py / object_detection.py / system_status.py / file_storage.py
```

## Flujo de ejecucion paso a paso

### 1. El router semantico deriva la solicitud

El router anterior al workflow decide que la solicitud corresponde a Pocket AI. La entrada minima al Webhook debe ser JSON:

```json
{
  "request_id": "req_001",
  "router": {
    "route": "vision",
    "intent": "object_detection",
    "confidence": 0.91
  },
  "text": "detecta objetos en la camara 0 y guarda la imagen anotada",
  "media": {
    "camera_id": "0",
    "image_source": "latest_frame"
  },
  "context": {
    "user": "local_device"
  }
}
```

### 2. n8n normaliza el payload

El nodo `Normalizar payload y tools` transforma la entrada a este contrato interno:

```json
{
  "request_id": "req_001",
  "stage": "post_routing_normalized",
  "router": { "route": "vision", "intent": "object_detection" },
  "input": {
    "text": "detecta objetos en la camara 0 y guarda la imagen anotada",
    "media": { "camera_id": "0", "image_source": "latest_frame" },
    "context": {}
  },
  "function_gemma_request": {
    "model": "google/functiongemma-270m-it",
    "mode": "single_tool_call",
    "temperature": 0,
    "tools": ["lista blanca de herramientas"],
    "strict_output_schema": "tool_name + arguments"
  }
}
```

### 3. Inferencia local en Function Gemma

El nodo `Function Gemma 270M Tool Call` llama a:

```text
http://function-gemma-agent:8090/tool-call
```

El microservicio `services/function_gemma_agent.py` carga el modelo local `google/functiongemma-270m-it` con Transformers y devuelve solo JSON:

```json
{
  "ok": true,
  "request_id": "req_001",
  "model": "google/functiongemma-270m-it",
  "tool_name": "object_detection.detect_objects",
  "arguments": {
    "image_source": "latest_frame",
    "model": "yolov8n",
    "confidence_threshold": 0.35,
    "save_annotated": true
  },
  "confidence": 0.88,
  "reason": "vision request for object detection"
}
```

### 4. n8n valida el Tool Call

El nodo `Validar tool call` rechaza cualquier herramienta que no este en la whitelist:

```text
camera_stream.start_camera_stream
camera_stream.stop_camera_stream
object_detection.detect_objects
object_detection.start_realtime_detection
object_detection.stop_realtime_detection
system_status.get_status
file_storage.save_result
```

### 5. n8n ejecuta Pocket AI

El nodo `Ejecutar Pocket AI tool` llama a:

```text
http://pocket-ai-executor:8091/execute
```

El body enviado al executor es:

```json
{
  "request_id": "req_001",
  "tool_name": "object_detection.detect_objects",
  "arguments": {
    "image_source": "latest_frame",
    "model": "yolov8n",
    "confidence_threshold": 0.35,
    "save_annotated": true
  }
}
```

El executor busca el modulo real dentro del repositorio Pocket AI:

```text
/opt/pocket-ai/object_detection.py
```

y llama una funcion permitida, por ejemplo:

```python
detect_objects(image_source="latest_frame", model="yolov8n", confidence_threshold=0.35, save_annotated=True)
```

Si el modulo no expone una funcion compatible, intenta un fallback como script:

```text
python object_detection.py --json '{...}'
```

## Variables de entorno necesarias

En n8n:

```env
FUNCTION_GEMMA_AGENT_URL=http://function-gemma-agent:8090/tool-call
FUNCTION_GEMMA_API_KEY=CAMBIA_ESTA_CLAVE
POCKET_AI_EXECUTOR_URL=http://pocket-ai-executor:8091/execute
POCKET_AI_API_KEY=CAMBIA_ESTA_CLAVE
```

En Docker Compose:

```env
FUNCTION_GEMMA_API_KEY=CAMBIA_ESTA_CLAVE
POCKET_AI_API_KEY=CAMBIA_ESTA_CLAVE
POCKET_AI_REPO=/opt/pocket-ai
FUNCTION_GEMMA_DEVICE=cpu
```

## Levantar servicios locales

Desde la carpeta del comprimido en Ubuntu:

```bash
cd docker
docker compose -f docker-compose.functiongemma.yml up -d --build
```

Verifica:

```bash
curl http://localhost:8090/health
curl http://localhost:8091/health
```

## Importar workflow en n8n

1. Abre n8n.
2. Importa `n8n/workflow_function_gemma_pocket_ai_post_routing.json`.
3. Revisa los nodos HTTP y confirma las variables de entorno.
4. En el Webhook usa:

```text
POST /webhook-test/pocket-ai/post-routing
```

para pruebas, y luego:

```text
POST /webhook/pocket-ai/post-routing
```

cuando el workflow este activo.

## Prueba desde Windows PowerShell

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor"
.\scripts\test_n8n_functiongemma_postrouting.ps1 `
  -WebhookUrl "https://carlospolo-n8n.duckdns.org/webhook-test/pocket-ai/post-routing"
```

## Respuesta esperada

```json
{
  "ok": true,
  "request_id": "req_001",
  "workflow": "post-routing-functiongemma-pocket-ai",
  "policy": "tool_calling_model_local_only_google_functiongemma_270m_it",
  "executed_tool": "object_detection.detect_objects",
  "result": {
    "objects": [],
    "annotated_image": "..."
  },
  "error": null
}
```

## Ajuste importante para tu servidor de 8 GB RAM

Para 8 GB de RAM, manten este flujo por etapas:

1. n8n solo orquesta.
2. Function Gemma 270M queda como microservicio ligero para Tool Calling.
3. Whisper y vision no deben ejecutarse simultaneamente si saturan RAM.
4. Usa modelos pequenos para deteccion, por ejemplo `yolov8n` o equivalente.
5. Si usas MinIO/PostgreSQL/Nginx en el mismo servidor, limita memoria de contenedores.

## Seguridad minima

- Cambia `FUNCTION_GEMMA_API_KEY` y `POCKET_AI_API_KEY`.
- No expongas `/execute` a Internet sin Nginx, TLS, API key e IP allowlist.
- Mantener whitelist evita que el modelo ejecute scripts arbitrarios.
- El executor solo debe apuntar a `POCKET_AI_REPO` y no aceptar rutas externas.
