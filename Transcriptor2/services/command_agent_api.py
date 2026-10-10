#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from command_agent_core import execute_command, system_health, voice_input_dir, sanitize_filename

API_KEY = os.getenv("COMMAND_AGENT_API_KEY", "").strip()

app = FastAPI(title="Transcriptor2 Command Agent API", version="2.0.0")


class CommandRequest(BaseModel):
    command: str = Field(default="crear documento excel")
    use_latest_voice: bool = False
    use_gemma: bool = True
    request_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


def check_key(x_api_key: Optional[str]) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="COMMAND_AGENT_API_KEY incorrecta o ausente")


@app.get("/health")
def health(x_api_key: Optional[str] = Header(default=None)):
    check_key(x_api_key)
    return system_health()


@app.post("/agent/execute")
def agent_execute(req: CommandRequest, x_api_key: Optional[str] = Header(default=None)):
    check_key(x_api_key)
    return JSONResponse(execute_command(req.command, req.use_latest_voice, req.use_gemma, req.context, req.request_id))


@app.post("/agent/upload")
async def agent_upload(
    file: UploadFile = File(...),
    command: str = Form(""),
    use_gemma: bool = Form(True),
    x_api_key: Optional[str] = Header(default=None),
):
    check_key(x_api_key)
    folder = voice_input_dir()
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_filename(file.filename or "upload.bin", "upload.bin")
    destination = folder / safe_name
    with destination.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    final_command = command or "agente usa el ultimo audio de ruta mp3"
    result = execute_command(final_command, use_latest_voice=True, use_gemma=use_gemma, context={"uploaded_file": str(destination)})
    result["uploaded_file"] = str(destination)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("COMMAND_AGENT_HOST", "127.0.0.1")
    port = int(os.getenv("COMMAND_AGENT_PORT", "53320"))
    uvicorn.run("command_agent_api:app", host=host, port=port, reload=False)
