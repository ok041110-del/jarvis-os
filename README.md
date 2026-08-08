# Jarvis OS v2 Starter Kit

## 이 Starter Kit은 무엇인가

Jarvis OS Architecture Baseline v1.4와 Development HQ Baseline v1.0을 기반으로 구성된 문서 패키지다. Development HQ MVP-0001은 이 Starter Kit의 최초 착수 대상이었고, 현재는 MVP-0013까지 완료된 상태다.

Architecture 자체에 대한 설명은 이 문서에서 반복하지 않는다. `docs/01_architecture/BASELINE.md`가 유일한 Architecture 원본이다.

## 상태

| 항목 | 상태 |
|---|---|
| Jarvis OS Architecture Baseline | v1.4, Frozen |
| Development HQ Baseline | v1.0, Frozen |
| Development HQ MVP | MVP-0001 ~ MVP-0013 완료 (Phase 1 종료) |
| Execution Layer MVP | MVP-0001 ~ MVP-0005 완료 |
| Starter Kit | **v1.0 Final** |

이 Starter Kit은 Frozen 상태다. Architecture, Concept, Layer, Component를 새로 추가하지 않는다. 변경이 필요하다고 판단되면 직접 수정하지 않고 `docs/02_rfc` → `docs/03_adc` → `docs/04_adr` 절차를 따른다.

## 시작 위치

Claude Code는 `development-hq/HANDOVER.md`를 가장 먼저 읽는다.

## 프로젝트 구조

```
jarvis-os-v2-starter-kit/
├── README.md
├── docs/
│   ├── 00_governance/
│   │   ├── ARCHITECTURE_GOVERNANCE.md
│   │   └── GLOSSARY.md
│   ├── 01_architecture/
│   │   └── BASELINE.md
│   ├── 02_rfc/
│   │   ├── README.md
│   │   └── RFC_CANDIDATES.md
│   ├── 03_adc/
│   │   ├── README.md
│   │   └── ADC.md
│   └── 04_adr/
│       └── README.md
└── development-hq/
    ├── README.md
    ├── MISSION.md
    ├── BOUNDARY.md
    ├── RESPONSIBILITY.md
    ├── STRUCTURE.md
    ├── BASELINE.md
    ├── MVP.md
    ├── IMPLEMENTATION_RULES.md
    └── HANDOVER.md
```

## 문서 읽는 순서

1. `README.md` (본 문서)
2. `development-hq/HANDOVER.md` — 인수인계 요약, 시작점
3. `docs/01_architecture/BASELINE.md` — Jarvis OS 전체 기준
4. `development-hq/BASELINE.md` — Development HQ 기준
5. `development-hq/MVP.md` — 무엇을 만드는가
6. `development-hq/IMPLEMENTATION_RULES.md` — 무엇을 만들면 안 되는가
7. `docs/03_adc/ADC.md` — 아직 결정되지 않은 것들 (구현과 무관, 참고용)
