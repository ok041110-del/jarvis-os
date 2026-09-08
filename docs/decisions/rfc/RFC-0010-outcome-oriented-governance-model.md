# RFC-0010: Outcome-Oriented Governance Model 도입 여부

**Status**: Proposed
**Author**: Claude Code (사용자 제공 "Jarvis OS Governance v2 Design
Principles" 문서에 대한 Governance 절차 적용)
**대상**: Jarvis OS Governance 자체(Tier 10.4 "Governance/Constitution
자체 변경" — 문서 원문의 표현으로는 P17, Governance Self-Review)
**Evidence 범위**: 사용자가 이번 세션에서 제공한 "Jarvis OS Governance
v2 Design Principles" 원문(P0~P17, Tier 0~4, Decision Model, Migration
Principle 포함), `docs/governance/README.md`, `docs/decisions/rfc/README.md`.
이 RFC는 새 실험을 하지 않는다.

> 본 RFC는 Governance를 즉시 교체하지 않는다. Governance 자체 변경은
> CLAUDE.md의 Frozen Architecture 규칙에 따라 RFC → ADC → ADR 절차를
> 거쳐야 하며, 이 문서는 그 절차의 첫 단계(Boundary Question 제기)다.

## 0. 이 RFC가 열린 이유

사용자가 "Jarvis OS Governance v2"라는 제목으로, Goal-over-Process·
Invariants-over-Rules·Tier 기반 강도 조절·Freeze는 실제 Invariant에만
적용·Deferred/Rejected는 영구 금지가 아님 등을 골자로 하는 별도의
Governance 설계 철학 문서를 제공했다. 이 문서는 저장소에 직접 반영하기
전에 두 가지 이유로 절차가 필요하다.

1. **Governance 자체의 변경**이다 — CLAUDE.md Frozen Architecture 규칙상
   RFC → ADC → ADR 없이 직접 수정할 수 없다.
2. **이름 충돌**이 있다 — `docs/governance/README.md`는 이미 "Governance
   v2"라는 이름으로 Observation 계층(OBS 문서 누적, Rule A/B, RFC-0004가
   그 절차로 열린 선례)을 Baseline으로 채택해 놓았다. 사용자 문서를 같은
   이름으로 그대로 반영하면 두 개의 서로 다른 "Governance v2"가 저장소에
   공존하게 된다.

## 1. Observation — 두 "Governance v2"의 관계

| 항목 | 기존 Baseline (`docs/governance/README.md`) | 사용자 제공 문서 |
|---|---|---|
| 이름 | Governance v2 (Observation 계층) | Governance v2 (Design Principles) |
| 범위 | RFC를 "언제 여는가"의 판단 근거 하나만 교체 (MVP 1회 → OBS 누적) | Governance 전체의 철학·Tier·Freeze·Deferred 정책 |
| 상태 | Baseline, RFC-0004로 이미 실사용됨 | Proposed (이 RFC 이전에는 저장소에 없던 문서) |
| RFC/ADC/ADR 관계 | 유지·확장 (P8 정의와 대체로 호환) | 유지하되 각 문서의 "역할"을 재정의 (P7~P9) |

두 문서는 상충하지 않는다 — 기존 Observation 계층은 "RFC를 언제 여는가"
라는 좁은 절차 규칙이고, 사용자 문서는 그보다 상위의 철학(왜 Governance가
존재하는가, Freeze를 언제 쓰는가, Tier를 어떻게 나누는가)이다. 다만 **같은
이름을 재사용하면 어느 쪽을 가리키는지 이후 문서에서 구분할 수 없다.**

## 2. Decision Boundary

### B-1. 같은 이름을 재사용할 것인가

**논의**: 기존 "Governance v2"는 이미 RFC-0004/ADC-0004, OBS-0001~0006에서
실제로 인용된 확정 명칭이다. 여기에 완전히 다른 철학 문서를 같은 이름으로
얹으면, 향후 "Governance v2"라는 참조가 Observation 계층을 가리키는지
Design Principles를 가리키는지 문서 자체만으로 판별 불가능해진다
(`docs/decisions/rfc/README.md`가 이미 지적한 "번호 재사용 vs 결정 내용
중복" 문제와 동일한 유형의 위험).

> **Decision B-1**: 사용자 제공 문서를 저장소에 반영할 경우, 기존
> Observation 계층과 구분되는 별도 명칭(예: "Governance v3" 또는
> "Outcome-Oriented Governance Model")을 사용한다. 기존 "Governance v2"
> (Observation 계층) 명칭과 그 Baseline은 그대로 유지하고 이 RFC가
> 재정의하지 않는다.

### B-2. RFC/ADC/ADR의 "역할" 재정의(P7~P9)를 그대로 채택할 것인가

사용자 문서 P7~P9는 RFC/ADC/ADR의 목적을 "미래를 통제하는 것이 아니라
현재 시점의 Decision과 그 근거를 기록하는 것"으로 규정한다. 이는
`docs/decisions/rfc/README.md`("RFC는 결정이 아니라 검토 대상"), 기존
ADR 문서들의 실제 서술 방식(Decision + Evidence + 재평가 조건)과 이미
사실상 일치한다.

> **Decision B-2**: P7~P9는 기존 관행의 명문화(Descriptive)에 가까우며
> Baseline과 충돌하지 않는다. 별도 ADR 없이 `docs/governance/README.md`
> "핵심 원칙" 절에 참조를 추가하는 정도로 흡수 가능하다고 판단한다 — 단,
> 최종 채택 여부는 후속 ADC가 확정한다.

### B-3. Freeze/Deferred/Tier 정책(P10, P15, P16)을 그대로 채택할 것인가

사용자 문서의 Tier 0~4 강도 모델과 "Freeze는 실제 Invariant에만", "Deferred/
Rejected ≠ 영구 금지" 원칙은 현재 저장소 실무와 부분적으로만 일치한다.
`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`처럼 이미 존재하는 Freeze 문서가
이 새 기준으로 재평가 대상이 되는지, RFC-0005/RFC-0007처럼 이미 "Not
Accepted"로 판정된 항목들이 이 문서의 "Rejected ≠ 영구 금지" 원칙 아래
재오픈 가능한 것으로 재해석되는지는 이 RFC의 범위에서 결정하지 않는다.

> **Decision B-3**: Tier 모델과 Freeze/Deferred 재정의는 기존 Freeze
> 문서·기존 RFC의 "Not Accepted" 판정에 소급 적용되지 않는다. 적용 여부는
> 개별 문서 단위로 별도 재평가가 필요하며, 이 RFC는 그 재평가를 강제하지
> 않는다.

## 3. Architecture Impact

- **없음(NONE)** — 이 RFC는 Development HQ/Kernel Architecture 어느
  쪽의 구조도 변경하지 않는다. Governance 절차와 명칭에 대한 논의로
  한정한다.

## 4. Contract Impact

- 없음 — 이 RFC는 코드/Public Contract를 변경하지 않는다.

## 5. 이 RFC가 정의하지 않는 것 (경계)

- 사용자 제공 문서의 전체 원문을 그대로 채택할지, 부분 채택할지는 후속
  ADC의 판단 대상이다.
- 기존 Freeze 문서·이미 Resolved된 RFC들의 소급 재평가 여부(B-3)는 이
  RFC에서 답하지 않는다.
- 명칭(B-1)을 "Governance v3"로 할지 다른 이름으로 할지 최종 확정은
  후속 ADC/ADR이 결정한다 — 이 RFC는 "기존 이름과 충돌해서는 안 된다"는
  제약만 건다.

## 6. Governance 변경 범위 (승인 시)

| 대상 | 변경 내용 |
|---|---|
| 신규 ADC 1건 | B-1(명칭 분리)/B-2(RFC·ADC·ADR 역할 참조 흡수)/B-3(소급 미적용) 판정 |
| 신규 ADR (조건부) | ADC가 B-2를 Accept할 경우, `docs/governance/README.md` "핵심 원칙" 절에 참조 추가를 Baseline 변경으로 기록 |
| `docs/governance/README.md` | ADR 확정 이후에만 수정 — 이 RFC 자체는 수정하지 않는다 |

## Decision

**보류(Open)** — 이 RFC는 Boundary Question만 제기한다. 사용자 제공
Governance 철학 문서를 저장소 Baseline에 어떤 형태로 반영할지는 후속
ADC가 B-1/B-2/B-3을 판정한 뒤 결정한다.
