# Execution Layer MVP-0001 Observation

## 목적

이번 MVP의 목적은 Execution Layer의 기능을 만드는 것이 아니라, Execution
Layer의 첫 번째 Artifact Contract(Implementation Specification →
Execution Request)를 검증하는 것이다. 이 문서는 사실만 기록한다.
Architecture 판단은 하지 않는다. Execution Layer 구조를 확장하지 않는다.
RFC/ADC/ADR을 생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0001/execution_request_builder.py`(신규) —
  `build_execution_request(implementation_specification: str) -> str`
  하나와, 검증 보조 함수 `find_known_sections(text: str) -> dict` 하나.
- `core/execution_layer/mvp_0001/tests/test_execution_request_builder.py`
  (신규) — 6개 테스트.
- `core/execution_layer/mvp_0001/dogfooding/run_dogfooding.py`(신규) —
  Development HQ `workflow_0008.run_pipeline()`을 호출(읽기 전용)해 실제
  Implementation Specification을 얻고, `build_execution_request()`에
  통과시킨다.
- Development HQ 파일은 어떤 것도 수정하지 않았다. `git status`로
  `development-hq/` 아래 변경 사항이 없음을 확인했다.

## Capability

`ExecutionRequestBuilder`(모듈 `execution_request_builder.py`) 하나만
구현했다. 책임은 `build_execution_request()` 함수 하나로 한정된다:
Implementation Specification 문자열 앞에 머리말
`"# Execution Request\n\n"`(21 글자)를 붙이는 것 외에 어떤 문자도
바꾸지 않는다.

## 실행 결과 (실측)

`python3 -m pytest development-hq/mvp/tests/ -q` → 3개 테스트 모두
통과(회귀 없음).

`python3 -m pytest core/execution_layer/mvp_0001/tests/ -q` → 6개 테스트
모두 통과.

`python3 core/execution_layer/mvp_0001/dogfooding/run_dogfooding.py`를
직접 실행한 콘솔 출력(그대로 인용):

```
--- real_issue ---
Implementation Specification length: 6602
Execution Request length: 6623
8 sections present before: {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
8 sections present after:  {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
before == after: True
implementation_specification in execution_request: True

--- toy_issue ---
Implementation Specification length: 2781
Execution Request length: 2802
8 sections present before: {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
8 sections present after:  {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
before == after: True
implementation_specification in execution_request: True
```

산출물은 `core/execution_layer/mvp_0001/dogfooding/output/`에 저장되어
있다: `real_issue.implementation_specification.md`,
`real_issue.execution_request.md`, `toy_issue.implementation_specification.md`,
`toy_issue.execution_request.md`.

## Dogfooding

실제 Issue는 `development-hq/mvp/workflow_0008.py`의 `REAL_ISSUE`(MVP-0008이
사용한 이 저장소 자신의 실제 Issue, "Project Intelligence 개선")를 그대로
재사용했다. 토이 Issue는 MVP-0004부터 반복 사용된 것과 동일한 무관 Issue
("reverse string")를 사용했다. 두 Issue 모두 `run_pipeline()`을 그대로
호출해(수정 없이) Implementation Specification을 얻었다. 토이 예제보다
실제 Artifact를 우선한다는 요구에 따라, 실제 Issue를 첫 번째 Case로
실행했다.

## Artifact Mapping (요약, 상세는 별도 문서)

상세 항목별 대응표는 `docs/core/execution-layer/MVP-0001-artifact-mapping.md`
에 기록했다. 두 Case(실제 Issue, 토이 Issue) 모두에서:

- 8개 항목(Target File / Public Interface / Functions / Classes /
  Dependencies / Algorithm Outline / Edge Cases / Validation Notes)의
  글자 수가 변환 전/후 완전히 동일했다.
- 원본 Implementation Specification 전체가 Execution Request 안에 부분
  문자열로 그대로 포함되었다(`in` 연산자로 직접 확인).
- 변환 전/후 전체 길이 차이는 두 Case 모두 정확히 21 글자였다(머리말
  길이와 일치, 그 외 추가된 내용 없음).

## Success Criteria 대조 (사실 확인)

| Success Criteria | 확인 결과 |
|---|---|
| 8개 항목 100% 보존 | 두 Case 모두 항목별 글자 수 동일, `in` 연산자로 부분 문자열 포함 확인 |
| 새 의미를 추가하지 않음 | 추가된 내용은 고정 머리말 21 글자뿐(항목 내용 변경 없음) |
| 정보를 제거하지 않음 | 원본 전체가 그대로 포함됨(길이 차이 = 머리말 길이만큼만 증가) |
| 동일 입력 → 동일 출력(Deterministic) | `test_transformation_is_deterministic`에서 동일 입력을 2회 호출해 결과 동일함을 확인 |
| Development HQ 코드 변경 없음 | `git status`로 확인, 변경 없음 |
| 기존 테스트 통과 | `development-hq/mvp/tests/` 3건 모두 통과 |

## Non-goals (이번 MVP에서 하지 않은 것)

- Prompt 생성, Model/Engine 호출, Session, Runtime — 모두 코드에 존재하지
  않는다(`test_no_ai_or_model_call_symbols_present_in_module`으로 소스
  코드 안에 `call_engine`, `openai`, `anthropic`, `requests.`, `subprocess`
  문자열이 없음을 확인).
- Development HQ(Planning, Design, Implementation Specification 생성,
  Validation, Project Intelligence, Workflow), Core RFC-0001, Core
  ADC-0001 문서 — 모두 수정하지 않았다.
- Execution Request의 8개 항목을 파싱해 별도 자료구조(dict, class)로
  재구성하는 것 — `build_execution_request()`는 문자열을 그대로 다룬다.
  `find_known_sections()`는 검증 보조 함수일 뿐, 변환 경로에 관여하지
  않는다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
