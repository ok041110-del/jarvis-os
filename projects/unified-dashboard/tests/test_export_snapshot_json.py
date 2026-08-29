"""export_snapshot_json.py — Functional + Boundary Validation."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import export_snapshot_json  # noqa: E402


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


def test_export_module_does_not_import_hq_code():
    """Boundary 검증: snapshot.py와 동일하게 hqs/mvp/trader를
    import하지 않는다 — snapshot.py가 이미 읽은 값을 직렬화만 한다."""
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "export_snapshot_json.py")
    assert "hqs" not in modules
    assert "mvp" not in modules
    assert "trader" not in modules


def test_build_snapshot_document_matches_python_snapshot():
    document = export_snapshot_json.build_snapshot_document()
    assert "generated_at" in document
    identities = {s["identity"] for s in document["snapshots"]}
    assert identities == {"Development HQ", "Investment HQ"}
    for snap in document["snapshots"]:
        assert snap["status"] in {"NORMAL", "WORKING", "BLOCKED", "DEFERRED", "UNKNOWN"}


def test_output_path_is_inside_frontend_public_data():
    assert export_snapshot_json.OUTPUT_PATH.parent == (
        PROTOTYPE_DIR / "frontend" / "public" / "data"
    )


def test_execution_field_reaches_json_document():
    """Execution Evidence Vertical Slice: Investment HQ의 execution이
    JSON 직렬화 과정에서 유실되지 않고 그대로 전달되는지 검증한다."""
    document = export_snapshot_json.build_snapshot_document()
    snaps = {s["identity"]: s for s in document["snapshots"]}
    assert "execution" in snaps["Investment HQ"]
    assert len(snaps["Investment HQ"]["execution"]) > 0
    assert snaps["Development HQ"]["execution"] == []


def test_history_field_reaches_json_document():
    """History Vertical Slice: Investment HQ의 history(9개 run 요약)가
    JSON 직렬화 과정에서 유실되지 않고 그대로 전달되는지 검증한다."""
    document = export_snapshot_json.build_snapshot_document()
    snaps = {s["identity"]: s for s in document["snapshots"]}
    assert "history" in snaps["Investment HQ"]
    assert len(snaps["Investment HQ"]["history"]) == 9
    assert snaps["Development HQ"]["history"] == []
