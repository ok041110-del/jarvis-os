# RFC

## 목적

RFC(Request For Comments)는 Architecture에 대한 새로운 논의를 제기하는 문서다. RFC는 결정이 아니라 검토 대상이다.

## 절차 상 위치

```
RFC → ADC → ADR → Architecture Baseline Update
```

RFC에서 논의된 내용 중 결정이 필요한 항목은 `docs/03_adc/ADC.md`에 Decision Candidate로 등록된다. RFC 자체는 Baseline을 변경하지 않는다.

## 현재 상태

Jarvis OS Architecture Baseline v1.6과 Development HQ Baseline v1.0은 Frozen이다. 새로운 RFC는 Baseline 변경이 불가피하다고 판단될 때만 작성한다.

과거 RFC(Meta Architecture, Concept Model, Core Component 등 논의)의 결과는 `docs/01_architecture/BASELINE.md`와 `docs/03_adc/ADC.md`에 이미 반영되어 있다.

## RFC 승격 대기 항목

`RFC_CANDIDATES.md`에는 이미 논의가 이루어졌고 MVP 검증 이후 정식 RFC로 승격될 가능성이 높은 Architecture 후보가 기록되어 있다. 이는 막연한 아이디어 목록이 아니라, Baseline 반영 가능성이 높다고 판단된 항목이다. 단, 정식 RFC로 승격되기 전까지는 Baseline에도, 구현에도 반영되지 않는다.

## 등록된 RFC

이 표는 `docs/02_rfc/`(Development HQ 수준) RFC만 다룬다. Kernel 수준 RFC는
`docs/architecture/core/`, Execution Layer 수준 RFC는
`docs/core/execution-layer/`에 별도로 등록되어 있다.

| ID | 제목 | 상태 | 후속 ADC | 후속 ADR |
|---|---|---|---|---|
| RFC-0001 | Kernel Boundary | Resolved | `docs/governance/adc/ADC-0001.md` | 없음(불필요) |
| RFC-0002 | Task Dispatcher Boundary | Resolved | `docs/governance/adc/ADC-0002.md` | 없음(불필요) |
| RFC-0003 | Development HQ SDLC Pivot | Resolved | `docs/governance/adc/ADC-0003.md` | `ADR-0001`(판단 1에 한해) |
| RFC-0004 | Task Dispatcher → Runtime Boundary | Resolved | `docs/governance/adc/ADC-0004.md` | 없음(불필요) |
| RFC-0005 | Development HQ ↔ Execution Layer Boundary | **Open** | 없음(미작성) | — |

(출처: `STABILITY-0001-core-architecture.md` §1.2 RFC→ADC 대응 전수 확인)

RFC-0001은 Development HQ MVP-0001 구현 중 관찰된 Kernel Extraction Candidate(Task
Dispatcher, Engine Gateway, Registry, Context 전달 메커니즘)를 근거로 Kernel Boundary
논의가 필요한 시점인지를 제기한다. 답은 제시하지 않는다. → `RFC-0001-kernel-boundary.md`

RFC-0005는 저장소 내 13개 RFC 중 유일하게 후속 ADC가 아직 작성되지 않은 채
Open으로 남아 있다. Kernel 영역도 Development HQ Phase 1(종료됨)도 이 RFC에
의존하지 않는다(`STABILITY-0001` §1.3).
