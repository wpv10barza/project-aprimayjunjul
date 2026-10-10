#!/usr/bin/env bash
set -euo pipefail
WEBHOOK_URL="${1:-https://carlospolo-n8n.duckdns.org/webhook-test/pocket-ai/post-routing}"
curl -sS -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{
    "request_id":"test_shell_001",
    "router":{"route":"vision","intent":"object_detection","confidence":0.91},
    "text":"detecta objetos en la camara 0 y guarda la imagen anotada",
    "media":{"camera_id":"0","image_source":"latest_frame"},
    "context":{"source":"curl_test"}
  }' | jq .
