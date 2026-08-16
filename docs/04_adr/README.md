# ADR (Architecture Decision Record)

## 목적

ADR은 ADC 중 NOW로 분류되어 실제로 결정된 사항을 기록하는 문서다. ADR이 작성되면 해당 ADC 항목은 `docs/03_adc/ADC.md`에서 상태가 Resolved로 갱신되고, 결정 내용은 `docs/01_architecture/BASELINE.md`에 반영된다.

## 최소 구성

| 필드 | 설명 |
|---|---|
| ID | ADR-XXXX |
| 제목 | |
| 상태 | Proposed / Accepted / Superseded |
| Context | 유래한 ADC, 당시 충돌 내용 |
| Decision | 최종 결정 내용 |
| Consequences | 이 결정으로 감수해야 하는 것, 향후 재검토 조건 |
| 관련 ADC | 이 ADR이 종결시키는 ADC ID |

## 현재 상태

이 표는 `docs/04_adr/`(Development HQ 수준) ADR만 다룬다. Kernel 수준 ADR은
`docs/architecture/core/`에 별도로 등록되어 있다(`ADR-0001-governance-module-baseline.md`,
`ADR-0002-execution-layer-module-baseline.md` — `docs/01_architecture/BASELINE.md`를
v1.4 → v1.6으로 갱신).

작성된 ADR 5건. 전부 Accepted다.

| ID | 제목 | 종결시킨 ADC |
|---|---|---|
| ADR-0001 | Development HQ Baseline에 Stage 기반 구조 반영 | `docs/governance/adc/ADC-0003.md` 판단 1 |
| ADR-0002 | Core → Kernel 용어 통합 및 Kernel 정의의 Baseline 반영 | `docs/architecture/core/ADC-0002.md` 판단 1·3·4 |
| ADR-0003 | Kernel Context Model의 Baseline 반영 | `docs/architecture/core/ADC-0003.md` 판단 1·2·3·5·6a |
| ADR-0004 | Kernel Public Contract의 Baseline 반영 | `docs/architecture/core/ADC-0004.md` 판단 1~8 |
| ADR-0005 | Kernel Logical Reference Architecture의 Baseline 반영과 §10 범위 한정 | `docs/architecture/core/ADC-0005.md` 판단 1~8 |

ADR-0002 ~ ADR-0005가 `docs/01_architecture/BASELINE.md`를 v1.0 → v1.4로 갱신했다.

`docs/03_adc/ADC.md`의 NOW 항목(ADC-02, ADC-09, ADC-10)은 여전히 Open이며, 위 5건 중 어느 것도 그 항목들을 종결시키지 않았다.
