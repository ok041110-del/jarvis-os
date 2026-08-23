"""Stage 01: Context Analysis 실행 진입점(ADR-0008) — 기존 `mvp/` 함수를
호출만 한다(CAPABILITIES.md, ADR-0001 §5)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.ast_context import build_dependency_closure, build_function_candidate_index
from mvp.project_intelligence import build_context_bundle, collect_relevant_context


def run_stage_01(issue: dict, target: tuple | None = None) -> dict:
    """Capability 5개를 실행해 후속 Stage 입력을 만든다. `target` 없으면
    `dependency_closure`는 `None`(시작점 식별은 이 Stage 책임 아님, CONTEXT.md)."""
    # build_context_bundle()이 버리는 키라 별도 호출로 얻는다(둘 다 Engine 미호출).
    directory_structure = collect_relevant_context(issue)["directory_structure"]
    context_bundle = build_context_bundle(issue)
    candidate_index = build_function_candidate_index()

    dependency_closure = None
    if target is not None:
        module, function = target
        dependency_closure = build_dependency_closure(module, function)

    return {
        "directory_structure": directory_structure,
        "context_bundle": context_bundle,
        "candidate_index": candidate_index,
        "target": target,
        "dependency_closure": dependency_closure,
    }
