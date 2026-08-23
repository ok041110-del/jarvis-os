"""hqs/development/cli.py — CLI -> `workflow.py`(01→05 Integrated
Workflow) 진입점.

사용자 입력(Issue JSON, `--expose-target` 옵션)을 받아 `run_workflow()`
를 호출하고 결과를 출력하는 것 외에는 아무 것도 하지 않는다. Context
Analysis/Planning/Design/Implementation/Validation은 전부 `workflow.py`
-> Stage 01~05에 위임한다 — Workflow의 결과(특히 Stage 05 `verdict`)를
재해석하지 않고 그대로 출력한다.

`hqs/development/mvp/cli.py`(MVP-0001, code 문자열을 입력받아 code_
review/test_execution을 출력하는 별도 CLI)와는 다른 진입점이다 — 그
파일의 입력/출력 Contract를 유지하기 위해 수정하지 않았다. 이 파일의
Input Contract(Issue JSON)는 `run_workflow()`가 이미 받는 `issue: dict`
그대로이며, 새 Interface/Contract를 추가하지 않았다.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from workflow import run_workflow  # noqa: E402


def _parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 01(Context Analysis)~05(Validation) Integrated Workflow 실행"
    )
    parser.add_argument(
        "issue_path",
        nargs="?",
        help="Issue JSON 파일 경로({'title', 'description', ...}) — 생략 시 stdin에서 읽는다",
    )
    parser.add_argument(
        "--expose-target",
        action="store_true",
        dest="expose_target",
        help="Stage 04가 식별한 Target File 전체를 노출하고 그 함수만 확장하도록 지시한다",
    )
    return parser.parse_args(argv)


def _load_issue(issue_path: str | None) -> dict:
    text = Path(issue_path).read_text(encoding="utf-8") if issue_path else sys.stdin.read()
    return json.loads(text)


def main() -> None:
    args = _parse_args(sys.argv[1:])

    try:
        issue = _load_issue(args.issue_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read issue input: {exc}", file=sys.stderr)
        sys.exit(1)

    result = run_workflow(issue, expose_target=args.expose_target)

    if result["failed_at"] is not None:
        print(f"WORKFLOW FAILED at {result['failed_at']}: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
