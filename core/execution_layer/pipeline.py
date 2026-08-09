"""Execution Layer Pipeline — 6개 Builder(MVP-0001~0006)를 하나의 함수로 묶는다.

## 이 파일이 존재하는 이유

`core/execution_layer/mvp_0001/dogfooding/run_dogfooding.py`부터
`mvp_0006/dogfooding/run_dogfooding.py`까지, 6개 Dogfooding 스크립트
전부가 이미 다음과 같은 동일한 순서(Execution Request → Prompt
Specification → Model Request → Execution Handle → Execution State →
Execution Result)로 6개 Builder를 직접 호출해 왔다 — 매번 거의
동일한 코드가 반복됐다. 이 모듈은 새 Architecture를 만드는 것이
아니라, **이미 6번 반복 검증된 순서를 하나의 함수로 추출**한다.

## 왜 Runtime/Scheduler가 아닌가

- Task 순서는 이 함수 본문에 **하드코딩**되어 있다 — 설정 파일, 파서,
  조건문으로 결정되지 않는다(`development-hq/IMPLEMENTATION_RULES.md`:
  "Task 1→Task 2는 직접 함수 호출로 충분. 파서는 Scheduler를 미리
  만드는 것과 동일" — 이미 `development-hq/mvp/workflow_0008.py`
  `run_pipeline()`이 Development HQ 수준에서 쓰는 것과 동일한 패턴).
- 이 함수는 상태를 보관하지 않는다 — 호출마다 독립적으로 실행되고
  끝난다. Session/Runtime의 책임 영역(재시도, 영속화, 다중 실행 추적)
  을 침범하지 않는다.
- Engine 호출 함수(`development-hq/mvp/engine.py`의 단일 호출 지점)를
  이 모듈은 쓰지 않는다. 시스템 시계·난수도 쓰지 않는다 — 6개
  Builder가 이미 지키는 것과 동일한 불변식이다(`ARTIFACT-STANDARD-v1.md`
  "AI 호출 없음, Runtime 없음").
- 새 Artifact/Contract를 만들지 않는다 — 6개 Builder가 이미 Governance
  절차(RFC-0001~0003 → ADC-0001~0003 → ADR-0001~0002)로 결정한
  Contract를 그대로 순서대로 호출할 뿐이다.

## 무엇을 결정하지 않는가

- `request_id`/`handle_id`는 6개 Dogfooding 스크립트가 이미 동일하게
  써 온 방식(SHA-256 해시 앞 16자, 결정론적 유도)을 그대로 재사용한다
  — 새 유도 방식을 만들지 않는다.
- `created_at`/`submitted_at`/`changed_at`/`produced_at`/`state`/
  `results`는 전부 caller가 제공해야 한다 — 이 함수는 시계를 읽거나
  상태·산출물을 스스로 결정하지 않는다(6개 Builder와 동일한 원칙).
"""

import hashlib
import re

from execution_layer.mvp_0001.execution_request_builder import (
    build_execution_request,
)
from execution_layer.mvp_0002.prompt_specification_builder import (
    build_prompt_specification,
)
from execution_layer.mvp_0003.model_request_builder import build_model_request
from execution_layer.mvp_0004.execution_handle_builder import (
    build_execution_handle,
)
from execution_layer.mvp_0005.execution_state_builder import build_execution_state
from execution_layer.mvp_0006.execution_result_builder import (
    build_execution_result,
)

_HANDLE_ID_LINE_PATTERN = re.compile(r"^- handle_id: (?P<value>.+)$", re.MULTILINE)


def _derive_id(content: str) -> str:
    """내용 기반 결정론적 ID(SHA-256 해시 앞 16자). 무작위 발급이 아니다.

    6개 Dogfooding 스크립트(mvp_0001~mvp_0006)가 이미 동일하게 쓰는
    방식을 그대로 재사용한다 — 새 유도 방식을 만들지 않는다.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _extract_handle_id(execution_handle: str) -> str:
    match = _HANDLE_ID_LINE_PATTERN.search(execution_handle)
    if not match:
        raise ValueError("execution_handle에서 handle_id를 찾을 수 없다")
    return match.group("value")


def run_execution_layer_pipeline(
    implementation_specification: str,
    *,
    created_at: str,
    submitted_at: str,
    state: str,
    changed_at: str,
    produced_at: str,
    results: list[str],
) -> str:
    """Implementation Specification에서 Execution Result까지 6개 Builder를
    순서대로 호출한다(Execution Request → Prompt Specification → Model
    Request → Execution Handle → Execution State → Execution Result).

    각 Builder의 Contract는 그대로 유지된다 — 이 함수는 어떤 Artifact의
    내용도 해석하거나 변형하지 않는다. `request_id`/`handle_id`는 이
    함수가 결정론적으로 유도한다(``_derive_id``). 그 외 caller-supplied
    값(`created_at`, `submitted_at`, `state`, `changed_at`,
    `produced_at`, `results`)은 그대로 각 Builder에 전달한다 — 이
    함수는 그 값들의 의미를 해석하거나 검증하지 않는다(각 Builder
    자신의 검증만 적용된다, 예: `state`의 5개 허용값 검증은
    `build_execution_state`가 그대로 수행한다).

    반환값은 최종 Execution Result(`str`)다. 중간 Artifact가 필요하면
    각 Builder를 직접 호출해야 한다 — 이 함수는 중간 결과를 반환하지
    않는다(6개 Dogfooding 스크립트와 달리, 파일로 저장하지도 않는다).
    """
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)

    request_id = _derive_id(prompt_specification)
    model_request = build_model_request(
        prompt_specification, request_id=request_id, created_at=created_at
    )

    handle_id = _derive_id(model_request)
    execution_handle = build_execution_handle(
        model_request, handle_id=handle_id, submitted_at=submitted_at
    )

    handle_id_from_handle = _extract_handle_id(execution_handle)
    execution_state = build_execution_state(
        execution_handle,
        handle_id=handle_id_from_handle,
        state=state,
        changed_at=changed_at,
    )

    return build_execution_result(
        execution_state,
        handle_id=handle_id_from_handle,
        produced_at=produced_at,
        results=results,
    )
