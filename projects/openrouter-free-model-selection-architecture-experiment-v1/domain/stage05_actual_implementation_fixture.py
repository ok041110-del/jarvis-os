"""Stage 05 Review 재실험 전용 — **실제** Stage 04 Implementation을 Review 대상으로 고정한다(이전 실험이 placeholder 텍스트를 전달했던 결함 제거).

**Stage 01~04를 재실행하지 않는다** — 이 세션이 이전에 실제로 성공시킨 Stage 04 결과(`OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` stage04 run 1)를 원본 JSON에서 그대로 복사해 바이트 단위로 동결(freeze)한 것이며, placeholder/dummy가 아니라 실제 LLM이 생성한 문자열 그 자체다.
"""

from __future__ import annotations

from pathlib import Path

_FIXTURE_FILE = Path(__file__).resolve().parent / "fixtures_data" / "stage04_actual_implementation.txt"

ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE = (
    "OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md stage04 run 1 "
    "(selected_model=inclusionai/ling-3.0-flash-vl:free, http_status=200, "
    "contract_passed=True, content_length=3341) — 이 세션이 이전에 실제로 "
    "실행한 결과를 원본 JSON에서 그대로 복사해 동결. 이번 Stage 05 재실험은 "
    "이 문자열을 새로 생성하지 않았다(Stage 01~04 재실행 금지 범위 준수)."
)

ACTUAL_STAGE04_IMPLEMENTATION = _FIXTURE_FILE.read_text(encoding="utf-8")
ACTUAL_STAGE04_TARGET_MODULE = "hqs/development/mvp/agents/backend.py"
ACTUAL_STAGE04_TARGET_FUNCTION = "backend_agent_code_review"
