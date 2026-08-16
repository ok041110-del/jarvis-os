#!/bin/bash
# Prototype D — 모델별 성능 비교. development-hq/mvp/engine.py는 건드리지 않는다
# (import도 하지 않음) — 동일 CLI 인자에 --model만 추가한 순수 진단 호출이다.
# 사용법: ./run_model.sh <model_alias> <prompt_file> <output_json_path>
set -euo pipefail
MODEL="$1"
PROMPT_FILE="$2"
OUT_PATH="$3"

cd /tmp
claude -p "$(cat "$PROMPT_FILE")" \
  --output-format json \
  --model "$MODEL" \
  --disallowedTools "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch" \
  --append-system-prompt "You are being invoked as a stateless text-in/text-out function call, not an interactive coding session. You have no filesystem or shell tools available on this call, and that is expected and permanent — do not report it, apologize for it, or ask for permissions. Respond only with the requested content as plain text." \
  > "$OUT_PATH" 2>&1
