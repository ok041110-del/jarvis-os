# ADC (Architecture Decision Candidate)

## 목적

ADC.md는 모든 Open Decision의 Single Source of Truth다. Architecture Baseline과 Development HQ Baseline은 Open Decision의 상세 내용을 직접 기록하지 않고 이 문서를 참조만 한다.

## 채택 기준

새로운 ADC는 다음 중 하나를 반드시 만족해야 한다.

1. 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다.
2. 결정이 늦어질수록 되돌리는 비용이 매우 커진다.

## Experimental Implementation과의 관계

ADC가 판단하는 대상은 Formal Architecture Decision이다. Experimental Implementation 단계 자체(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" 참조)는 ADC Accept를 필요로 하지 않는다. Experimental 결과를 Formal Architecture 또는 Core Component로 승격하려는 경우에만 위 채택 기준을 적용한다.

## 우선순위 분류

NOW / NEXT / LATER / NEVER — 정의는 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` 참조.

## 상태

ADC는 Open → (ADR 작성) → Resolved 순으로 전환된다. Resolved된 ADC는 관련 ADR ID와 함께 기록되고 ADC.md에서 상태만 갱신된다 (항목 삭제하지 않음).
