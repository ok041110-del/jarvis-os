"""IN-7-4 전용 별도 프로세스 진입점.

fresh 인터프리터에서 checkpoint 파일을 로드해 run_phase2만 실행한다 —
adapter 모듈이 폐기된 상태에서, 실제 Engine 텍스트가 담긴 값으로도
재개가 성립함을 보인다. stdout에 최종 State를 JSON으로 출력한다.

이 프로세스는 실제 Engine을 호출하지 않는다 — phase1에서 이미 캡처된
값이 checkpoint 파일에 값으로 실려 있을 뿐이다(engine_cache 재사용 없음,
필요도 없음).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import caller  # noqa: E402


def _adapter(name: str):
    if name == "sequential":
        from adapters import sequential

        return sequential
    if name == "worklist":
        from adapters import worklist

        return worklist
    if name == "recursive":
        from adapters import recursive

        return recursive
    if name == "langgraph":
        from adapters import langgraph

        return langgraph
    raise SystemExit(f"unknown adapter: {name}")


def main() -> None:
    adapter_name, checkpoint_path = sys.argv[1], sys.argv[2]
    result = caller.load_and_phase2(_adapter(adapter_name), checkpoint_path)
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
