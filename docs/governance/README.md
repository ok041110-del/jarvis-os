# Governance Charter

## 목적

이 문서는 Jarvis OS Development HQ에서 현재까지 확정된 Governance 흐름의
개요를 설명한다. 새로운 Architecture를 제안하지 않으며, 새로운 Governance
단계를 추가하지 않는다. RFC, ADC, RT의 역할과 관계만 설명한다.

## 단계

### MVP

실제 동작을 구현하여 Observation을 확보하는 단계.

### RFC

Observation으로부터 Kernel Boundary를 질문하는 단계.

### ADC

Boundary에 대해 승격 여부만 판단하는 단계.

### RT

Keep in MVP가 된 Candidate의 재평가 조건을 정의하는 단계.

> ADR은 현재 Governance Flow에 포함하지 않는다. ADC-0001의 모든 Decision이
> Keep in MVP였으므로, Baseline 변경을 기록하는 ADR은 아직 사용되지 않았다.

## 현재까지 확정된 흐름

```
MVP
 ↓
RFC
 ↓
ADC
 ├── Promote
 │
 └── Keep
      ↓
     RT
      ↓
새로운 Observation
      ↓
다음 RFC
```

Promote 이후의 구현 절차는 이 문서의 범위가 아니다.

## Document Numbering

- `RFC-xxxx` — Boundary Question (현재: `docs/02_rfc/RFC-0001-kernel-boundary.md`)
- `ADC-xxxx` — Architecture Decision Candidate (현재: `docs/governance/adc/ADC-0001.md`)
- `RT-xxxx` — Re-evaluation Trigger (현재: `docs/governance/rt/RT-0001.md`)

번호는 문서 종류별로 독립적으로 증가한다. RFC가 생성되었다고 반드시 ADC가
생성되는 것은 아니며, ADC가 생성되었다고 반드시 RT가 생성되는 것도 아니다.
각 문서는 Governance 진행 결과에 따라 독립적으로 존재할 수 있다.

## 핵심 원칙

- **Observation First** — 모든 판단은 실제로 관찰된 사실에서 시작한다.
- **Boundary Before Design** — 설계보다 Boundary(무엇이 Kernel의 몫인지)를
  먼저 묻는다.
- **Decision Before Implementation** — 구현하기 전에 승격 여부를 결정한다.
- **Re-evaluate Only After New Observation** — 새로운 Observation이 생기기
  전까지는 재평가하지 않는다.
- **No Architecture Drift** — 어떤 단계도 새로운 Layer/Component/Service를
  만들지 않는다.
- **No Kernel Leak** — 어떤 단계도 Kernel의 내부 구조나 구현 방법을
  결정하지 않는다.

## Self Review Checklist

- [x] 새로운 Governance 단계를 만들지 않았는가 — MVP/RFC/ADC/RT 네 단계만
      설명했다. ADR은 흐름에 포함하지 않았다.
- [x] 구현을 설명하지 않았는가 — Kernel 구조·Runtime·Registry·Scheduler·
      Memory·EventBus·Engine Gateway 구현을 설명하지 않았다.
- [x] Architecture Drift가 없는가 — 없음.
- [x] Kernel Leak가 없는가 — 없음.
- [x] RFC/ADC/RT와 모순되지 않는가 — RFC-0001·ADC-0001·RT-0001에서 실제로
      쓰인 역할 정의와 흐름(Keep in MVP → RT → 재평가)만 반영했다.
- [x] 현재 MVP-0001 결과만 기반으로 작성했는가 — ADC-0001의 Keep in MVP
      결과 외의 사실을 근거로 사용하지 않았다.
- [x] 문서 번호 규칙이 명확한가 — RFC/ADC/RT 각각 문서 종류별 독립 증가
      번호임을 명시했고, 실제 존재하는 세 문서의 경로를 그대로 인용했다.
      RFC-0001은 `docs/02_rfc/`에, ADC-0001·RT-0001은 `docs/governance/`
      하위에 있어 위치가 다르지만, 번호 체계 자체는 문서 종류별 독립
      규칙이므로 모순되지 않는다.
