"""`_directory_structure()`의 `max_depth` Blind Spot 회귀 테스트
(DEV-HQ-V2.0-CATEGORY-PATHS-BLIND-SPOT-REVIEW-0001 §7.2 Next Task).

실제 파일시스템(ROOT)을 그대로 사용한다 — 이 함수는 mock 대상 외부
의존성이 없고, 버그 자체가 실제 경로 깊이 계산에 있었기 때문이다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.project_intelligence import _directory_structure, collect_relevant_context


def test_directory_structure_includes_entries_below_base_directories():
    # 수정 전에는 ROOT 기준 depth를 세어 base(hqs/development, docs)
    # 자체가 이미 max_depth를 소모했다 — base 바로 아래 파일도 전부 누락됐다.
    result = _directory_structure()
    assert any(entry.startswith("hqs/development/mvp/") for entry in result)


def test_directory_structure_respects_max_depth_from_each_base():
    result = _directory_structure(max_depth=1)
    assert "hqs/development/mvp/" in result
    assert not any(entry.startswith("hqs/development/mvp/") and entry != "hqs/development/mvp/" for entry in result)


def test_directory_structure_excludes_noise_dirs():
    result = _directory_structure(max_depth=3)
    assert not any("__pycache__" in entry for entry in result)


# CATEGORY_PATHS["source_code"] Blind Spot 회귀 테스트 (Phase 2.5 Case D).
# 수정 전에는 hqs/development/mvp만 대상이라 cli.py/workflow.py/stages/가
# candidate에서 구조적으로 제외됐다 — 각 파일의 고유 식별자를 키워드로
# 써서 실제로 후보에 포함되는지 확인한다.


def test_source_code_scope_includes_v2_workflow_entrypoint():
    # 흔한 Korean filler 없이 고유 식별자만으로 질의 — 범용 단어가 섞이면
    # 다른 무관 파일들이 score에서 앞서 top-3 밖으로 밀려난다.
    context = collect_relevant_context({"title": "_load_stage", "description": "_load_stage"})
    assert "hqs/development/workflow.py" in context["source_code"]


def test_source_code_scope_includes_v2_cli():
    context = collect_relevant_context(
        {
            "title": "_warn_if_expose_target_degraded_checks",
            "description": "_warn_if_expose_target_degraded_checks",
        }
    )
    assert "hqs/development/cli.py" in context["source_code"]


def test_source_code_scope_includes_stages_directory():
    context = collect_relevant_context(
        {"title": "_assemble_build_input", "description": "_assemble_build_input"}
    )
    assert "hqs/development/stages/04_implementation/stage_04.py" in context["source_code"]
