"""Stage 04 Architecture Validation — Ponytail Adapter(§11). **실제 Ponytail
Supervisor가 아니다** — LLM 판단 없이 결정적 규칙으로 후보를 고르는 controlled
adapter일 뿐이며, Architecture를 이미 채택한 것처럼 보이게 만들지 않는다."""


def select_final_candidate(candidates: list) -> dict | None:
    """고정 ID 순서로 tie-break한다 — "품질이 가장 좋다"는 판단이 아니라
    실행 완료 순서에 결과가 좌우되지 않게 하기 위함이다."""
    passed = [c for c in candidates if c["gate"]["passed"]]
    if not passed:
        return None
    order = {"implementation": 0, "consistency": 1, "minimality": 2}
    return min(passed, key=lambda c: order.get(c["id"], len(order)))
