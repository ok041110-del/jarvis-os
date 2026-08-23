# Stage 03: Validation

## 검증 원칙

Capability 1은 순수 함수라 mock 없이 결정적으로 단위 테스트한다.
Capability 2는 기존 `design_agent_design()`을 재사용하므로 그 자체
동작은 기존 테스트가 이미 검증했다 — 여기서는 (a) 골격+Specification이
반영된 `requirement`가 실제로 전달되는지, (b) Engine 실패 시 기존
오류 포맷 유지 여부를 mock으로 확인하고, (c) 실제 Engine 호출 1건으로
Stage 01/02 Context가 Design에 반영되는지, Design이 Stage 04
Input(`identify_target`)으로 쓰일 수 있는 형태인지 확인한다.

## 테스트 위치

`hqs/development/mvp/tests/test_stage_03.py` — Stage 01/02와 동일하게
Stage 폴더 하위가 아닌 기존 공통 `tests/` 위치를 쓴다(ADR-0008 §1).

## 검증 항목

| 항목 | 방법 |
|---|---|
| Skeleton 4개 키가 Stage 01/02 Output을 정확히 반영 | Stage 01 `candidate_index`가 `component_candidates`로, Stage 02 `skeleton`의 3개 필드가 그대로 옮겨지는지 단위 테스트 |
| Skeleton이 비어 있어도 예외 없이 빈 값 처리 | Stage 02 `skeleton`의 해당 필드가 빈 리스트일 때도 동일하게 처리되는지 확인 |
| Engine이 골격+Specification이 반영된 `requirement`를 실제로 받는지 | `design_agent_design`을 mock해 전달된 `requirement` 인자에 Specification 원문과 골격 텍스트(예: Component Candidates 항목)가 모두 포함됐는지 확인 |
| Engine 실패 시 오류 포맷 유지 | mock이 예외를 던질 때 `design`이 `_engine_failure_message()` 형식인지 확인 |
| Stage 01/02 Context가 실제 Design에 반영(real Engine) | 아래 "real Engine E2E" 참고 |
| Stage 04가 소비 가능한 형태인지 | `design`이 `str`이며 `workflow_ast_context.identify_target(design)`에 그대로 전달 가능한지 real Engine E2E에서 함께 확인(호출 자체는 하지 않고 타입/시그니처 정합성만 확인 — 실제 호출은 Stage 04 범위) |

## real Engine E2E

Stage 03도 Engine을 1회 호출하므로(Capability 2), 핵심 요구사항 —
"Stage 01/02가 Design 생성에 실제로 활용되는가" — 는 mock만으로
증명되지 않는다. 실제 `call_engine()`으로 1건을 실행해:

1. Stage 01 → Stage 02 → Stage 03을 순서대로 실제 실행한다(Blind
   Issue — 실제 파일명/함수명을 언급하지 않음).
2. 반환된 `design` 텍스트가 Stage 01 Component Candidates/Stage 02
   Scope Candidates·Constraints·Risks를 실제로 반영하는지 확인한다.
3. `design`이 9개 관점(Architecture Definition/Component
   Identification/Responsibility Allocation/Interface·Contract
   Identification/Data Flow/Dependency·Boundary Definition/
   Implementation Strategy/Design Constraints/Design Risks)을 실제로
   포함하는지 확인한다.
4. 결과와 판정(PASS/PARTIAL/FAIL)을 이 Stage의 최종 보고(세션 기록)에
   남긴다 — 이 문서는 방법론만 고정하고 특정 시점의 결과를 반복
   기록하지 않는다.

Stage 04(Implementation)와 달리, 이 E2E는 실제 코드 파일을 수정하지
않는다 — Design은 텍스트 산출물이므로 backup/apply/revert 절차가
필요 없다. `identify_target(design)` 호출 자체도 이 E2E 범위 밖이다
(Stage 04의 실제 구현/E2E에서 검증).
