# Governance Charter

## 목적

이 문서는 Jarvis OS Development HQ에서 현재까지 확정된 Governance 흐름의
개요를 설명한다. 새로운 Architecture를 제안하지 않는다. RFC, ADC, RT,
ADR, 그리고 Governance v2에서 추가된 Observation의 역할과 관계만
설명한다.

## 단계

### MVP

실제 동작을 구현하여 Observation을 확보하는 단계.

### RFC

Observation으로부터 Kernel Boundary를 질문하는 단계.

### ADC

Boundary에 대해 승격 여부만 판단하는 단계.

### RT

Keep in MVP가 된 Candidate의 재평가 조건을 정의하는 단계.

### ADR

ADC에서 Accept/Promote로 판단된 사항을 실제 Baseline 문서 변경 결정으로
기록하는 단계. (최초 사용: ADR-0001, ADC-0003 판단 1의 Stage 기반 구조
반영.)

### Observation (Governance v2, Baseline)

> Observe First, Decide Later.
> Accumulate Before Escalate.

MVP가 끝날 때마다 자동으로 RFC를 여는 대신, 사실만 담은 OBS 문서를
누적한다. 새로운 규칙은 다음 두 개뿐이다.

- **Rule A**: RT Trigger 충족 → RFC
- **Rule B**: 동일 Tag Observation 3회 → RFC

OBS는 사실만 기록한다. Architecture 제안, 판단, Decision은 금지한다.
Sub Tag와 Impact는 검색 메타데이터로만 쓰며 Governance 판단에는 사용하지
않는다. 상세 규칙은 `docs/governance/observations/README.md` 참조.

## 현재까지 확정된 흐름 (Governance v1, 기록용)

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

Promote 이후의 구현 절차는 이 문서의 범위가 아니다. 이 흐름은 RFC-0001~
0003, ADC-0001~0003, ADR-0001의 실제 진행 방식을 그대로 기록한 것이며,
Governance v2 도입 이후에도 삭제하지 않는다.

## Governance v2 흐름 (Observation 계층 추가)

```
MVP
 ↓
Observation 축적 (OBS 문서)
 ↓
Pattern 발견
 ├── A. RT-0001 Trigger 충족 확인
 └── B. 동일 Tag OBS 3개 이상 누적
 ↓
RFC
 ↓
ADC
 ↓
ADR (Accept/Promote인 경우만)
```

이 흐름은 Governance v1을 대체하지 않는다. RFC/ADC/ADR의 정의와 절차는
그대로이며, "RFC를 언제 여는가"의 판단 근거만 MVP 하나의 단일 관찰에서
누적된 OBS 문서로 바뀐다.

## Document Numbering

- `RFC-xxxx` — Boundary Question (`docs/02_rfc/`, 현재 RFC-0001~0005)
- `ADC-xxxx` — Architecture Decision Candidate (`docs/governance/adc/`, 현재 ADC-0001~0005)
- `RT-xxxx` — Re-evaluation Trigger (`docs/governance/rt/`, 현재 RT-0001)
- `ADR-xxxx` — Architecture Decision Record (`docs/04_adr/`, 현재 ADR-0001~0005)
- `OBS-xxxx` — Observation, Governance v2 (`docs/governance/observations/`, 현재 OBS-0001~0006)

번호는 문서 종류별로 독립적으로 증가한다. RFC가 생성되었다고 반드시 ADC가
생성되는 것은 아니며, ADC가 생성되었다고 반드시 RT/ADR이 생성되는 것도
아니다. OBS 문서가 여러 개 쌓인다고 반드시 RFC가 생성되는 것도 아니다
(Pattern 판정 규칙을 충족해야 한다). 각 문서는 Governance 진행 결과에
따라 독립적으로 존재할 수 있다.

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
- **Accumulate Before Escalate (Governance v2)** — MVP 하나가 끝났다고
  자동으로 RFC를 열지 않는다. OBS 문서로 사실을 누적하고, Pattern 판정
  규칙(RT-0001 Trigger 충족 또는 동일 Tag OBS 3개 이상)을 충족한 뒤에만
  RFC를 연다.

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

## Self Review Checklist (Governance v2 추가분)

- [x] 새로운 Governance 단계를 만들었는가 — Observation은 완전히 새로운
      단계가 아니라 "RFC를 여는 시점" 앞에 붙는 축적 단계다. RFC/ADC/RT/
      ADR의 정의와 역할은 그대로 유지했다.
- [x] Observation이 판단을 포함하는가 — 아니다.
      `docs/governance/observations/README.md`의 원칙 1·2·3과
      OBS-TEMPLATE.md의 Non-Analysis 선언으로 명시했다.
- [x] Pattern 판정이 주관적 판단인가 — 아니다. RT-0001의 기존 Trigger
      재사용(규칙 A) 또는 동일 Tag OBS 3개 이상이라는 수치 기준(규칙 B)
      만 사용했다.
- [x] 기존 Governance(RFC-0001~0003, ADC-0001~0003, RT-0001, ADR-0001)와
      충돌하는가 — 아니다. 모두 그대로 유지했고, 이 문서에서 참조만
      추가했다.
- [x] Architecture Drift가 있는가 — 없음. OBS는 Jarvis OS Concept Model이나
      Development HQ Baseline에 어떤 항목도 추가하지 않는다.
