"""IN-3 전용 별도 프로세스 진입점.

fresh 인터프리터에서 checkpoint 파일을 로드해 run_phase2만 실행한다 —
adapter 객체·in-memory saver가 폐기된 상태에서 재개가 성립함을 보인다.
stdout에 최종 State를 JSON으로 출력한다.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import caller  # noqa: E402


def _adapter(name: str):
    if name == "worklist":
        from adapters import worklist

        return worklist
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
