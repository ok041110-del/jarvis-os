"""Stage 04 Architecture Validation — Quality 구조 신호(§8). LOC를 품질 지표로 쓰지 않으며, Readability/Cognitive Load처럼 사람·LLM-judge가 필요한 판단은 다루지 않는다(README 참고)."""

import ast


def count_ternary_expressions(code: str) -> int:
    tree = ast.parse(code)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.IfExp))


def max_comprehension_nesting(code: str) -> int:
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
    tree = ast.parse(code)

    def chain_length(node):
        length = 0
        while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            length += 1
            node = node.func.value
        return length

    return max((chain_length(node) for node in ast.walk(tree) if isinstance(node, ast.Call)), default=0)


def count_lambda(code: str) -> int:
    tree = ast.parse(code)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Lambda))


def max_control_flow_nesting(code: str) -> int:
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
    """값이 낮을수록 명시적이라는 신호일 뿐, 사람이 실제로 헷갈리는지는
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
    if _safe_parse(code) is None:
        return -1
    return max_control_flow_nesting(code)


def _safe_parse(code: str):
    try:
        return ast.parse(code)
    except SyntaxError:
        return None
