# ADR-0010: Outcome-Oriented Governance Model — Baseline 반영 결정

| 필드 | 내용 |
|---|---|
| ID | ADR-0010 |
| 제목 | RFC-0010(Boundary Question) → ADC-0008(Q-1/Q-2/Q-3 Final Judgment)의 판단을 실제 Baseline 반영 결정으로 확정한다 |
| 상태 | **Accepted.** 사용자 승인 후 §5의 신설 절 텍스트를 `docs/governance/README.md`에 그대로 등재했다(§4 실제 반영 범위 참고). |
| Context | `docs/decisions/rfc/RFC-0010-outcome-oriented-governance-model.md`(Q-1/Q-2/Q-3 Boundary Question) + `docs/governance/adc/ADC-0008.md`(Q-1 Accept, Q-2/Q-3 Scoped Accept·소급 미적용) |
| 관련 RFC | `docs/decisions/rfc/RFC-0010-outcome-oriented-governance-model.md` |
| 관련 ADC | `docs/governance/adc/ADC-0008.md` |
| 선례 | `ADR-0009`(Scoped Accept를 실제 Baseline 반영 결정으로 옮기는 형식), `ADR-0018`(Deferred/Not Adopted를 종결하며 선행 Decision을 다시 논의하지 않는 형식) |

이 ADR은 ADC-0008이 이미 내린 Q-1/Q-2/Q-3 Final Judgment를 다시
논의하지 않는다. 이 ADR이 하는 일은 그 판단을 **실제 문서에 무엇을,
어디에, 어떤 문구로 반영할 것인지**로 구체화하고, 사용자 승인을 받은
뒤 그 반영을 실행하는 것이다 — 승인 전 어떤 반영도 실행하지 않는다는
CLAUDE.md Frozen Architecture 규칙("Architecture/Baseline은 직접
수정하지 않는다")을 그대로 따랐고, 승인 이후 §4의 반영을 완료했다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| 기존 "Governance v2"(Observation 계층)의 명칭·내용·Rule A/B | ADC-0008 판단 1 — 이 ADR이 재정의·폐기하지 않는다 |
| `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`, `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 등 기존 Freeze 선언 | ADC-0008 판단 3 — 소급 재평가 대상 아님, 이 ADR로 재론하지 않음 |
| `docs/architecture/core/` 트리의 Not Accepted RFC(RFC-0008~0012)·`docs/decisions/rfc/`의 RFC-0005(Open) | ADC-0008 판단 3 — 소급 재평가 대상 아님 |
| `ADR-0018`이 이미 종결한 LangGraph Deferred/Not Adopted 판정 | ADC-0008 판단 3 — 재론하지 않음 |
| Kernel Public Contract(Jarvis OS Architecture Baseline §14), Stage Data Contract(ADR-0009) | Governance **절차 서술**에 대한 ADR이며 어떤 Contract도 변경하지 않음 |
| 코드/Architecture 구조 | 변경 없음(§6 확인) |

---

## Decision

### 1. 공식 명칭 확정 (ADC-0008 Q-1 Final Judgment 반영)

사용자 제공 Governance 철학 문서는 저장소에서 **"Outcome-Oriented
Governance Model"**을 공식 명칭으로 한다. "Governance v2"라는 명칭은
계속 기존 Observation 계층(`docs/governance/README.md`)의 전용
명칭으로 남으며, 이 ADR은 그 문서의 "Governance v2" 절을 한 글자도
바꾸지 않는다.

### 2. RFC/ADC/ADR 역할 원칙 (ADC-0008 Q-2 Final Judgment 반영)

다음 원칙을 Outcome-Oriented Governance Model의 일부로 채택하되,
**참조 수준으로만** 반영한다 — 기존 `docs/decisions/rfc/README.md`,
`docs/decisions/adc/README.md`의 정의를 교체하지 않는다.

- RFC/ADC/ADR은 미래 구현을 사전에 통제하는 문서가 아니라, 결정
  시점의 Decision과 그 근거(Evidence)를 기록하는 문서다.
- **RFC는 모든 변경의 필수 관문(mandatory gateway)이 아니다.** 다만
  RFC가 정확히 어떤 범위에서 필요한지는 이 ADR이 새로 정의하지
  않는다 — 그 범위는 저장소가 이미 정의한 대로 따른다(`docs/
  decisions/rfc/README.md`의 RFC 정의, `hqs/development/
  IMPLEMENTATION_RULES.md`가 개별적으로 명시한 RFC 대상 조항들,
  `ADR-0004` 등 관련 ADR). 이 원칙은 **기존에 이미 RFC 대상으로
  확정된 범위를 넓히거나 좁히지 않으며, 이 ADR의 다른 어떤 조항도
  그 범위를 재정의하는 것으로 해석하지 않는다.**

### 3. Tier / Freeze / Deferred 원칙 (ADC-0008 Q-3 Final Judgment 반영, 소급 미적용)

다음 원칙을 Outcome-Oriented Governance Model의 일부로 채택하며,
**이후 새로 작성되는 RFC/ADC/ADR/Freeze 판단에만** 적용한다.

- Governance 절차의 강도는 변경의 위험(Risk)과 영향 범위(Impact)에
  따라 다르게 적용한다(Tier 0 Local ~ Tier 4 Governance 자체 변경).
- **Freeze는 실제 불변(Invariant)에만 사용한다** — Security Boundary,
  Data Integrity, 기존 Contract 호환성, 되돌릴 수 없는 파괴적 동작,
  Compliance 요구사항 등. 통상적인 설계 선택에는 Freeze를 사용하지
  않는다.
- **Deferred/Not Accepted는 영구 금지와 동일하지 않다.** 새 Evidence가
  나타나면 재평가 대상이 될 수 있다. 단, 그 재평가는 이 원칙의 채택
  자체로 자동 시작되지 않으며, 해당 문서가 속한 절차(RT Trigger 충족,
  동일 Tag OBS 누적, 또는 개별 RFC 재개설)를 통해서만 열린다.

> **소급 적용 범위 (명시)**: 위 원칙은 이 ADR 승인 이후 새로 작성되는
> Governance 판단에 적용한다. `DEVELOPMENT-HQ-V1.0/V2.0-FREEZE-0001.md`
> 등 기존 Freeze 문서, 이미 Resolved 또는 Not Accepted로 판정된
> 기존 RFC/ADC/ADR(RFC-0005, RFC-0008~0012, `ADR-0018`의 LangGraph
> Deferred/Not Adopted 판정 등)은 이 ADR로 재평가되지 않는다. 재평가가
> 필요하다고 판단되면 각 문서 단위로 별도 RFC/RT 절차를 연다 — 이
> 목록은 "후속 재평가 대상"이라는 표시일 뿐, 재평가를 지금 지시하지
> 않는다.

### 4. 실제 반영 범위 (승인 후 적용 완료)

| 대상 파일 | 반영 내용 | 실행 상태 |
|---|---|---|
| `docs/governance/README.md` | "Governance v2 흐름" 절 다음에 "Outcome-Oriented Governance Model" 신설 절 추가 — §5 초안 텍스트를 그대로 등재 | 적용 완료 |
| `docs/decisions/rfc/README.md` | RFC-0010 등록 행의 "후속 ADR" 칸과 상태를 `ADR-0010`(Accepted)로 갱신 | 적용 완료 |
| `docs/decisions/adr/README.md` | ADR-0010 행 상태를 Accepted로 갱신 | 적용 완료 |
| 그 외 | 없음 — 코드·Architecture·Contract 문서는 대상이 아니다 | — |

### 5. 신설 절 초안 (승인 시 `docs/governance/README.md`에 그대로 등재할 텍스트)

> ## Outcome-Oriented Governance Model (Governance v2와 별개 명칭)
>
> `RFC-0010` → `docs/governance/adc/ADC-0008.md` → `ADR-0010` 경로로
> 채택된 원칙이며, 위의 "Governance v2"(Observation 계층)와는 다른
> 별개의 서술이다.
>
> - RFC/ADC/ADR은 미래 구현을 통제하지 않고, 결정 시점의 Decision과
>   근거를 기록한다.
> - RFC는 모든 변경의 필수 관문이 아니다 — 다만 RFC가 정확히 어떤
>   범위에서 필요한지는 이 문서가 새로 정의하지 않으며, 저장소가
>   이미 정의한 범위(`docs/decisions/rfc/README.md`, `hqs/development/
>   IMPLEMENTATION_RULES.md`, 관련 ADR)를 그대로 따른다.
> - Governance 절차 강도는 변경의 위험/영향 범위에 따라 다르게
>   적용한다.
> - Freeze는 실제 불변(Invariant: Security/Data Integrity/Contract
>   호환성/되돌릴 수 없는 파괴적 동작/Compliance)에만 사용한다.
> - Deferred/Not Accepted는 영구 금지와 다르다 — 새 Evidence가 있으면
>   재평가될 수 있으나, 재평가는 해당 절차(RT Trigger, OBS 누적, 개별
>   RFC 재개설)를 통해서만 열린다.
>
> **적용 범위**: 이 원칙은 이후 새로 작성되는 RFC/ADC/ADR/Freeze
> 판단에 적용한다. 기존 Freeze 문서와 이미 Resolved/Not Accepted된
> RFC/ADC/ADR에는 소급 적용하지 않는다(`ADR-0010` §3 참고).

이 초안은 사용자 승인 이후 `docs/governance/README.md`의 "Governance
v2 흐름" 절 다음에 그대로 등재되었다. 등재된 문구는 위 초안과 문구
단위로 동일하다.

## 6. Architecture/Contract 불변 확인

- Development HQ/Kernel Architecture 구조를 변경하지 않는다.
- 어떤 Public Contract도 변경하지 않는다(Kernel Public Contract §14,
  Stage Data Contract §ADR-0009 전부 무변경).
- 코드 파일은 이 ADR로 일절 수정하지 않는다.

## 7. 기존 RFC/ADC/ADR/Freeze와의 충돌 확인

- **`docs/governance/README.md`(Governance v2, Observation 계층)**:
  충돌 없음 — 새 절을 추가할 뿐 기존 절을 재정의하지 않는다(§4).
- **`docs/decisions/rfc/README.md`, `hqs/development/
  IMPLEMENTATION_RULES.md`, `ADR-0004` 등 관련 ADR**: 충돌 없음 —
  §2는 이 문서들이 이미 정의한 RFC 적용 범위를 그대로 따른다고만
  선언할 뿐, 그 범위를 스스로 재정의하지 않는다.
- **`DEVELOPMENT-HQ-V1.0/V2.0-FREEZE-0001.md`**: 충돌 없음 — §3의
  소급 미적용 명시로 기존 Freeze 선언의 근거·효력을 그대로 유지한다.
- **`ADR-0018`(LangGraph Deferred/Not Adopted)**: 충돌 없음 — 이
  ADR이 채택하는 "Deferred ≠ 영구 금지" 원칙은 `ADR-0018`의 기존
  판정을 재론하지 않는다는 전제 위에서만 적용한다(§3 인용).
- **RFC-0010 / ADC-0008**: 이 ADR은 두 문서가 이미 확정한 Final
  Judgment를 그대로 옮긴 것이며, 새로운 판단을 추가하지 않는다.

---

## Consequences

- `docs/governance/README.md`에 "Outcome-Oriented Governance Model"
  절이 신설되어, "RFC가 언제 필수인가", "Freeze를 언제 쓰는가",
  "Deferred가 영구 금지가 아니라는 것"이 명시적으로 문서화됐다.
  이후 새로운 Governance 판단에서 이 세 가지를 판단 기준으로 인용할
  수 있다.
- `docs/governance/README.md`의 기존 "Governance v2"(Observation
  계층) 서술은 한 글자도 바뀌지 않았다 — 신설 절은 그 다음에
  추가됐을 뿐이다.
- 기존 Freeze 문서·기존 Resolved/Not Accepted RFC/ADC/ADR은 이
  ADR로 인해 어떤 상태 변화도 겪지 않았다 — 재평가가 필요하면 이후
  각 문서 단위로 별도 RFC/RT 절차가 열려야 한다(이 ADR이 그 절차를
  대신하거나 생략하지 않는다).
- 절차 부채 해소됨: §5 초안 텍스트를 `docs/governance/README.md`에
  등재하는 반영과 Registry(§4) 갱신을 이 ADR의 Accepted 전환과 같은
  작업 단위로 완료했다.
