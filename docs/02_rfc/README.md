# RFC

## 목적

RFC(Request For Comments)는 Architecture에 대한 새로운 논의를 제기하는 문서다. RFC는 결정이 아니라 검토 대상이다.

## 절차 상 위치

```
RFC → ADC → ADR → Architecture Baseline Update
```

RFC에서 논의된 내용 중 결정이 필요한 항목은 `docs/03_adc/ADC.md`에 Decision Candidate로 등록된다. RFC 자체는 Baseline을 변경하지 않는다.

## 현재 상태

Jarvis OS Architecture Baseline v1.0과 Development HQ Baseline v1.0은 Frozen이다. 새로운 RFC는 Baseline 변경이 불가피하다고 판단될 때만 작성한다.

과거 RFC(Meta Architecture, Concept Model, Core Component 등 논의)의 결과는 `docs/01_architecture/BASELINE.md`와 `docs/03_adc/ADC.md`에 이미 반영되어 있다.

## RFC 승격 대기 항목

`RFC_CANDIDATES.md`에는 이미 논의가 이루어졌고 MVP 검증 이후 정식 RFC로 승격될 가능성이 높은 Architecture 후보가 기록되어 있다. 이는 막연한 아이디어 목록이 아니라, Baseline 반영 가능성이 높다고 판단된 항목이다. 단, 정식 RFC로 승격되기 전까지는 Baseline에도, 구현에도 반영되지 않는다.
