"""hqs/development/cli.py — CLI -> `workflow.py` 진입점. 사용자 입력을 받아
`run_workflow()`를 호출하고 결과를 재해석 없이 출력한다(`mvp/cli.py`와는 별개 진입점)."""

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
