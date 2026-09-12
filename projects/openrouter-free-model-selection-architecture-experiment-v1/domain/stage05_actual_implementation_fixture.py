"""Stage 05 Review 재실험 전용 — **실제** Stage 04 Implementation을
Review 대상으로 고정한다. 이전 실험(`OPENROUTER-FREE-MODEL-SELECTION-
ARCHITECTURE-EXPERIMENT-0001.md` §5~§7 NOT DETERMINED, 그리고 그보다
앞선 `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` §13/§19)가
placeholder 텍스트를 Review에 전달했던 결함을 제거하는 것이 이 파일의
유일한 목적이다.

**Stage 01~04를 이번 작업에서 재실행하지 않는다**(사용자 지시 범위) —
대신 이 세션이 이전에 실제로 실행해 성공시킨 Stage 04 결과(`OPENROUTER-
AUTO-SELECTION-V1-VALIDATION-0001.md`가 기록한 15/15 성공 실행 중
stage04 run 1)를 **바이트 단위로 그대로 동결(freeze)**해 재사용한다 —
`fixtures_data/stage04_actual_implementation.txt`는 그 실행 당시 실제
OpenRouter 응답(`inclusionai/ling-3.0-flash-vl:free`, HTTP 200, Contract
PASS)의 `final_raw_content`를 손으로 옮겨 적지 않고 원본 JSON에서
그대로 복사한 것이다(전사 오류 방지 — 손으로 재입력하지 않음).

placeholder/dummy/원본 source 어느 것도 아니다 — 실제 LLM이 실제로
생성한 Implementation 문자열 그 자체다."""

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
