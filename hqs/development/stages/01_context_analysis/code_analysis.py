"""Stage 01 Code Analysis Executors — RepositorySnapshot을 입력으로 삼는
결정적(Engine 미호출) 분석 3종(Structure/Relevant Discovery/AST Candidate)과
Context Aggregator, 그리고 조건부 Dependency Analysis(RFC-0033 §8/§9).

기존 `mvp/project_intelligence.py`·`mvp/ast_context.py`의 순수 로직
(`_keywords`, 단어 경계 스코어링, `_candidate_entries_from_source`, 8-key
Context Bundle 형태, `KNOWN`/미해결 마커 판정)을 재사용하고, local
filesystem 순회 부분만 GitHub Snapshot 기반으로 바꾼다 — 알고리즘 자체는
다시 작성하지 않는다."""

import fnmatch
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp import ast_context  # noqa: E402
from mvp.ast_context import build_dependency_closure  # noqa: E402
from mvp.project_intelligence import CATEGORY_PATHS, ROOT, _keywords  # noqa: E402

# `CATEGORY_PATHS`는 절대경로 `Path`를 쓴다 — Snapshot 경로(ROOT-relative
# POSIX 문자열)와 매칭하려면 상대 경로로 변환한다. 이 저장소를 대상으로 하는
# 한(§13 실제 GitHub 검증 대상이 이 저장소 자체) 로컬 구조와 GitHub 트리
# 구조가 같으므로 이 변환은 유효하다.
_OPEN_WORD_RE = re.compile(r"\bopen\b", re.IGNORECASE)
_OPEN_KOREAN_MARKERS = ("미해결", "검토가 필요")

# 파일 content를 실제로 fetch하는 상한 — GitHub API 호출 비용을 억제한다
# (§7 "Repository 전체 파일을 무조건 preload하지 않는다"). 파일명만으로 1차
# 후보를 추린 뒤 상위 N개만 content까지 확인한다.
_MAX_CONTENT_FETCH_PER_CATEGORY = 8
_MAX_RESULTS_PER_CATEGORY = 3


def _category_specs():
    """`CATEGORY_PATHS`를 (category, [ROOT-relative dir 문자열], glob 패턴,
    제외 디렉토리명)로 정규화한다."""
    specs = []
    for category, (directories, pattern, exclude_dirs) in CATEGORY_PATHS.items():
        dirs = (directories,) if isinstance(directories, Path) else directories
        rel_dirs = [str(d.relative_to(ROOT)) for d in dirs]
        specs.append((category, rel_dirs, pattern, exclude_dirs))
    return specs


def _tree_paths(snapshot) -> list:
    return [entry.path for entry in snapshot.tree if entry.type == "blob"]


def _matches_category(path: str, rel_dirs: list, pattern: str, exclude_dirs: set) -> bool:
    if not any(path == d or path.startswith(d + "/") for d in rel_dirs):
        return False
    if exclude_dirs & set(Path(path).parts):
        return False
    return fnmatch.fnmatch(Path(path).name, pattern)


def structure_analysis(snapshot) -> list:
    """Repository Structure — Snapshot Tree를 그대로 나열한다(GitHub Tree
    API가 이미 완전한 목록을 주므로 별도 순회 알고리즘이 필요 없다)."""
    entries = sorted(entry.path for entry in snapshot.tree)
    return entries


def relevant_discovery(snapshot, fetch_content, issue: dict, search_specification: dict) -> dict:
    """Relevant File/Document Discovery — 기존 `collect_relevant_context`/
    `build_context_bundle`의 8-key Context Bundle 형태와 카테고리 구조를
    재사용하되, 파일 순회는 Snapshot Tree에서, 채점은 fetch된 content에서
    수행한다(`fetch_content: Callable[[str], str | None]`).

    비용 억제를 위해 2단계로 채점한다: (1) 파일명 자체에 키워드가 포함되는지로
    1차 후보를 추리고 (2) 상위 후보만 content를 fetch해 최종 점수를 매긴다 —
    로컬 파일시스템(무료 읽기)과 달리 GitHub API 호출에는 비용이 있기 때문에
    필요한 최소 수정이다(RFC-0033 §9)."""
    keywords = _keywords(f"{issue['title']} {issue['description']}") | set(
        kw.lower() for kw in search_specification.get("keywords", [])
    )
    tree_paths = _tree_paths(snapshot)

    context = {}
    for category, rel_dirs, pattern, exclude_dirs in _category_specs():
        candidates = sorted(
            path for path in tree_paths if _matches_category(path, rel_dirs, pattern, exclude_dirs)
        )
        # 1차: 파일명 매칭 개수로 정렬해 content fetch 대상만 추린다.
        name_scored = sorted(
            candidates,
            key=lambda p: sum(1 for kw in keywords if kw in p.lower()),
            reverse=True,
        )[:_MAX_CONTENT_FETCH_PER_CATEGORY]

        content_scored = []
        for path in name_scored:
            content = fetch_content(path)
            if content is None:
                continue
            haystack = (Path(path).name + "\n" + content).lower()
            score = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", haystack))
            if score > 0:
                content_scored.append((score, path))
        content_scored.sort(key=lambda pair: pair[0], reverse=True)
        context[category] = [path for _, path in content_scored[:_MAX_RESULTS_PER_CATEGORY]]

    relevant_code = list(context.get("source_code", []))
    relevant_code += [p for p in context.get("existing_workflow", []) if p not in relevant_code]

    relevant_documents = context.get("mvp_documents", []) + context.get("rfc_documents", [])
    relevant_decisions = context.get("adc_documents", []) + context.get("adr_documents", [])
    decision_and_doc_paths = relevant_documents + relevant_decisions + context.get("obs_documents", [])

    open_questions = []
    for rel_path in decision_and_doc_paths:
        content = fetch_content(rel_path)
        if content is None:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if _OPEN_WORD_RE.search(stripped) or any(marker in stripped for marker in _OPEN_KOREAN_MARKERS):
                open_questions.append(f"{rel_path}: {stripped}")
    open_questions = open_questions[:5]

    return {
        "issue": issue,
        "goal": issue.get("goal", issue["title"]),
        "relevant_documents": relevant_documents,
        "relevant_code": relevant_code,
        "relevant_observations": context.get("obs_documents", []),
        "relevant_decisions": relevant_decisions,
        "known_constraints": context.get("rt_documents", []),
        "open_questions": open_questions,
    }


def ast_candidate_analysis(snapshot, fetch_content) -> str:
    """AST Function Candidate Index — `mvp/ast_context.py`의
    `_candidate_entries_from_source()`(RFC-0033 §9로 추출된 순수 함수)를
    그대로 재사용하고, 대상 파일만 Snapshot Tree(`hqs/development/mvp/*.py`)
    +fetch로 공급한다."""
    mvp_prefix = str((ROOT / "hqs" / "development" / "mvp").relative_to(ROOT))
    py_paths = sorted(
        entry.path
        for entry in snapshot.tree
        if entry.type == "blob"
        and entry.path.startswith(mvp_prefix + "/")
        and entry.path.endswith(".py")
        and "__pycache__" not in entry.path
    )

    sections = []
    for path in py_paths:
        content = fetch_content(path)
        if content is None:
            continue
        entries = ast_context._candidate_entries_from_source(content, filename=path)
        if entries:
            sections.append(f"FILE: {path}\n" + "\n".join(entries))
    return "\n\n".join(sections)


def dependency_analysis(target) -> str:
    """AST Dependency Closure — `target`(module, function)이 명확히 주어진
    경우에만 실행한다(§8 Conditional). 현재 이 Capability는 로컬 파일시스템
    기준 `build_dependency_closure()`를 그대로 재사용한다 — Stage 01은 실제
    호출 경로에서 `target`을 받은 적이 없어(§ RESPONSIBILITY.md "시작점 자동
    식별 없음") Snapshot 기반 재구현은 이번 반복에서 보류한다(Known
    Limitation, 최종 보고서 참조)."""
    module, function = target
    return build_dependency_closure(module, function)


def aggregate_context(directory_structure: list, context_bundle: dict, candidate_index: str, target, dependency_closure, prd: dict) -> dict:
    """Context Aggregator — `ContextAnalysisResult` Public Contract
    6개 키(`stages/contracts.py`, `prd`는 RFC-0034/ADC-0037/ADR-0022로
    추가)를 그대로 채운다. 재해석 없이 조립만 한다."""
    return {
        "directory_structure": directory_structure,
        "context_bundle": context_bundle,
        "candidate_index": candidate_index,
        "target": target,
        "dependency_closure": dependency_closure,
        "prd": prd,
    }
