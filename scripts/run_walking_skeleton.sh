#!/usr/bin/env bash
# 네트워크 접근이 없는 환경에서도 즉시 실행 가능하도록 PYTHONPATH를 직접 구성.
# uv sync가 가능한 실제 개발 환경에서는 `uv run poc-runner`로 대체 예정 (uv sync 이후).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/packages/core/src:$ROOT/packages/shared/src:$ROOT/adapters/policy-inmemory/src:$ROOT/adapters/connector-mock/src:$ROOT/apps/poc-runner/src"
python3 -m jarvis_poc_runner.main
