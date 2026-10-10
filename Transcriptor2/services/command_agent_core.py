#!/usr/bin/env python3
"""Transcriptor2 local command agent.

Purpose:
- Receive a Spanish command from n8n, CLI, GUI, or uploaded/latest voice text.
- Ask local Function Gemma 270M to select a whitelisted tool.
- Execute only safe internal tools: create Excel, create Word, create folder, create text file.
- Record the action plan as JSON for audit/replay.

This file intentionally does NOT execute arbitrary shell commands.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

DEFAULT_BASE_DIR = r"D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
DEFAULT_VOICE_DIR = r"D:\118102025\Downloads\Nueva carpeta\Transcriptor2\mp3"
DEFAULT_DISK_C_BASE = r"C:\Transcriptor2_Agent_Output"

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma", ".mp4"}
TEXT_EXTENSIONS = {".txt", ".md", ".json"}


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def root_dir() -> Path:
    return Path(os.getenv("TRANSCRIPTOR2_BASE_DIR", DEFAULT_BASE_DIR))


def voice_input_dir() -> Path:
    return Path(os.getenv("VOICE_INPUT_DIR", DEFAULT_VOICE_DIR))


def output_dir() -> Path:
    return Path(os.getenv("OUTPUT_DIR", str(root_dir() / "salidas_doc_xls")))


def actions_dir() -> Path:
    return Path(os.getenv("ACTIONS_DIR", str(root_dir() / "acciones_grabadas")))


def disk_c_base() -> Path:
    return Path(os.getenv("DISK_C_BASE", DEFAULT_DISK_C_BASE))


def ensure_dirs() -> Dict[str, str]:
    dirs = {
        "base_dir": root_dir(),
        "voice_input_dir": voice_input_dir(),
        "output_dir": output_dir(),
        "actions_dir": actions_dir(),
        "disk_c_base": disk_c_base(),
        "logs_dir": root_dir() / "logs",
        "librery_dir": root_dir() / "librery",
        "dist_exe_dir": root_dir() / "dist_exe",
    }
    created: Dict[str, str] = {}
    for key, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        created[key] = str(path)
    return created


def sanitize_filename(name: str, default: str = "archivo") -> str:
    name = (name or default).strip().replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^A-Za-z0-9_.()\- áéíóúÁÉÍÓÚñÑ]", "_", name)
    name = re.sub(r"_+", "_", name).strip(" ._")
    return name or default


def safe_output_file(filename: str, suffix: str) -> Path:
    filename = sanitize_filename(filename, f"salida_{now_stamp()}{suffix}")
    if not filename.lower().endswith(suffix.lower()):
        filename += suffix
    return output_dir() / filename


def safe_disk_c_file(filename: str, suffix: str = ".txt") -> Path:
    """Create files only inside DISK_C_BASE, never arbitrary Windows C drive paths."""
    filename = sanitize_filename(filename, f"archivo_creado_{now_stamp()}{suffix}")
    if not Path(filename).suffix:
        filename += suffix
    # Intentionally ignore user-provided absolute path and store under a safe base.
    return disk_c_base() / filename


def latest_file(folder: Path, extensions: Optional[set[str]] = None) -> Optional[Path]:
    if not folder.exists():
        return None
    files: List[Path] = []
    for item in folder.iterdir():
        if not item.is_file():
            continue
        if extensions is None or item.suffix.lower() in extensions:
            files.append(item)
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def read_text_file(path: Path) -> str:
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in ("text", "command", "transcripcion_whisper", "transcription"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        except Exception:
            pass
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=enc).strip()
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="ignore").strip()


def transcribe_audio_if_possible(audio_path: Path) -> Dict[str, Any]:
    """Try local Whisper CLI if available. Returns a dict with ok/text/error."""
    cli = os.getenv("TRANSCRIPTOR_CLI_PATH", "").strip()
    candidates = []
    if cli:
        candidates.append(Path(cli))
    candidates.append(root_dir() / "local_whisper_cli.py")
    candidates.append(Path(__file__).resolve().parents[1] / "local_whisper_cli.py")

    cli_path = next((p for p in candidates if p.exists()), None)
    if cli_path is None:
        return {
            "ok": False,
            "audio": str(audio_path),
            "error": "No se encontro local_whisper_cli.py. Coloca un TXT con la transcripcion en la carpeta mp3 o configura TRANSCRIPTOR_CLI_PATH.",
        }

    txt_output = audio_path.with_name(audio_path.stem + "_transcrito.txt")
    json_output = audio_path.with_name(audio_path.stem + "_transcrito.json")
    cmd = [
        sys.executable,
        str(cli_path),
        "--audio",
        str(audio_path),
        "--modelo",
        os.getenv("WHISPER_MODEL", "base"),
        "--language",
        os.getenv("WHISPER_LANGUAGE", "es"),
        "--txt-output",
        str(txt_output),
        "--json-output",
        str(json_output),
    ]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=int(os.getenv("WHISPER_TIMEOUT", "900")))
        if proc.returncode != 0:
            return {"ok": False, "audio": str(audio_path), "returncode": proc.returncode, "stderr": proc.stderr[-4000:], "stdout": proc.stdout[-4000:]}
        text = read_text_file(txt_output) if txt_output.exists() else ""
        return {"ok": True, "audio": str(audio_path), "txt_output": str(txt_output), "json_output": str(json_output), "text": text}
    except Exception as exc:
        return {"ok": False, "audio": str(audio_path), "error": str(exc), "trace": traceback.format_exc(limit=2)}


def get_latest_voice_command() -> Dict[str, Any]:
    folder = voice_input_dir()
    folder.mkdir(parents=True, exist_ok=True)
    latest = latest_file(folder, TEXT_EXTENSIONS | AUDIO_EXTENSIONS)
    if latest is None:
        return {"ok": False, "folder": str(folder), "error": "No hay TXT/audio en la carpeta mp3."}
    if latest.suffix.lower() in TEXT_EXTENSIONS:
        return {"ok": True, "source_type": "text", "path": str(latest), "text": read_text_file(latest)}
    result = transcribe_audio_if_possible(latest)
    result["source_type"] = "audio"
    result["path"] = str(latest)
    return result


def tool_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "office.create_xlsx",
            "description": "Crea un archivo Excel .xlsx con OpenPyXL en la carpeta salidas_doc_xls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "title": {"type": "string"},
                    "rows": {"type": "array", "items": {"type": "array"}},
                },
                "required": [],
            },
        },
        {
            "name": "office.create_docx",
            "description": "Crea un documento Word .docx en la carpeta salidas_doc_xls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "title": {"type": "string"},
                    "paragraphs": {"type": "array", "items": {"type": "string"}},
                },
                "required": [],
            },
        },
        {
            "name": "office.create_docx_xlsx_bundle",
            "description": "Crea un Word y un Excel juntos, usando el mismo comando como contenido base.",
            "parameters": {"type": "object", "properties": {"base_name": {"type": "string"}, "title": {"type": "string"}}, "required": []},
        },
        {
            "name": "disk.create_file",
            "description": "Crea un archivo de texto seguro en C:\\Transcriptor2_Agent_Output.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
                "required": [],
            },
        },
        {
            "name": "disk.create_folder",
            "description": "Crea una carpeta vacia segura dentro de C:\\Transcriptor2_Agent_Output.",
            "parameters": {"type": "object", "properties": {"folder_name": {"type": "string"}}, "required": []},
        },
        {
            "name": "agent.execute_plan",
            "description": "Ejecuta varias acciones internas en orden. Usar cuando el usuario pida Excel y archivo/carpeta en la misma frase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "actions": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"tool_name": {"type": "string"}, "arguments": {"type": "object"}}},
                    }
                },
                "required": ["actions"],
            },
        },
        {
            "name": "system.health",
            "description": "Devuelve estado local del agente, rutas y disponibilidad de carpetas.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    ]


def deterministic_tool_call(command: str, reason: str = "fallback local") -> Dict[str, Any]:
    text = (command or "").lower()
    wants_excel = any(w in text for w in ["excel", "xlsx", "hoja de calculo", "hoja de cálculo", "libro"])
    wants_word = any(w in text for w in ["word", "docx"]) or ("documento" in text and not wants_excel)
    wants_file = any(w in text for w in ["archivo", "fichero", "txt", "disco c", "unidad c"])
    wants_folder = any(w in text for w in ["carpeta", "directorio"]) and any(w in text for w in ["vacia", "vacía", "crear"])
    title = "Documento generado por Gemma"

    actions: List[Dict[str, Any]] = []
    if wants_excel:
        actions.append({"tool_name": "office.create_xlsx", "arguments": {"title": title}})
    if wants_word and not wants_excel:
        actions.append({"tool_name": "office.create_docx", "arguments": {"title": title}})
    elif wants_word and wants_excel:
        # Excel already in plan; add Word explicitly.
        actions.append({"tool_name": "office.create_docx", "arguments": {"title": title}})
    if wants_folder:
        actions.append({"tool_name": "disk.create_folder", "arguments": {"folder_name": "carpeta_vacia_gemma"}})
    elif wants_file:
        actions.append({"tool_name": "disk.create_file", "arguments": {"filename": "archivo_creado_por_gemma.txt"}})

    if len(actions) > 1:
        return {"tool_name": "agent.execute_plan", "arguments": {"actions": actions}, "confidence": 0.55, "reason": reason}
    if len(actions) == 1:
        return {"tool_name": actions[0]["tool_name"], "arguments": actions[0]["arguments"], "confidence": 0.55, "reason": reason}
    if any(w in text for w in ["estado", "health", "status"]):
        return {"tool_name": "system.health", "arguments": {}, "confidence": 0.7, "reason": reason}
    return {"tool_name": "office.create_xlsx", "arguments": {"title": title}, "confidence": 0.3, "reason": reason + ": default excel"}


def call_function_gemma(command: str, request_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = os.getenv("FUNCTION_GEMMA_TOOL_URL", "http://127.0.0.1:8090/tool-call").strip()
    api_key = os.getenv("FUNCTION_GEMMA_API_KEY", "").strip()
    if not url or requests is None:
        return deterministic_tool_call(command, "Function Gemma no disponible: requests/url ausente")
    body = {
        "request_id": request_id,
        "model": os.getenv("FUNCTION_GEMMA_MODEL", "google/functiongemma-270m-it"),
        "temperature": 0,
        "max_new_tokens": 256,
        "mode": "single_tool_call",
        "system": (
            "Eres Function Gemma para Tool Calling local. Devuelve solo JSON valido. "
            "No ejecutes comandos arbitrarios. Selecciona solo herramientas permitidas. "
            "Si el usuario pide varias acciones, usa agent.execute_plan."
        ),
        "user": {"text": command, "context": context or {}, "language": "es"},
        "tools": tool_definitions(),
        "strict_output_schema": {
            "type": "object",
            "required": ["tool_name", "arguments", "confidence", "reason"],
            "properties": {
                "tool_name": {"type": "string"},
                "arguments": {"type": "object"},
                "confidence": {"type": "number"},
                "reason": {"type": "string"},
            },
        },
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    try:
        res = requests.post(url, headers=headers, json=body, timeout=int(os.getenv("FUNCTION_GEMMA_TIMEOUT", "120")))
        res.raise_for_status()
        data = res.json()
        tool_name = data.get("tool_name") or (data.get("tool_call") or {}).get("tool_name")
        arguments = data.get("arguments") or (data.get("tool_call") or {}).get("arguments") or {}
        if tool_name not in {t["name"] for t in tool_definitions()}:
            return deterministic_tool_call(command, f"Function Gemma devolvio tool no permitido: {tool_name}")
        return {
            "tool_name": tool_name,
            "arguments": arguments,
            "confidence": float(data.get("confidence") or 0),
            "reason": data.get("reason") or "Function Gemma local",
            "gemma_raw": {k: v for k, v in data.items() if k not in {"raw_model_output"}},
        }
    except Exception as exc:
        return deterministic_tool_call(command, f"Function Gemma no respondio: {exc}")


def create_xlsx(arguments: Dict[str, Any], command: str) -> Dict[str, Any]:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    ensure_dirs()
    title = str(arguments.get("title") or "Documento Excel generado por Gemma")
    filename = str(arguments.get("filename") or f"excel_gemma_{now_stamp()}.xlsx")
    path = safe_output_file(filename, ".xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:C1")
    ws["A1"].alignment = Alignment(horizontal="center")

    rows = arguments.get("rows")
    if not isinstance(rows, list) or not rows:
        rows = [
            ["Campo", "Valor", "Observacion"],
            ["Comando", command, "Entrada procesada"],
            ["Fecha", datetime.now().isoformat(timespec="seconds"), "Hora local"],
            ["Modelo", "google/functiongemma-270m-it", "Tool Calling local"],
            ["Salida", str(path), "Archivo creado con OpenPyXL"],
        ]
    start_row = 3
    for r_index, row in enumerate(rows, start=start_row):
        if not isinstance(row, list):
            row = [str(row)]
        for c_index, value in enumerate(row, start=1):
            cell = ws.cell(row=r_index, column=c_index, value=value)
            if r_index == start_row:
                cell.font = Font(bold=True)
    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 28
    wb.save(path)
    return {"ok": True, "type": "xlsx", "path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}


def create_docx(arguments: Dict[str, Any], command: str) -> Dict[str, Any]:
    ensure_dirs()
    title = str(arguments.get("title") or "Documento Word generado por Gemma")
    filename = str(arguments.get("filename") or f"documento_gemma_{now_stamp()}.docx")
    path = safe_output_file(filename, ".docx")
    paragraphs = arguments.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        paragraphs = [
            "Documento creado por el agente local Transcriptor2.",
            f"Comando procesado: {command}",
            f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        ]
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(title, 0)
        for paragraph in paragraphs:
            doc.add_paragraph(str(paragraph))
        doc.save(path)
        return {"ok": True, "type": "docx", "path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}
    except Exception as exc:
        fallback = path.with_suffix(".txt")
        fallback.write_text(title + "\n\n" + "\n".join(map(str, paragraphs)), encoding="utf-8")
        return {"ok": False, "type": "docx", "error": str(exc), "fallback_txt": str(fallback), "exists": fallback.exists()}


def create_disk_file(arguments: Dict[str, Any], command: str) -> Dict[str, Any]:
    ensure_dirs()
    filename = str(arguments.get("filename") or f"archivo_creado_por_gemma_{now_stamp()}.txt")
    path = safe_disk_c_file(filename, ".txt")
    content = str(arguments.get("content") or "")
    if not content.strip():
        content = (
            "Archivo creado por Transcriptor2 CommandAgent\n"
            f"Fecha: {datetime.now().isoformat(timespec='seconds')}\n"
            f"Comando: {command}\n"
            "Nota: por seguridad, se guarda dentro de C:\\Transcriptor2_Agent_Output.\n"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "type": "disk_file", "path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}


def create_disk_folder(arguments: Dict[str, Any], command: str) -> Dict[str, Any]:
    ensure_dirs()
    folder_name = sanitize_filename(str(arguments.get("folder_name") or f"carpeta_vacia_gemma_{now_stamp()}"), "carpeta_vacia")
    path = disk_c_base() / folder_name
    path.mkdir(parents=True, exist_ok=True)
    marker = path / "README_creado_por_agente.txt"
    if not marker.exists() and str(arguments.get("with_readme", "true")).lower() != "false":
        marker.write_text(f"Carpeta creada por Transcriptor2 CommandAgent.\nComando: {command}\n", encoding="utf-8")
    return {"ok": True, "type": "disk_folder", "path": str(path), "exists": path.exists()}


def system_health() -> Dict[str, Any]:
    dirs = ensure_dirs()
    return {"ok": True, "service": "Transcriptor2 CommandAgent", "dirs": dirs, "tools": [t["name"] for t in tool_definitions()]}


def execute_tool(tool_name: str, arguments: Dict[str, Any], command: str) -> Dict[str, Any]:
    arguments = arguments or {}
    if tool_name == "office.create_xlsx":
        return create_xlsx(arguments, command)
    if tool_name == "office.create_docx":
        return create_docx(arguments, command)
    if tool_name == "office.create_docx_xlsx_bundle":
        base_name = sanitize_filename(str(arguments.get("base_name") or f"bundle_gemma_{now_stamp()}"), "bundle")
        title = str(arguments.get("title") or "Paquete DOCX/XLSX generado por Gemma")
        return {
            "ok": True,
            "type": "bundle",
            "results": [
                create_docx({"filename": base_name + ".docx", "title": title}, command),
                create_xlsx({"filename": base_name + ".xlsx", "title": title}, command),
            ],
        }
    if tool_name == "disk.create_file":
        return create_disk_file(arguments, command)
    if tool_name == "disk.create_folder":
        return create_disk_folder(arguments, command)
    if tool_name == "agent.execute_plan":
        results = []
        for action in arguments.get("actions") or []:
            child_tool = action.get("tool_name")
            child_args = action.get("arguments") or {}
            if child_tool == "agent.execute_plan":
                results.append({"ok": False, "error": "Nested agent.execute_plan no permitido"})
            elif child_tool not in {t["name"] for t in tool_definitions()}:
                results.append({"ok": False, "error": f"Tool no permitido: {child_tool}"})
            else:
                results.append(execute_tool(child_tool, child_args, command))
        return {"ok": all(r.get("ok") for r in results), "type": "plan", "results": results}
    if tool_name == "system.health":
        return system_health()
    return {"ok": False, "error": f"Tool no soportado: {tool_name}"}


def record_action_plan(payload: Dict[str, Any]) -> str:
    ensure_dirs()
    path = actions_dir() / f"action_plan_{payload.get('request_id','req')}_{now_stamp()}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def execute_command(command: str = "", use_latest_voice: bool = False, use_gemma: bool = True, context: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
    ensure_dirs()
    request_id = request_id or f"req_{int(time.time() * 1000)}"
    command = (command or "").strip()
    context = context or {}

    latest_info: Optional[Dict[str, Any]] = None
    if use_latest_voice or any(s in command.lower() for s in ["ultimo audio", "último audio", "ultima voz", "última voz", "ruta mp3"]):
        latest_info = get_latest_voice_command()
        if latest_info.get("ok") and latest_info.get("text"):
            # If the typed command only requests latest audio, the transcription becomes the executable command.
            command = str(latest_info.get("text")).strip() or command
        else:
            # Keep original command and expose the problem in response.
            context["latest_voice_error"] = latest_info

    if not command:
        command = "crear documento excel"

    tool_call = call_function_gemma(command, request_id, context) if use_gemma else deterministic_tool_call(command, "Gemma desactivado por parametro")
    result = execute_tool(tool_call["tool_name"], tool_call.get("arguments") or {}, command)

    response = {
        "ok": bool(result.get("ok")),
        "request_id": request_id,
        "command": command,
        "use_latest_voice": use_latest_voice,
        "latest_voice": latest_info,
        "model_policy": "Function Gemma local first; fallback deterministico local si el servicio no responde",
        "tool_call": {k: v for k, v in tool_call.items() if k != "gemma_raw"},
        "gemma_raw": tool_call.get("gemma_raw"),
        "result": result,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    response["action_plan_path"] = record_action_plan(response)
    return response
