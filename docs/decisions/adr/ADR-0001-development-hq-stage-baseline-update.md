# ADR-0001 — Development HQ Baseline에 Stage 기반 구조 반영

> ADC-0003(`docs/governance/adc/ADC-0003.md`) 판단 1이 이미 내린 Accept
> 결정을 다시 논의하지 않는다. 이 ADR은 그 결정을 Baseline 문서 변경으로
> 옮기기 위한 구현 결정만 기록한다.

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | ADR-0001 |
| Status | Accepted |
| Owner / Scope | Development HQ 내부 구조(Stage 도입) |
| Context | `docs/governance/adc/ADC-0003.md` 판단 1(Stage 기반 내부 조직화, Decision: Accept, Next Step: ADR Required) |
| 관련 ADC | `docs/governance/adc/ADC-0003.md` 판단 1 |

## 2. Context & Decision Drivers

| Item | Description |
|---|---|
| Context | ADC-0003 판단 1이 Stage 기반 내부 조직화를 Accept — 이를 실제 Baseline 문서 변경으로 옮긴다 |
| Decision Drivers | RFC-0003 §8이 제시한 6개 Stage 명칭·목적 |
| Out of Scope | Model Routing/Engine Adapter/Multi Model(ADC-0003 판단 4, Jarvis OS 수준 별도 절차), Jarvis OS Layer(Concept Model/Meta Architecture/System Boundary) 변경, 신규 Capability 추가(ADC-0003 판단 2, Defer) |

## 3. Decision

변경 대상은 `development-hq/STRUCTURE.md` **하나뿐**이다.

1. **STRUCTURE.md 갱신**: "내부 계층" 절에 "Stage는 Development HQ가 선택적으로 사용할 수 있는 또 다른 내부 조직 구조이며, Division/Team과 마찬가지로 Jarvis OS Meta Architecture의 필수 계층이 아니다"를 추가한다. Division/Team 표기는 삭제하지 않는다 — Stage는 대체가 아니라 동위의 선택지다. `MISSION.md`/`BOUNDARY.md`/`RESPONSIBILITY.md`/`development-hq/BASELINE.md`는 수정하지 않는다(이미 특정 구조에 못박지 않은 서술이라 충돌 없음). Capability 목록(예시)도 그대로 유지한다.
2. **Directory 구조**: 코드 디렉토리(`development-hq/mvp/`)는 변경하지 않는다. 문서 전용 `stages/01_repository_intelligence/` ~ `06_devops_release/` 6개 README를 신설한다. 각 README는 §4(Stage 정의)의 목적·Responsibility·Reference만 담고, Capability 배정이나 실행 코드 배치는 규정하지 않는다.
3. **Domain Model**: Stage를 Division/Team과 동일한 지위의 HQ 내부 개념으로 추가한다. 기존 `Workflow → Task → Capability → Agent` Concept Model은 그대로 유지한다.
4. **Stage 정의**(RFC-0003 §8 그대로 채택, 재논의 없음):

   | Stage | 목적 |
   |---|---|
   | Repository Intelligence | 프로젝트를 이해한다 |
   | Planning & Specification | Intent를 실행 가능한 명세로 변환한다 |
   | Architecture & Design | 구현 전에 구조를 설계한다 |
   | Implementation | 명세를 코드로 구현한다 |
   | Validation | 구현 결과를 검증한다 |
   | DevOps & Release | 배포와 운영을 자동화한다 |

5. **기존 MVP-0001~0003 재사용**: 기존 코드(`agents.py`/`engine.py`/`workflow.py`/`workflow_0002.py`/`tests/`)는 이동·수정하지 않는다. `stages/04_implementation/`·`stages/05_validation/` README는 이 코드를 "참고 구현 예시"로 링크만 건다. MVP-0003(계획 단계, 구현 없음)은 이동 대상이 없다.
6. **Migration Strategy**: (1) STRUCTURE.md §1 Stage 문단 추가 → (2) `stages/<n>/README.md` 6개 생성 → (3) Implementation/Validation README에 기존 `mvp/` 참조 링크 추가(코드 이동 없음) → (4) 각 Step 이후 기존 MVP-0001/0002 테스트 통과 확인 → (5) MVP-0004 이후 로드맵(ADC-0003 판단 3)은 이 Migration 완료 후 별도 작업.

## 4. Rationale & Alternatives

### Rationale

| Reason | Explanation | Evidence |
|---|---|---|
| Baseline 문서 1개만 변경 | Stage 도입이 STRUCTURE.md의 "내부 계층" 서술 범위에만 해당 — 다른 Baseline 문서는 이미 특정 구조에 못박지 않음 | STRUCTURE.md 현재 문구, ADC-0003 판단 1 |
| 코드 이동 없이 문서만 신설 | 기존 코드를 재조직 근거로 이동시킬 필요 없음(ADC-0003 판단 2가 Capability 확장을 Defer) | `mvp/` 기존 구조 |

### Rejected Alternatives

이 ADR 단계에서 별도로 기각한 대안은 없다 — 방향 자체는 ADC-0003이 이미 Accept했으며, 이 문서는 그 구현 방식만 확정한다.

## 5. Consequences & Impact

| Category | Impact |
|---|---|
| Positive Consequences | STRUCTURE.md와 신규 `stages/` 문서에 Stage 개념이 명시적으로 도입된다. 다른 Development HQ 문서(MISSION/BOUNDARY/RESPONSIBILITY/BASELINE)와 Jarvis OS Architecture Baseline은 무변경 |
| Negative Consequences / Trade-offs | 없음 — 순수 추가(additive) 변경 |
| Risks | 없음으로 평가 — 기존 코드/테스트 경로 무변경 |
| Operational Impact | §6에 정의된 실제 파일 변경(Baseline Update)은 별도 실행이 필요하며, 이 ADR 자체가 그 변경을 수행하지 않는다. 이후 MVP-0004~0006(ADC-0003 판단 3)은 이 Stage 구조를 전제로 진행될 수 있다. Model Routing/Engine Adapter/Multi Model/신규 Capability는 여전히 미해결로 남으며 각각 ADC-0003 판단 2·4가 지정한 별도 절차(Defer 재관찰, Jarvis OS 수준 RFC)를 따른다 |

## 6. Architecture Baseline & Implementation

| Item | Description |
|---|---|
| Architecture Baseline Impact | 없음 — Jarvis OS Architecture Baseline은 변경하지 않는다 |
| Public Contract Impact | 없음 |
| Implementation Scope | `development-hq/STRUCTURE.md` §1 갱신 + `stages/` 6개 README 신설(§3의 Migration Strategy) |
| Follow-up Work | MVP-0004~0006(ADC-0003 판단 3), Model Routing/Engine Adapter/Multi Model(ADC-0003 판단 4, Jarvis OS 수준 RFC) |

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` | Stage 명칭·목적의 출처(§8) |
| ADC | `docs/governance/adc/ADC-0003.md` | 판단 1 — 이 ADR이 구현하는 Accept 결정 |
| ADR | — | 없음 |
| Open Decision | — | 없음 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | ADC-0003 판단 1 구현 |
