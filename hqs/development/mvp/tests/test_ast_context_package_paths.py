"""ADC-0006(RFC-0008 후속) — `ast_context.py`의 dotted package module path
additive extension 전용 테스트. 기존 `test_ast_context.py`는 수정하지
않았다 — 이 파일은 평면 module path 동작(기존 파일)과 별개로, 패키지
디렉터리를 인식하는 새 경로만 검증한다.

모든 패키지 시나리오는 `tmp_path`에 합성 파일을 만들고 `ast_context.ROOT`/
`ast_context._MVP_DIR`을 그 경로로 monkeypatch해 검증한다 — 실제
저장소에 `agents/` 등 어떤 디렉터리도 생성하지 않는다(RFC-0008/ADC-0006
금지 사항)."""

import pytest

from .. import ast_context


def _patch_mvp_dir(monkeypatch, tmp_path):
    """ROOT/_MVP_DIR을 합성 트리로 바꿔치기한다 — `build_function_candidate_
    index()`가 `path.relative_to(ROOT)`를 계산하므로 둘 다 같은 트리를
    가리켜야 한다."""
    monkeypatch.setattr(ast_context, "ROOT", tmp_path)
    monkeypatch.setattr(ast_context, "_MVP_DIR", tmp_path)


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# --- 1. 기존 평면 module path 동작 보존(실제 저장소 기준, monkeypatch 없음) ---


def test_flat_module_source_path_unchanged_for_non_dotted_name():
    assert ast_context.module_source_path("engine") == ast_context._MVP_DIR / "engine.py"


def test_flat_dependency_closure_still_works_for_real_repo_module():
    closure = ast_context.build_dependency_closure("agents", "_strip_code_fence")
    assert "# module: agents" in closure
    assert "def _strip_code_fence(text: str) -> str:" in closure


# --- 2. package directory를 module path로 식별 ---


def test_bare_name_resolves_to_package_init_when_no_flat_file(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(
        tmp_path / "pkg2" / "__init__.py",
        "def _pkg2_func() -> str:\n    return 'ok'\n",
    )

    closure = ast_context.build_dependency_closure("pkg2", "_pkg2_func")

    assert "# module: pkg2" in closure
    assert "def _pkg2_func() -> str:" in closure


def test_resolve_source_path_prefers_flat_file_over_package(monkeypatch, tmp_path):
    """평면 파일과 패키지 디렉터리가 같은 이름으로 동시에 존재할 수는
    없지만(Python 제약), 평면 파일이 있으면 패키지 폴백을 시도조차 하지
    않는다는 우선순위 자체를 확인한다."""
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "solo.py", "def solo() -> str:\n    return 'flat'\n")

    resolved = ast_context._resolve_source_path("solo")

    assert resolved == tmp_path / "solo.py"


# --- 3. dotted child module을 정확한 파일 경로로 resolve ---


def test_module_source_path_resolves_dotted_name_to_nested_file(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)

    assert ast_context.module_source_path("pkg.backend") == tmp_path / "pkg" / "backend.py"
    # 잘못된 해석("pkg.backend.py"라는 단일 파일명)이 아님을 명시적으로 확인.
    assert not (tmp_path / "pkg.backend.py").exists()


def test_resolve_source_path_finds_existing_dotted_module_file(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "pkg" / "__init__.py", "")
    target = _write(tmp_path / "pkg" / "backend.py", "def f() -> None:\n    pass\n")

    assert ast_context._resolve_source_path("pkg.backend") == target


# --- 4. dotted 모듈의 function candidate index ---


def test_candidate_index_includes_package_module_after_flat_files(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "flat_module.py", 'def flat_func() -> None:\n    """flat doc."""\n')
    _write(tmp_path / "pkg" / "__init__.py", "")
    _write(
        tmp_path / "pkg" / "backend.py",
        'def _strip_code_fence(text: str) -> str:\n    """패키지 함수 doc."""\n    return text\n',
    )

    index = ast_context.build_function_candidate_index()

    assert "FILE: flat_module.py" in index
    assert "FILE: pkg/backend.py" in index
    assert "FUNCTION: def _strip_code_fence(text: str) -> str" in index
    assert "패키지 함수 doc." in index
    # 평면 파일 섹션이 패키지 섹션보다 먼저 나온다(기존 순서 보존).
    assert index.index("FILE: flat_module.py") < index.index("FILE: pkg/backend.py")


def test_candidate_index_excludes_package_init_file_itself(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "pkg" / "__init__.py", 'def _init_only() -> None:\n    """init에만 있음."""\n')

    index = ast_context.build_function_candidate_index()

    assert "_init_only" not in index


# --- 5. dotted 모듈의 dependency closure ---


def test_dependency_closure_for_dotted_module_follows_relative_import_to_sibling_flat_module(
    monkeypatch, tmp_path
):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "engine.py", "def call_engine(prompt: str) -> str:\n    return prompt\n")
    _write(tmp_path / "pkg" / "__init__.py", "")
    _write(
        tmp_path / "pkg" / "backend.py",
        "from ..engine import call_engine\n\n\n"
        "def _strip_code_fence(text: str) -> str:\n    return call_engine(text)\n",
    )

    closure = ast_context.build_dependency_closure("pkg.backend", "_strip_code_fence")

    assert "# module: pkg.backend" in closure
    assert "def _strip_code_fence(text: str) -> str:" in closure
    assert "# module: engine" in closure
    assert "def call_engine(prompt: str) -> str:" in closure


# --- 6. 존재하지 않는 dotted module은 기존 오류 의미 유지 ---


def test_dependency_closure_raises_for_missing_module_inside_existing_package(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)
    _write(tmp_path / "pkg" / "__init__.py", "")

    with pytest.raises(ValueError, match=r"pkg\.missing\.whatever"):
        ast_context.build_dependency_closure("pkg.missing", "whatever")


def test_dependency_closure_raises_for_missing_package_entirely(monkeypatch, tmp_path):
    _patch_mvp_dir(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match=r"nopkg\.nomodule\.whatever"):
        ast_context.build_dependency_closure("nopkg.nomodule", "whatever")
