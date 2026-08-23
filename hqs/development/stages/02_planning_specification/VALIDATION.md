# Stage 02: Validation

## 검증 원칙

Capability 1(Skeleton 추출)은 순수 함수이므로 mock 없이 결정적으로
단위 테스트한다. Capability 2(Requirement & Specification 생성)는
기존 `requirements_agent_requirement_analysis()`를 그대로 재사용하므로,
그 함수 자체의 Engine 호출 동작은 이미 기존 테스트(`test_workflow_
project_intelligence.py` 등)가 간접 검증한 바 있다 — 여기서는 (a)
Stage 02가 그 함수에 올바른 입력(골격이 반영된 Issue)을 넘기는지, (b)
Engine 실패 시 기존 오류 포맷을 유지하는지만 mock으로 추가 검증하고,
(c) 실제 Engine 호출 1건으로 Stage 01 Context가 Specification에 실제로
반영되는지 확인한다.

## 테스트 위치

`hqs/development/mvp/tests/test_stage_02.py` — Stage 01과 동일하게
Stage 폴더 하위가 아닌 기존 공통 `tests/` 위치를 쓴다(ADR-0008 §1).

## 검증 항목

| 항목 | 방법 |
|---|---|
| Skeleton 4개 키가 Stage 01 Context를 정확히 반영 | `context_bundle`의 `known_constraints`/`open_questions`/`relevant_code`가 각각 `constraints`/`risks`/`scope_candidates`로 그대로 옮겨지는지 단위 테스트 |
| Skeleton이 비어 있어도 예외 없이 빈 값 처리 | `context_bundle`의 해당 필드가 빈 리스트일 때 `skeleton`도 빈 값인지 확인 |
| Engine이 골격이 반영된 Issue를 실제로 받는지 | `requirements_agent_requirement_analysis`를 mock해 전달된 `issue["description"]`에 골격 텍스트(예: Constraints 항목)가 포함됐는지 확인 |
| Engine 실패 시 오류 포맷 유지 | mock이 예외를 던질 때 `specification`이 `_engine_failure_message()` 형식인지 확인 |
| Stage 01 Context가 실제 Specification에 반영(real Engine) | 아래 "real Engine E2E" 참고 |

## real Engine E2E

Stage 02는 Stage 01과 달리 Engine을 1회 호출하므로(Capability 2), 이
Stage의 핵심 요구사항 — "Stage 01의 Context가 Stage 02의 Requirement/
Specification 생성에 실제로 활용되는 것을 검증한다" — 는 mock만으로는
증명되지 않는다. 실제 `call_engine()`으로 1건을 실행해:

1. Stage 01 Context에 특정 신호(예: 알려진 `known_constraints`/
   `relevant_code` 경로)가 존재하는 실제 Issue로 `run_stage_02()`를
   실행한다.
2. 반환된 `specification` 텍스트가 그 신호(파일 경로, Constraint
   문서명 등)를 실제로 언급하는지 확인한다.
3. 결과와 판정(PASS/PARTIAL/FAIL)을 이 Stage의 최종 보고(세션 기록)에
   남긴다 — 이 문서는 방법론만 고정하고 특정 시점의 결과를 반복
   기록하지 않는다.

Stage 04(Implementation)와 달리, 이 E2E는 실제 코드 파일을 수정하지
않는다 — Specification은 텍스트 산출물이므로 backup/apply/revert
절차가 필요 없다.
