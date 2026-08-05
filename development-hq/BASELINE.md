# Development HQ Baseline v1.0

## Version

| 항목 | 내용 |
|---|---|
| Version | 1.0.0 |
| Status | Active |
| Architecture State | Frozen |

## Scope

Development HQ는 Jarvis OS Architecture Baseline 위에서 동작하는 첫 번째 Reference HQ이다.

Development HQ는 Architecture를 변경하지 않는다. Development HQ는 Architecture를 검증한다.

## Included Documents

- `README.md`
- `MISSION.md`
- `RESPONSIBILITY.md`
- `BOUNDARY.md`
- `STRUCTURE.md`

## Not Included

- Kernel Design
- Scheduler
- Engine Gateway
- Registry Implementation
- Communication Implementation
- Runtime
- MVP Implementation (별도 `MVP.md` 참조)
- Connector Implementation

## Open Decisions

Development HQ에는 Architecture Open Decision이 존재하지 않는다. Architecture Open Decision은 Jarvis OS의 `docs/03_adc/ADC.md`를 참조한다. Development HQ는 Architecture Decision을 소유하지 않는다.

## Governance

Development HQ 변경은 Jarvis OS Governance를 그대로 따른다.

```
RFC
↓
ADC
↓
ADR
↓
Architecture Baseline Update
↓
Development HQ Baseline Update
↓
Implementation
```

## Final Declaration

> Development HQ Baseline v1.0은 Jarvis OS 위에서 동작하는 첫 번째 공식 Reference HQ이다.
>
> 이 Baseline은 Development HQ의 Mission, Responsibility, Boundary, Structure를 정의한다.
>
> 구현, Kernel, Runtime, MVP는 본 Baseline의 범위가 아니다.
>
> Development HQ는 Jarvis OS Architecture를 수정하기 위해 존재하는 것이 아니라, Jarvis OS Architecture를 현실에서 검증하기 위해 존재한다.
