# Execution Layer MVP-0003 Observation

## 목적

이번 MVP의 목적은 Prompt Specification을 Model Request로 변환하는
것이다. AI 모델은 호출하지 않는다. 이 문서는 사실만 기록한다.
Architecture 판단은 하지 않는다. RFC/ADC/ADR을 생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0003/model_request_builder.py`(신규) —
  `build_model_request(prompt_specification, *, request_id, created_at) -> str`
  하나와, 고정 상수 `ARTIFACT_VERSION`, `TARGET_ENGINE_PLACEHOLDER`.
- `core/execution_layer/mvp_0003/tests/test_model_request_builder.py`
  (신규) — 6개 테스트.
- `core/execution_layer/mvp_0003/dogfooding/run_dogfooding.py`(신규) —
  Development HQ `workflow_0008.run_pipeline()` → MVP-0001
  `build_execution_request()` → MVP-0002 `build_prompt_specification()`
  → MVP-0003 `build_model_request()` 전체 4단계를 순서대로 호출한다
  (모두 읽기 전용, 수정 없음).
- Development HQ, MVP-0001(`execution_request_builder.py`), MVP-0002
  (`prompt_specification_builder.py`) 모두 수정하지 않았다. `git status`
  로 세 경로에 변경 사항이 없음을 확인했다.

## Capability

`ModelRequestBuilder`(모듈 `model_request_builder.py`) 하나만 구현했다.
책임은 `build_model_request()` 함수 하나로 한정된다: Prompt
Specification 앞에 `## Metadata` 절(4개 필드: request_id,
artifact_version, created_at, target_engine)만 추가한다. Prompt
Specification 본문은 바꾸지 않는다.

## request_id / created_at을 생성하지 않기로 한 이유 (설계 사실)

`build_model_request()`는 `request_id`와 `created_at`을 필수 인자로
받으며, 함수 내부에서 시스템 시계를 읽거나 무작위 값을 생성하지 않는다.
이는 값 생성 자체가 "무엇을 언제 요청했는가"를 추적하는 Session/Runtime의
책임 영역과 겹치기 때문이다 — 이번 MVP의 Constraints("Session 금지",
"Runtime 금지")를 넘지 않기 위해, 두 값을 순수하게 호출자 주입 방식으로
남겨 두었다. 이 설계 덕분에 함수는 부작용이 없고(시계·난수 의존 없음),
동일한 세 인자가 주어지면 항상 동일한 출력을 만든다.

Dogfooding 스크립트는 호출자로서 두 값을 다음과 같이 채웠다(이 결정은
`model_request_builder.py`가 아니라 `run_dogfooding.py`에 있다):

- `request_id`: Prompt Specification 내용의 SHA-256 해시 앞 16자 —
  무작위 발급이 아니라 내용 기반 결정론적 유도(같은 입력 → 같은 값).
- `created_at`: 고정 placeholder 문자열 `"unresolved"` — 이 MVP는 실제
  시계를 읽지 않는다는 사실을 그대로 반영했다.

## 실행 결과 (실측)

`python3 -m pytest development-hq/mvp/tests/ core/execution_layer/mvp_0001/tests/ core/execution_layer/mvp_0002/tests/ core/execution_layer/mvp_0003/tests/ -q`
→ 22개 테스트 모두 통과(회귀 없음: 기존 3건 + MVP-0001 6건 + MVP-0002
7건 + MVP-0003 6건).

`python3 core/execution_layer/mvp_0003/dogfooding/run_dogfooding.py`를
직접 실행한 콘솔 출력(그대로 인용):

```
--- real_issue ---
Implementation Specification length: 6602
Execution Request length: 6623
Prompt Specification length: 6700
Model Request length: 6883
request_id (derived): 099012e5add6bcb1
prompt_specification in model_request: True

--- toy_issue ---
Implementation Specification length: 2781
Execution Request length: 2802
Prompt Specification length: 2879
Model Request length: 3062
request_id (derived): 4b70a4540220e098
prompt_specification in model_request: True
```

산출물은 `core/execution_layer/mvp_0003/dogfooding/output/`에 저장되어
있다: 각 Case별 `.implementation_specification.md`,
`.execution_request.md`, `.prompt_specification.md`,
`.model_request.md` 4개 파일씩, 총 8개.

## Dogfooding

실제 Issue는 이전 두 MVP와 동일하게 `development-hq/mvp/workflow_0008.py`
의 `REAL_ISSUE`("Project Intelligence 개선")를 재사용했다. 토이 Issue도
동일하게 "reverse string"을 사용했다. `run_pipeline()` →
`build_execution_request()` → `build_prompt_specification()` →
`build_model_request()`를 그대로 연쇄 호출해, Implementation
Specification부터 Model Request까지 전체 Artifact Chain(4단계)을 한
번에 관찰했다. 토이 예제보다 실제 Artifact를 우선한다는 요구에 따라
실제 Issue를 첫 번째 Case로 실행했다.

## Artifact Mapping (요약, 상세는 별도 문서)

상세 항목 대응표는 `docs/core/execution-layer/MVP-0003-artifact-mapping.md`
에 기록했다. 두 Case(실제 Issue, 토이 Issue) 모두에서:

- Prompt Specification 전체가 Model Request 안에 원문 그대로(byte 단위)
  포함되었다(`in` 연산자로 확인).
- 전체 길이 증가분(Prompt Specification → Model Request)은 두 Case
  모두 정확히 183 글자로 동일했다 — 메타데이터 절 구조(제목, 4개 필드
  줄, 절 마커)만 추가되었음을 보여준다.
- `artifact_version`, `target_engine`은 두 Case에서 완전히 동일한
  값(`execution-layer-mvp-0003`, `unresolved`)이었다. `request_id`만
  Case마다 달랐는데, 이는 입력(Prompt Specification 내용)이 다르기
  때문이며 무작위성 때문이 아니다.

## Success Criteria 대조 (사실 확인)

| Success Criteria | 확인 결과 |
|---|---|
| Prompt Specification 정보 100% 보존 | 두 Case 모두 원문 전체가 `in` 연산자로 확인됨 |
| Execution Layer 메타데이터만 추가 | 추가된 내용은 4개 메타데이터 필드와 절 마커뿐(두 Case 모두 183 글자로 동일) |
| Deterministic Transformation | `test_transformation_is_deterministic`에서 동일 3개 인자로 2회 호출해 결과 동일함을 확인 |
| Development HQ 변경 없음 | `git status`로 확인, 변경 없음 |
| 기존 테스트 모두 통과 | 22개 테스트(기존 3 + MVP-0001 6 + MVP-0002 7 + MVP-0003 6) 모두 통과 |
| AI 호출 없음 | `test_no_ai_or_model_call_symbols_present_in_module`으로 소스 코드 안에 `call_engine`, `openai`, `anthropic`, `requests.`, `subprocess`, `urllib`, `http.client`, `datetime.now`, `uuid.uuid4` 문자열이 없음을 확인 |

## Model Independent 확인 (실측)

`test_target_engine_is_a_placeholder_not_a_real_model_name`은
Model Request의 메타데이터 절 텍스트를 소문자로 변환한 뒤,
`claude`/`gpt`/`codex`/`qwen`/`openai`/`anthropic` 6개 문자열이 모두
없음을 확인한다. `target_engine`은 두 Dogfooding Case 모두에서
`unresolved`였다.

## Non-goals (이번 MVP에서 하지 않은 것)

- Model/Engine 호출, HTTP 요청, Session, Runtime, Retry, Scheduler —
  모두 코드에 존재하지 않는다(위 테스트로 확인).
- 실제 request_id 발급 체계(무작위 UUID, 순번 카운터 등)나 실제 시계
  읽기 — 이 MVP는 두 값을 호출자 주입으로 남겨 두었을 뿐, 발급 체계
  자체를 설계하지 않았다.
- Development HQ, MVP-0001, MVP-0002 코드 — 모두 수정하지 않았다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
