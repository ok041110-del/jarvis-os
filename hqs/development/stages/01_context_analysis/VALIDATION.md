# Stage 01: Validation

## 검증 원칙

Stage 01은 기존 `mvp/` 함수를 재사용만 하므로, 1차 검증은 그 함수들의
기존 테스트(36건, `mvp/tests/`)가 이미 담당한다. 이 문서는 그 위에
추가된 두 가지만 다룬다: (1) `run_stage_01()`이 CONTEXT.md 스키마를
정확히 만족하는지, (2) Stage 01 신설로 인한 회귀가 없는지.

## 테스트 위치

`hqs/development/mvp/tests/test_stage_01.py` — Stage 폴더 하위가
아니라 기존 공통 `tests/` 위치를 그대로 쓴다(ADR-0008 §1: `tests/`는
Stage 하위가 아닌 기존 공통 구조 유지).

## 검증 항목

| 항목 | 방법 |
|---|---|
| `directory_structure` 채워짐 | 실제 저장소 경로 목록에 알려진 항목이 포함되는지 확인 |
| `context_bundle`이 8개 키 계약을 유지 | `build_context_bundle()` 기존 계약과 동일한 키 집합 확인 |
| `candidate_index` 비어있지 않음 | 알려진 함수 시그니처 포함 확인(`ast_context` 기존 테스트와 중복 확인) |
| `target=None`일 때 `dependency_closure=None` | 명시적 단위 테스트 |
| `target` 지정 시 `dependency_closure` 계산됨 | 실제 함수(`agents._strip_code_fence`)로 폐쇄 계산 후 내용 포함 확인 |
| 전체 회귀 | `pytest hqs/development/mvp/tests/ -q` — Stage 01 추가 전후 결과 비교 |

## Engine 호출 여부

Stage 01의 5개 Capability는 전부 Engine을 호출하지 않는다
(`RESPONSIBILITY.md`) — 따라서 모든 검증은 real Engine 없이 결정적으로
수행 가능하다. 이는 Stage 03(Design) 이후에야 필요한 real Engine E2E
검증(`DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-E2E-0001.md`)과의
차이점이다 — Stage 01 자체는 그런 E2E를 요구하지 않는다.

## 현재 결과

`pytest hqs/development/mvp/tests/test_stage_01.py -v`와 전체 회귀
결과는 이 Stage 구현의 최종 보고(세션 기록)에 남긴다 — 이 문서는
방법론만 고정하고 특정 시점의 통과/실패 숫자를 반복 기록하지 않는다
(숫자는 세션 로그가 갖고 있으면 충분).
