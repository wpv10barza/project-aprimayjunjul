#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from command_agent_core import execute_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcriptor2 Command Agent CLI")
    parser.add_argument("--command", "-c", default="crear documento excel", help="Comando en español")
    parser.add_argument("--latest", action="store_true", help="Usar ultimo TXT/audio de la carpeta mp3")
    parser.add_argument("--no-gemma", action="store_true", help="No llamar Function Gemma; usar fallback local")
    parser.add_argument("--request-id", default="", help="ID opcional")
    parser.add_argument("--json-output", default="", help="Guardar respuesta JSON en archivo")
    args = parser.parse_args()

    result = execute_command(
        command=args.command,
        use_latest_voice=args.latest,
        use_gemma=not args.no_gemma,
        request_id=args.request_id or None,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text, encoding="utf-8")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
