"""`test_execution_host.py`가 Worker Process에서 실행할 pytest 대상
헬퍼. `ProcessPoolExecutor`로 전달되는 함수는 모듈 최상위에서
importable해야 하므로 별도 모듈로 분리한다(`projects/runtime-boundary`
Prototype의 `rtb_runtime._run_pytest`와 동일한 이유)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


class _ResultCollector:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when != "call":
            return
        if report.outcome == "passed":
            self.passed += 1
        elif report.outcome == "failed":
            self.failed += 1


def run_pytest_target(target_path: str) -> tuple[int, int, int]:
    """`target_path`(REPO_ROOT 상대 경로)를 pytest로 실행하고
    (return_code, passed, failed)를 반환한다."""
    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    collector = _ResultCollector()
    absolute_target = str(REPO_ROOT / target_path)
    return_code = pytest.main(
        ["-q", "-s", "-p", "no:cacheprovider", absolute_target], plugins=[collector]
    )
    return int(return_code), collector.passed, collector.failed
