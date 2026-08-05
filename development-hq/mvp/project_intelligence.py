"""MVP-0005: Project Intelligence — 최소 Context 수집 계층.

Issue -> Project Intelligence -> Relevant Context -> Planning

Task Dispatcher, Runtime, Stage Runner, Pipeline Runner를 구현하지
않는다. 이 파일은 Project 전체에서 Issue와 관련된 자료를 규칙 기반
(키워드 겹침)으로 찾아 하나의 dict로 반환하는 함수 하나만 제공한다.
ML/임베딩/벡터 검색 없이, 기존 `engine.py`와 동일한 "규칙 기반" 방식을
그대로 재사용한다.

이 계층은 Development HQ 내부 전용이다. Jarvis OS 공통 계층으로
일반화하지 않는다. 향후 다른 HQ에서도 동일한 요구가 반복 관찰될 때만
Governance 절차로 공통 계층 승격 여부를 판단한다.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 카테고리별 (검색 대상 디렉토리, glob 패턴, 제외 디렉토리명)
CATEGORY_PATHS = {
    "source_code": (ROOT / "development-hq" / "mvp", "*.py", {"tests", "__pycache__"}),
    "existing_workflow": (ROOT / "development-hq" / "mvp", "workflow*.py", {"__pycache__"}),
    "mvp_documents": (ROOT / "docs" / "01_mvp", "*.md", set()),
    "obs_documents": (ROOT / "docs" / "governance" / "observations", "OBS-*.md", set()),
    "rfc_documents": (ROOT / "docs" / "02_rfc", "RFC-*.md", set()),
    "adc_documents": (ROOT / "docs" / "governance" / "adc", "ADC-*.md", set()),
    "adr_documents": (ROOT / "docs" / "04_adr", "ADR-*.md", set()),
    "rt_documents": (ROOT / "docs" / "governance" / "rt", "RT-*.md", set()),
}


def _keywords(text: str) -> set:
    # 라틴 문자/숫자 토큰과 한글 음절 토큰을 별도로 추출한다. `\w+` 하나로
    # 묶으면 "Dispatcher를"처럼 한글 조사가 영문 단어에 그대로 붙어 하나의
    # 토큰이 되어, 조사 없는 원어(RFC/ADC 본문 등)와 매칭되지 않는다.
    latin = re.findall(r"[A-Za-z0-9_]+", text)
    hangul = re.findall(r"[가-힣]+", text)
    return {w.lower() for w in latin + hangul if len(w) >= 2}


def _score(keywords: set, path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    haystack = (path.name + "\n" + content).lower()
    return sum(1 for kw in keywords if kw in haystack)


def _relevant_files(keywords: set, directory: Path, pattern: str, exclude_dirs: set, limit: int = 3) -> list:
    if not directory.exists():
        return []
    candidates = []
    for path in sorted(directory.rglob(pattern)):
        if not path.is_file():
            continue
        if exclude_dirs & set(path.parts):
            continue
        score = _score(keywords, path)
        if score > 0:
            candidates.append((score, path))
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return [str(p.relative_to(ROOT)) for _, p in candidates[:limit]]


def _directory_structure(max_depth: int = 2) -> list:
    structure = []
    for base in (ROOT / "development-hq", ROOT / "docs"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(ROOT)
            if len(rel.parts) > max_depth or "__pycache__" in rel.parts:
                continue
            structure.append(str(rel) + ("/" if path.is_dir() else ""))
    return structure


def collect_relevant_context(issue: dict) -> dict:
    """Issue와 관련된 Project 자료를 규칙 기반으로 수집해 dict로 반환한다."""
    keywords = _keywords(f"{issue['title']} {issue['description']}")

    context = {"directory_structure": _directory_structure()}
    for category, (directory, pattern, exclude_dirs) in CATEGORY_PATHS.items():
        context[category] = _relevant_files(keywords, directory, pattern, exclude_dirs)
    return context
