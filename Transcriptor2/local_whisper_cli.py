import os
import sys
import json
import time
import argparse
import warnings
from pathlib import Path
from shutil import which

warnings.filterwarnings("ignore")


def check_ffmpeg():
    if which("ffmpeg") is None:
        raise RuntimeError("FFmpeg no esta instalado o no esta en PATH. Instala FFmpeg con winget install --id Gyan.FFmpeg -e")


def detect_device():
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", torch.cuda.get_device_name(0), True
    except Exception:
        pass
    return "cpu", None, False


def main():
    parser = argparse.ArgumentParser(description="Transcriptor Local Whisper CLI")
    parser.add_argument("--audio", required=True, help="Ruta del archivo de audio/video")
    parser.add_argument("--modelo", default=os.getenv("WHISPER_MODEL", "medium"), help="tiny, base, small, medium, large")
    parser.add_argument("--language", default=os.getenv("WHISPER_LANGUAGE", "es"), help="es, en, etc. Usa auto para autodetectar")
    parser.add_argument("--task", default="transcribe", choices=["transcribe", "translate"])
    parser.add_argument("--json-output", default="", help="Ruta JSON de salida opcional")
    parser.add_argument("--txt-output", default="", help="Ruta TXT de salida opcional")
    args = parser.parse_args()

    audio = Path(args.audio.strip('"').strip("'"))
    if not audio.exists():
        print(f"[ERROR] El archivo no existe: {audio}", file=sys.stderr)
        return 2

    try:
        check_ffmpeg()
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 3

    device, gpu_name, fp16 = detect_device()
    print("=" * 60)
    if device == "cuda":
        print(f"[MODO GPU] NVIDIA detectada: {gpu_name}")
    else:
        print("[MODO CPU] No se detecto GPU NVIDIA compatible")
    print(f"[INFO] Modelo: {args.modelo} | Device: {device}")
    print("=" * 60)

    start = time.time()
    try:
        import whisper
        model = whisper.load_model(args.modelo, device=device)
        language = None if str(args.language).lower() == "auto" else args.language
        result = model.transcribe(str(audio), fp16=fp16, language=language, task=args.task)
        text = (result.get("text") or "").strip()

        txt_out = Path(args.txt_output) if args.txt_output else audio.with_name(audio.stem + "_transcrito.txt")
        txt_out.write_text(text, encoding="utf-8")

        payload = {
            "ok": True,
            "audio": str(audio),
            "txt_output": str(txt_out),
            "model": args.modelo,
            "language_requested": language,
            "language_detected": result.get("language"),
            "device": device,
            "gpu": gpu_name,
            "seconds": round(time.time() - start, 2),
            "transcripcion_whisper": text,
        }

        if args.json_output:
            Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        print("-" * 60)
        print("[EXITO] Transcripcion guardada")
        print(f"TXT: {txt_out}")
        if args.json_output:
            print(f"JSON: {args.json_output}")
        print("-" * 60)
        return 0
    except Exception as exc:
        print(f"[ERROR FATAL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
