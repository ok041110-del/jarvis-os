"""격리 검증 — `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`
"Experimental Implementation"(HQ production path 무단 연결 금지)을
정적으로 확인한다. `runtime-boundary` Prototype의
`test_no_direct_hq_or_kernel_import`와 동일한 방법론(AST 기반)이다.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROTOTYPE_DIR.parents[1]

MODULE_FILES = ["rp_execution_host.py", "rp_runtime.py", "rp_target.py"]

FORBIDDEN_IMPORT_ROOTS = {"hqs", "core", "mvp", "dashboard"}


def _imported_module_roots(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


def test_no_direct_hq_or_kernel_import():
    """`rp_*.py` 세 모듈 전부 `hqs`/`core`/`mvp`/`dashboard`를 직접
    import하지 않는다 — Execution Host Contract는 재구현으로
    재현했을 뿐, Production 모듈을 연결하지 않았다."""
    for filename in MODULE_FILES:
        roots = _imported_module_roots(PROTOTYPE_DIR / filename)
        offending = roots & FORBIDDEN_IMPORT_ROOTS
        assert not offending, f"{filename} imports forbidden roots: {offending}"


def test_production_paths_unmodified():
    """`hqs/`, `core/`가 이 Prototype 작업으로 수정되지 않았음을
    `git diff`로 확인한다(`runtime-boundary`/`dev-hq-vertical-slice`
    Prototype과 동일한 검증)."""
    result = subprocess.run(
        ["git", "diff", "--stat", "origin/main", "--", "hqs/", "core/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "", f"hqs/ or core/ modified:\n{result.stdout}"


def test_task_style_unit_module_does_not_reference_executor_classes_directly():
    """`rp_runtime.py`가 `ProcessPoolExecutor`/`ThreadPoolExecutor`
    클래스 이름을 직접 참조하지 않아도 되는지 확인하지 않는다 —
    Runtime은 스스로 `ThreadPoolExecutor`(제출/폴링용)를 두는 것이
    설계이므로 이 검증은 Execution Host 내부(`rp_execution_host.py`)
    에만 적용한다: Execution Host가 사용하는 `ProcessPoolExecutor`를
    Runtime이 직접 import하지 않고 `run_isolated()` 함수 호출로만
    위임하는지 확인한다."""
    tree = ast.parse((PROTOTYPE_DIR / "rp_runtime.py").read_text(encoding="utf-8"))
    source = ast.dump(tree)
    assert "ProcessPoolExecutor" not in source
