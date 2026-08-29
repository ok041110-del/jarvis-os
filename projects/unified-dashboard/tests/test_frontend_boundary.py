"""Frontend(TS/TSX) Observe-only Boundary Validation — 텍스트 기반 검사.

작업 지시(§8): Frontend에서 subprocess/child_process/fs를 통한
Repository 접근, Python 실행, Engine/Agent/Workflow 실행을 구현하지
않는다. tsc/JS 실행 환경 없이도 CI에서 검증 가능하도록 순수 문자열
검사로 강제한다 — snapshot.py의 AST 기반 Boundary 테스트와 대칭되는
Frontend 쪽 최소 대응.
"""

from __future__ import annotations

import re
from pathlib import Path

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"

# 실제 import/require/호출 구문만 검사한다 — 주석·문서 문자열에 원칙을
# 설명하기 위해 등장하는 단어(예: "subprocess/child_process/fs로
# 접근하지 않는다")까지 위반으로 오탐하지 않도록, 코드로서 의미를
# 갖는 패턴만 정규식으로 한정한다.
_FORBIDDEN_CODE_PATTERNS = (
    re.compile(r"""(?:from|require\()\s*["'](node:)?(child_process|fs|fs/promises)["']"""),
    re.compile(r"\bexecSync\s*\("),
    re.compile(r"\bspawn(Sync)?\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\bDeno\.run\s*\("),
)


def _source_files() -> list[Path]:
    return sorted(FRONTEND_SRC.rglob("*.ts")) + sorted(FRONTEND_SRC.rglob("*.tsx"))


def _strip_comments(text: str) -> str:
    """block(/* */)·line(//) 주석을 제거해 주석 속 설명 문구가 코드
    패턴 검사에 걸리지 않게 한다(간이 처리 — 문자열 리터럴 안의
    `//`는 이 Prototype 소스에 없으므로 별도 처리하지 않는다)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    return text


def test_frontend_sources_exist():
    files = _source_files()
    assert files, "frontend/src 아래에 .ts/.tsx 파일이 있어야 함"


def test_frontend_does_not_access_repository_or_execute_processes():
    files = _source_files()
    violations = []
    for path in files:
        code = _strip_comments(path.read_text(encoding="utf-8"))
        for pattern in _FORBIDDEN_CODE_PATTERNS:
            if pattern.search(code):
                violations.append(f"{path.relative_to(FRONTEND_SRC)}: {pattern.pattern}")
    assert not violations, f"Observe-only Boundary 위반 후보: {violations}"


def test_frontend_only_fetches_static_snapshot_json():
    app_tsx = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
    assert "fetch(" in app_tsx
    assert "snapshot.json" in app_tsx
