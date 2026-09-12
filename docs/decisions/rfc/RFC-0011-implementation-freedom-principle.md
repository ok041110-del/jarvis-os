# RFC-0011: "Implementation Freedom" 원칙 도입 여부

**Status**: Resolved — `docs/governance/adc/ADC-0009.md`로 종결됨(Scoped
Accept). 후속 `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md`는
**Accepted** — `docs/governance/README.md`에 반영 완료.
**Author**: Claude Code (사용자 제공 "Governance constrains outcomes and
invariants, not implementation preference" 원칙에 대한 Governance
절차 적용)
**대상**: Outcome-Oriented Governance Model(`docs/governance/README.md`,
`RFC-0010` → `docs/governance/adc/ADC-0008.md` → `ADR-0010` 경로로
이미 채택됨)의 확장 여부
**Evidence 범위**: `docs/governance/README.md`, `ADR-0010`, `RFC-0010`,
`ADC-0008`, `hqs/development/CONSTITUTION.md`, `hqs/development/
IMPLEMENTATION_RULES.md`, `docs/architecture/core/ADR-0016-omniroute-thin-caller-freeze-scoped-relaxation.md`,
`docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`.
이 RFC는 새 실험을 하지 않으며, LangGraph/Graphify 등 특정 기술의
채택 여부를 다루지 않는다.

> 본 RFC는 Governance를 즉시 교체하지 않는다. 이 RFC는 사용자가 제시한
> 5개 명제("Implementation Freedom")가 기존 Outcome-Oriented
> Governance Model에 이미 포함되어 있는지, 포함되지 않았다면 최소
> 추가가 필요한지를 묻는 Boundary Question이다. 판단은 후속 ADC로
> 넘긴다.

## 0. 이 RFC가 열린 이유

사용자가 다음 원칙("Implementation Freedom")을 Governance V2에
공식화할 것을 요청했다.

> Governance constrains outcomes and invariants, not implementation
> preference.

부연 5개 명제:

1. Evidence의 부재만으로 Implementation Technology 선택을 금지하지
   않는다.
2. 개발자/사용자/AI는 Goal과 Invariant를 만족하는 범위에서 구현
   기술을 자유롭게 선택할 수 있다.
3. Evidence는 구현 기술 선택의 사전 허가 조건이 아니라 구현 결과를
   평가하고 Architecture Evolution을 판단하기 위한 근거다.
4. Deferred / Not Accepted는 Forbidden을 의미하지 않는다.
5. Governance는 구현 선호 자체가 아니라 실제 Invariant, Contract,
   Boundary 및 위험을 통제한다.

`ADR-0010`이 이미 Outcome-Oriented Governance Model을
`docs/governance/README.md`에 반영했으므로, 이 RFC는 위 5개 명제가
그 문서에 이미 포함되어 있는지부터 대조한다(중복 문구 방지, 사용자
지시 4번).

## 1. Observation — 기존 문서와의 문구 대조

| 명제 | 기존 `docs/governance/README.md`("Outcome-Oriented Governance
Model" 절)의 대응 문구 | 포함 여부 |
|---|---|---|
| 1. Evidence 부재 ≠ 구현 기술 선택 금지 | 없음 — 가장 가까운 문구는 "Freeze는 실제 불변에만 사용한다"이나, 이는 Freeze 판단 기준일 뿐 "Evidence가 사전 금지 조건이 아니다"를 일반적으로 선언하지 않는다 | **미포함** |
| 2. 개발자/사용자/AI의 구현 기술 자유 선택권(Goal·Invariant 범위 내) | 없음 — 어떤 문구도 "구현 기술을 자유롭게 선택할 수 있다"는 긍정 형태의 권리를 서술하지 않는다 | **미포함** |
| 3. Evidence = 사전 허가 조건이 아니라 사후 평가·Architecture Evolution 근거 | 없음 — "Deferred/Not Accepted는... 재평가는 절차를 통해서만 열린다"는 재평가 절차만 다루고, Evidence의 역할(사전 허가 vs 사후 평가) 자체는 서술하지 않는다 | **미포함** |
| 4. Deferred/Not Accepted ≠ Forbidden | "Deferred/Not Accepted는 영구 금지와 다르다 — 새 Evidence가 있으면 재평가될 수 있으나..." | **이미 포함** (문구 단위로 사실상 동일) |
| 5. Governance는 구현 선호가 아니라 실제 Invariant/Contract/Boundary/위험을 통제 | "Freeze는 실제 불변(Invariant: Security/Data Integrity/Contract 호환성/되돌릴 수 없는 파괴적 동작/Compliance)에만 사용한다" | **부분 포함** — Freeze라는 한 가지 절차에만 적용된 진술이며, Governance 전체(RFC 개설, ADC 판단, Freeze 등 모든 절차)에 대한 일반 원칙으로 일반화되어 있지 않다 |

## 2. Boundary Questions

### Q-1. 명제 1·2·3, 그리고 명제 5의 일반화가 최소 추가로 필요한가

- **Question**: 위 대조표에서 "미포함"·"부분 포함"으로 확인된 부분을
  `docs/governance/README.md`에 추가할 것인가, 추가한다면 최소
  범위는 무엇인가?
- **Evidence**: §1의 대조표. 명제 4는 이미 문구 단위로 존재하므로
  추가 대상에서 제외해야 한다(사용자 지시 4번, 중복 방지).
- **Options**:
  - (a) 5개 명제 원문을 전부 새 절로 추가한다(명제 4 중복 포함).
  - (b) 명제 1·2·3과 명제 5의 일반화만 최소 문구로 추가하고, 명제
    4는 기존 문구를 그대로 인용·참조만 한다(중복 없음).
  - (c) 추가하지 않는다 — 기존 "Freeze는 실제 Invariant에만"
    문구로 이미 충분하다고 본다.
- **ADC에서 결정할 사항**: 위 옵션 중 채택안과, (b)를 선택할 경우
  정확한 추가 문구.

### Q-2. `hqs/development/CONSTITUTION.md`의 "Architecture Freeze" 목록이 이 원칙과 긴장 관계에 있는가

- **Question**: `CONSTITUTION.md`("Architecture Freeze" 절)는 Runtime/
  Pipeline Generalization/Task Dispatcher Generalization/Stage
  Runner/Event Bus/Scheduler/Multi-Agent Runtime/Engine Adapter/
  Model Routing을 "충분한 Evidence가 나올 때까지 동결한다"고 선언하고
  "반복된 실전 Evidence 없이는 개발하지 않는다"고 명시한다. 이는
  명제 1("Evidence 부재만으로 구현 기술 선택을 금지하지 않는다")과
  문면상 반대 방향을 가리키는가?
- **Evidence**:
  - `CONSTITUTION.md`의 이 목록은 Security/Data Integrity/Contract
    호환성/되돌릴 수 없는 파괴적 동작/Compliance 중 어디에도
    해당하지 않는 항목들(구현 일반화 패턴)로 구성된다 —
    `ADR-0010` §3이 정의한 "Freeze는 실제 Invariant에만" 기준과
    문면상 다른 근거(조기 일반화 방지)로 운용되고 있다.
  - 그러나 같은 목록의 `Engine Adapter`·`Model Routing` 두 항목은
    이미 `ADR-0016`(Scoped 예외) → `ADC-0027`(Conditional Accept)
    경로로 실제 Evidence(OmniRoute 안전 설정 실증, `EVIDENCE-0012`)에
    근거해 **Governance 절차를 통해 조건부 해제**된 선례가 있다 —
    즉 이 Freeze는 "사전 허가 없이는 시도조차 금지"가 아니라
    "Evidence가 쌓이면 Governance 절차로 재평가 가능한 동결"로 이미
    실제 운용되고 있다.
  - `docs/architecture/baseline/BASELINE.md` §10/§11(Kernel Component
    Architecture는 Out of Scope, Kernel은 책임이지 구현이 아니다)은
    이 Freeze 목록과 같은 항목(Scheduler/Registry/Runtime 등)을
    "설계 Evidence가 아직 없다"는 이유로 명시적 Out of Scope로
    유지하며, 이 근거 6개(`GOVERNANCE-REVIEW-0001` §5)는 "아직도
    유효하다"고 반복 확인되어 왔다(`GOVERNANCE-REVIEW-0006`).
- **Options**:
  - (a) 긴장 관계가 실재한다고 보고, `CONSTITUTION.md`를 재평가
    대상 후보로 명시적으로 기록한다(이 RFC가 직접 수정하지 않음).
  - (b) 긴장 관계가 없다고 본다 — `CONSTITUTION.md`의 Freeze는
    "특정 사용자가 특정 기술을 자유롭게 선택하는 것"을 막는 것이
    아니라 "Development HQ가 스스로 일반화된 Component를 조기
    설계하는 것"을 막는 자기 제약이며, 명제 1~5는 후자에 적용되지
    않는다.
  - (c) 판단을 보류한다 — 이 RFC의 범위를 벗어난다.
- **ADC에서 결정할 사항**: 위 옵션 중 채택안. 이 RFC는 어느 경우에도
  `CONSTITUTION.md` 본문을 수정하지 않는다(사용자 지시 6·9번).

## 3. Architecture Impact

- **없음(NONE)** — 이 RFC는 Development HQ/Kernel Architecture 구조를
  변경하지 않는다. `CONSTITUTION.md`의 Architecture Freeze 목록,
  LangGraph/Graphify의 Deferred/Not Adopted 상태는 이 RFC로 변경되지
  않는다(사용자 지시 9번).

## 4. Contract Impact

- 없음 — 이 RFC는 코드/Public Contract를 변경하지 않는다.

## 5. 이 RFC가 정의하지 않는 것 (경계)

- Q-1/Q-2 중 어느 옵션을 채택할지는 후속 ADC의 판단 대상이다.
- `CONSTITUTION.md`의 Architecture Freeze 목록을 실제로 개정할지는
  이 RFC·후속 ADC 어느 것도 결정하지 않는다 — Q-2에서 긴장 관계가
  실재한다고 판단되더라도, 그 자체가 "후속 재평가가 필요한 Architecture
  Impact 후보"로 보고될 뿐 구현하지 않는다(사용자 지시 11번).
- LangGraph, Graphify를 포함한 어떤 구체적 기술의 채택 여부도 이 RFC의
  범위 밖이다.

## Decision

**Scoped Accept — `docs/governance/adc/ADC-0009.md` 판정을 그대로
따른다.** Q-1은 명제 1·2·3 압축 + 명제 5의 Governance 전반 일반화를
최소 추가로 Scoped Accept(명제 4는 이미 존재해 재서술하지 않음), Q-2는
`CONSTITUTION.md`와의 문면상 불일치를 인정하되 개정하지 않고 "후속
재평가 후보"로만 기록하는 것으로 Scoped Accept됐다. 실제 Baseline
문서 반영(`docs/governance/README.md`)은 이 RFC·ADC 어느 것도
수행하지 않으며 후속 ADR 대상으로 남긴다.

후속 ADR은 `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md`로
작성되었다 — **Status: Accepted**. 사용자 승인 후 `docs/governance/
README.md`에 ADR-0011 §1의 두 원칙을 등재했다.
