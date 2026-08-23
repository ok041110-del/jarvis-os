"""ADC-0005 §1/§2 — AST Function Candidate Index / Dependency Closure, Engine
미호출 순수 정적 분석 함수 2개(`project_intelligence.py`의 경로-only 성질 유지, RFC-0007 §4).
ADC-0006: dotted package module path 지원을 additive extension으로 추가(평면 module path 동작 무변경)."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_MVP_DIR = ROOT / "hqs" / "development" / "mvp"

_MAX_CLOSURE_DEPTH = 6


def _mvp_source_files() -> list:
    return [path for path in sorted(_MVP_DIR.glob("*.py")) if path.is_file()]


def _mvp_package_dirs() -> list:
    """`__init__.py`를 가진 mvp/ 바로 아래 디렉터리만 패키지로 인식한다
    (ADC-0006 additive extension — 평면 탐색(`_mvp_source_files`)과는 별개로
    유지, 기존 반환값을 바꾸지 않는다)."""
    return [
        path
        for path in sorted(_MVP_DIR.iterdir())
        if path.is_dir() and (path / "__init__.py").is_file()
    ]


def _package_source_files() -> list:
    """패키지 디렉터리 하위 `*.py`(`__init__.py` 제외)를 dotted 이름과 함께
    나열한다(ADC-0006 additive extension)."""
    entries = []
    for pkg_dir in _mvp_package_dirs():
        for path in sorted(pkg_dir.glob("*.py")):
            if path.name == "__init__.py":
                continue
            entries.append((f"{pkg_dir.name}.{path.stem}", path))
    return entries


def module_source_path(module: str) -> Path:
    """`module` 이름을 `hqs/development/mvp/*.py` 경로로 변환(Target File
    Exposure 배선용, ADC-0005 §7). dotted 이름(`pkg.sub`)은 `pkg/sub.py`로
    변환한다(ADC-0006 additive extension) — 점이 없는 이름의 반환값은
    기존과 동일하다(`_MVP_DIR.joinpath(f"{module}.py")` == 기존
    `_MVP_DIR / f"{module}.py"`)."""
    *package_parts, module_name = module.split(".")
    return _MVP_DIR.joinpath(*package_parts, f"{module_name}.py")


def _resolve_source_path(module: str):
    """실제 파일 존재 여부까지 확인해 `module`을 경로로 해석한다(ADC-0006
    additive extension). 평면 파일을 우선 시도하고(기존과 동일 경로),
    없으면 점 없는 이름에 한해 동명의 패키지 `__init__.py`를 시도한다.
    둘 다 없으면 `None`."""
    flat_path = module_source_path(module)
    if flat_path.exists():
        return flat_path
    if "." not in module:
        package_init = _MVP_DIR / module / "__init__.py"
        if package_init.exists():
            return package_init
    return None


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


def _candidate_entries(path: Path):
    """`path` 하나의 함수/클래스 후보 목록을 추출한다(본문 없음). 파싱 불가 시
    `None`(`build_function_candidate_index()`의 기존 `try/except continue`와
    동일 의미, ADC-0006 additive extension — 평면/패키지 양쪽에서 재사용)."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return None
    entries = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = _first_doc_line(node)
            entries.append(f"FUNCTION: {_signature(node)}" + (f" -- {doc}" if doc else ""))
        elif isinstance(node, ast.ClassDef):
            doc = _first_doc_line(node)
            entries.append(f"CLASS: {node.name}" + (f" -- {doc}" if doc else ""))
    return entries


def build_function_candidate_index() -> str:
    """저장소 함수 후보를 이름+시그니처+docstring 첫 줄로 색인화(본문 없음) —
    RFC-0007 §2 시작점 식별용, T17~T19 3/3 재현. 평면 파일 목록·순서·형식은
    그대로이며, 패키지 디렉터리가 있으면 그 뒤에 이어 붙인다(ADC-0006
    additive extension — 현재 저장소는 패키지 디렉터리가 없어 출력이
    기존과 완전히 동일하다)."""
    sections = []
    for path in _mvp_source_files() + [pkg_path for _, pkg_path in _package_source_files()]:
        entries = _candidate_entries(path)
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

        path = _resolve_source_path(module_name)
        if path is None:
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
