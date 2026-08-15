# PHASE10-CLOSURE-0001: Prompt Specification 필요성 검증 — 종료 판정

**문서 성격**: Governance 판단(종료 선언). 새 RFC/ADC/ADR을 작성하지
않는다. Prompt Specification을 설계·도입하지 않는다.

## 진행 순서 (전부 실제 Engine 호출 기반 Evidence)

1. `PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md` — Prompt Specification의
   현재 정의(Execution Layer MVP-0002 전용, Development HQ 미사용)와
   `NO_ISSUES_MARKER` 반복성 한계(3회 중 1회)를 실측 확인. 분류 B
   (Capability Prototype으로 해결 시도).
2. `MVP-0050-observation.md` — 1차 Prototype("issue" 범위 확대) →
   **Failure**(1/3 → 0/3, 악화), 변경 되돌림.
3. `MVP-0051-observation.md` — 2차 Prototype("real issue"의 정의를
   명시, marker 자체는 강조하지 않음) → **Success**(1/3 → 3/3), 채택.
4. `MVP-0052-observation.md` — 채택된 기준을 더 모호한 경계 입력으로
   검증 → **Success**(15회 전체에서 기준 자기모순 0건).

## 최종 분류

**B — Capability Prototype으로 해결됨.** Prompt Specification 없이,
`agents.py`의 Capability 지시문 한 문장 재정의만으로 반복성 한계가
해소됐고, 더 모호한 경계 입력에서도 그 해결이 유지됨을 실측으로
확인했다.

## Prompt Specification — NEED-DRIVEN DEFER

Prompt Specification(Execution Layer MVP-0002)을 Development HQ에
도입할 필요성은 이번 Phase 10 전 과정(Audit + 2회 Prototype + Boundary
Validation)에서 **한 번도 확보되지 않았다.** 지금 설계·도입하지
않는다. 다음 조건 중 하나가 **실제로** 관찰될 때만 재검토한다(지금
선제적으로 만들지 않는다):

1. Capability 지시문 수정만으로 해결되지 않는 반복성/일관성 문제가
   실제로 나타날 때(이번 Phase 10에서는 매번 지시문 수정 범위 안에서
   해결됨).
2. 입력 자체의 구조화(여러 파일, 구조화된 Context)가 실제로 필요한
   Use Case가 나타날 때 — `code_review`처럼 단일 문자열 입력으로
   충분한 현재 Capability들과는 다른 경우.

## 잔여 관찰 (Phase 10 범위 밖, 별도 기록만)

`MVP-0052` §2가 새로 발견한 "탐지 재현율 편차"(Engine이 같은 잠재
결함을 매번 알아채지는 못함)는 Prompt Specification으로도, 지시문
재정의로도 해결되는 종류가 아니라고 판단했다 — 단일 stochastic
Engine 호출의 본질적 특성이다. 별도 구현 대상으로 열지 않는다.

## Architecture/Governance

RFC/ADC/ADR 없음. Baseline 무수정.

## Phase 10 종료

**종료한다.**
