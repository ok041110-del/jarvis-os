# Investment HQ Structure

`hqs/development/STRUCTURE.md`와 동일한 원칙을 따른다 — Investment HQ는
Development HQ가 확립한 Reference Architecture를 재사용해서 만든
두 번째 HQ다(`docs/architecture/baseline/BASELINE.md` §4 "Reference
Architecture", §3 "Composable HQ" 원칙).

## 내부 계층

```
Investment HQ
↓
(선택적) Investment Division
↓
(선택적) Team (Stock / ETF / Dividend Stock)
↓
Agent/Role
↓
Execution
```

Division과 Team은 Investment HQ 내부의 선택적 관례이며, Jarvis OS
Meta Architecture의 필수 계층이 아니다(`docs/architecture/baseline/
BASELINE.md` §5). Jarvis OS Kernel은 Division/Team의 존재 여부를
알지 못하며, 이 계층은 Registry에 등록되지 않는다 — Development HQ와
완전히 동일한 원칙이다.

이 계층 구조를 인스턴스화하는 것은 새 Architecture Concept을 만드는
것이 아니라, Development HQ가 이미 정의한 계층을 두 번째 HQ에 그대로
적용하는 것이다. 따라서 RFC → ADC → ADR 절차의 대상이 아니다(Stock/
ETF/Dividend Stock Team 각 Definition 문서가 이미 동일하게 판단함).

## Team (현재 3개, `docs/research/INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`에서 Closure)

| Team | 분석 Role 수 | 근거 |
|---|---|---|
| Stock | 5 | `docs/research/STOCK-TEAM-DEFINITION-0001.md`, 5회 Dogfooding |
| ETF | 6 | `docs/research/ETF-TEAM-DEFINITION-0001.md`, 6회 Dogfooding |
| Dividend Stock | 7 | `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`, 7회 Dogfooding |

세 Team 모두 동일한 4-Wave 실행 패턴(N개 분석 병렬 → Bull/Bear 병렬 →
Synthesis → Final Report)을 공유한다 — Closure 문서 참조.

## Execution — 신규 표준 실행 패턴 재사용

PR #80에서 검증·채택되고 PR #81~83에서 프로덕션 반복 검증된 표준
패턴을 그대로 쓴다:

1. **병렬화** — 상호 독립적인 분석 호출을 `ThreadPoolExecutor`로 동시
   실행(Wave 순서는 하드코딩, Workflow Parser/Scheduler 아님)
2. **출력 최적화** — Report Writer instruction에 800~1200단어 제약
3. **Checkpointing** — 단계 완료 즉시 저장, 재실행 시 완료 단계 스킵
4. **180초 Timeout 안전장치** — `hqs/development/mvp/engine.py`의
   `ENGINE_TIMEOUT_SECONDS`는 상향하지 않는다

## 금지 사항 (`hqs/development/IMPLEMENTATION_RULES.md`와 동일 원칙)

Development HQ MVP-0001이 스스로에게 부과한 금지 사항을 Investment
HQ MVP에도 그대로 적용한다:

| 금지 항목 | 이유 |
|---|---|
| Workflow Parser 구현 금지 | Wave 순서는 직접 함수 호출로 충분 |
| Scheduler 구현 금지 | Team 선택은 리터럴 딕셔너리로 충분 |
| Registry 구현/일반화 금지 | Team-Role 매핑은 리터럴 딕셔너리 이상으로 발전시키지 않는다 |
| Runtime 구현 금지 | 개념 자체가 아직 Open Decision |
| Engine Gateway/Routing 구현 금지 | `hqs/development/mvp/engine.py`의 `call_engine()` 단일 함수를 그대로 import해서 쓴다 |
| Policy/Memory Service/Event Bus 구현 금지 | Development HQ와 동일 |
| `hqs/development/` 수정 금지 | Platform은 건드리지 않는다 |
| 기존 완료 프로젝트 소급 수정 금지 | AAPL/NVDA/MSFT/JPM/CAT, QQQ/SCHD/AGG/GLD/VNQ/UUP, JNJ/KO/PG/Nestlé/Toyota/Realty Income/EPD 어느 것도 건드리지 않는다 |

## Engine과의 관계

`hqs/development/STRUCTURE.md`의 "Engine과의 관계" 절과 동일 —
Investment HQ는 Engine 호출을 직접 소유하지 않고, Kernel(Engine
Port/Adapter 성격의 `call_engine()`)을 그대로 import해서 쓴다.
