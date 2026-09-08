# ADR-0011: "Implementation Freedom" 원칙 — Baseline 반영 결정 (승인 대기)

| 필드 | 내용 |
|---|---|
| ID | ADR-0011 |
| 제목 | RFC-0011(Boundary Question) → ADC-0009(Q-1/Q-2 Final Judgment)의 판단을 실제 Baseline 반영 결정으로 확정한다 — 반영 실행은 사용자 승인 이후로 미룬다 |
| 상태 | **Proposed — 사용자 승인 대기.** 이 ADR이 승인되기 전까지 `docs/governance/README.md`를 포함한 어떤 Governance 문서도 이 ADR로 수정하지 않는다. |
| Context | `docs/decisions/rfc/RFC-0011-implementation-freedom-principle.md`(Q-1/Q-2 Boundary Question) + `docs/governance/adc/ADC-0009.md`(Q-1 Scoped Accept, Q-2 Scoped Accept·개정 없음) |
| 관련 RFC | `docs/decisions/rfc/RFC-0011-implementation-freedom-principle.md` |
| 관련 ADC | `docs/governance/adc/ADC-0009.md` |
| 선례 | `ADR-0010`(Outcome-Oriented Governance Model 최초 반영 결정과 동일한 승인 대기 → 승인 후 반영 형식) |

이 ADR은 ADC-0009가 이미 내린 Q-1/Q-2 Final Judgment를 다시 논의하지
않는다. 이 ADR이 하는 일은 그 판단을 실제 문서에 무엇을, 어디에, 어떤
문구로 반영할 것인지로 구체화하는 것뿐이다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| 명제 4("Deferred/Not Accepted ≠ Forbidden") 재서술 | ADC-0009 판단 1 — 이미 존재, 중복 서술하지 않는다 |
| `hqs/development/CONSTITUTION.md`의 Architecture Freeze 목록 개정 | ADC-0009 판단 2 — 개정 없음, 후속 재평가 후보로만 기록 |
| LangGraph, Graphify 등 구체적 기술의 채택 여부 | 이 작업 범위 밖(사용자 지시 9·10·12번) |
| 기존 Freeze 문서·기존 Resolved/Not Accepted RFC/ADC/ADR의 소급 재평가 | `ADR-0010` §3 소급 미적용 원칙을 그대로 유지 |
| 코드/Architecture 구조 | 변경 없음 |

---

## Decision

### 1. 추가할 원칙 (ADC-0009 Q-1 Final Judgment 반영)

`docs/governance/README.md`의 "Outcome-Oriented Governance Model" 절
말미(현재 "**적용 범위**" 문단 다음)에 아래 두 항목을 추가한다.

> - **Implementation Freedom** — Evidence의 부재 자체는 구현 기술
>   선택을 금지하는 사전 허가 조건이 아니다. Goal과 Invariant를
>   만족하는 범위에서 개발자·사용자·AI는 구현 기술을 자유롭게 선택할
>   수 있으며, Evidence는 그 선택을 사전에 승인하는 관문이 아니라
>   구현 결과를 평가하고 Architecture Evolution 여부를 판단하는
>   근거로 쓰인다.
> - **Freeze/Governance는 선호가 아니라 Invariant를 통제한다** —
>   위 "Freeze는 실제 Invariant에만 사용한다" 원칙을 Freeze 판단
>   하나에 한정하지 않고, RFC 개설·ADC 판단을 포함한 Governance
>   전반에 일반화한다: Governance는 구현 방식에 대한 선호 자체를
>   통제하지 않으며, 실제 Invariant·Contract·Boundary·위험만 통제
>   대상으로 삼는다.
>
> **적용 범위**: 위 두 원칙도 이후 새로 작성되는 판단에만 적용하며,
> 기존 Freeze 문서(`CONSTITUTION.md`의 Architecture Freeze 목록
> 포함)와 이미 Resolved/Not Accepted/Deferred로 판정된 기존 RFC/
> ADC/ADR에는 소급 적용하지 않는다 — 그 상태들은 각자의 재검토
> 절차(RT Trigger, OBS 누적, 개별 RFC 재개설)를 통해서만 재평가
> 대상이 된다.

명제 4는 추가하지 않는다 — 기존 "Deferred/Not Accepted는 영구 금지와
다르다..." 문구를 그대로 둔다.

### 2. `CONSTITUTION.md`에 대한 조치 (ADC-0009 Q-2 Final Judgment 반영)

`hqs/development/CONSTITUTION.md`는 이 ADR로 **수정하지 않는다.**
ADC-0009가 식별한 문면상 불일치("반복된 실전 Evidence 없이는 개발하지
않는다"는 절대형 표현 vs 실제로는 `ADR-0016`/`ADC-0027` 선례로 이미
Evidence 기반 조건부 해제가 가능함이 실증됨)는 **Architecture 변경
후보로만 보고**하고 구현하지 않는다(사용자 지시 11번).

> **보고용 Architecture 변경 후보(구현하지 않음)**: 향후 Development
> HQ 수준 RFC가 이 후보를 다룰 경우, `CONSTITUTION.md`의 "반복된
> 실전 Evidence 없이는 개발하지 않는다"는 문구를 "Evidence 없이는
> Formal Architecture로 승격하지 않는다"처럼 **승격 절차**에 한정된
> 표현으로 정정할지 검토할 수 있다 — 단, 이는 이 ADR의 결정이
> 아니며 별도 RFC → ADC → ADR을 거쳐야 한다.

### 3. 실제 반영 범위 (승인 후 적용 — 이 ADR 자체는 실행하지 않음)

| 대상 파일 | 반영 내용 | 실행 시점 |
|---|---|---|
| `docs/governance/README.md` | "Outcome-Oriented Governance Model" 절 말미에 §1의 두 원칙 추가 | 이 ADR 승인 후, 별도 커밋 |
| `docs/decisions/rfc/README.md` | RFC-0011 등록 행 추가, 후속 ADC/ADR 연결 | 이 ADR 승인 후(상태 연결은 이번 커밋에서 선반영 가능) |
| `docs/decisions/adr/README.md` | ADR-0011 행 추가(Proposed) | 이 ADR 승인 후 Accepted로 갱신 |
| `hqs/development/CONSTITUTION.md` | 없음 | 이 ADR의 범위 밖 — §2의 보고용 후보만 기록 |
| 그 외 | 없음 — 코드·Architecture·Contract 문서는 대상이 아니다 | — |

## 4. Architecture/Contract 불변 확인

- Development HQ/Kernel Architecture 구조를 변경하지 않는다.
- `hqs/development/CONSTITUTION.md`의 Architecture Freeze 목록,
  LangGraph/Graphify의 Deferred/Not Adopted 상태를 변경하지 않는다.
- 어떤 Public Contract도 변경하지 않는다.
- 코드 파일은 이 ADR로 일절 수정하지 않는다.

## 5. 기존 RFC/ADC/ADR/Freeze와의 충돌 확인

- **`docs/governance/README.md`("Governance v2"·"Outcome-Oriented
  Governance Model" 절)**: 충돌 없음 — 새 항목을 추가할 뿐 기존
  문구(명제 4에 대응하는 부분 포함)를 재정의하지 않는다.
- **`ADR-0010`**: 충돌 없음 — §1의 두 원칙은 `ADR-0010` §3("Freeze는
  실제 Invariant에만")을 일반화한 것이며, 그 문구를 대체하지 않고
  나란히 추가된다. 소급 미적용 문구도 `ADR-0010` §3과 동일 형식을
  재사용한다.
- **`CONSTITUTION.md`, `ADR-0016`, `ADC-0027`**: 충돌 없음 — 이 ADR은
  그 문서들을 수정하지 않으며, 문면상 불일치는 개정하지 않고 보고만
  한다.
- **RFC-0011 / ADC-0009**: 이 ADR은 두 문서가 이미 확정한 Final
  Judgment를 그대로 옮긴 것이며, 새로운 판단을 추가하지 않는다.

---

## Consequences

- **승인 시**: `docs/governance/README.md`에 "Implementation Freedom"과
  "Freeze/Governance는 선호가 아니라 Invariant를 통제한다"는 두
  원칙이 명시적으로 문서화되어, 향후 특정 구현 기술(LangGraph 포함
  임의의 기술)에 대한 판단에서 "Evidence가 아직 부족하다"는 사실만으로
  자동으로 그 기술의 시도 자체를 금지하지 않는다는 점이 재확인
  가능해진다.
- **승인 전(현재 상태)**: 이 ADR은 결정 내용을 기록만 하고, 어떤
  Governance 문서도 아직 변경되지 않는다.
- `CONSTITUTION.md`의 Architecture Freeze 목록, LangGraph/Graphify의
  기존 Deferred/Not Adopted 판정은 이 ADR로 인해 어떤 상태 변화도
  겪지 않는다.
- 남는 절차 부채: `CONSTITUTION.md` 문면 정정 후보(§2)는 별도
  Development HQ 수준 RFC가 열릴 때만 다뤄진다 — 이 ADR이 그 절차를
  대신하지 않는다.
