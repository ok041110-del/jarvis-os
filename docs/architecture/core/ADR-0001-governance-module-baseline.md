# ADR-0001: Governance Kernel Module의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0001` (docs/04_adr/ADR-0001과 다른 문서 — 네임스페이스로 구분) |
| 제목 | Kernel `ADC-0001-core-baseline.md` Module 1(Governance)의 Accept 결정을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0001-core-baseline.md` Module 1(Governance) — **Decision: Accept**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` §4.1(Governance Module 정의) |
| 관련 ADC | `docs/architecture/core/ADC-0001-core-baseline.md` Module 1 |
| 관련 Documentation Issue | `docs/architecture/core/DOC-TRIAGE-0001.md` D-8("Kernel ADC-0001의 미작성 ADR 2건") |

이 ADR은 `ADC-0001-core-baseline.md`가 이미 내린 Governance Module
Accept 결정을 다시 논의하지 않는다. 새로운 철학이나 Architecture를
제안하지 않는다. 그 Accept 결정을 실제 Baseline 문서 변경으로 옮기기
위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

ADC-0001이 Accept 범위에서 명시하지 않은 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| Governance의 실행 주체(누가/무엇이 RFC/ADC/ADR 문서의 등록·상태를 물리적으로 관리하는가) | ADC-0001 Module 1 Risks: "그 실행 주체는 여전히 미정이다. 이 Accept는... 그 구현 방식을 결정하지 않는다" |
| Registry, 자동화 도구 등 Component Design | `BASELINE.md` §10 Out of Scope 그대로 유지 |
| Workflow/Memory/Event Bus 3개 Module(Defer) | ADC-0001 Module 2·3·5, 상태만 기록하고 설계하지 않는다 |
| Execution Layer Module(Accept, ADR Required) | 별도 ADR(`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`)의 범위 |
| Kernel Architecture 및 Component Design | `BASELINE.md` §10 Out of Scope 그대로 유지 |
| Development HQ 및 Execution Layer의 문서·코드 | Phase 1 종료 후 불변(ADR-0001·ADR-0002 dev-hq/kernel-terminology 선례). §4에서 이 제약의 충족을 실제로 확인한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/01_architecture/BASELINE.md` | §16 "Kernel Modules" 신설(Governance 상세 반영, Execution Layer는 후속 ADR 대기 표시, Workflow/Memory/Event Bus는 상태만 기록), 기존 §16 Version → §17로 이동, v1.4 → v1.5 |
| `docs/architecture/core/DOC-TRIAGE-0001.md` | "§16 Version" 인용 2건을 "§17 Version"으로 갱신(D-6b, A-1) |

그 외 어떤 파일도 변경하지 않는다.

### 2. `BASELINE.md` 절 번호 정책

ADR-0002(core-to-kernel-terminology-unification, `docs/04_adr/`)가 확립한
정책을 그대로 따른다 — **기존 절의 번호를 재배치하지 않고, 새 절을
Version 앞에 삽입한 뒤 Version을 마지막으로 민다.**

| 절 | 변경 전 | 변경 후 |
|---|---|---|
| §1 ~ §15 | 그대로 | **그대로** |
| Kernel Modules | (없음) | **§16 (신설)** |
| Version | §16 | **§17** |

**깨지는 외부 인용**: 전수 검색 결과 `BASELINE.md` §16(Version)을
인용하는 문서는 `docs/architecture/core/DOC-TRIAGE-0001.md` 2건
(D-6b, A-1)뿐이다. 이 2건을 "§17"로 갱신해 추적 사슬을 보존한다.

**과거 ADR 본문의 절 번호 언급은 갱신하지 않는다** — `ADR-0005`
본문의 "기존 §15 Version → §16" 언급 등은 **당시 수행한 변경의
기록**이지 현재 Baseline에 대한 참조가 아니다. 과거 기록을 소급
수정하지 않는다는 이 프로젝트의 원칙을 따른다(ADR-0002 §2.1 선례와
동일).

### 3. §16 Kernel Modules(신설) — 반영할 내용

`ADC-0001-core-baseline.md`가 이미 판단한 것만 옮긴다. 새 문장을
만들지 않는다.

```markdown
## 16. Kernel Modules

> 근거: `docs/architecture/core/ADC-0001-core-baseline.md`(Module 1~5
> 판단), `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`
> §4(Module 정의)

Kernel은 5개 Module 후보(Governance/Workflow/Memory/Execution
Layer/Event Bus)에 대해 각각 Kernel Module로서의 존재 여부를
판단했다(`ADC-0001-core-baseline.md` 종합). 이 절은 그중 **Accept된
Module만** Baseline에 반영한다 — Defer된 Module은 상태만 기록하고
설계하지 않는다.

### 16.1 Governance (Accept)

**책임**: Architecture Decision 관리.

**근거**: `RFC → ADC → ADR → Baseline Update` 절차
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`)가 Jarvis OS
수준(`docs/03_adc/ADC.md` ADC-01~12)과 Development HQ 수준
(`docs/governance/adc/ADC-0001~0004`, `docs/04_adr/ADR-0001`) 양쪽에서
반복 실행되어 실패 없이 동작했다(`ADC-0001-core-baseline.md` Module 1
Decision Rationale: "이미 Jarvis OS 수준과 Development HQ 수준 양쪽에서
반복 실행되어 실패 없이 동작한 절차 그 자체").

**Kernel Module로서 다루는 것**: RFC/ADC/ADR 문서의 등록과 상태
(§14.3 G-7 각주가 이미 이 사실을 전제로 인용했다: "Kernel Module로
Accept된 Governance는 문서의 등록과 상태를 다룬다").

**이 Accept가 결정하지 않는 것**: 그 실행 주체(누가/무엇이 문서
등록·상태를 물리적으로 관리하는가)는 여전히 미정이다
(`ADC-0001-core-baseline.md` Module 1 Risks). Registry나 자동화 등
Component Design은 §10 Out of Scope 그대로다.

### 16.2 Execution Layer (Accept)

Baseline 반영은 별도 ADR(`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`)에서
완료한다. 이 ADR은 그 내용을 결정하지 않는다.

### 16.3 미결 항목

Workflow, Memory, Event Bus는 Kernel Module 후보로 검토됐으나
**Defer**됐다(`ADC-0001-core-baseline.md` Module 2·3·5) — 재평가
조건은 각 Module의 Decision Rationale·Risks를 참조한다. 이 절은 그
상태를 재판단하지 않는다.
```

**16.2가 "Execution Layer Accept"만 미리 적고 내용을 비워 두는 이유**:
이 ADR은 Governance 하나만 판단 대상으로 삼는다. Execution Layer의
Accept 내용을 이 ADR이 대신 채우면 그 Module의 Baseline 반영을
Governance ADR의 부산물로 만드는 것이 되어, 두 Module을 각각 별도
ADR로 판단하라는 절차 자체를 무력화한다. 빈 자리를 남기는 것이
"§16 Kernel Modules가 신설됐다"는 사실과 "Execution Layer의 반영은
아직 완료되지 않았다"는 사실을 동시에 정직하게 드러낸다(Freeze
원칙).

### 4. Development HQ · Execution Layer 불변 확인

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/*/` 이하 소스 코드는 어떤 파일도 변경하지
  않는다.
- 55개 테스트(`core/execution_layer`)는 이번 변경으로 영향받지
  않는다(문서만 변경).

### 5. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** `docs/03_adc/ADC.md`는 Jarvis OS 수준
ADC-01~12만 관리하는 Single Source of Truth이며(직전 D-7 정정으로
그 범위가 명시됐다), Kernel `ADC-0001-core-baseline.md`의 Module
판단은 이 문서가 아니라 `docs/architecture/core/`에서 독립적으로
추적된다 — 기존 ADR(0002~0005)이 같은 상황에서 내린 판단과 동일하다.

### 6. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.4 | **v1.5** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0001(kernel) → ADC-0001(kernel)
→ 이 ADR 절차를 그대로 거쳤다. ADR-0002~0005의 선례와 동일하다.

**Minor 증가(v1.5)를 택한 이유**: 기존 §1~§15의 어떤 문장도 수정하지
않고 새 절 하나(Governance 1개 Module 상세 + 나머지 상태 기록)를
추가하는 형태이므로, ADR-0002(§13·§14 신설, v1.1/v1.2)와 같은 규모다.

### 7. Migration Strategy

1. `BASELINE.md` — §16 Kernel Modules 삽입(§16.1 Governance 상세,
   §16.2 Execution Layer 빈 자리, §16.3 미결 항목), 기존 §16 Version
   → §17 이동 및 v1.5 갱신, 변경 이력 한 줄 추가.
2. `DOC-TRIAGE-0001.md` — "§16 Version" 인용 2건(D-6b, A-1)을 "§17
   Version"으로 갱신.
3. 검증:
   - `BASELINE.md`의 절 번호가 §1~§17로 연속하는지 확인.
   - `python3 -m pytest core/execution_layer -q` 55건이 그대로
     통과하는지 확인(문서만 변경했으므로 결과가 달라지면 안 된다).
   - `git status`로 `development-hq/`·`core/`(소스) 이하에 변경이
     없는지 확인.
4. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.4 → v1.5가 되고, Governance가
  Kernel Module로서 처음 Baseline에 이름을 올린다.
- `DOC-TRIAGE-0001.md` D-8("Kernel ADC-0001의 미작성 ADR 2건")이
  절반(Governance) 해소된다. Execution Layer 절반은 여전히 열려
  있으며, 별도 ADR을 필요로 한다.
- Governance의 실행 주체(문서 등록·상태를 누가/무엇이 관리하는가)는
  여전히 결정되지 않는다 — 이 공백은 새로운 문제가 아니라
  `ADC-0001-core-baseline.md` Module 1 Risks가 이미 인정한 것이다.
- `docs/03_adc/ADC.md`는 변경되지 않는다(§5).
- 이 ADR은 **승인되었으며**, §3에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.

## Self Review

- ADC-0001이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(실행 주체, Component Design, 다른 4개 Module)은
  손대지 않았다.
- Kernel Component Architecture를 설계했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**(§5).
- Execution Layer Module의 내용을 대신 채웠는가 — **아니오**(§3,
  16.2는 별도 ADR 대기로만 표시했다).
- Development HQ·Execution Layer 코드를 변경했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  ADC-0001이 이미 인지한 것 이상의 새 결정 지점은 나타나지 않았다.
