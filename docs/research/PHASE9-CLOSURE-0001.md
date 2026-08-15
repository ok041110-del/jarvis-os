# PHASE9-CLOSURE-0001: Engine Adapter 필요성 검증 — 종료 판정

**문서 성격**: Governance 판단(종료 선언). 새 RFC/ADC/ADR을 작성하지
않는다. Engine Adapter/Gateway를 설계·도입하지 않는다.

## 진행 순서 (전부 실제 Engine 호출 기반 Evidence)

1. `ENGINE-USECASE-0001-parallel-independent-tasks.md` — 독립 Task
   2개를 순차/병렬(스레드) 실행 비교. `call_engine()` 무수정, 새
   Gateway/Adapter/Registry 없이 병렬 실행 성공(순차 32.19s → 병렬
   20.11s), 교차오염 없음(실측).
2. `ENGINE-USECASE-0002-nway-parallel-validation.md` — 독립 Task를
   3개·4개로 확장. 4-way까지 실제 Engine 호출 총 16회 전부 성공,
   실패·timeout·교차오염 0건. 병렬 단축률은 N이 늘수록 편차가 커짐(성능
   특성이며 기능적 실패 아님).

## 최종 분류

**현재 구조(단일 `call_engine()` 함수 + 호출부 스레드화)로 충분.**
4-way 병렬까지 Adapter/Gateway/Registry/Scheduler 없이 실제로 동작함을
확인했다. 유일하게 관찰된 구조적 한계는 비용 관측 불가(`--output-format
text`가 토큰/비용 필드를 반환하지 않음)이며, 이는 새로운 결함이 아니라
기존 계약("텍스트를 받아 텍스트를 반환한다")이 처음부터 다루지 않는
영역의 재확인이다.

## Engine Adapter — NEED-DRIVEN DEFER

Engine Adapter(Port/Adapter 추상화)를 지금 설계·도입하지 않는다.
`development-hq/CONSTITUTION.md` Architecture Freeze 목록의 "Engine
Adapter" 항목, `RT-0001` Candidate 2(Engine Gateway, Re-evaluation
Trigger: "Engine 수 ≥ 2")와 일치하는 결론이다. 다음 조건 중 하나가
**실제로** 관찰될 때만 재검토한다(지금 선제적으로 설계하지 않는다):

1. **두 번째 실제 Engine이 실제로 추가될 때**(`call_engine()` 호출
   지점이 둘 이상의 서로 다른 Engine을 대상으로 하게 됨) — `RT-0001`
   Candidate 2와 동일한 조건. 현재 Engine 수: 1(Claude Code).
2. **현재 `call_engine()`으로 해결 불가능한 실제 Use Case가 발생할
   때** — 이번 Phase 9(4-way 병렬까지)에서는 발생하지 않았다. 유일한
   후보였던 "비용 관측"도 Contract 변경(`--output-format json`) 없이는
   불가능하다는 사실만 확인했을 뿐, 그 자체가 Adapter를 요구하지는
   않는다(Contract 변경과 Adapter 도입은 서로 다른 결정).

## Production Caller 위치와의 관계

Production Engine Caller 위치(`ADC-0010`/`ADC-0011`, C1~C6 전부 Not
Accepted)는 이 판정과 별개의 독립된 Blocking으로 남는다 — 두 번째
Engine이 생기거나 위 Use Case가 발생해도, Caller 위치 자체는 여전히
별도 Governance(RFC → ADC → ADR)를 거쳐야 한다. 이 문서는 그 판단을
재론하지 않는다.

## Architecture/Governance

RFC/ADC/ADR 없음. Baseline 무수정. `RT-0001`의 기존 Trigger 정의를
그대로 인용했을 뿐, 새 Trigger를 만들지 않았다.

## Phase 9 종료

**종료한다.**
