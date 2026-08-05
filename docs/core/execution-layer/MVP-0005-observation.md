# Execution Layer MVP-0005 Observation

## 목적

이번 MVP의 목적은 Execution State Contract를 정의하는 것이다. State
Machine을 구현하지 않는다. Runtime을 구현하지 않는다. Execution
Handle에 대한 상태 계약만 구현한다. 이 문서는 사실만 기록한다.
Architecture 판단, State Machine 논의, Runtime 논의는 하지 않는다.
RFC/ADC/ADR을 생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0005/execution_state_builder.py`(신규) —
  `build_execution_state(execution_handle, *, handle_id, state, changed_at) -> str`
  하나와, 보조 추출 함수 `_extract_request_id()`, 고정 상수
  `ARTIFACT_VERSION`, `ALLOWED_STATES`(5개), 예외
  `InvalidExecutionStateError`.
- `core/execution_layer/mvp_0005/tests/test_execution_state_builder.py`
  (신규) — 9개 테스트(5개 허용 상태에 대한 파라미터화 테스트 포함).
- `core/execution_layer/mvp_0005/dogfooding/run_dogfooding.py`(신규) —
  Development HQ `workflow_0008.run_pipeline()` → MVP-0001~0004 →
  MVP-0005 `build_execution_state()` 전체 6단계를 순서대로 호출한다
  (모두 읽기 전용, 수정 없음).
- Development HQ, MVP-0001(`execution_request_builder.py`), MVP-0002
  (`prompt_specification_builder.py`), MVP-0003
  (`model_request_builder.py`), MVP-0004
  (`execution_handle_builder.py`) 모두 수정하지 않았다. `git status`로
  다섯 경로에 변경 사항이 없음을 확인했다.

## Capability

`ExecutionStateBuilder`(모듈 `execution_state_builder.py`) 하나만
구현했다. 책임은 `build_execution_state()` 함수 하나로 한정된다:
Execution Handle 앞에 `## State` 절(5개 필드: handle_id, request_id,
state, changed_at, artifact_version)을 추가한 **새 Artifact**를
만든다. Execution Handle 본문은 바꾸지 않으며, Execution Handle 자체도
수정되지 않는다(새 Artifact 생성일 뿐).

## state를 "이름만 검증"하기로 한 것 (설계 사실)

`build_execution_state()`는 `state`가 `ALLOWED_STATES`
(PENDING/RUNNING/COMPLETED/FAILED/CANCELLED) 5개 중 하나인지만
확인한다. 어떤 상태에서 어떤 상태로 전이할 수 있는지(State Transition
규칙)는 검증하지 않는다. 테스트
(`test_state_validation_does_not_check_transition_rules`)로 이를
직접 확인했다: 동일한 Execution Handle에 대해 `state="COMPLETED"`로
Execution State를 만든 뒤, 곧바로 같은 Execution Handle에
`state="PENDING"`으로도 Execution State를 만들 수 있었다 — 거부되지
않았다.

## handle_id / state / changed_at을 생성하지 않기로 한 이유 (설계 사실)

`build_execution_state()`는 `handle_id`, `state`, `changed_at` 셋 다
필수 인자로 받으며, 함수 내부에서 시스템 시계를 읽거나 상태를 스스로
결정하지 않는다 — MVP-0003, MVP-0004와 동일한 이유다(값 생성·결정
자체가 Runtime/Scheduler의 책임 영역과 겹친다). `request_id`만 예외로,
Execution Handle의 `## Handle` 절에 이미 있는 값을 정규식으로 그대로
읽어서 재사용한다(Execution Handle을 Canonical 참조로 유지).

Dogfooding 스크립트는 호출자로서 세 값을 다음과 같이 채웠다(이 결정은
`execution_state_builder.py`가 아니라 `run_dogfooding.py`에 있다):

- `handle_id`: 방금 만든 Execution Handle 자신의 `## Handle` 절에서
  추출한 값을 그대로 재사용했다(새로 유도하지 않음).
- `state`: 이번 MVP가 다루는 5개 값 중 `"PENDING"`(Execution Handle이
  막 만들어진 직후의 최초 상태)을 사용했다.
- `changed_at`: 고정 placeholder 문자열 `"unresolved"` — 이전 MVP의
  `created_at`/`submitted_at`과 동일하게, 이 MVP는 실제 시계를 읽지
  않는다는 사실을 그대로 반영했다.

## 실행 결과 (실측)

`python3 -m pytest development-hq/mvp/tests/ core/execution_layer/mvp_0001/tests/ core/execution_layer/mvp_0002/tests/ core/execution_layer/mvp_0003/tests/ core/execution_layer/mvp_0004/tests/ core/execution_layer/mvp_0005/tests/ -q`
→ 42개 테스트 모두 통과(회귀 없음: 기존 3건 + MVP-0001 6건 + MVP-0002
7건 + MVP-0003 6건 + MVP-0004 7건 + MVP-0005 9건).

`python3 core/execution_layer/mvp_0005/dogfooding/run_dogfooding.py`를
직접 실행한 콘솔 출력(그대로 인용):

```
--- real_issue ---
Implementation Specification length: 6602
Execution Request length: 6623
Prompt Specification length: 6700
Model Request length: 6883
Execution Handle length: 7082
Execution State length: 7279
request_id (derived): 099012e5add6bcb1
handle_id (derived): 3774bd87e088a9f5
handle_id (from execution_handle): 3774bd87e088a9f5
execution_handle in execution_state: True

--- toy_issue ---
Implementation Specification length: 2781
Execution Request length: 2802
Prompt Specification length: 2879
Model Request length: 3062
Execution Handle length: 3261
Execution State length: 3458
request_id (derived): 4b70a4540220e098
handle_id (derived): f8e2ef639b4d6b92
handle_id (from execution_handle): f8e2ef639b4d6b92
execution_handle in execution_state: True
```

산출물은 `core/execution_layer/mvp_0005/dogfooding/output/`에 저장되어
있다: 각 Case별 `.implementation_specification.md`,
`.execution_request.md`, `.prompt_specification.md`,
`.model_request.md`, `.execution_handle.md`, `.execution_state.md`
6개 파일씩, 총 12개.

## Dogfooding

실제 Issue는 이전 네 MVP와 동일하게 `development-hq/mvp/workflow_0008.py`
의 `REAL_ISSUE`("Project Intelligence 개선")를 재사용했다. 토이 Issue도
동일하게 "reverse string"을 사용했다. `run_pipeline()` →
`build_execution_request()` → `build_prompt_specification()` →
`build_model_request()` → `build_execution_handle()` →
`build_execution_state()`를 그대로 연쇄 호출해, Implementation
Specification부터 Execution State까지 전체 Artifact Chain(6단계)을
한 번에 관찰했다. 토이 예제보다 실제 Artifact를 우선한다는 요구에 따라
실제 Issue를 첫 번째 Case로 실행했다.

## Artifact Mapping (요약, 상세는 별도 문서)

상세 항목 대응표는 `docs/core/execution-layer/MVP-0005-artifact-mapping.md`
에 기록했다. 두 Case(실제 Issue, 토이 Issue) 모두에서:

- Execution Handle 전체가 Execution State 안에 원문 그대로(byte 단위)
  포함되었다(`in` 연산자로 확인). Execution Handle 자체는 변경되지
  않았다.
- 전체 길이 증가분(Execution Handle → Execution State)은 두 Case 모두
  정확히 197 글자로 동일했다.
- `handle_id`(호출자가 전달한 값)와 Execution Handle 본문 안의
  `handle_id`가 두 Case 모두 완전히 일치했다.
- `request_id`는 두 Case 모두 MVP-0003·MVP-0004 Dogfooding에서 기록된
  값과 완전히 일치했다 — 체인 전체에서 값이 한 번도 바뀌지 않았다.

## Success Criteria 대조 (사실 확인)

| Success Criteria | 확인 결과 |
|---|---|
| Execution Handle 100% 보존 | 두 Case 모두 원문 전체가 `in` 연산자로 확인됨 |
| Execution State 메타데이터만 추가 | 추가된 내용은 5개 State 필드와 절 마커뿐(두 Case 모두 197 글자로 동일) |
| State 이름만 검증 | 5개 허용 상태 각각에 대한 파라미터화 테스트로 확인, 허용되지 않은 이름은 `InvalidExecutionStateError`로 거부됨, Transition 규칙은 미검증(COMPLETED 다음 PENDING도 허용됨을 테스트로 확인) |
| Deterministic Transformation | `test_transformation_is_deterministic`에서 동일 4개 인자로 2회 호출해 결과 동일함을 확인 |
| Development HQ 변경 없음 | `git status`로 확인, 변경 없음 |
| 기존 테스트 모두 통과 | 42개 테스트(기존 3 + MVP-0001 6 + MVP-0002 7 + MVP-0003 6 + MVP-0004 7 + MVP-0005 9) 모두 통과 |
| AI 호출 없음 | 소스 코드 안에 `call_engine`, `openai`, `anthropic`, `requests.`, `subprocess`, `urllib`, `http.client`, `datetime.now`, `uuid.uuid4`, `time.time` 문자열이 없음을 확인 |
| Runtime 없음 | 코드 안에 Scheduler/Runtime을 구현한 클래스나 함수 호출이 없음(모듈은 상태 이름 검증과 텍스트 조합만 수행) |

## Non-goals (이번 MVP에서 하지 않은 것)

- State Machine, State Transition 규칙(어떤 상태에서 어떤 상태로
  옮겨갈 수 있는지) — 구현하지 않았다. `state`는 5개 허용된 이름 중
  하나인지만 확인한다.
- Runtime, Scheduler, Retry — 코드에 존재하지 않는다(위 테스트로 확인).
- 실제 handle_id 재검증(Execution Handle 안의 값과 호출자가 전달한
  값이 실제로 같은지 교차 확인) — 이 MVP는 `request_id`만 Execution
  Handle에서 읽고, `handle_id`는 호출자가 전달한 값을 그대로 신뢰한다
  (요청 원문이 `handle_id`를 호출자 전달 항목으로 명시했기 때문).
- 시스템 시계 접근 — `changed_at`은 호출자가 전달한다.
- Development HQ, MVP-0001~0004 코드 — 모두 수정하지 않았다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
