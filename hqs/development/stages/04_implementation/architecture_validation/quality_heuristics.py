"""Stage 04 Architecture Validation — Quality 구조 신호(§8). LOC를 품질
지표로 쓰지 않는다("Short code is not automatically simple code"). 이
모듈은 §8의 Explicitness 체크리스트(과도한 one-liner/comprehension/중첩
conditional/chaining) 중 코드로 결정적으로 셀 수 있는 부분만 다룬다 —
Readability/Cognitive Load/전체 Maintainability처럼 "새 개발자가 얼마나
추론해야 하는가"를 묻는 판단은 사람 또는 LLM-judge가 필요해 이 모듈이
대신하지 않는다(README 참고)."""

import ast


def count_ternary_expressions(code: str) -> int:
    """중첩 conditional expression(`a if c else b`) 개수 — §8."""
    tree = ast.parse(code)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.IfExp))


def max_comprehension_nesting(code: str) -> int:
    """comprehension 중첩 깊이의 최댓값 — 지나친 comprehension(§8) 신호."""
    tree = ast.parse(code)
    comp_types = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

    def depth(node, current):
        best = current
        for child in ast.iter_child_nodes(node):
            child_depth = depth(child, current + 1 if isinstance(child, comp_types) else current)
            best = max(best, child_depth)
        return best

    return depth(tree, 0)


def max_chained_calls(code: str) -> int:
    """`.a().b().c()` 형태의 chaining 길이 최댓값 — 과도한 chaining(§8) 신호."""
    tree = ast.parse(code)

    def chain_length(node):
        length = 0
        while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            length += 1
            node = node.func.value
        return length

    return max((chain_length(node) for node in ast.walk(tree) if isinstance(node, ast.Call)), default=0)


def count_lambda(code: str) -> int:
    """`lambda` 표현식 개수 — 숨겨진 side effect/암묵적 함수(§8) 신호."""
    tree = ast.parse(code)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Lambda))


def max_control_flow_nesting(code: str) -> int:
    """if/for/while/try의 중첩 깊이 최댓값 — 복잡도(Simplicity 근사) 신호."""
    tree = ast.parse(code)
    control_types = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try)

    def depth(node, current):
        best = current
        for child in ast.iter_child_nodes(node):
            child_depth = depth(child, current + 1 if isinstance(child, control_types) else current)
            best = max(best, child_depth)
        return best

    return depth(tree, 0)


def explicitness_issue_count(code: str) -> int:
    """§8 Explicitness 구조 신호 합계 — 값이 낮을수록 명시적이다. 이 값
    자체가 "명시성 점수"는 아니다. 사람이 읽었을 때 실제로 헷갈리는지는
    이 값만으로 판단할 수 없다(README/Evidence 문서 한계 참고)."""
    tree_ok = _safe_parse(code)
    if tree_ok is None:
        return -1
    return (
        count_ternary_expressions(code)
        + max(0, max_comprehension_nesting(code) - 1)
        + max(0, max_chained_calls(code) - 2)
        + count_lambda(code)
    )


def simplicity_issue_count(code: str) -> int:
    """제어 흐름 중첩 깊이를 Simplicity의 구조적 근사로 쓴다 — 값이
    낮을수록 단순하다. LOC는 사용하지 않는다."""
    if _safe_parse(code) is None:
        return -1
    return max_control_flow_nesting(code)


def _safe_parse(code: str):
    try:
        return ast.parse(code)
    except SyntaxError:
        return None
