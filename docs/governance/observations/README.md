# Observations (Governance v2)

## 이 계층이 추가되는 이유

Governance v1(RFC → ADC → ADR)에서는 MVP 하나가 끝날 때마다 그 MVP의
Observation을 근거로 RFC를 열었다(RFC-0001 ← MVP-0001, RFC-0002 ←
MVP-0002). MVP 수가 늘어날수록 이 방식은 "MVP마다 RFC를 쓴다"는 패턴으로
굳어지며, 각 RFC는 단 하나의 MVP가 만든 단일 사건만 근거로 삼는다.

Governance v2는 이 지점에 **Observation 축적 계층**을 추가한다. RFC/ADC/
ADR의 정의와 절차는 그대로 유지하며, 오직 "RFC를 언제 여는가"의 앞
단계만 바꾼다.

```
MVP
  ↓
Observation 축적 (OBS 문서, 이 문서 체계)
  ↓
Pattern 발견 (아래 "Pattern 판정 규칙" 참조)
  ↓
RFC
  ↓
ADC
  ↓
ADR
```

이 계층은 기존 `docs/02_rfc/`, `docs/governance/adc/`,
`docs/governance/rt/`, `docs/04_adr/`를 대체하지 않는다. RFC-0001~0003,
ADC-0001~0003, RT-0001, ADR-0001은 그대로 유지된다. 이 문서는 그
이전 단계(무엇을 근거로 RFC를 열 것인가)만 다룬다.

## 원칙

1. **Observation은 사실만 기록한다.** 실제로 실행되었거나 실제로
   관찰된 코드/테스트 결과만 적는다. 예상이나 추측은 기록하지 않는다.
2. **판단하지 않는다.** OBS 문서는 "이래야 한다", "이것이 필요하다"
   같은 결론을 내리지 않는다. 판단은 ADC의 몫이다.
3. **Architecture를 제안하지 않는다.** API, 구조, Kernel 설계를
   제안하지 않는다. 제안은 RFC의 몫이며, RFC조차 결정하지 않고
   질문만 제기한다(기존 RFC 원칙 그대로).
4. **Pattern이 반복될 때만 RFC를 연다.** MVP 하나가 끝났다고 자동으로
   RFC를 열지 않는다. 아래 "Pattern 판정 규칙"을 충족해야 한다.
5. **기존 Governance와 충돌하지 않는다.** RT-0001이 이미 정의한
   Candidate별 Re-evaluation Trigger를 재정의하지 않고 그대로 재사용한다.
6. **Architecture Drift를 만들지 않는다.** OBS는 Jarvis OS Concept
   Model이나 Development HQ Baseline에 어떤 항목도 추가하지 않는
   순수 기록 문서다.

## Pattern 판정 규칙 (기계적 기준, 판단 아님)

Pattern은 다음 두 가지 방식 중 하나로만 성립한다. 둘 다 "판단"이 아니라
"조건 충족 여부 확인"이다.

- **A. RT-0001 연동**: 하나 이상의 OBS 문서가, `docs/governance/rt/RT-0001.md`
  에 이미 정의된 Re-evaluation Trigger(예: "Engine 수 ≥ 2", "하드코딩된
  Task 호출 체인 수 ≥ 2")가 실제로 충족되었다는 사실을 기록하면, 그
  자체가 Pattern이다. RFC는 그 OBS 문서(들)를 근거로 즉시 열릴 수 있다.
  이는 새로운 판정 기준이 아니라 RT-0001이 이미 정한 기준을 그대로
  적용하는 것이다.
- **B. 반복 관찰(RT-0001이 아직 다루지 않는 주제)**: RT-0001에 대응하는
  Trigger가 없는 주제에 대해서는, 동일한 `Tag`를 가진 OBS 문서가
  **3개 이상** 존재하고 서로 모순되지 않을 때 Pattern으로 본다. 이
  숫자(3)는 Governance v2가 도입하는 유일한 새 규칙이며, "몇 번 반복돼야
  RFC를 열 자격이 있는가"라는 절차적 기준일 뿐 Architecture 판단이
  아니다.

Pattern으로 판정된 OBS 문서(들)는 상태를 `Absorbed into RFC-XXXX`로
갱신한다. Pattern이 아직 성립하지 않은 OBS는 `Open`으로 남는다.

## 디렉토리 구조

```
docs/governance/observations/
├── README.md          (본 문서)
├── OBS-TEMPLATE.md     (신규 OBS 작성 시 복사해서 사용하는 최소 템플릿)
├── OBS-0001.md
├── OBS-0002.md
└── ...
```

## 문서 번호 체계

- `OBS-xxxx` — Observation (사실 기록 전용)
- 번호는 `docs/governance/README.md`의 Document Numbering 규칙과
  동일하게 문서 종류별로 독립 증가한다. OBS가 여러 개 쌓인다고 반드시
  RFC가 생성되는 것은 아니다(Pattern 판정 규칙을 충족해야 한다).

## Tag (주제 분류, 새 Concept 아님)

OBS 문서는 다음 5개 Tag 중 하나를 반드시 붙인다. 이 Tag는 이미
`docs/governance/adc/ADC-0001.md`가 정의한 4개 Kernel Extraction
Candidate와 "그 외" 하나를 그대로 재사용한 것이며, 새로운 분류 체계가
아니다.

- `Task Dispatcher`
- `Engine Gateway`
- `Registry`
- `Context 전달 메커니즘`
- `Other` (위 4개 Candidate에 해당하지 않는 사실. RT-0001 Trigger가
  없으므로 Pattern 판정은 §Pattern 판정 규칙 B(반복 관찰, 3개 이상)만
  적용된다)

## 최소 템플릿

`OBS-TEMPLATE.md` 참조. 필드는 다음 6개뿐이다: ID, Source, Tag, Fact,
Non-Analysis 선언, Status.

## 기존 MVP Observation 문서와의 관계

`docs/01_mvp/MVP-000X-observation.md`(기존 형식)는 계속 그대로 작성한다.
이 문서들은 특정 MVP 하나에 대한 전체 관찰 기록이다. OBS 문서는 그중
Candidate/Tag별로 재사용 가능한 사실만 뽑아 별도로 기록하는, 더 작고
누적 가능한 단위다. 하나의 MVP Observation 문서에서 여러 개의 OBS가
나올 수도 있고, 하나도 나오지 않을 수도 있다(그 MVP가 어떤 Candidate와도
무관한 사실만 남겼다면).
