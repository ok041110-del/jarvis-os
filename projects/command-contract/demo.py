"""Command Contract Prototype — 수동 실행 데모(Evidence 문서용).

실행: python3 projects/command-contract/demo.py
"""

from __future__ import annotations

from resolver import run_command

DEMO_INPUTS = [
    "Development HQ 상태를 보여줘",
    "Investment HQ 최신 상태를 보여줘",
    "Trading HQ 상태를 보여줘",
    "Development HQ에서 주문을 실행해줘",
]


def main() -> None:
    for raw_input in DEMO_INPUTS:
        result = run_command(raw_input)
        print(f"> {raw_input}")
        if result.status == "ok":
            print(f"  status=ok hq={result.hq_identity}")
            for line in result.detail:
                print(f"    - {line}")
        else:
            print(f"  status=invalid reason={result.reason}")
        print()


if __name__ == "__main__":
    main()
