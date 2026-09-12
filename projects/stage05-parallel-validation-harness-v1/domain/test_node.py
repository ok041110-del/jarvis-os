"""Test Validator — 유일하게 파일 시스템에 쓰기를 하는 Validator
(RFC-0039 §2.5, `STAGE05-TEST-ISOLATION-VALIDATION-0001.md`). 반드시
`TestWorkspace`를 통해서만 실행하고, 원본 repository는 절대 참조하지
않는다. Workspace 생성 실패/Implementation 적용 실패/pytest 실행
실패/cleanup 실패를 각각 구분해 반환한다(사용자 지시 Part 3)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .results import ValidatorResult
from .workspace import (
    ImplementationApplyError,
    TestWorkspace,
    WorkspaceCreationError,
)


@dataclass
class TestNodeConfig:
    source_repo_root: Path
    target_relative_path: str
    tests_relative_dir: str
    pytest_bin: str = "/root/.local/bin/pytest"
    base_tmp_dir: Path | None = None


def run_test_validator(implementation: str, config: TestNodeConfig) -> ValidatorResult:
    """4단계(workspace 생성 -> implementation 적용 -> pytest 실행 -> cleanup)를
    전부 거치고, 각 단계 실패를 `detail`에 구분해 기록한다. cleanup 실패는
    Validator 결과 자체를 FAIL로 만들지 않는다 — Production 소스에 영향이
    없기 때문이다(Evidence 문서 §7 판단과 동일)."""
    start = time.perf_counter()
    detail: dict = {
        "workspace_creation": {"succeeded": None, "error": None, "latency_ms": None},
        "implementation_apply": {"succeeded": None, "error": None},
        "pytest_execution": {"executed": None, "returncode": None, "error": None, "latency_ms": None},
        "cleanup": {"attempted": None, "succeeded": None, "error": None},
    }

    workspace = TestWorkspace(config.source_repo_root, base_tmp_dir=config.base_tmp_dir)

    # 1) Workspace 생성
    ws_start = time.perf_counter()
    try:
        workspace.create()
        detail["workspace_creation"]["succeeded"] = True
    except WorkspaceCreationError as exc:
        detail["workspace_creation"]["succeeded"] = False
        detail["workspace_creation"]["error"] = str(exc)
        detail["workspace_creation"]["latency_ms"] = (time.perf_counter() - ws_start) * 1000
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ValidatorResult("test", "ERROR", elapsed_ms, detail, error="workspace_creation_failed")
    detail["workspace_creation"]["latency_ms"] = (time.perf_counter() - ws_start) * 1000

    # 2) Implementation 적용
    try:
        workspace.apply_implementation(config.target_relative_path, implementation)
        detail["implementation_apply"]["succeeded"] = True
    except ImplementationApplyError as exc:
        detail["implementation_apply"]["succeeded"] = False
        detail["implementation_apply"]["error"] = str(exc)
        cleanup_result = workspace.cleanup()
        detail["cleanup"] = {
            "attempted": cleanup_result.attempted,
            "succeeded": cleanup_result.succeeded,
            "error": cleanup_result.error,
        }
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ValidatorResult("test", "ERROR", elapsed_ms, detail, error="implementation_apply_failed")

    # 3) pytest 실행
    pytest_start = time.perf_counter()
    pytest_result = workspace.run_pytest(config.tests_relative_dir, pytest_bin=config.pytest_bin)
    detail["pytest_execution"] = {
        "executed": pytest_result["executed"],
        "returncode": pytest_result.get("returncode"),
        "error": pytest_result.get("error"),
        "latency_ms": (time.perf_counter() - pytest_start) * 1000,
        "output_tail": pytest_result.get("output", "")[-1000:],
    }

    # 4) Cleanup(결과와 무관하게 항상 시도)
    cleanup_result = workspace.cleanup()
    detail["cleanup"] = {
        "attempted": cleanup_result.attempted,
        "succeeded": cleanup_result.succeeded,
        "error": cleanup_result.error,
    }

    elapsed_ms = (time.perf_counter() - start) * 1000

    if not pytest_result["executed"]:
        return ValidatorResult("test", "ERROR", elapsed_ms, detail, error="pytest_execution_failed")

    status = "PASS" if pytest_result["returncode"] == 0 else "FAIL"
    return ValidatorResult("test", status, elapsed_ms, detail)
