"""Execution Layer MVP-0006: ExecutionResultBuilder.

Execution State(Execution Layer MVP-0005의 Artifact)에 대한 Execution
Result(Execution Layer의 여섯 번째 공식 Artifact)를 만든다.

Contract (Governance 사이클 기준):
- Input: Execution State (`str`, MVP-0005 `build_execution_state()`가
  생성하는 형태).
- Output: Execution Result (`str`) — Execution State를 그대로 참조하는
  독립 Artifact. Execution State 자체는 수정하지 않는다(새 Artifact를
  생성할 뿐).
- Execution Result에는 산출물 목록(``results``, `list[str]`)과 식별
  메타데이터만 추가된다(handle_id, request_id, produced_at,
  artifact_version).
- ``results`` 목록의 각 항목이 무엇을 의미하는지(파일/로그/텍스트
  보고 구분)는 이 모듈이 해석하지 않는다 — opaque 문자열로만
  다룬다(`ADC-0003-execution-result-item-schema.md` Decision).
- ``results``의 빈 목록 허용 여부, 최소/최대 개수는 검증하지 않는다
  — `ADC-0003`이 명시적으로 범위 밖에 둔 결정이다.
- AI/LLM/Model 호출 없음. Runtime/Scheduler/Retry 없음. 시스템 시계
  접근 없음.

## handle_id / produced_at / results를 이 모듈이 생성하지 않는 이유

MVP-0003(request_id/created_at)부터 MVP-0005(state/changed_at)까지와
같은 이유다: 실행 산출물이 "언제, 무엇으로" 만들어졌는지를 판단·기록
하는 행위는 Runtime/Scheduler/Engine의 책임 영역과 겹친다. 그래서
`build_execution_result()`는 `handle_id`, `produced_at`, `results`
셋 다 호출자가 전달한 값을 그대로 사용하며, 내부에서 시계를 읽거나
산출물을 스스로 만들지 않는다. `request_id`만 예외다 — 이 값은
Execution State의 `## State` 절에 이미 있으므로, MVP-0004·MVP-0005가
`request_id`를 재사용했던 것과 동일하게 그대로 읽어서 재사용한다
(Execution State를 Canonical 참조로 유지하기 위함). `handle_id`도
Execution State의 `## State` 절에 이미 있으나, MVP-0005가
`handle_id`를 "호출자가 전달하고 관례상 같은 값을 재사용" 방식으로
다뤘던 것과 동일하게 이 모듈도 호출자 전달 값을 그대로 쓴다(추출하지
않는다).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0006"

EXECUTION_RESULT_HEADER = "# Execution Result\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


def _extract_request_id(execution_state: str) -> str:
    """Execution State의 `## State` 절에 이미 기록된 `request_id` 값을
    그대로 읽는다. 새 값을 만들지 않는다 — 단순 텍스트 추출이다.
    """
    match = _REQUEST_ID_LINE_PATTERN.search(execution_state)
    if not match:
        raise ValueError("execution_state에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_result(
    execution_state: str,
    *,
    handle_id: str,
    produced_at: str,
    results: list[str],
) -> str:
    """Execution State에 대한 Execution Result를 만든다.

    Execution State의 텍스트를 한 글자도 바꾸지 않고, 그 앞에 결과
    메타데이터 절(``## Result``)과 산출물 목록 절(``## Results``)만
    추가한 새 Artifact를 반환한다. ``handle_id``, ``produced_at``,
    ``results``는 호출자가 제공해야 한다(이 함수는 셋 다 생성하지
    않는다). ``results``의 각 항목은 opaque 문자열로만 다루며 내용을
    해석하지 않는다 — 항목 개수도 검증하지 않는다(빈 목록도 허용).
    ``request_id``는 Execution State에서 그대로 읽어온다.
    ``artifact_version``은 항상 모듈 상수다.
    """
    request_id = _extract_request_id(execution_state)

    result_lines = "\n".join(
        [
            f"- handle_id: {handle_id}",
            f"- request_id: {request_id}",
            f"- produced_at: {produced_at}",
            f"- artifact_version: {ARTIFACT_VERSION}",
        ]
    )

    results_lines = "\n".join(f"- {item}" for item in results)

    return (
        f"{EXECUTION_RESULT_HEADER}"
        f"## Result\n{result_lines}\n\n"
        f"## Results\n{results_lines}\n\n"
        f"## Execution State\n{execution_state}"
    )
