#!/usr/bin/env python3
"""Local Function Gemma 270M tool-call microservice.

This service is intentionally small and local-first. It receives a normalized
post-routing request from n8n and returns a strict JSON tool call.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

MODEL_ID = os.getenv("FUNCTION_GEMMA_MODEL", "google/functiongemma-270m-it")
API_KEY = os.getenv("FUNCTION_GEMMA_API_KEY", "change-me")
DEVICE = os.getenv("FUNCTION_GEMMA_DEVICE", "auto")

app = FastAPI(title="Function Gemma Tool Caller", version="1.0.0")
_pipe = None

class ToolDef(BaseModel):
    name: str
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ToolCallRequest(BaseModel):
    request_id: str
    model: str = MODEL_ID
    temperature: float = 0
    max_new_tokens: int = 256
    mode: str = "single_tool_call"
    system: str
    user: Dict[str, Any]
    tools: List[ToolDef]
    strict_output_schema: Optional[Dict[str, Any]] = None


def check_key(x_api_key: Optional[str]) -> None:
    if API_KEY and API_KEY != "change-me" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid x-api-key")


def load_pipeline():
    global _pipe
    if _pipe is not None:
        return _pipe
    from transformers import pipeline
    kwargs: Dict[str, Any] = {"model": MODEL_ID}
    if DEVICE == "cpu":
        kwargs["device"] = -1
    _pipe = pipeline("text-generation", **kwargs)
    return _pipe


def build_prompt(req: ToolCallRequest) -> str:
    tools_json = json.dumps([t.model_dump() for t in req.tools], ensure_ascii=False)
    user_json = json.dumps(req.user, ensure_ascii=False)
    schema_json = json.dumps(req.strict_output_schema or {}, ensure_ascii=False)
    return (
        f"{req.system}\n\n"
        "Available tools JSON:\n"
        f"{tools_json}\n\n"
        "User and router payload JSON:\n"
        f"{user_json}\n\n"
        "Required output schema JSON:\n"
        f"{schema_json}\n\n"
        "Return only valid JSON. Example: "
        "{\"tool_name\":\"system_status.get_status\",\"arguments\":{\"scope\":\"all\"},\"confidence\":0.9,\"reason\":\"status request\"}"
    )


def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def deterministic_fallback(req: ToolCallRequest, reason: str) -> Dict[str, Any]:
    text = str(req.user.get("text") or "").lower()
    media = req.user.get("media") or {}
    allowed = {t.name for t in req.tools}
    if "status" in text or "estado" in text:
        name = "system_status.get_status"
        args = {"scope": "all"}
    elif "stop" in text and "detect" in text:
        name = "object_detection.stop_realtime_detection"
        args = {"job_id": media.get("job_id") or req.user.get("job_id") or "unknown"}
    elif "stream" in text and ("detect" in text or "objeto" in text or "object" in text):
        name = "object_detection.start_realtime_detection"
        args = {"stream_id": media.get("stream_id") or "default", "model": "yolov8n", "confidence_threshold": 0.35, "fps_limit": 5}
    elif "camera" in text or "camara" in text:
        name = "camera_stream.start_camera_stream"
        args = {"camera_id": str(media.get("camera_id") or 0), "resolution": "640x480", "fps": 15}
    else:
        name = "object_detection.detect_objects"
        args = {"image_source": media.get("image_source") or media.get("stream_id") or "latest_frame", "model": "yolov8n", "confidence_threshold": 0.35, "save_annotated": True}
    if name not in allowed:
        name = next(iter(allowed))
        args = {}
    return {"tool_name": name, "arguments": args, "confidence": 0.35, "reason": f"fallback: {reason}"}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "model": MODEL_ID, "service": "function-gemma-agent"}


@app.post("/tool-call")
def tool_call(req: ToolCallRequest, x_api_key: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    check_key(x_api_key)
    allowed = {t.name for t in req.tools}
    raw_output = ""
    try:
        pipe = load_pipeline()
        prompt = build_prompt(req)
        out = pipe(prompt, max_new_tokens=req.max_new_tokens, do_sample=False, temperature=req.temperature)
        raw_output = out[0].get("generated_text", "")
        if raw_output.startswith(prompt):
            raw_output = raw_output[len(prompt):].strip()
        parsed = extract_json(raw_output)
    except Exception as exc:
        parsed = deterministic_fallback(req, str(exc))

    tool_name = parsed.get("tool_name")
    if tool_name not in allowed:
        raise HTTPException(status_code=422, detail={"error": "Tool not allowed", "tool_name": tool_name, "raw_model_output": raw_output})
    args = parsed.get("arguments") or {}
    if not isinstance(args, dict):
        raise HTTPException(status_code=422, detail="arguments must be an object")
    return {
        "ok": True,
        "request_id": req.request_id,
        "model": MODEL_ID,
        "tool_name": tool_name,
        "arguments": args,
        "confidence": float(parsed.get("confidence") or 0),
        "reason": parsed.get("reason") or "",
        "raw_model_output": raw_output[-2000:]
    }
