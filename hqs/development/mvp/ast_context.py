"""ADC-0005 §1/§2 — AST Function Candidate Index / Dependency Closure, Engine
미호출 순수 정적 분석 함수 2개(`project_intelligence.py`의 경로-only 성질 유지, RFC-0007 §4)."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_MVP_DIR = ROOT / "hqs" / "development" / "mvp"

_MAX_CLOSURE_DEPTH = 6


def _mvp_source_files() -> list:
    return [path for path in sorted(_MVP_DIR.glob("*.py")) if path.is_file()]


def module_source_path(module: str) -> Path:
    """`module` 이름을 `hqs/development/mvp/*.py` 경로로 변환(Target File
    Exposure 배선용, ADC-0005 §7)."""
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
    """저장소 함수 후보를 이름+시그니처+docstring 첫 줄로 색인화(본문 없음) —
    RFC-0007 §2 시작점 식별용, T17~T19 3/3 재현."""
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
    """`module`.`function`의 직접·간접 의존성만 폐쇄로 포함(Full Source
    대체, RFC-0007 §2/§6). 모듈 수준 상수는 추적하지 않는다(T09~T19 검증 범위 밖)."""
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
