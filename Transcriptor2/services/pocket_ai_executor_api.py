#!/usr/bin/env python3
"""Pocket AI executor API for whitelisted local repository functions."""
import importlib.util
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

API_KEY = os.getenv("POCKET_AI_API_KEY", "change-me")
POCKET_AI_REPO = Path(os.getenv("POCKET_AI_REPO", "/opt/pocket-ai")).resolve()
TOOLS_PATH = Path(os.getenv("POCKET_AI_TOOLS_JSON", "/app/pocket_ai_tools.functiongemma.json"))

app = FastAPI(title="Pocket AI Executor", version="1.0.0")

class ExecuteRequest(BaseModel):
    request_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


def check_key(x_api_key: Optional[str]) -> None:
    if API_KEY and API_KEY != "change-me" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid x-api-key")


def load_tools() -> Dict[str, Any]:
    with TOOLS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {t["name"]: t for t in data["tools"]}


def import_module_from_file(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_python_function(module_path: Path, candidates, args: Dict[str, Any]) -> Any:
    module = import_module_from_file(module_path)
    for name in candidates:
        fn = getattr(module, name, None)
        if not callable(fn):
            continue
        if name == "main":
            continue
        sig = inspect.signature(fn)
        filtered = {k: v for k, v in args.items() if k in sig.parameters}
        return fn(**filtered)
    raise AttributeError(f"No callable function found in {module_path.name}. Candidates: {candidates}")


def call_script_fallback(module_path: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(args, ensure_ascii=False)
    proc = subprocess.run(
        [sys.executable, str(module_path), "--json", payload],
        cwd=str(module_path.parent),
        text=True,
        capture_output=True,
        timeout=int(os.getenv("POCKET_AI_TOOL_TIMEOUT", "120"))
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout[-8000:], "stderr": proc.stderr[-8000:]}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "repo": str(POCKET_AI_REPO), "service": "pocket-ai-executor"}


@app.post("/execute")
def execute(req: ExecuteRequest, x_api_key: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    check_key(x_api_key)
    tools = load_tools()
    if req.tool_name not in tools:
        raise HTTPException(status_code=422, detail=f"Tool not whitelisted: {req.tool_name}")
    spec = tools[req.tool_name]
    module_path = (POCKET_AI_REPO / spec["module"]).resolve()
    if not module_path.exists():
        raise HTTPException(status_code=404, detail=f"Pocket AI module not found: {module_path}")
    if POCKET_AI_REPO not in module_path.parents and module_path != POCKET_AI_REPO:
        raise HTTPException(status_code=403, detail="Unsafe module path")
    try:
        result = call_python_function(module_path, spec.get("function_candidates", []), req.arguments)
    except Exception as import_exc:
        result = {"fallback_script": True, "import_error": str(import_exc), "script_result": call_script_fallback(module_path, req.arguments)}
    return {"ok": True, "request_id": req.request_id, "tool_name": req.tool_name, "arguments": req.arguments, "result": result}
