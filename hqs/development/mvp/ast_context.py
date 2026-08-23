"""ADC-0005 §1/§2 — AST Function Candidate Index / Dependency Closure.

Build Capability(`backend_agent_code_generation`)에 실제 프로젝트 소스
Context를 제공하기 위한 두 개의 순수 정적 분석 함수만 담는다(Engine
호출 없음). `project_intelligence.py`는 "경로만 반환한다"는 기존
성질을 유지해야 하므로(RFC-0007 §4 옵션 2), 파일 **내용**을 반환하는
이 두 함수는 별도 모듈로 분리했다. Runtime/Registry/Capability를
새로 만들지 않는다 — 두 함수 모두 `hqs/development/mvp/*.py`를 읽어
문자열을 반환하는 것뿐이다.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_MVP_DIR = ROOT / "hqs" / "development" / "mvp"

_MAX_CLOSURE_DEPTH = 6


def _mvp_source_files() -> list:
    return [path for path in sorted(_MVP_DIR.glob("*.py")) if path.is_file()]


def module_source_path(module: str) -> Path:
    """`module`(확장자 없는 이름)에 대응하는 `hqs/development/mvp/*.py`
    경로를 반환한다 — Target File Exposure 배선(ADC-0005 §7)이 대상
    파일 전체를 읽어야 할 때 경로 조합 로직을 이 모듈 하나로 모은다."""
    return _MVP_DIR / f"{module}.py"


def _signature(node) -> str:
    """body/decorator 없는 시그니처 한 줄만 얻기 위해 빈 body로 치환 후 unparse."""
    stub = type(node)(
        name=node.name,
        args=node.args,
        body=[ast.Pass()],
        decorator_list=[],
        returns=node.returns,
        type_comment=None,
    )
    ast.fix_missing_locations(stub)
    return ast.unparse(stub).splitlines()[0].rstrip(":")


def _first_doc_line(node) -> str:
    doc = ast.get_docstring(node, clean=True)
    return doc.strip().splitlines()[0] if doc else ""


def build_function_candidate_index() -> str:
    """저장소 함수 후보를 이름+시그니처+docstring 첫 줄만 담은 저비용
    인덱스로 만든다(본문 없음) — RFC-0007 §2 시작점 자동 식별용,
    T17~T19에서 3/3 재현된 최소 입력(`DEV-HQ-V2.0-AST-CANDIDATE-INDEX-
    REPRODUCTION-0001.md`)."""
    sections = []
    for path in _mvp_source_files():
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError):
            continue
        entries = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = _first_doc_line(node)
                entries.append(f"FUNCTION: {_signature(node)}" + (f" -- {doc}" if doc else ""))
            elif isinstance(node, ast.ClassDef):
                doc = _first_doc_line(node)
                entries.append(f"CLASS: {node.name}" + (f" -- {doc}" if doc else ""))
        if entries:
            rel = path.relative_to(ROOT)
            sections.append(f"FILE: {rel}\n" + "\n".join(entries))
    return "\n\n".join(sections)


def build_dependency_closure(module: str, function: str) -> str:
    """`module`.`function`에서 시작해 직접·간접 의존성만 폐쇄로 포함한다
    (Full Source 대체) — RFC-0007 §2/§6, T09~T19 Evidence(Full Source와
    동등한 Build 정확성, 기존 코드 손상 0건).

    알고리즘: `ast.parse` + Load-context 이름 추적 + 상대 import 재귀.
    모듈 수준 상수(딕셔너리 등)는 추적하지 않는다 — Evidence(T09~T19)가
    검증한 범위(함수/클래스 폐쇄)를 벗어나지 않기 위함이다."""
    order = []
    seen = set()

    def resolve(module_name: str, name: str, depth: int = 0) -> None:
        if (module_name, name) in seen or depth > _MAX_CLOSURE_DEPTH:
            return
        seen.add((module_name, name))

        path = _MVP_DIR / f"{module_name}.py"
        if not path.exists():
            return
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        top_defs = {}
        imports = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                top_defs[node.name] = node
            elif isinstance(node, ast.ImportFrom) and node.level >= 1 and node.module:
                for alias in node.names:
                    imports[alias.asname or alias.name] = (node.module, alias.name)

        target = top_defs.get(name)
        if target is None:
            return

        segment = ast.get_source_segment(source, target)
        if segment:
            order.append((module_name, segment))

        referenced = set()
        for node in ast.walk(target):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                referenced.add(node.value.id)

        for ref in sorted(referenced):
            if ref == name:
                continue
            if ref in top_defs:
                resolve(module_name, ref, depth + 1)
            elif ref in imports:
                origin_module, orig_name = imports[ref]
                resolve(origin_module, orig_name, depth + 1)

    resolve(module, function)
    if not order:
        raise ValueError(f"AST closure를 계산할 대상을 찾지 못했다: {module}.{function}")

    grouped = {}
    for module_name, segment in order:
        grouped.setdefault(module_name, []).append(segment)

    sections = [f"# module: {mod}\n" + "\n\n".join(segments) for mod, segments in grouped.items()]
    return "\n\n".join(sections)
