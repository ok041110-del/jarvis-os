"""MVP-0001 실행 진입점.

사용법: python development-hq/mvp/cli.py <파일 경로>
        (또는 stdin으로 코드를 넣어 실행)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mvp.workflow import run_mvp_0001  # noqa: E402


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = run_mvp_0001(code)

    print("## Code Review")
    print(result["code_review"])
    print()
    print("## Test Case Suggestions")
    print(result["test_execution"])


if __name__ == "__main__":
    main()
