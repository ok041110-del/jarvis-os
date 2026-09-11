"""Stage 02: Planning & Specification 실행 진입점(ADR-0008 §4).

PRD/Specification 생성 책임은 Stage 01로 이동했다(RFC-0034/ADC-0037/
ADR-0022) — Stage 01이 Multi-Agent Reasoning(Structured Understanding)과
Repository Context를 종합해 이미 `stage_01_context["prd"]`를 만들어
Handover한다. Stage 02는 이제 자체 Engine 호출 없이 이를 그대로
전달(passthrough)한다 — `SpecificationResult` Output Contract(`skeleton`/
`specification` 2키)는 무변경이라 Stage 03/05는 수정 없이 그대로
동작한다."""


def run_stage_02(issue: dict, stage_01_context: dict) -> dict:
    """Stage 01의 PRD/Specification Synthesis 결과를 그대로 전달한다
    (재생성하지 않음, ADR-0022). `stage_01_context["prd"]`가 이미
    `{skeleton, specification}` 형태(`SpecificationResult`와 동일)다."""
    return dict(stage_01_context["prd"])
