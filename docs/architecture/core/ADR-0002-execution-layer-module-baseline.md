# ADR-0002: Execution Layer Kernel Module의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0002` (docs/04_adr/ADR-0002 core-to-kernel-terminology-unification과 다른 문서 — 네임스페이스로 구분) |
| 제목 | Kernel `ADC-0001-core-baseline.md` Module 4(Execution Layer)의 Accept 결정을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0001-core-baseline.md` Module 4(Execution Layer) — **Decision: Accept**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` §4.4(Execution Layer Module 정의) |
| 관련 ADC | `docs/architecture/core/ADC-0001-core-baseline.md` Module 4 |
| 관련 Documentation Issue | `docs/architecture/core/DOC-TRIAGE-0001.md` D-8("Kernel ADC-0001의 미작성 ADR 2건") — 이 ADR로 나머지 절반이 해소된다 |
| 선행 ADR | `docs/architecture/core/ADR-0001-governance-module-baseline.md`(같은 절차로 Governance Module을 먼저 반영, §16 Kernel Modules를 신설한 선례) |

이 ADR은 `ADC-0001-core-baseline.md`가 이미 내린 Execution Layer
Module Accept 결정을 다시 논의하지 않는다. 새로운 철학이나
Architecture를 제안하지 않는다. 그 Accept 결정을 실제 Baseline 문서
변경으로 옮기기 위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

ADC-0001이 Accept 범위에서 명시하지 않은 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| Execution Layer 내부 구조(Prompt 구성, Model 선택, 재시도 정책) | ADC-0001 Module 4 Risks: "내부 구조는 `docs/03_adc/ADC.md`의 ADC-01·ADC-02가 여전히 Open... 이 Accept를 'Execution Layer의 설계가 결정되었다'는 의미로 확장 해석하면 안 된다" |
| Multi-Model 지원 | `docs/governance/adc/ADC-0003.md` 판단 4, Out of Authority — 이 ADR의 권한이 아니다 |
| `core/execution_layer/`의 실제 구현(6개 Builder + Pipeline) | 이미 별도 절차(RFC-0002~0004, ADC-0002~0004, ADR-0001·0002 execution-layer)로 진행 중이며, 이 ADR은 그 Contract를 재론하지 않는다 |
| Execution Result Consumer, Runtime 존폐(ADC-02) | 각각 `ADC-0004-execution-result-consumer.md`, `ADC-0008-runtime-existence-boundary.md`가 Not Accepted로 이미 판단했다 — 이 ADR이 재판단하지 않는다 |
| Governance Module(Accept) | 별도 ADR(`docs/architecture/core/ADR-0001-governance-module-baseline.md`)에서 이미 완료 |
| Workflow/Memory/Event Bus 3개 Module(Defer) | ADC-0001 Module 2·3·5, `ADR-0001`이 이미 상태만 기록했다 — 이 ADR도 재판단하지 않는다 |
| Kernel Architecture 및 Component Design | `BASELINE.md` §10 Out of Scope 그대로 유지 |
| Development HQ의 문서·코드 | Phase 1 종료 후 불변 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/01_architecture/BASELINE.md` | §16.2 "Execution Layer (Accept)"의 빈 자리(`ADR-0001`이 남겨 둔 대기 표시)를 실제 내용으로 채운다. 절 번호·Version 절 위치는 변경하지 않는다(신설 절 없음) |

그 외 어떤 파일도 변경하지 않는다. `docs/architecture/core/DOC-TRIAGE-0001.md`도
이번에는 건드리지 않는다 — §16.2 변경은 새 절 삽입이 아니라 기존
§16.2 자리의 내용 대체이므로, 절 번호가 다시 밀리지 않는다.

### 2. `BASELINE.md` §16.2 갱신 내용

`ADC-0001-core-baseline.md` Module 4와 `RFC-0001-jarvis-os-core-baseline.md`
§4.4가 이미 정리한 것만 옮긴다. 새 문장을 만들지 않는다.

기존(`ADR-0001`이 남긴) 문구:

```markdown
### 16.2 Execution Layer (Accept)

Baseline 반영은 별도 ADR(`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`)에서
완료한다. 이 ADR은 그 내용을 결정하지 않는다.
```

교체할 문구:

```markdown
### 16.2 Execution Layer (Accept)

**책임**: Specification 기반 AI 실행.

**근거**: `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`가
Development HQ는 Implementation Specification(Target File / Public
Interface / Functions / Classes / Dependencies / Algorithm Outline /
Edge Cases / Validation Notes 8개 항목)을 생성하고 그 구조적
완전성만 검증하는 지점에서 끝난다는 것과, 그 Specification으로부터
실제 코드를 생성·실행·테스트하고 Model/Engine을 선택·호출하는
지점부터 Execution Layer가 시작된다는 것을 사실 근거로 이미
정리했다. `development-hq/BOUNDARY.md`("Engine 호출 — Kernel Engine
Port/Adapter의 책임")와 §7("Engine 호출의 표준 인터페이스 제공
(Port/Adapter)")은 이 경계를 이미 확정해 두었다
(`ADC-0001-core-baseline.md` Module 4 Decision Rationale: "9개 MVP
전부 일관, Phase 1 시작 이전부터 Frozen 경계").

**Kernel Module로서 다루는 것**: Development HQ가 만든 Implementation
Specification을 입력으로 받아, 코드 생성·실행·테스트, Model/Engine
선택·호출까지의 경계(`RFC-0001-jarvis-os-core-baseline.md` §4.4).

**이 Accept가 결정하지 않는 것**: 내부 구조(Prompt 구성, Model 선택,
재시도 정책, Multi-Model Routing)는 `docs/03_adc/ADC.md`의
ADC-01(Model↔Component 대응)·ADC-02(Runtime 존폐)와
`docs/governance/adc/ADC-0003.md` 판단 4(Multi-Model, Out of
Authority)가 여전히 Open으로 남긴 영역이다
(`ADC-0001-core-baseline.md` Module 4 Risks: "이 Accept를 'Execution
Layer의 설계가 결정되었다'는 의미로 확장 해석하면 안 된다"). 이 두
Open Decision은 각각 `ADC-0008-runtime-existence-boundary.md`(ADC-02,
Not Accepted)로 한 차례 대조됐으나 여전히 미해소다.
```

### 3. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** `ADR-0001`(governance-module-baseline) §5와
동일한 판단 — Kernel `ADC-0001-core-baseline.md`의 Module 판단은
`docs/03_adc/ADC.md`(Jarvis OS 수준 ADC-01~12 전용)가 아니라
`docs/architecture/core/`에서 독립적으로 추적된다.

### 4. Development HQ · Execution Layer 소스 불변 확인

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/*/` 이하 소스 코드는 어떤 파일도 변경하지
  않는다 — 이 ADR은 6개 Builder + Pipeline의 Contract를 재론하지
  않는다.
- 55개 테스트(`core/execution_layer`)는 이번 변경으로 영향받지
  않는다(문서만 변경).

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.5 | **v1.6** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0001(kernel) → ADC-0001(kernel)
→ 이 ADR 절차를 그대로 거쳤다. `ADR-0001`(governance-module)의
선례와 동일하다.

**Minor 증가(v1.6)를 택한 이유**: 새 절을 신설하지 않고, `ADR-0001`이
남겨 둔 §16.2의 빈 자리를 채우는 형태다. 절 구조 변경이 없는
내용 채움이라는 점에서 `ADR-0001`(신설, v1.5)보다 작은 변경이지만,
Baseline 본문 내용이 실질적으로 늘어나므로 별도 Patch 없이 Minor로
기록한다(선행 4개 ADR 전부 Minor 단위였던 것과 동일한 granularity).

### 6. Migration Strategy

1. `BASELINE.md` — §16.2 내용 교체(§2), 변경 이력 한 줄 추가, v1.6
   갱신.
2. 검증:
   - `BASELINE.md`의 절 번호가 §1~§17로 그대로 유지되는지 확인(신설
     절 없음).
   - `python3 -m pytest core/execution_layer -q` 55건이 그대로
     통과하는지 확인(문서만 변경했으므로 결과가 달라지면 안 된다).
   - `git status`로 `development-hq/`·`core/`(소스) 이하에 변경이
     없는지 확인.
3. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.5 → v1.6이 되고, Execution
  Layer가 Kernel Module로서 처음 Baseline에 상세 반영된다.
- `DOC-TRIAGE-0001.md` D-8("Kernel ADC-0001의 미작성 ADR 2건")이
  이번 ADR로 **완전히 해소**된다 — Governance(ADR-0001)와 Execution
  Layer(이 ADR) 둘 다 Baseline에 반영됐다.
- Execution Layer의 내부 구조(ADC-01·ADC-02)는 여전히 Open으로
  남는다 — 이 공백은 새로운 문제가 아니라 `ADC-0001-core-baseline.md`
  Module 4 Risks가 이미 인정했고, `ADC-0008-runtime-existence-boundary.md`
  가 한 차례 대조까지 마친 것이다.
- `core/execution_layer/`의 실제 구현(6개 Builder + Pipeline)은 이
  ADR과 별개로 이미 진행 중이며, 이 ADR이 그 진행에 새 제약을 추가
  하지 않는다 — Kernel 수준의 "Module로서 존재한다"는 사실을
  뒤늦게 Baseline에 기록했을 뿐이다.
- `docs/03_adc/ADC.md`는 변경되지 않는다(§3).
- 이 ADR은 **승인되었으며**, §2에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.

## Self Review

- ADC-0001이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(내부 구조, Multi-Model, 실제 구현, Consumer,
  Runtime, 다른 4개 Module)은 손대지 않았다.
- Execution Layer 내부 구조를 설계했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**(§3).
- `core/execution_layer/`의 Contract를 재론했는가 — **아니오**.
- 새 절을 신설했는가 — **아니오**. 기존 §16.2 자리를 채웠을
  뿐이다(§2).
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  ADC-0001이 이미 인지한 것 이상의 새 결정 지점은 나타나지 않았다.
