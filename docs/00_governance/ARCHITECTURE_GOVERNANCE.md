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

## Experimental Implementation

이 절은 위 "적용 범위"가 요구하는 중단 원칙과 별도로, Formal Architecture Decision 없이 허용되는 실험적 구현의 범위를 정의한다. Experimental Implementation은 Formal Architecture 결정과 동일하지 않다 — 제한된 범위에서 실제 실행·검증을 통해 Evidence를 얻는 것을 허용할 뿐, 그 자체로 Architecture를 확정하지 않는다.

Experimental Implementation은 다음 범위를 벗어나지 않는다.

- 명확한 목적과 제한된 scope
- 명시적 owner
- 테스트/검증 수행
- 기존 Formal Component의 Contract 보호(수정하지 않음)
- 기존 Frozen Boundary 보호(Structure v1.0, Architecture Baseline을 변경하지 않음)
- 기존 HQ production path(`hqs/development/`, `hqs/investment/`)에 무단 연결 금지
- 성공/실패/폐기 기준 기록

**허용**: `projects/` 기반 Prototype, 격리된 실행 환경에서의 구현, 실제 HQ traffic pattern을 복제한 실험, 테스트용 실행, 성능/신뢰성/경계 검증, Experimental Component의 수정·폐기.

**금지**: `hqs/development/`·`hqs/investment/` production path에 Experimental Component를 직접 연결하는 것, 기존 Formal Component의 Contract 변경, Structure v1.0 Boundary 변경, 새로운 Core 책임을 Experimental 상태로 사실상 선언하는 것, Engine Gateway/Routing/Adapter 등 기존 Frozen 또는 Deferred Boundary를 우회하는 것, "Experimental"이라는 명목으로 기존 Governance의 Formal Decision을 우회하는 것.

Experimental은 필요 없다고 판단되면 RFC 없이 즉시 제거할 수 있다. 반복적인 가치와 Architecture 승격 필요성이 실제로 확인된 경우에만 Formal Promotion을 검토하며, 이 경우 위 "변경 절차"(RFC → ADC → ADR → Architecture Baseline Update → Implementation)를 그대로 따른다. **Experimental Evidence는 그 존재만으로 Formal Architecture Decision이나 ADC Accept를 발생시키지 않는다** — Promotion 여부는 여전히 아래 "ADC 채택 기준"으로 판단한다.

## Architecture Need

Architecture Need란 현재 Architecture로 해결하기 어려운 실제 문제, 반복되는 요구사항, 또는 새로운 공통 책임의 필요성이 개발·운영 과정에서 실제로 관찰된 상태를 말한다. 단순한 아이디어나 선호는 Architecture Need가 아니다.

이 원칙은 사전에 정의된 특정 Trigger(예: `docs/governance/rt/RT-0001.md`의 "Engine 수 ≥ 2")가 충족되지 않았더라도, 실제 Architecture Need가 관찰되면 재검토를 시작할 권한을 부여한다. 미리 예상한 모든 상황을 새 Trigger로 목록화하는 것이 아니라, 실제 Need가 발생했을 때 그것을 검토할 수 있는 경로를 여는 것이다. 기존 Trigger 체계(RT-0001의 개별 Re-evaluation Trigger, "Engine 수 ≥ 2" 포함)는 이 원칙으로 대체되거나 약화되지 않는다 — Architecture Need는 그 상위의 진입 원칙이며, 개별 Trigger는 Architecture Need의 관찰 가능한 특수 사례로 계속 유효하다.

### 진입 흐름

```
실제 Need 발생
  ↓
현재 Architecture로 해결 가능한가?
  ├─ YES → 기존 Architecture 사용(Governance 진입 불필요)
  └─ NO
       ↓
     Experimental Implementation(위 절)으로 검증 가능한가?
       ├─ YES → Experimental 수행
       │          ├─ 가치 없음 → 폐기(RFC 불필요)
       │          └─ 가치 있음 → Formal Architecture Review
       └─ NO → Formal Architecture Review
                  ↓
                RFC → ADC → ADR(위 "변경 절차")
```

### 반드시 구분할 것

- Architecture Need 발생 ≠ Architecture 변경 승인
- Experimental 성공 ≠ Architecture 변경 승인
- Prototype 존재 ≠ Core Component 승격

Architecture Need는 오직 "검토를 시작할 근거"만 제공한다. 검토 결과 Formal Architecture 변경이 실제로 필요한지는 여전히 아래 "ADC 채택 기준"이 판단하며, 이 원칙이 그 기준을 대신하지 않는다.

### 안전장치

- 실제 문제/요구가 있어야 한다 — 추측·선호는 Need가 아니다.
- 기존 Architecture로 해결 가능한지 먼저 확인한다.
- 가능하면 Experimental Implementation(위 절)으로 먼저 검증한다.
- Experimental은 위 절의 조건(격리 영역, HQ production path 무단 연결 금지 등)을 그대로 따른다.
- Frozen Architecture(Structure v1.0, Architecture Baseline)를 임의로 수정하지 않는다.
- Core 책임을 Prototype 단계에서 사실상 선언하지 않는다.
- Formal 변경은 예외 없이 RFC → ADC → ADR을 거친다.
- Architecture Need의 존재만으로 Formal Promotion이 자동 발생하지 않는다.
- 필요성이 사라지면 Prototype/Experimental은 자유롭게 폐기할 수 있다.

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
