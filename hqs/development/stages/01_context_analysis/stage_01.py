"""Stage 01: Context Analysis 실행 진입점 (ADR-0008).

5개 Capability(CAPABILITIES.md)를 호출만 한다 — 재구현하지 않는다.
`hqs/development/mvp/`의 기존 함수를 그대로 재사용한다(ADR-0001 §5,
ADR-0008 §1: 기존 MVP 코드는 이동하지 않는다).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.ast_context import build_dependency_closure, build_function_candidate_index
from mvp.project_intelligence import build_context_bundle, collect_relevant_context


def run_stage_01(issue: dict, target: tuple | None = None) -> dict:
    """Context Analysis Capability 5개를 실행해 후속 Stage 입력을 만든다.

    `target`(module, function)이 주어지지 않으면 `dependency_closure`는
    `None`이다 — 시작점 식별은 이 Stage의 책임이 아니다(CONTEXT.md 참고).

    `directory_structure`는 `build_context_bundle()`이 버리는 키라서
    `collect_relevant_context()`를 별도로 한 번 더 호출해 얻는다 — 둘 다
    순수 파일 탐색이라 Engine 호출 없이 중복 비용이 작다. 기존 함수
    시그니처는 바꾸지 않는다."""
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
