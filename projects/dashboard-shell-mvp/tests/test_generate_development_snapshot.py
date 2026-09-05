"""Dashboard Shell MVP — Development Snapshot Generator Boundary/Functional Validation.

`projects/unified-dashboard/tests/test_snapshot.py`의 AST 기반 import
검사 방식을 재사용한다.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import generate_development_snapshot as gen  # noqa: E402


def _imported_top_level_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_generator_does_not_import_hq_code():
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "generate_development_snapshot.py")
    assert "hqs" not in modules
    assert "mvp" not in modules


def test_generator_reuses_unified_dashboard_build_dev_hq_snapshot():
    """새 Evidence 수집 로직을 만들지 않고 기존 함수 객체를 그대로
    가져다 쓰는지 확인한다(같은 로직을 복제하지 않았는지 검증)."""
    from snapshot import build_dev_hq_snapshot as canonical

    assert gen.build_dev_hq_snapshot is canonical


def test_document_has_no_fabricated_progress_percent():
    doc = gen.build_document()
    assert doc["progressPercent"] is None, (
        "Development HQ에는 진행률(%) Evidence가 없다 — 임의 숫자를 채우면 안 됨"
    )


def test_document_stage_and_current_task_match_real_freeze_doc():
    doc = gen.build_document()
    assert doc["stage"].startswith("Stable v2.0 Freeze")
    assert "ADC-02 Open" in doc["currentTask"]


def test_document_agents_match_real_agents_directory():
    agents_dir = gen.REPO_ROOT / "hqs/development/mvp/agents"
    expected = sorted(p.stem for p in agents_dir.glob("*.py") if p.stem != "__init__")
    doc = gen.build_document()
    assert doc["agents"] == expected


def test_document_source_files_point_to_real_paths():
    doc = gen.build_document()
    assert doc["sourceFiles"], "실제 Evidence 파일 경로가 최소 1개는 있어야 함"
    freeze_doc = doc["sourceFiles"][0]
    assert (gen.REPO_ROOT / freeze_doc).is_file()


def test_document_is_json_serializable():
    doc = gen.build_document()
    json.dumps(doc)
