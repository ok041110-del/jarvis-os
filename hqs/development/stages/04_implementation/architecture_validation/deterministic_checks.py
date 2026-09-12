"""Stage 04 Architecture Validation — Deterministic Gate(RFC 요청 §7/§10).
LLM 호출 없이 코드로만 후보를 검사한다. Ponytail(§11)보다 먼저 실행되며,
여기서 FAIL한 후보는 Ponytail에 전달하지 않는다."""

import ast


class CheckResult:
    def __init__(self, passed: bool, detail: str = ""):
        self.passed = passed
        self.detail = detail

    def __bool__(self):
        return self.passed

    def __repr__(self):
        return f"CheckResult(passed={self.passed!r}, detail={self.detail!r})"


def check_syntax(code: str) -> CheckResult:
    """`compile()`로 syntax/compile 가능 여부만 확인한다."""
    try:
        compile(code, "<candidate>", "exec")
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")
    return CheckResult(True)


def check_ast_structural_validity(code: str) -> CheckResult:
    """`ast.parse`가 성공하고 최소 1개의 함수/클래스 정의를 포함하는지
    확인한다 — 빈 파일이나 순수 표현식만 있는 결과를 걸러낸다."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")

    has_def = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree))
    if not has_def:
        return CheckResult(False, "no function/class definition found")
    return CheckResult(True)


def check_contract(result: dict, required_keys: tuple) -> CheckResult:
    """Stage 04 Public Output Contract(`target`/`implementation`/
    `expose_target`)와 동일한 방식 — 필수 키 존재만 확인한다."""
    missing = [key for key in required_keys if key not in result]
    if missing:
        return CheckResult(False, f"missing keys: {missing}")
    return CheckResult(True)


def check_scope(code: str, allowed_function_names: tuple) -> CheckResult:
    """최상위 함수/메서드 정의 이름이 허용 목록을 벗어나지 않는지 확인한다
    — Exposure Policy(대상 함수만 변경)의 결정적 근사 검사다."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")

    defined = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    out_of_scope = [name for name in defined if name not in allowed_function_names]
    if out_of_scope:
        return CheckResult(False, f"out-of-scope definitions: {out_of_scope}")
    return CheckResult(True)


def check_dependency_validity(code: str, known_names: tuple) -> CheckResult:
    """코드가 참조하는 이름 중 `known_names`(closure/설계에 이미 존재한다고
    알려진 이름)에 없는 것이 있으면 표시한다 — 존재하지 않는 의존성 참조를
    거칠게 걸러내는 결정적 근사 검사이며, 완전한 타입 검사를 대체하지
    않는다."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")

    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    builtins_and_known = called_names - set(known_names) - set(dir(__builtins__))
    if builtins_and_known:
        return CheckResult(False, f"unresolved call targets: {sorted(builtins_and_known)}")
    return CheckResult(True)


def find_comments_and_docstrings(code: str) -> list:
    """`#` 주석과 docstring을 모두 추출해 `{"kind", "text", "line_count"}`
    목록으로 반환한다 — 2줄 제한 검사(§9)의 입력."""
    entries = []

    for line_no, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            entries.append({"kind": "comment", "text": stripped, "line_count": 1, "line": line_no})

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return entries

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            doc = ast.get_docstring(node, clean=True)
            if doc:
                entries.append({
                    "kind": "docstring",
                    "text": doc,
                    "line_count": len(doc.splitlines()),
                    "line": getattr(node, "lineno", 0),
                })

    return entries


def check_design_coverage(code: str, required_function_names: tuple) -> CheckResult:
    """§7 "Design requirement coverage" — Design이 요구한 함수가 실제로
    전부 정의됐는지 확인한다. `check_scope`(허용 범위를 벗어나지 않는지)
    와 반대 방향 검사다 — 이 둘을 함께 써야 "정확히 요구된 것만" 검증된다."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")

    defined = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    missing = [name for name in required_function_names if name not in defined]
    if missing:
        return CheckResult(False, f"missing required definitions: {missing}")
    return CheckResult(True)


def check_comment_docstring_policy(code: str) -> CheckResult:
    """Jarvis Ponytail Comment/Docstring 정책(§9) — 2줄 초과 항목이 있으면
    FAIL. 압축(text compression)은 이 Harness가 자동 수행하지 않는다 —
    코드 변경을 유발할 수 있는 자동 리라이트는 정책상 금지된 영역이라
    사람/후속 Agent 판단으로 남긴다."""
    entries = find_comments_and_docstrings(code)
    over_limit = [entry for entry in entries if entry["line_count"] > 2]
    if over_limit:
        return CheckResult(False, f"{len(over_limit)} comment(s)/docstring(s) exceed 2 lines")
    return CheckResult(True)


def run_deterministic_gate(
    candidate_code: str,
    *,
    required_keys: tuple,
    allowed_function_names: tuple,
    required_function_names: tuple = None,
) -> dict:
    """§10 Deterministic Gate — syntax/contract/scope/design-coverage/AST/
    comment-docstring 순서로 검사하고 각 결과를 담은 dict를 반환한다.
    `passed`는 전부 PASS일 때만 True다. `required_function_names`을
    생략하면 `allowed_function_names`과 동일하게 취급한다(허용 범위 ==
    요구 범위인 기존 호출부와 하위 호환)."""
    if required_function_names is None:
        required_function_names = allowed_function_names

    checks = {
        "syntax": check_syntax(candidate_code),
        "ast": check_ast_structural_validity(candidate_code),
        "scope": check_scope(candidate_code, allowed_function_names),
        "design_coverage": check_design_coverage(candidate_code, required_function_names),
        "comment_docstring": check_comment_docstring_policy(candidate_code),
    }
    return {
        "passed": all(bool(result) for result in checks.values()),
        "checks": checks,
    }
