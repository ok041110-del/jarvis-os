"""Stage 04 Architecture Validation — Ponytail Adapter(RFC 요청 §11).

**이것은 실제 Ponytail Supervisor가 아니다.** 실제 Supervisor는 아직
존재하지 않으므로, 이 Harness는 Deterministic Gate를 통과한 후보 중
하나를 결정적 규칙으로 고르는 controlled adapter만 제공한다 — LLM
판단을 흉내 내지 않고, Architecture를 이미 채택한 것처럼 보이게 만들지
않는다. 실제 Ponytail의 LLM 비용/품질을 검증하려면 별도 experimental
path로 분리해야 한다(§11)."""


def select_final_candidate(candidates: list) -> dict | None:
    """PASS한 후보 중 고정 ID 순서(§10 — `implementation` <
    `consistency` < `minimality`)로 가장 먼저 오는 것을 고른다. 이는
    "품질이 가장 좋다"는 판단이 아니라, 실행 완료 순서에 결과가
    좌우되지 않도록 하는 결정적 tie-break일 뿐이다.

    `candidates`: `{"id": str, "code": str, "gate": dict}` 목록.
    `gate["passed"]`가 True인 것만 대상이다.
    """
    passed = [c for c in candidates if c["gate"]["passed"]]
    if not passed:
        return None
    order = {"implementation": 0, "consistency": 1, "minimality": 2}
    return min(passed, key=lambda c: order.get(c["id"], len(order)))
