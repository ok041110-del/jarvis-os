"""MVP-0005: Project Intelligence — 규칙 기반 Context 수집.
Development HQ 내부 전용이며 Jarvis OS 공통 계층으로 일반화하지 않는다.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# 카테고리별 (검색 대상 디렉토리, glob 패턴, 제외 디렉토리명)
CATEGORY_PATHS = {
    "source_code": (ROOT / "hqs" / "development" / "mvp", "*.py", {"tests", "__pycache__"}),
    "existing_workflow": (ROOT / "hqs" / "development" / "mvp", "workflow*.py", {"__pycache__"}),
    "mvp_documents": (ROOT / "docs" / "01_mvp", "*.md", set()),
    "obs_documents": (ROOT / "docs" / "governance" / "observations", "OBS-*.md", set()),
    "rfc_documents": (ROOT / "docs" / "decisions" / "rfc", "RFC-*.md", set()),
    "adc_documents": (ROOT / "docs" / "governance" / "adc", "ADC-*.md", set()),
    "adr_documents": (ROOT / "docs" / "decisions" / "adr", "ADR-*.md", set()),
    "rt_documents": (ROOT / "docs" / "governance" / "rt", "RT-*.md", set()),
}


# 도메인과 무관하게 항상 의미가 없는 영문 관사/전치사/접속사/대명사/
# 조동사만 담는다 — 도메인 단어(workflow/engine/exception 등)는
# 매칭 신호로 쓰이므로 제외하지 않는다.
_STOPWORDS = frozenset(
    (
        "a", "an", "the",
        "in", "on", "of", "at", "by", "to", "for", "with", "from", "as",
        "and", "or", "but", "if", "when", "while",
        "is", "are", "was", "were", "be", "been", "being",
        "do", "does", "did", "doing",
        "not", "no",
        "it", "its", "this", "that", "these", "those",
        "can", "could", "should", "would", "will", "may", "might", "must",
        "instead",
    )
)


def _keywords(text: str) -> set:
    # `\w+` 하나로 묶으면 "Dispatcher를"처럼 한글 조사가 붙어 원어와
    # 매칭되지 않으므로 라틴/한글 토큰을 별도로 추출한다.
    latin = re.findall(r"[A-Za-z0-9_]+", text)
    hangul = re.findall(r"[가-힣]+", text)
    return {w.lower() for w in latin + hangul if len(w) >= 2 and w.lower() not in _STOPWORDS}


def _score(keywords: set, path: Path) -> int:
    # 부분 문자열 매칭("so" in "also", "on" in "constitution")은 무관한
    # 파일의 점수를 부풀리므로 단어 경계(`\b`) 매칭을 쓴다.
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    haystack = (path.name + "\n" + content).lower()
    return sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", haystack))


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


# 생성된 도구 캐시(`__pycache__` 등)는 프로젝트 구조가 아니므로 제외한다.
_NOISE_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"})


def _directory_structure(max_depth: int = 2) -> list:
    structure = []
    for base in (ROOT / "hqs" / "development", ROOT / "docs"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(ROOT)
            if len(rel.parts) > max_depth or _NOISE_DIR_NAMES & set(rel.parts):
                continue
            structure.append(str(rel) + ("/" if path.is_dir() else ""))
    return structure


class IssueValidationError(ValueError):
    """`issue`에 필수 필드(title/description)가 없거나 빈 값일 때 발생한다."""


def validate_issue(issue: dict) -> None:
    """`title`/`description`만 필수 Issue 필드로 검사한다."""
    if not isinstance(issue, dict):
        raise IssueValidationError(f"issue must be a dict, got {type(issue).__name__}")

    missing = [
        field
        for field in ("title", "description")
        if not isinstance(issue.get(field), str) or not issue.get(field).strip()
    ]
    if missing:
        raise IssueValidationError(
            f"issue is missing required non-empty string field(s): {', '.join(missing)}"
        )


def collect_relevant_context(issue: dict) -> dict:
    validate_issue(issue)
    keywords = _keywords(f"{issue['title']} {issue['description']}")

    context = {"directory_structure": _directory_structure()}
    for category, (directory, pattern, exclude_dirs) in CATEGORY_PATHS.items():
        context[category] = _relevant_files(keywords, directory, pattern, exclude_dirs)
    return context


# "재평가 조건"(RT 문서)과 자유 텍스트 속 "미결정" 서술을 구분하는 마커.
# 새 카테고리 디렉토리 없이 기존 수집 결과를 재분류만 한다.
_OPEN_WORD_RE = re.compile(r"\bopen\b", re.IGNORECASE)
_OPEN_KOREAN_MARKERS = ("미해결", "검토가 필요")


def _extract_open_questions(paths: list, limit: int = 5) -> list:
    """`open` 마커는 단어 경계로 매칭한다 — 부분 문자열 매칭 시
    "OpenHands"/"OpenAI" 같은 고유명사가 오탐된다."""
    questions = []
    for rel_path in paths:
        path = ROOT / rel_path
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if _OPEN_WORD_RE.search(stripped) or any(marker in stripped for marker in _OPEN_KOREAN_MARKERS):
                questions.append(f"{rel_path}: {stripped}")
    return questions[:limit]


def build_context_bundle(issue: dict) -> dict:
    """새 수집 로직 없이 `collect_relevant_context()` 결과를 Planning이
    쓸 8개 항목 구조로 재배치한다."""
    context = collect_relevant_context(issue)

    relevant_code = list(context["source_code"])
    relevant_code += [p for p in context["existing_workflow"] if p not in relevant_code]

    relevant_documents = context["mvp_documents"] + context["rfc_documents"]
    relevant_decisions = context["adc_documents"] + context["adr_documents"]

    decision_and_doc_paths = relevant_documents + relevant_decisions + context["obs_documents"]

    return {
        "issue": issue,
        "goal": issue.get("goal", issue["title"]),
        "relevant_documents": relevant_documents,
        "relevant_code": relevant_code,
        "relevant_observations": context["obs_documents"],
        "relevant_decisions": relevant_decisions,
        "known_constraints": context["rt_documents"],
        "open_questions": _extract_open_questions(decision_and_doc_paths),
    }
