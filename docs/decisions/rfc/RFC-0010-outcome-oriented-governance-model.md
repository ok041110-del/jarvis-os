# RFC-0010: Outcome-Oriented Governance Model 도입 여부

**Status**: Resolved — `docs/governance/adc/ADC-0008.md`로 종결됨(Scoped
Accept). 후속 `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md`는
Proposed(사용자 승인 대기). RFC 자체는 결정 문서가 아니며, 이 라벨은
절차 진행 상태만 반영한다.
**Author**: Claude Code (사용자 제공 "Jarvis OS Governance v2 Design
Principles" 문서에 대한 Governance 절차 적용)
**대상**: Jarvis OS Governance 자체(문서 원문의 표현으로는 P17,
Governance Self-Review)
**Evidence 범위**: 사용자가 이번 세션에서 제공한 "Jarvis OS Governance
v2 Design Principles" 원문(P0~P17, Tier 0~4, Decision Model, Migration
Principle 포함), `docs/governance/README.md`, `docs/decisions/rfc/README.md`.
이 RFC는 새 실험을 하지 않는다.

> 본 RFC는 Governance를 즉시 교체하지 않는다. Governance 자체 변경은
> CLAUDE.md의 Frozen Architecture 규칙에 따라 RFC → ADC → ADR 절차를
> 거쳐야 하며, 이 문서는 그 절차의 첫 단계(Boundary Question 제기)다.
> 이 RFC는 어떤 항목도 채택/기각을 판단하지 않는다 — 판단은 후속 ADC의
> 몫이다.

## 0. 이 RFC가 열린 이유

사용자가 "Jarvis OS Governance v2"라는 제목으로, Goal-over-Process·
Invariants-over-Rules·Tier 기반 강도 조절·Freeze는 실제 Invariant에만
적용·Deferred/Rejected는 영구 금지가 아님 등을 골자로 하는 별도의
Governance 설계 철학 문서를 제공했다. 이 문서는 저장소에 직접 반영하기
전에 두 가지 이유로 절차가 필요하다.

1. **Governance 자체의 변경**이다 — CLAUDE.md Frozen Architecture 규칙상
   RFC → ADC → ADR 없이 직접 수정할 수 없다.
2. **이름 충돌**이 있다 — `docs/governance/README.md`는 이미 "Governance
   v2"라는 이름을 Observation 계층(OBS 문서 누적, Rule A/B, RFC-0004가
   그 절차로 열린 선례)에 대해 사용하고 있다. 사용자 문서를 같은 이름으로
   그대로 반영하면 두 개의 서로 다른 "Governance v2"가 저장소에 공존하게
   된다.

## 1. Observation — 두 "Governance v2" 명칭 충돌

| 항목 | 기존 문서 (`docs/governance/README.md`) | 사용자 제공 문서 |
|---|---|---|
| 이름 | Governance v2 (Observation 계층) | Governance v2 (Design Principles) |
| 범위 | RFC를 "언제 여는가"의 판단 근거 (MVP 1회 → OBS 누적) | Governance 절차 전반에 대한 설계 철학(Goal/Invariant/Tier/Freeze/Deferred 등) |
| 상태 | 기존 문서에 이미 기록되어 RFC-0004에서 실사용됨 | Proposed (이 RFC 이전에는 저장소에 없던 문서) |
| 다루는 대상 | RFC 개설 시점 판단 규칙 하나 | RFC/ADC/ADR 각 문서의 역할 정의, Freeze/Deferred 정책, Tier 구분 등 여러 항목 |

이 표는 두 문서 중 어느 쪽이 "상위" 또는 "우선"인지를 규정하지 않는다.
확인된 사실은 **두 문서가 서로 다른 내용을 같은 이름("Governance
v2")으로 부르고 있다**는 점뿐이며, 그 결과 향후 "Governance v2"라는
참조가 어느 쪽을 가리키는지 문서만으로 판별할 수 없게 된다는 것이 이
RFC가 제기하는 문제다. 두 문서가 실제로 상충하는지, 어느 쪽 표현을
유지할지는 아래 §2의 질문들로 넘긴다.

## 2. Boundary Questions

이 절의 각 항목은 결론이 아니라 후속 ADC가 판정해야 할 질문이다. 이
RFC는 Question/Evidence/Options만 제시한다.

### Q-1. 같은 이름("Governance v2")을 그대로 재사용할 것인가

- **Question**: 사용자 제공 문서를 저장소에 반영할 때, 기존
  Observation 계층과 같은 이름("Governance v2")을 유지할 것인가, 별도
  명칭을 사용할 것인가?
- **Evidence**: 기존 "Governance v2"(Observation 계층)는 이미
  RFC-0004/ADC-0004, OBS-0001~0006에서 실제로 인용된 명칭이다.
  `docs/decisions/rfc/README.md`는 서로 다른 트리에서 RFC 번호가
  재사용되는 사례를 이미 "번호만으로는 구분되지 않는다"는 위험으로
  기록한 바 있다 — 이번 이름 충돌도 같은 유형의 위험이다.
- **Options**:
  - (a) 같은 이름 유지 — 참조 시 항상 범위를 병기해야 하는 부담이
    생긴다.
  - (b) 별도 명칭 사용(예: "Governance v3", "Outcome-Oriented
    Governance Model") — 기존 "Governance v2"(Observation 계층)
    명칭과 그 내용은 그대로 둔다.
  - (c) 두 문서를 하나로 통합하고 번호를 다시 매긴다 — 통합 범위와
    방식은 별도 검토가 필요하다.
- **ADC에서 결정할 사항**: 위 옵션 중 채택안, 그리고 채택 시 실제
  명칭.

### Q-2. RFC/ADC/ADR의 "역할" 재정의(P7~P9)를 채택할 것인가

- **Question**: 사용자 문서 P7~P9(RFC/ADC/ADR의 목적을 "미래를
  통제하는 것이 아니라 현재 시점의 Decision과 근거를 기록하는 것"으로
  규정)를 저장소 Governance 문서에 명문화할 것인가?
- **Evidence**: `docs/decisions/rfc/README.md`는 이미 "RFC는 결정이
  아니라 검토 대상"이라고 서술한다. 기존 ADR 문서들의 실제 작성
  방식(Decision + Evidence + 재평가 조건 병기, 예: RFC-0009)도 P7~P9의
  서술과 유사하다.
- **Considerations**: 기존 실무와 표현이 겹치는 부분이 많아 보이지만,
  "겹쳐 보인다"는 것이 "동일하다"는 결론을 자동으로 보장하지는 않는다
  — 문구 단위 대조는 이 RFC의 범위 밖이다.
- **ADC에서 결정할 사항**: P7~P9를 그대로/부분적으로/채택하지 않음 중
  선택, 채택 시 반영 위치(`docs/governance/README.md` 등)와 방식(참조
  추가 대 본문 교체).

### Q-3. Freeze/Deferred/Tier 정책(P10, P15, P16)을 채택할 것인가, 채택 시 기존 문서에 소급 적용할 것인가

- **Question**: 사용자 문서의 Tier 0~4 강도 모델과 "Freeze는 실제
  Invariant에만", "Deferred/Rejected ≠ 영구 금지" 원칙을 저장소
  Governance에 반영할 것인가? 반영한다면 이미 존재하는 Freeze
  문서(`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 등)와 이미 "Not
  Accepted"로 판정된 RFC(RFC-0005, RFC-0007 등)에 소급 적용할 것인가?
- **Evidence**: 기존 Freeze 문서와 "Not Accepted" 판정들은 현재
  Baseline 상태로 실사용 중이며, 이 RFC는 그 내용을 재검토하지 않았다.
- **Options**:
  - (a) 신규 원칙으로만 도입 — 기존 Freeze/Not Accepted 판정은
    무변경.
  - (b) 신규 원칙 도입 + 기존 문서 개별 재평가 착수 — 재평가는 각
    문서 단위 별도 RFC/ADC 대상.
  - (c) 도입하지 않음.
- **ADC에서 결정할 사항**: 위 옵션 중 채택안. (b)를 선택할 경우 재평가
  대상 문서 목록과 우선순위는 이 RFC가 아니라 후속 절차에서 정한다.

## 3. Architecture Impact

- **없음(NONE)** — 이 RFC는 Development HQ/Kernel Architecture 어느
  쪽의 구조도 변경하지 않는다. Governance 절차와 명칭에 대한 질문
  제기로 한정한다.

## 4. Contract Impact

- 없음 — 이 RFC는 코드/Public Contract를 변경하지 않는다.

## 5. 이 RFC가 정의하지 않는 것 (경계)

- Q-1/Q-2/Q-3 중 어느 옵션을 채택할지는 이 RFC가 결정하지 않는다 —
  후속 ADC의 판단 대상이다.
- 기존 Freeze 문서·이미 Resolved된 RFC들의 소급 재평가 여부(Q-3)는 이
  RFC에서 답하지 않는다.
- 사용자 제공 문서의 전체 원문을 그대로 채택할지, 부분 채택할지도 이
  RFC의 범위 밖이다.

## 6. Governance 변경 범위 (승인 시)

| 대상 | 변경 내용 |
|---|---|
| 신규 ADC 1건 | Q-1(명칭)/Q-2(RFC·ADC·ADR 역할 서술 반영 여부)/Q-3(Freeze·Deferred·Tier 도입 및 소급 적용 여부) 판정 |
| 신규 ADR (조건부) | ADC가 Q-2 또는 Q-3의 반영을 Accept할 경우, 해당 반영을 `docs/governance/README.md` 등 Baseline 변경으로 기록 |
| `docs/governance/README.md` | ADR 확정 이후에만 수정 — 이 RFC 자체는 수정하지 않는다 |

## Decision

**Scoped Accept — `docs/governance/adc/ADC-0008.md` 판정을 그대로
따른다.** Q-1은 별도 명칭("Outcome-Oriented Governance Model") 채택으로
Accept, Q-2(RFC/ADC/ADR 역할 참조)와 Q-3(Tier/Freeze/Deferred 원칙의
향후 적용, 소급 미적용)은 Scoped Accept로 판정되었다. 기존 Freeze
문서와 기존 Not Accepted/Resolved RFC의 소급 재평가는 이 RFC·ADC
어느 쪽도 수행하지 않으며, ADC-0008 "판단 3"이 나열한 문서들은 각자의
절차(RT Trigger, OBS 누적, 개별 RFC 재개설)를 통해서만 재평가 대상이
된다. 실제 Baseline 문서 반영(`docs/governance/README.md` 등)은 이
RFC·ADC 어느 것도 수행하지 않으며 후속 ADR 대상으로 남긴다.

후속 ADR은 `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md`로
작성되었다 — **Status: Proposed(사용자 승인 대기)**. ADR-0010이
승인되기 전까지 `docs/governance/README.md`는 수정되지 않는다.
