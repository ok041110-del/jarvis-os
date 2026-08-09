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

MVP-0009: `collect_relevant_context()`(카테고리별 파일 목록)는 그대로
두고, 그 결과를 8개 항목(Issue/Goal/Relevant Documents/Relevant Code/
Relevant Observations/Relevant Decisions/Known Constraints/Open
Questions)으로 재구성하는 `build_context_bundle()`을 추가한다. 새
Runtime/Task Dispatcher/Stage Runner/Pipeline Runner/Capability는
추가하지 않는다.
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


# 실제 Issue("Investigate timeout handling" 등 영문 관사/전치사/접속사가
# 섞인 문장)로 `_score()`를 직접 실행해 확인함: "in"/"an"/"the"/"of"/
# "not"/"does"/"but"/"when"/"should"/"instead" 같은 순수 문법 기능어는
# `development-hq/mvp/`의 거의 모든 `.py` 파일 docstring/주석에 등장해,
# 실제로 그 Issue와 무관한 파일까지 `engine.py`(가장 직접적으로 관련된
# 파일)와 동점에 가까운 점수를 받게 만든다 — Issue의 진짜 주제어
# (timeout/crash/handling 등)가 내는 신호가 기능어의 "어디에나 있음"
# 신호에 묻힌다. 여기 등록한 목록은 도메인과 무관하게 항상 의미가
# 없는 영문 관사/전치사/접속사/대명사/조동사만 담는다 — 도메인 단어
# (workflow/engine/exception 등, 위 실측에서도 실제로 의미가 있었다)는
# 제외하지 않는다.
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
    # 라틴 문자/숫자 토큰과 한글 음절 토큰을 별도로 추출한다. `\w+` 하나로
    # 묶으면 "Dispatcher를"처럼 한글 조사가 영문 단어에 그대로 붙어 하나의
    # 토큰이 되어, 조사 없는 원어(RFC/ADC 본문 등)와 매칭되지 않는다.
    latin = re.findall(r"[A-Za-z0-9_]+", text)
    hangul = re.findall(r"[가-힣]+", text)
    return {w.lower() for w in latin + hangul if len(w) >= 2 and w.lower() not in _STOPWORDS}


def _score(keywords: set, path: Path) -> int:
    # 부분 문자열 매칭("so" in "also", "on" in "constitution")이 실제로
    # 무관한 파일의 점수를 부풀리는 것을 위 `_STOPWORDS` 테스트 중
    # 직접 확인했다(`_extract_open_questions`의 `_OPEN_WORD_RE`가 이미
    # "OpenHands"/"OpenAI" 오탐을 막기 위해 쓰던 것과 같은 종류의 문제).
    # 그 함수가 이미 쓰는 단어 경계(`\b`) 매칭을 여기도 그대로 적용한다
    # — 새 기법이 아니라 기존에 검증된 기법의 재사용이다.
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


# MVP-0009: Governance 문서 중 "재평가 조건이 곧 제약"인 것과, 자유 텍스트
# 내부에 "아직 결정되지 않았다"는 사실을 담고 있는 것을 구분하는 규칙.
# 새 카테고리 디렉토리를 추가하지 않는다 — 이미 `collect_relevant_context()`가
# 수집한 파일들의 *내용*을 규칙 기반으로 재분류할 뿐이다.
_OPEN_WORD_RE = re.compile(r"\bopen\b", re.IGNORECASE)
_OPEN_KOREAN_MARKERS = ("미해결", "검토가 필요")


def _extract_open_questions(paths: list, limit: int = 5) -> list:
    """주어진 (repo-relative) 문서 경로들의 본문에서 "아직 결정되지 않음"을
    나타내는 문장만 골라낸다. 문장 분리·마커 매칭 외의 판단은 하지 않는다.

    영문 마커(`open`)는 단어 경계로 매칭한다 — 부분 문자열로 매칭하면
    "OpenHands"/"OpenAI" 같은 고유명사가 "Open Decision"과 동일하게
    잡혀 Open Questions가 실제로는 열린 질문이 아닌 문장으로 오염된다
    (이 저장소의 RFC-0003이 실제 사례).
    """
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
    """`collect_relevant_context()`가 반환한 카테고리별 파일 목록을,
    Planning이 그대로 입력으로 사용할 수 있는 8개 항목짜리 구조화된
    Context Bundle로 재구성한다.

    새 수집 로직을 추가하지 않는다 — `collect_relevant_context()`가 이미
    찾은 파일 목록을 재배치(relevant_documents/relevant_code/...)하고,
    그중 RT 문서와 "Open" 마커가 있는 문서에서 Known Constraints/Open
    Questions만 규칙 기반으로 뽑아낸다.
    """
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
