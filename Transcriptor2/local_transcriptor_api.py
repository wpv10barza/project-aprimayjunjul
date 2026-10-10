import os
import sys
import time
import tempfile
import hashlib
import traceback
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse

load_dotenv()

APP_NAME = "Transcriptor Local Whisper API"
DEFAULT_MODEL = os.getenv("WHISPER_MODEL", "medium")
DEFAULT_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "es") or None
API_KEY = os.getenv("TRANSCRIPTOR_API_KEY", "").strip()
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2048"))

app = FastAPI(title=APP_NAME, version="1.0.0")
_model_cache = {}
_device_info = None


def _check_auth(x_api_key: Optional[str]) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta o ausente")


def _get_device():
    global _device_info
    if _device_info is not None:
        return _device_info
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            _device_info = {"device": "cuda", "gpu": name, "fp16": True}
        else:
            _device_info = {"device": "cpu", "gpu": None, "fp16": False}
    except Exception:
        _device_info = {"device": "cpu", "gpu": None, "fp16": False}
    return _device_info


def _load_model(model_name: str):
    model_name = (model_name or DEFAULT_MODEL).strip()
    device = _get_device()["device"]
    key = f"{model_name}:{device}"
    if key not in _model_cache:
        import whisper
        _model_cache[key] = whisper.load_model(model_name, device=device)
    return _model_cache[key]


def _safe_suffix(filename: str) -> str:
    suffix = Path(filename or "audio").suffix.lower()
    if suffix and len(suffix) <= 10:
        return suffix
    return ".bin"


@app.get("/health")
def health(x_api_key: Optional[str] = Header(default=None)):
    _check_auth(x_api_key)
    return {
        "ok": True,
        "service": APP_NAME,
        "device": _get_device(),
        "loaded_models": list(_model_cache.keys()),
        "default_model": DEFAULT_MODEL,
        "default_language": DEFAULT_LANGUAGE,
        "max_upload_mb": MAX_UPLOAD_MB,
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form(DEFAULT_MODEL),
    language: Optional[str] = Form(DEFAULT_LANGUAGE),
    task: str = Form("transcribe"),
    include_segments: bool = Form(False),
    x_api_key: Optional[str] = Header(default=None),
):
    _check_auth(x_api_key)

    task = (task or "transcribe").strip().lower()
    if task not in {"transcribe", "translate"}:
        raise HTTPException(status_code=400, detail="task debe ser transcribe o translate")

    suffix = _safe_suffix(file.filename)
    temp_path = None
    start = time.time()
    bytes_written = 0

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_UPLOAD_MB * 1024 * 1024:
                    raise HTTPException(status_code=413, detail=f"Archivo excede MAX_UPLOAD_MB={MAX_UPLOAD_MB}")
                tmp.write(chunk)

        if bytes_written == 0:
            raise HTTPException(status_code=400, detail="Archivo vacio")

        model_obj = _load_model(model)
        device = _get_device()
        result = model_obj.transcribe(
            temp_path,
            fp16=device["fp16"],
            language=(language or None),
            task=task,
        )

        text = (result.get("text") or "").strip()
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]
        payload = {
            "ok": True,
            "filename": file.filename,
            "bytes": bytes_written,
            "model": model,
            "language_requested": language,
            "language_detected": result.get("language"),
            "task": task,
            "device": device,
            "seconds": round(time.time() - start, 2),
            "sha256_text_16": digest,
            "transcripcion_whisper": text,
        }
        if include_segments:
            payload["segments"] = result.get("segments", [])
        return JSONResponse(payload)

    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": str(exc),
                "trace": traceback.format_exc(limit=3),
            },
        )
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("LOCAL_API_HOST", "127.0.0.1")
    port = int(os.getenv("LOCAL_API_PORT", "8765"))
    uvicorn.run("local_transcriptor_api:app", host=host, port=port, reload=False)
