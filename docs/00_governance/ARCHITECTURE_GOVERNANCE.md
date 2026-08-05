# Architecture Governance

## 변경 절차

```
RFC
↓
ADC
↓
ADR
↓
Architecture Baseline Update
↓
(Development HQ Baseline Update — 해당 시)
↓
Implementation
```

이 절차를 우회한 변경은 Baseline에 반영되지 않는다.

## 적용 범위

이 Governance는 구현 단계뿐 아니라 설계·문서화 단계에도 동일하게 적용된다. **Architecture 변경이 필요한 상황이 발생하면 현재 작업을 중단한다.** 이는 코드를 작성하는 중이든, 문서를 정리하는 중이든, RFC를 검토하는 중이든 동일하게 적용되는 원칙이다. 그 자리에서 직접 결정하지 않고 위 절차(RFC → ADC → ADR)를 따른다.

## ADC 채택 기준

새로운 Architecture Decision Candidate(ADC)는 다음 중 하나를 반드시 만족해야 채택된다.

1. 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다.
2. 결정이 늦어질수록 되돌리는 비용이 매우 커진다.

두 조건을 만족하지 않으면 해당 사안은 현재 단계에서 다루지 않는다.

## ADC 우선순위 분류

| 분류 | 의미 |
|---|---|
| NOW | 지금 결정하지 않으면 Architecture를 진행할 수 없음 |
| NEXT | Kernel 설계 전에 결정 |
| LATER | Subsystem 설계에서 결정 |
| NEVER | 현재는 결정하지 않는 것이 맞음 |

## Single Source of Truth

모든 Open Decision은 `docs/03_adc/ADC.md`에서 관리한다. Architecture Baseline과 Development HQ Baseline은 Open Decision의 상세 내용을 직접 기록하지 않고 `ADC.md`를 참조만 한다.

## Freeze 원칙

Architecture Baseline은 "모든 문제가 해결된 상태"가 아니라 "지금 결정할 것과 나중에 결정할 것이 명확히 구분되고 추적되는 상태"를 의미한다. 미결정 사항이 없는 것이 목표가 아니라, 미결정 사항이 정직하게 드러나 추적되는 것이 목표다.

## Good Architecture Principle

좋은 Architecture는 모든 것을 미리 설계한 Architecture가 아니라, 필요한 것만 적절한 시점에 결정한 Architecture다.
