# Execution Layer MVP-0002 Observation

## 목적

이번 MVP의 목적은 Execution Request를 Prompt Specification으로
Rendering하는 것이다. Execution Request를 해석하거나 변경하지 않는다.
이 문서는 사실만 기록한다. Architecture 판단은 하지 않는다. Prompt
Engineering 일반론은 다루지 않는다. RFC/ADC/ADR을 생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0002/prompt_specification_builder.py`(신규)
  — `build_prompt_specification(execution_request: str) -> str` 하나와,
  고정 배치표 `RENDERING_MAP`, 검증 보조 함수 `find_prompt_sections()`.
- `core/execution_layer/mvp_0002/tests/test_prompt_specification_builder.py`
  (신규) — 7개 테스트.
- `core/execution_layer/mvp_0002/dogfooding/run_dogfooding.py`(신규) —
  Development HQ `workflow_0008.run_pipeline()` → MVP-0001
  `build_execution_request()` → MVP-0002 `build_prompt_specification()`
  전체 흐름을 순서대로 호출한다(모두 읽기 전용, 수정 없음).
- Development HQ, `core/execution_layer/mvp_0001/execution_request_builder.py`
  모두 수정하지 않았다. `git status`로 두 경로에 변경 사항이 없음을
  확인했다.

## Capability

`PromptSpecificationBuilder`(모듈 `prompt_specification_builder.py`)
하나만 구현했다. 책임은 `build_prompt_specification()` 함수 하나로
한정된다: 고정된 배치표(`RENDERING_MAP`)에 따라 Execution Request의
9개 절(8개 Implementation Specification 항목 + Reference Design)을
Prompt Structure의 5개 절(Mission / Input / Constraints / Expected
Output / Validation Notes) 아래로 재배치한다. 각 절의 본문 텍스트는
바꾸지 않는다.

## Rendering Map (배치 규칙)

| Execution Request 절 | → | Prompt Specification 절 |
|---|---|---|
| Target File, Public Interface | → | Mission |
| Dependencies, Reference Design | → | Input |
| Classes, Edge Cases | → | Constraints |
| Functions, Algorithm Outline | → | Expected Output |
| Validation Notes | → | Validation Notes |

이 배치표는 코드(`RENDERING_MAP`)에 고정되어 있으며, 실행 시점에 조건에
따라 달라지지 않는다. 상세 항목별 대응표는
`docs/core/execution-layer/MVP-0002-artifact-mapping.md`에 기록했다.

## 실행 결과 (실측)

`python3 -m pytest development-hq/mvp/tests/ core/execution_layer/mvp_0001/tests/ core/execution_layer/mvp_0002/tests/ -q`
→ 16개 테스트 모두 통과(회귀 없음: 기존 3건 + MVP-0001 6건 + MVP-0002
7건).

`python3 core/execution_layer/mvp_0002/dogfooding/run_dogfooding.py`를
직접 실행한 콘솔 출력(그대로 인용):

```
--- real_issue ---
Implementation Specification length: 6602
Execution Request length: 6623
Prompt Specification length: 6700
8 ER sections present: {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
5 Prompt sections present: {'Mission': True, 'Input': True, 'Constraints': True, 'Expected Output': True, 'Validation Notes': True}
all 9 source section bodies verbatim in prompt spec: True

--- toy_issue ---
Implementation Specification length: 2781
Execution Request length: 2802
Prompt Specification length: 2879
8 ER sections present: {'Target File': True, 'Public Interface': True, 'Functions': True, 'Classes': True, 'Dependencies': True, 'Algorithm Outline': True, 'Edge Cases': True, 'Validation Notes': True}
5 Prompt sections present: {'Mission': True, 'Input': True, 'Constraints': True, 'Expected Output': True, 'Validation Notes': True}
all 9 source section bodies verbatim in prompt spec: True
```

산출물은 `core/execution_layer/mvp_0002/dogfooding/output/`에 저장되어
있다: 각 Case별 `.implementation_specification.md`,
`.execution_request.md`, `.prompt_specification.md` 3개 파일씩, 총 6개.

## Dogfooding

실제 Issue는 MVP-0001과 동일하게 `development-hq/mvp/workflow_0008.py`의
`REAL_ISSUE`("Project Intelligence 개선")를 재사용했다. 토이 Issue도
MVP-0001과 동일한 "reverse string"을 사용했다. `run_pipeline()` →
`build_execution_request()` → `build_prompt_specification()`을 그대로
연쇄 호출해, Implementation Specification부터 Prompt Specification까지
실제 Artifact Flow 전체를 한 번에 관찰했다. 토이 예제보다 실제 Artifact를
우선한다는 요구에 따라 실제 Issue를 첫 번째 Case로 실행했다.

## Artifact Mapping (요약, 상세는 별도 문서)

상세 항목별 대응표는 `docs/core/execution-layer/MVP-0002-artifact-mapping.md`
에 기록했다. 두 Case(실제 Issue, 토이 Issue) 모두에서:

- Execution Request의 9개 절(8개 항목 + Reference Design) 본문이
  Prompt Specification 안에 원문 그대로(byte 단위) 포함되었다(`in`
  연산자로 9개 절 전부 확인).
- 전체 길이 증가분(Execution Request → Prompt Specification)은 두 Case
  모두 정확히 77 글자로 동일했다 — 입력 데이터와 무관하게 고정된 구조용
  텍스트(문서 제목 1개 + Prompt Section 제목 5개 + 원본 소제목 9개의
  구분 개행)만 추가되었음을 보여준다.
- Execution Request 자체는 `build_prompt_specification()` 호출 전후로
  변경되지 않았다(직접 비교 확인).

## Success Criteria 대조 (사실 확인)

| Success Criteria | 확인 결과 |
|---|---|
| Execution Request 정보 100% 보존 | 두 Case 모두 9개 절 본문이 원문 그대로 포함됨을 `in` 연산자로 확인 |
| LLM이 읽기 쉬운 구조 | 요청된 5개 절(Mission/Input/Constraints/Expected Output/Validation Notes)이 최상위 `# ` 마커로 모두 존재 |
| 새 의미를 추가하지 않음 | 추가된 텍스트는 절 제목·구분 개행뿐(두 Case 모두 77 글자로 동일) |
| 동일 입력 → 동일 출력(Deterministic) | `test_rendering_is_deterministic`에서 동일 입력을 2회 호출해 결과 동일함을 확인 |
| Development HQ 변경 없음 | `git status`로 확인, 변경 없음 |
| ExecutionRequestBuilder(MVP-0001) 변경 없음 | `git status`로 확인, 변경 없음 |
| 기존 테스트 모두 통과 | 16개 테스트(기존 3 + MVP-0001 6 + MVP-0002 7) 모두 통과 |

## Non-goals (이번 MVP에서 하지 않은 것)

- Prompt 생성 후 실행, Model/Engine 호출, Session, Runtime, Model
  Connector, Retry, Cost 관리 — 모두 코드에 존재하지 않는다
  (`test_no_ai_or_model_call_symbols_present_in_module`으로 소스 코드
  안에 `call_engine`, `openai`, `anthropic`, `requests.`, `subprocess`
  문자열이 없음을 확인).
- Development HQ(Planning, Design, Implementation Specification 생성,
  Validation, Project Intelligence, Workflow), `ExecutionRequestBuilder`
  (MVP-0001), Kernel RFC-0001, Kernel ADC-0001 문서 — 모두 수정하지 않았다.
- Prompt Engineering 일반론(어떤 문구가 더 효과적인 Prompt인지, Few-shot
  예시 삽입 여부 등) — 다루지 않았다. 이 MVP는 구조 재배치(Rendering)만
  다룬다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
