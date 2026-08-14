# Jarvis OS v2 Starter Kit

## 이 Starter Kit은 무엇인가

Jarvis OS Architecture Baseline과 Development HQ Baseline을 기반으로, Development HQ MVP-0001 착수 이후 MVP Dogfooding, Kernel Architecture 연구(RFC/ADC/ADR), Investment 영역(Stock/ETF/Dividend Stock) Dogfooding까지 실제로 진행되어 온 저장소다. 원래의 Starter Kit 문서 패키지(v1.0 Final)는 이 저장소의 시작점이었고, 그 이후 범위가 `core/`, `projects/`, `docs/01_mvp/`, `docs/research/` 등으로 확장되었다.

Architecture 자체에 대한 설명은 이 문서에서 반복하지 않는다. `docs/01_architecture/BASELINE.md`가 유일한 Architecture 원본이다.

## 상태

| 항목 | 상태 |
|---|---|
| Jarvis OS Architecture Baseline | v1.6 (RFC → ADC → ADR 경로로만 갱신) |
| Development HQ Baseline | v1.0, Frozen |
| Development HQ MVP | MVP-0001 ~ MVP-0048 완료 (Evidence 기반, `docs/01_mvp/`) |
| Execution Layer MVP | MVP-0001 ~ MVP-0006 완료 (`core/execution_layer/`) |
| Investment 영역 Dogfooding | Stock Team·ETF Team·Dividend Stock Team 모두 Promoted (`docs/research/`) |
| Development HQ MVP Validation | 종료 권고됨(`GOVERNANCE-REVIEW-0007`), Kernel Validation 단계로 전환 |
| 원본 Starter Kit 문서 패키지 | v1.0 Final (그 이후 문서·코드가 이 패키지 범위 밖으로 확장됨) |

Architecture Baseline과 Development HQ Baseline은 직접 수정하지 않는다. 변경이 필요하다고 판단되면 `docs/02_rfc` → `docs/03_adc` → `docs/04_adr` 절차를 따른다.

## 시작 위치

Claude Code는 `development-hq/HANDOVER.md`를 가장 먼저 읽는다.

## 프로젝트 구조 (주요 디렉토리)

```
jarvis-os/
├── README.md
├── docs/
│   ├── 00_governance/            Governance 원칙, 용어집
│   ├── 01_architecture/          BASELINE.md — Jarvis OS Architecture 원본
│   ├── 01_mvp/                   Development HQ MVP별 plan/observation
│   ├── 02_rfc/                   RFC (Architecture 변경 제안)
│   ├── 03_adc/                   ADC.md — Open Decision Single Source of Truth
│   ├── 04_adr/                   ADR (채택된 결정)
│   ├── architecture/core/        Kernel Architecture RFC/ADC/ADR·Governance Review
│   ├── core/execution-layer/     Execution Layer 수준 ADC/관찰
│   └── research/                 Investment 영역(Stock/ETF/Dividend Stock) Dogfooding 검토
├── development-hq/
│   ├── README.md, MISSION.md, BOUNDARY.md, RESPONSIBILITY.md, STRUCTURE.md
│   ├── BASELINE.md, MVP.md, IMPLEMENTATION_RULES.md, HANDOVER.md
│   └── mvp/                      MVP-0001 구현 코드
├── core/execution_layer/         Execution Layer MVP 코드
└── projects/                     Dogfooding 대상 실제 프로젝트(notekeeper, textkit, stock/etf 분석 등)
```

## 문서 읽는 순서

1. `README.md` (본 문서)
2. `development-hq/HANDOVER.md` — 인수인계 요약, 시작점
3. `docs/01_architecture/BASELINE.md` — Jarvis OS 전체 기준
4. `development-hq/BASELINE.md` — Development HQ 기준
5. `development-hq/MVP.md` — MVP-0001이 무엇을 만들었는가
6. `development-hq/IMPLEMENTATION_RULES.md` — 무엇을 만들면 안 되는가
7. `docs/03_adc/ADC.md` — 아직 결정되지 않은 것들 (구현과 무관, 참고용)
8. `docs/01_mvp/` — MVP-0002 이후 실제 진행 내역(Evidence)
9. `docs/research/` — Investment 영역(Stock/ETF/Dividend Stock) Dogfooding 검토
