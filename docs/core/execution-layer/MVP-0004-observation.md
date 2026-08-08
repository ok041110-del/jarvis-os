# Execution Layer MVP-0004 Observation

## 목적

이번 MVP의 목적은 Model Request를 Execution Handle로 변환하는 것이다.
AI 모델은 호출하지 않는다. 이 문서는 사실만 기록한다. Architecture
판단은 하지 않는다. Runtime, Session은 논의하지 않는다. RFC/ADC/ADR을
생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0004/execution_handle_builder.py`(신규) —
  `build_execution_handle(model_request, *, handle_id, submitted_at) -> str`
  하나와, 보조 추출 함수 `_extract_request_id()`, 고정 상수
  `ARTIFACT_VERSION`, `STATUS_PENDING`.
- `core/execution_layer/mvp_0004/tests/test_execution_handle_builder.py`
  (신규) — 7개 테스트.
- `core/execution_layer/mvp_0004/dogfooding/run_dogfooding.py`(신규) —
  Development HQ `workflow_0008.run_pipeline()` → MVP-0001
  `build_execution_request()` → MVP-0002 `build_prompt_specification()`
  → MVP-0003 `build_model_request()` → MVP-0004
  `build_execution_handle()` 전체 5단계를 순서대로 호출한다(모두 읽기
  전용, 수정 없음).
- Development HQ, MVP-0001(`execution_request_builder.py`), MVP-0002
  (`prompt_specification_builder.py`), MVP-0003
  (`model_request_builder.py`) 모두 수정하지 않았다. `git status`로 네
  경로에 변경 사항이 없음을 확인했다.

## Capability

`ExecutionHandleBuilder`(모듈 `execution_handle_builder.py`) 하나만
구현했다. 책임은 `build_execution_handle()` 함수 하나로 한정된다: Model
Request 앞에 `## Handle` 절(5개 필드: handle_id, request_id, status,
submitted_at, artifact_version)만 추가한다. Model Request 본문은 바꾸지
않는다.

## handle_id / submitted_at을 생성하지 않기로 한 이유 (설계 사실)

`build_execution_handle()`은 `handle_id`와 `submitted_at`을 필수 인자로
받으며, 함수 내부에서 시스템 시계를 읽거나 무작위 값을 생성하지 않는다
— MVP-0003의 `request_id`/`created_at` 설계와 동일한 이유다(값 생성
자체가 Session/Runtime의 책임 영역과 겹친다). `request_id`는 아예 인자로
받지 않는다 — Model Request의 `## Metadata` 절에 이미 기록된 값을 정규식
(`re.search`)으로 그대로 읽어서 재사용한다. 이는 같은 정보를 두 곳에서
따로 입력받아 서로 어긋날 위험을 만들지 않기 위함이며, Model Request를
Canonical 참조 대상으로 유지한다는 요청 원문의 요구와 일치한다.

Dogfooding 스크립트는 호출자로서 두 값(`handle_id`, `submitted_at`)을
다음과 같이 채웠다(이 결정은 `execution_handle_builder.py`가 아니라
`run_dogfooding.py`에 있다):

- `handle_id`: Model Request 내용의 SHA-256 해시 앞 16자 — 무작위
  발급이 아니라 내용 기반 결정론적 유도(같은 입력 → 같은 값).
- `submitted_at`: 고정 placeholder 문자열 `"unresolved"` — 이 MVP는
  실제 시계를 읽지 않는다는 사실을 그대로 반영했다.

## 실행 결과 (실측)

`python3 -m pytest development-hq/mvp/tests/ core/execution_layer/mvp_0001/tests/ core/execution_layer/mvp_0002/tests/ core/execution_layer/mvp_0003/tests/ core/execution_layer/mvp_0004/tests/ -q`
→ 29개 테스트 모두 통과(회귀 없음: 기존 3건 + MVP-0001 6건 + MVP-0002
7건 + MVP-0003 6건 + MVP-0004 7건).

`python3 core/execution_layer/mvp_0004/dogfooding/run_dogfooding.py`를
직접 실행한 콘솔 출력(그대로 인용):

```
--- real_issue ---
Implementation Specification length: 6602
Execution Request length: 6623
Prompt Specification length: 6700
Model Request length: 6883
Execution Handle length: 7082
request_id (derived): 099012e5add6bcb1
handle_id (derived): 3774bd87e088a9f5
model_request in execution_handle: True

--- toy_issue ---
Implementation Specification length: 2781
Execution Request length: 2802
Prompt Specification length: 2879
Model Request length: 3062
Execution Handle length: 3261
request_id (derived): 4b70a4540220e098
handle_id (derived): f8e2ef639b4d6b92
model_request in execution_handle: True
```

산출물은 `core/execution_layer/mvp_0004/dogfooding/output/`에 저장되어
있다: 각 Case별 `.implementation_specification.md`,
`.execution_request.md`, `.prompt_specification.md`,
`.model_request.md`, `.execution_handle.md` 5개 파일씩, 총 10개.

## Dogfooding

실제 Issue는 이전 세 MVP와 동일하게 `development-hq/mvp/workflow_0008.py`
의 `REAL_ISSUE`("Project Intelligence 개선")를 재사용했다. 토이 Issue도
동일하게 "reverse string"을 사용했다. `run_pipeline()` →
`build_execution_request()` → `build_prompt_specification()` →
`build_model_request()` → `build_execution_handle()`을 그대로 연쇄
호출해, Implementation Specification부터 Execution Handle까지 전체
Artifact Chain(5단계)을 한 번에 관찰했다. 토이 예제보다 실제 Artifact를
우선한다는 요구에 따라 실제 Issue를 첫 번째 Case로 실행했다.

## Artifact Mapping (요약, 상세는 별도 문서)

상세 항목 대응표는 `docs/core/execution-layer/MVP-0004-artifact-mapping.md`
에 기록했다. 두 Case(실제 Issue, 토이 Issue) 모두에서:

- Model Request 전체가 Execution Handle 안에 원문 그대로(byte 단위)
  포함되었다(`in` 연산자로 확인).
- 전체 길이 증가분(Model Request → Execution Handle)은 두 Case 모두
  정확히 199 글자로 동일했다 — Handle 절 구조(제목, 5개 필드 줄, 절
  마커)만 추가되었음을 보여준다.
- `status`, `artifact_version`은 두 Case에서 완전히 동일한 값
  (`PENDING`, `execution-layer-mvp-0004`)이었다.
- `request_id`는 두 Case 모두 MVP-0003 Dogfooding에서 기록된 값과
  완전히 일치했다(real_issue: `099012e5add6bcb1`, toy_issue:
  `4b70a4540220e098`) — 새로 생성되지 않고 Model Request에서 그대로
  재사용되었음을 실측으로 확인했다.
- `handle_id`만 Case마다 값이 달랐는데, 이는 입력(Model Request 내용)이
  다르기 때문이며 무작위성 때문이 아니다.

## Success Criteria 대조 (사실 확인)

| Success Criteria | 확인 결과 |
|---|---|
| Model Request 100% 보존 | 두 Case 모두 원문 전체가 `in` 연산자로 확인됨 |
| Execution Handle 메타데이터만 추가 | 추가된 내용은 5개 Handle 필드와 절 마커뿐(두 Case 모두 199 글자로 동일) |
| status=PENDING | 두 Case 모두 `- status: PENDING` 확인, RUNNING/COMPLETED/FAILED/CANCELLED 미등장 |
| 동일 입력 → 동일 Handle(Deterministic) | `test_transformation_is_deterministic`에서 동일 3개 인자로 2회 호출해 결과 동일함을 확인 |
| Development HQ 변경 없음 | `git status`로 확인, 변경 없음 |
| 기존 테스트 모두 통과 | 29개 테스트(기존 3 + MVP-0001 6 + MVP-0002 7 + MVP-0003 6 + MVP-0004 7) 모두 통과 |
| AI 호출 없음 | `test_no_ai_or_model_call_symbols_present_in_module`으로 소스 코드 안에 `call_engine`, `openai`, `anthropic`, `requests.`, `subprocess`, `urllib`, `http.client`, `datetime.now`, `uuid.uuid4`, `time.time` 문자열이 없음을 확인 |

## Non-goals (이번 MVP에서 하지 않은 것)

- Model/Engine 호출, HTTP 요청, Session, Runtime, Retry, Scheduler,
  시스템 시계 접근, Handle ID 자체 생성 — 모두 코드에 존재하지 않는다
  (위 테스트로 확인).
- RUNNING/COMPLETED/FAILED/CANCELLED 등 status 전이 — 다루지 않았다.
  status는 `"PENDING"` 고정값 하나뿐이다.
- Development HQ, MVP-0001, MVP-0002, MVP-0003 코드 — 모두 수정하지
  않았다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
