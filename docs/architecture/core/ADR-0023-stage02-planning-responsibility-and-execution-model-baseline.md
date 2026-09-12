# ADR-0023: Stage 02 Planning Responsibility & Execution Model — Baseline Reflection

**Status**: Accepted
**근거**: `RFC-0035-stage02-planning-responsibility-and-execution-model.md`,
`ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md`

## Decision (최종 채택)

ADC-0038의 5개 Decision을 확정한다.

1. Stage 02는 Task Decomposition + Dependency Judgment(1개 신규 Agent,
   "Task & Dependency Agent")와 Dependency Ordering + Implementation
   Planning(Deterministic Code)으로 구성된다.
2. Acceptance Criteria는 Stage 01 PRD의 기존 값을 그대로 유지한다 — 신규
   Agent 없음.
3. `SpecificationResult`(Stage 02 Output, Public Contract)에 `tasks`/
   `dependencies`/`plan` 3개 키를 추가한다.

## 결정 이유

- **재추론 회피**: Task Decomposition/Acceptance Criteria는 이미 Stage
  01의 `prd_synthesis.py` 1회 호출 안에서 생성된다는 사실이 LLM 영향력
  조사에서 확인됐다 — Stage 02가 다시 판단하면 동일 판단을 두 번 하는
  것이며, `RFC-0034`가 PRD Synthesis에 대해 이미 세운 "재추론 금지"
  원칙과 정면으로 어긋난다.
- **유일한 신규 판단만 Agent화**: Dependency Judgment(Task 간 의미적
  의존관계)만이 문서상 어디에도 존재하지 않는 진짜 신규 판단이었다 —
  "독립적 판단 책임이 존재하는가"라는 동일 기준(RFC-0030 methodology)을
  Stage 01의 4개 Agent 선정 때와 동일하게 적용한 결과다.
- **1개 Agent로 충분**: Stage 01의 Requirement Agent가 이미 "1회
  호출·다중 구조화 필드 출력"을 증명했으므로, Task 구조화와 Dependency
  판단을 억지로 순차 2-Agent로 쪼갤 필요가 없었다 — 오히려 분리하면
  Multi-Engine 호출 회피 원칙(Stage 02/03이 지금까지 지켜온 "정확히
  1회")을 깨는 쪽이 된다.
- **판단 vs 알고리즘 분리**: Dependency Ordering(위상 정렬)은 그래프
  이론의 확정 해가 있는 문제이므로 LLM 판단이 개입할 이유가 없다 —
  Stage 01/04/05가 이미 실증한 "LLM 판단과 결정적 후처리를 분리"하는
  패턴(RFC-0030 §4)을 그대로 따른다.

## 검토한 대안

| 대안 | 기각/채택 이유 |
|---|---|
| Task Decomposition Agent + Dependency Judgment Agent로 분리(2개 Agent, 순차) | 기각 — 재추론 위험 없이도 실현 가능하지만, Stage 01 패턴(1개 Agent·다중 필드)과 불일치하고 Multi-Engine 호출을 늘림. 근거 문서(LLM 영향력 조사 §3)가 명시적으로 비권고 |
| Acceptance Criteria도 Task 단위로 구조화(Task별 AC Agent 추가) | 기각(현재) — 소비자(Stage03/05 어디도 AC를 구조적으로 쓰지 않음)가 없어 지금 구조화할 근거 부족. §6 재평가 조건으로 이관 |
| Dependency Ordering/Implementation Planning에도 LLM을 남겨 "확인" 역할을 부여 | 기각 — 문서 근거 없는 판단 추가이며, 사용자 지시("불필요하게 Agent를 추가하지 말 것")에 정면으로 반함 |
| `SpecificationResult`를 확장하지 않고 `specification` prose 안에만 Task/Dependency 결과를 남김 | 기각 — Stage 02 재정의의 실질적 목적(Task/Dependency를 다룰 수 있는 책임으로 승격)이 무력화됨. 구조화된 데이터가 없으면 Deterministic Ordering이 애초에 동작할 입력이 없다 |
| 별도 "PlanningResult" Contract 신설(SpecificationResult 대체) | 기각 — `ADR-0009`가 5개 Stage Contract를 이름으로 고정했고, `SpecificationResult`라는 이름 자체가 여전히 적합(PRD가 더 정교해진 것일 뿐 성격이 바뀐 게 아님). 기존 이름 확장이 더 최소 변경 |

## Trade-off

- **얻는 것**: Task/Dependency/Plan이 구조화되어 향후 Stage 03/04/05가
  prose 재해석 없이 프로그램적으로 소비할 수 있는 기반이 생긴다. Agent
  수를 최소(1개)로 유지해 Engine 호출 비용/실패 지점을 늘리지 않는다.
- **잃는 것/위험**: Cycle Detection이 구조적 무결성만 보장하고 의미적
  오판(잘못됐지만 순환은 아닌 의존관계)을 걸러내지 못한다는 한계를
  그대로 안고 간다 — 이는 의도적으로 받아들인 위험이며 §Rollback/재평가
  조건에서 관찰 대상으로 명시한다. 또한 `SpecificationResult` Contract
  확장은 이 Contract를 사용하는 모든 기존 테스트 fixture(예:
  `test_stage_contracts.py`, `test_stage_02.py`)가 실제 구현 시 갱신을
  요구한다는 후속 비용이 있다(이 ADR은 그 구현을 수행하지 않는다).

## 영향

- **Architecture**: 없음(Development HQ 내부 Scoped, Kernel Public
  Contract 무변경).
- **Contract**: `SpecificationResult` 5키로 확장(Scoped Public 변경).
  나머지 4개 Stage Contract 무변경.
- **기존 구현**: 실제 코드(`stage_02.py`, `contracts.py`)는 이 ADR로
  아직 변경되지 않는다 — Decision 기록과 실제 반영을 분리한다
  (Outcome-Oriented Governance 원칙, `ADR-0010`).
- **기존 문서**: Stage 02 `RESPONSIBILITY.md`/`CAPABILITIES.md`/
  `SPECIFICATION.md`가 이 Decision과 모순되는지 별도로 확인했다(본
  세션의 최종 보고 §7 참조) — 문서 수정은 이번 ADR의 범위가 아니다.

## 향후 재평가 조건 (Rollback 대신)

이 Decision은 "문제가 생기면 되돌린다" 성격보다 "관찰되면 확장한다"
성격에 가깝다 — RFC-0035 §6과 동일하게 다음을 재평가 Trigger로 기록한다.

1. Cycle Detection이 못 잡는 의미적 오판이 반복 관찰 → Dependency
   Judgment 검증 강화 여부 재론.
2. Stage 03/05가 Acceptance Criteria를 구조적으로 소비할 필요 관찰 →
   AC 구조화/Agent 여부 재론.
3. Task 목록 규모가 반복적으로 단일 호출 컨텍스트 한계에 부딪힘 → 분할
   호출 전략 재론.

이 세 조건 중 어느 것도 관찰되지 않는 한, 이 ADR의 구조(1 Agent +
Deterministic 체인, 3키 Contract 확장)를 그대로 실제 구현의 목표
설계로 삼는다.

## Next Step

Task & Dependency Agent, Deterministic Layer(Schema Validation/
Dependency Graph Validation/Cycle Detection/Topological Ordering/
Implementation Plan Assembly/Final Aggregation), `contracts.py`
확장, Stage 02 문서 갱신을 실제로 구현하는 것은 별도 후속 작업이다 —
이 ADR 이후 별도 Governance 승인 없이 자유 재량으로 진행한다
(ADC-0038 §Out of Scope).
