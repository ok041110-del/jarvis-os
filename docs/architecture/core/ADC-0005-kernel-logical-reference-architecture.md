# ADC-0005: Kernel Logical Reference Architecture 채택 판단 (RFC-0005 후속)

## 목적

`docs/architecture/core/RFC-0005-kernel-logical-reference-architecture.md`
가 제안한 내용을 **항목별로 개별 판단**한다. 일괄 승인하지 않는다.

**이 ADC에는 다른 ADC와 다른 성격의 판단이 하나 있다.** 판단 1은
`BASELINE.md` §10 Out of Scope의 범위에 관한 것이며, **그 판단이
Reject 또는 Defer면 나머지 판단은 전부 무의미해진다.** 따라서 판단 1을
Gating Judgment로 두고 먼저 처리한다.

근거는 RFC-0005, 그리고 그 RFC가 인용한 기존 문서·코드
(`docs/01_architecture/BASELINE.md` v1.3,
`docs/architecture/core/RFC-0002`~`RFC-0004`, `ADC-0001`~`ADC-0004`,
`docs/04_adr/ADR-0002`~`ADR-0004`,
`docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md` §5,
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`docs/03_adc/ADC.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`core/execution_layer/mvp_0002/prompt_specification_builder.py`)에
실제로 기록된 사실로만 한정한다.

**이 ADC가 매 판단마다 확인하는 기준선**

| 기준선 | 내용 |
|---|---|
| B-1 | RFC-0002 §15의 미결 3개 책임(Task 전달·Capability 탐색·Engine 호출)을 닫지 않는다. |
| B-2 | `BASELINE.md` §13.6·§14.7의 Defer 8건을 해제하지 않는다. |
| B-3 | Kernel ADC-0001의 Module 판단(2 Accept / 3 Defer)을 뒤집지 않는다. |
| B-4 | **Kernel Component Architecture를 열지 않는다.** |

---

## 판단 1 (Gating). `BASELINE.md` §10의 "Kernel Architecture"가 무엇을 배제하는가

### Evidence

**§10의 문언 (v1.0부터 변경 없음)**

```
- Kernel Architecture
- Component Design (Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)
```

두 항목은 **별도의 불릿**이다. 후자가 전자의 설명이 아니다 — RFC-0005
§0이 이 사실을 스스로 인정했다.

**`GOVERNANCE-REVIEW-0001-post-adc-0001.md` §5의 근거 6개를 개별
재확인한 결과** (연구자가 원문에서 직접 확인):

| §5의 근거 | 무엇에 대한 판단인가 | 2026-08 현재 |
|---|---|---|
| §10이 Out of Scope로 남겨 둠, "아직 뒤집힌 적이 없다" | **절차** | 유효. 뒤집으려면 절차가 필요하다 |
| 5개 Module 중 3개(Workflow/Memory/Event Bus) Defer | **Component 통합** | 유효. 3개 모두 Defer 유지 |
| ADC-02(Runtime 개념의 존폐) Open, NOW | **Component 존폐** | 유효. `docs/03_adc/ADC.md`에서 여전히 Open |
| Kernel 방향으로 승격된 대상이 없음 | **Component 승격** | 유효 |
| Engine Gateway Trigger("Engine 수 ≥ 2") 미충족 | **Component 필요성** | 유효. Engine 호출 0회 |
| Execution Result(6번째 Artifact) 미설계 | Execution Layer 완결성 | 유효 |

**6개 전부 지금도 유효하다.** 그리고 6개 중 5개는 Component 수준
판단이며, 어느 것도 "이미 결정된 Context 책임들이 어떤 순서로
이어지는가"에 대한 것이 아니다.

**§5 이후 Context 영역에서 결정된 것**: Baseline §13 전체(v1.2),
§14 전체(v1.3). ADC-0003 10개 판단, ADC-0004 9개 판단을 거쳤다.

**ADC 채택 기준** (`ARCHITECTURE_GOVERNANCE.md`): "지금 결정하지 않으면
상위 Architecture를 진행할 수 없다" 또는 "결정이 늦어질수록 되돌리는
비용이 매우 커진다" 중 하나를 만족해야 한다.

### 검토한 반론 (기록)

- **"§10을 문언 그대로 읽으면 Logical Reference Architecture도
  배제된다"** — 그 읽기가 옳다. RFC-0005 §0이 그것을 인정했고, 이
  ADC도 인정한다. **따라서 이 판단은 "해석"이 아니라 "범위 변경"이다.**
  해석으로 처리하면 절차를 우회하는 것이 되므로, ADR을 통한 §10 문언
  변경으로 다룬다.
- **"ADC-0002 판단 4가 이미 같은 일을 하지 않았는가"** — 성격이
  다르다. ADC-0002 판단 4는 §10을 **건드리지 않은 채** "Kernel 정의는
  Architecture 설계가 아니다"로 통과시켰다. 이번은 그 우회가 불가능하다
  — 배선도는 §10이 말하는 "Architecture"에 문언상 해당한다. **그래서
  이번에는 §10 자체를 바꾸는 것으로 다룬다.** 이 차이를 기록한다.
- **"경계를 한 번 조정하면 다음 단계에서 또 조정을 요구하게 되지
  않는가"** — 실재하는 위험이다. 다음 단계(Kernel API)는 §10의
  "Implementation" 항목과 맞닿는다. **이 ADC는 그 다음 단계를 미리
  허가하지 않는다** — API 단계가 §10과 충돌하는지는 그때 별도로
  판단되어야 하며, 이번 Accept를 선례로 삼아 자동 통과시켜서는 안
  된다. 이 문장을 Accept 조건에 포함한다.
- **"Component Architecture를 열지 않는다는 보장이 있는가"** —
  RFC-0005는 C-3(어떤 Component도 명명하지 않는다)을 스스로 부과하고
  §7에서 점검했다. 이 ADC가 판단 2~7에서 그 충족 여부를 개별
  재확인한다. 나아가 §10의 변경 문언에 **"Kernel Component
  Architecture"를 명시적으로 남기는 것**을 Accept 조건으로 삼는다.

### Decision

**Accept** (아래 4개 조건을 전부 충족하는 경우에 한한다)

1. **§10의 "Kernel Architecture" 항목을 "Kernel Component
   Architecture(Component의 존재·설계·상호작용 구조)"로 바꾼다.**
   삭제가 아니라 **한정**이다. Component Architecture는 계속 Out of
   Scope다(B-4).
2. **여는 범위는 "이미 Baseline에 결정된 책임들의 논리적 연결"로
   한정한다.** 결정되지 않은 책임의 배선은 열리지 않는다.
3. **이번 Accept를 다음 단계의 선례로 삼지 않는다.** Kernel API가
   §10의 "Implementation"과 충돌하는지는 별도 판단 대상이다.
4. **RFC-0005의 C-1~C-3(새 책임·Model 요소·Component 없음)이 실제로
   충족되었음이 판단 2~7에서 확인되어야 한다.** 확인되지 않으면 이
   Accept의 전제가 무너진다.

### Decision Rationale

ADC 채택 기준 1을 만족한다 — **다음 단계(Kernel API)를 배선 없이
설계하면 인터페이스의 형태에서 배선이 역산되며, 그것은 KP-1이 고정한
인과 방향("Kernel은 구현 객체가 아니라 책임 경계다")을 뒤집는다.**
이 프로젝트는 RFC-0002 §12.1(Cache는 결과이지 목적이 아니다),
RFC-0004 §0(계약이 위, API가 아래)에서 같은 방향 규칙을 두 번
적용했다. 배선을 건너뛰면 세 번째 적용이 무너진다.

`GOVERNANCE-REVIEW-0001` §5의 "아직 아니다"는 판단은 **뒤집히지
않는다.** 그 6개 근거는 Component Architecture에 대한 것이고, 조건
1이 그 영역을 그대로 Out of Scope로 남긴다. 이 Accept가 여는 것은
§5가 판단 대상으로 삼지 않았던 영역이다.

Freeze 원칙("지금 결정할 것과 나중에 결정할 것이 명확히 구분되고
추적되는 상태")에 비추어도, §10이 하나의 항목으로 두 가지 다른 것을
가리키던 상태를 나누는 것은 구분을 **더 명확하게** 만든다.

### Risks

- **경계 조정의 선례가 만들어진다.** 조건 3이 이를 문서로 막을 뿐,
  구조적으로 막지는 못한다. 다음 단계에서 "ADC-0005도 §10을
  조정했다"는 논거가 나올 수 있으며, 그때 이 조건 3이 인용되어야
  한다.
- **§10은 v1.0부터 5건의 외부 인용을 갖는다**(RFC-0001 2건,
  GOVERNANCE-REVIEW-0001 1건, ADC-0002 2건). 문언이 바뀌면 그 인용들이
  가리키는 내용이 미묘하게 달라진다. 인용 처리 방식은 ADR에 위임한다.
- `GOVERNANCE-REVIEW-0001` §5의 6개 근거가 **전부 유효한 상태에서**
  범위를 여는 것이다. 그 근거들이 Component Architecture에 대한
  것이라는 이 ADC의 독해가 틀렸다면, 이 Accept는 근거를 잃는다.

### Next Step

**ADR Required**

---

## 판단 2. Responsibility Flow — 6개 단계 (RFC-0005 §2)

### Evidence (단계별 — C-1 검증)

| 단계 | Baseline 상의 출처 | 새 책임인가 |
|---|---|---|
| ① Collect | §13.2 수집 | **아니오** |
| ② Merge | §13.2 병합 | **아니오** |
| ③ Validate | §13.2 검증 | **아니오** |
| ④ Order | §13.2 정렬 | **아니오** |
| ⑤ Assemble | §13.3 | **아니오** |
| ⑥ Render | §13.4 | **아니오** |

**C-1 충족 확인**: 6개 단계 전부 Baseline v1.3에 이미 존재하는
책임이다. RFC-0005가 새로 도입한 것은 **단계가 아니라 단계 사이의
순서**뿐이다.

각 단계의 "하지 않는 것" 열도 전부 기존 출처가 있다 — CM-4(해석
금지), §13.2(요약 금지), A-1·A-2(변경·증감 금지), R-2·R-4(정본
불변·내용 무생성).

### 검토한 반론 (기록)

- **"순서를 정하는 것 자체가 새 결정 아닌가"** — 맞다. 그것이 이
  RFC의 내용이며, 판단 2b에서 별도로 다룬다. 판단 2는 **단계 목록**에
  대한 것이다.
- **"6개가 아니라 4개(§13.2) + 1개(§13.3) + 1개(§13.4)로 흩어져 있던
  것을 한 줄로 세우면 없던 구조가 생기지 않는가"** — 생기는 것은
  구조가 아니라 **가시성**이다. 세 절에 흩어져 있어도 ⑤가 ①~④의
  결과를 받는다는 것은 §13.3("검증되고 정렬된 Segment 열을 하나의
  값으로 확정")에 이미 쓰여 있었다.

### Decision

**Accept** (①~⑥)

### Decision Rationale

새 책임이 하나도 없으므로 새 commitment가 발생하지 않는다. 이 목록은
Baseline v1.2·v1.3이 세 절에 나눠 기록한 것을 한자리에 모은 것이다.

### Next Step

**ADR Required**

---

## 판단 2b. 단계 간 순서 진술 (RFC-0005 §2.3)

### Evidence

- §13.2 병합 규칙: *"같은 Identifier + 다른 Content는 **오류**다."*
- 이 오류는 두 Source의 Segment를 나란히 놓은 뒤에만 판정 가능하다 —
  병합을 시도하지 않고 이 검증을 수행할 방법이 없다.
- G-6(No Silent Failure)는 그 오류가 드러날 것을 요구한다.
- §13.3 A-2: *"Segment가 조용히 추가되거나 사라지지 않는다."*
- §13.3은 Assembly의 입력을 "검증되고 정렬된 Segment 열"로 이미
  서술했다.
- **§13.2는 4개 책임의 실행 순서를 말하지 않았다** — 이 공백이 이번
  판단의 대상이다.

### 검토한 반론 (기록)

- **"배선도가 ②Merge → ③Validate로 그린 것이 순서를 고정하는가"** —
  RFC-0005 §2.3이 스스로 이를 구분했다: 계약이 요구하는 것은 **"검증은
  ⑤Assemble 이전에 완료된다"** 하나뿐이며, 배선도의 ②→③ 배치는
  가능한 배치 하나의 예시다. 구체 배치는 H-2(Builder 내부 구조,
  Hidden)에 속한다.
- **"그렇다면 Accept 대상은 무엇인가"** — 최소 진술 하나다. 배선도의
  구체 배치는 Accept 대상이 아니다.

### Decision

**Accept** (최소 진술 하나에 한정)

Accept되는 것: **"검증은 Assemble 이전에 완료되어야 한다."**

Accept되지 **않는** 것:

- ②Merge → ③Validate라는 구체적 배치 — **예시**로만 남는다.
- 검증이 몇 번 일어나는가, 어느 검사가 어느 지점에 놓이는가 —
  H-2(Hidden).

### Decision Rationale

최소 진술은 §13.2 병합 규칙과 G-6·A-2에서 **도출**된다. Assemble이
검증되지 않은 입력을 받으면 G-6이 성립할 수 없고, §13.3이 이미
Assembly 입력을 "검증되고 정렬된" 것으로 서술했다.

구체 배치까지 Accept하면 Builder 내부 구조를 고정하게 되어 H-2(Hidden)와
IN-1(단계는 구현 단위가 아니다)을 동시에 침해한다.

### Next Step

**ADR Required**

---

## 판단 3. Kernel 경계선의 배치 (RFC-0005 §2.4)

### Evidence

| 배치 | 근거 |
|---|---|
| Source 선언·Content 제공 = 밖(HQ) | §13.5, §14.2 PR-1의 "제공 ≠ 내용 마련", CM-4 |
| Ordering Policy 선택 = 밖 / 구현은 주입 | §13.2(Policy는 입력), X-2, H-1 |
| ①~⑤ = 안 | §13.2·§13.3 |
| Kernel Context = 안에서 생성되어 밖으로 나감 | §14.2 PR-1 |
| Renderer = 계약은 안, 구현은 교체 가능 | §14.2 PR-4, §14.4 3층 구분, §14.5 X-1 |
| Output = 밖 | §13.4 |

전부 Baseline v1.3에 이미 있는 배치이며, 이 절은 그것을 하나의
그림으로 옮겼다.

### 검토한 반론 (기록)

- **"⑥Render를 '경계 위에 걸친 단계'로 그리는 것이 새 개념인가"** —
  §14.4가 이미 3층 구분(교체 가능성 = Public / 계약 = Public / 구현
  = Hidden)을 확정했다. "경계 위에 걸침"은 그 3층을 그림으로 옮긴
  표현이며 새 개념이 아니다. 다만 **표현 자체는 이 RFC가 처음
  쓰므로** 신규 표현으로 표시한다.

### Decision

**Accept**

### Decision Rationale

경계 배치는 §13.5·§14.2·§14.4가 이미 결정한 것의 도식화다. 경계선을
그리는 일 자체가 새 경계를 만들지 않는다 — 오히려 흩어져 있던 배치를
한 그림에서 검증 가능하게 만든다.

### Next Step

**ADR Required**

---

## 판단 4. Data Flow (RFC-0005 §3)

### Evidence — C-2 검증

- RFC-0005 §3.1이 **"이것은 새 Model 요소가 아니다"**를 절 첫머리에
  명시했다. 6개 이름(수집된 Segment들 / 중복 제거된 집합 / 검증된
  집합 / 순서가 부여된 열 / Kernel Context / 표현)은 동일한 데이터가
  거쳐가는 **논리적 상태**다.
- 그중 실제 Model 요소는 **Kernel Context 하나뿐**이며(§13.1), 나머지
  5개는 §13.1에 등재되지 않는다.
- §3.3(1) Content 불변: A-1 + R-4 + §13.2 병합 규칙이 각 구간을 덮는다.
  선례로 Execution Layer 5개 Builder 전부가 "Wrap, not rewrite"였다
  (`ARTIFACT-STANDARD-v1.md`).
- §3.3(2) 단방향: §13.4가 "역방향(Prompt → Context)은 정의하지
  않는다"를 이미 확정했다.
- §3.4 영속화 없음: N-4(Memory Service Non-Goal), G-7(Context 경로
  Stateless).

### 검토한 반론 (기록)

- **"논리적 상태에 이름을 붙이면 결국 Model이 6개로 늘어난 것과
  같지 않은가"** — 다르다. 판별 기준은 **"그것이 §13.1에 등재되어
  Kernel이 관리하는 대상이 되는가"**다. 5개 중간 상태는 어느 것도
  Identifier·Metadata·Source를 갖지 않으며, 단계 사이에서만 존재하고
  외부에 노출되지 않는다(PR-1은 Kernel Context만 반환한다). Accept
  조건으로 **"§13.1의 Model은 5개 요소 그대로이며 이 표가 그것을
  확장하지 않는다"**는 문장을 함께 기록한다.
- **"§3.3(1)의 'Content는 한 글자도 바뀌지 않는다'가 Render에도
  적용되는가"** — R-4는 "Renderer가 덧붙이는 것은 고정된 구조 틀
  뿐이며 Context에 없는 내용을 만들어내지 않는다"이다. 즉 Renderer는
  **틀을 덧붙일 수 있다.** RFC-0005 §3.3의 진술은 "Content를 **쓰지**
  않는다"이지 "출력 길이가 같다"가 아니다. 이 구분이 유지되어야 한다.

### Decision

**Accept** (아래 조건 포함)

- **"5개 중간 상태는 §13.1의 Model 요소가 아니다"**를 명시한다.
- **Render 단계의 Content 불변은 "Content를 쓰지 않는다"는 뜻이며,
  R-4가 허용한 고정 구조 틀의 추가를 금지하지 않는다**를 명시한다.

### Decision Rationale

Data Flow는 새 데이터 타입을 만들지 않고, 이미 결정된 보장들
(A-1·R-4·G-2·G-1·G-5·G-6)이 흐름의 어느 구간을 덮는지를 대응시킨다.
그 대응이 있어야 "이 단계에서 무엇이 보장되는가"를 말할 수 있다.

### Next Step

**ADR Required**

---

## 판단 5. Responsibility Relationship 및 RR-1 ~ RR-3 (RFC-0005 §4)

### Evidence

- **명칭 변경(Component → Responsibility)**: KP-1(*"Kernel은 구현
  객체가 아니라 책임 경계다"*), §11(*"구현으로 정의하지 않는다. 책임으로
  정의한다"*)이 근거다. RFC-0005 §4.1이 변경 사실과 이유를 기록했다.
- RR-1(역방향 의존 금지): §13.4(역방향 미정의) + G-1.
- RR-2(단계 건너뛰기 금지): G-6 + A-2 + 판단 2b.
- RR-3(공유 가변 상태 금지): G-1 + G-7. 공유 가변 상태가 있으면 같은
  입력에 다른 결과가 나올 수 있어 G-1이 직접 깨진다.

### 검토한 반론 (기록)

- **"요청은 Component Relationship이었는데 바꾼 것이 임의적인가"** —
  아니다. Builder/Assembly/Validation/Renderer를 Component로 다루면
  그것들이 별개의 객체·모듈·서비스여야 한다는 전제가 생기고, 그 전제는
  구현 결정이자 판단 1이 유지하기로 한 B-4(Component Architecture
  비개방)를 침해한다. **다루는 내용은 그대로이고 이름만 바뀐다.**
- **"RR-3은 구현 제약 아닌가"** — 경계에 있다. 그러나 RR-3이 없으면
  G-1(Deterministic)을 보장할 수 없다 — 공유 가변 상태는 결정론을
  깨는 가장 흔한 경로다. **구현 방법을 규정하지 않고 결과만 금지**하는
  형태이므로 계약 수준 진술로 성립한다.

### Decision

**Accept** (명칭 변경 포함, RR-1 ~ RR-3)

### Decision Rationale

RR-1~RR-3은 전부 기존 보장(G-1·G-6·G-7·A-2·§13.4)에서 도출되며 새
제약을 만들지 않는다. 명칭 변경은 KP-1을 지키기 위한 것이고, 내용의
손실이 없다.

### Next Step

**ADR Required**

---

## 판단 5b. RR-4 (Render가 정렬에 관여하지 않는다)

**RFC-0005 §4.3·§7이 스스로 "기존 제외 결정과 겹친다"고 표시한
항목이다.**

### Evidence

- ADC-0003 판단 5는 R-3("Renderer는 Segment 순서를 재배치하지
  않는다")을 **Accept 범위에서 제외**했다. 이유는 Execution Layer
  MVP-0002 `RENDERING_MAP`이 실제로 9개 절을 5개 절로 재배치하며,
  그것을 금지하면 코드 재설계를 요구하게 되기 때문이었다.
- `BASELINE.md` §13.4의 각주가 이 제외를 "누락이 아니라 의도적
  제외"로 기록하고 있다.
- **`core/execution_layer/mvp_0002/prompt_specification_builder.py`는
  Kernel Renderer가 아니다** — Kernel Context를 입력으로 받지 않고,
  Execution Request(Execution Layer의 Canonical Artifact)를 받는다
  (연구자가 소스에서 직접 확인). Kernel Context Model이 존재하기 이전에
  작성된 코드다.
- **Kernel Renderer는 현재 0개다**(ADC-0004 판단 5b: Renderer는 0개).
- O-4: *"순서 규칙은 Policy로 명시되며 코드에 암묵적으로 흩어지지
  않는다."*

### 검토한 반론 (기록)

- **"RR-4를 Accept하면 R-3 제외 결정을 뒤집는 것 아닌가"** — 적용
  대상이 다르다. R-3은 **Execution Layer의 기존 Builder**에 대한
  요구였고, RR-4는 **Kernel Reference Architecture 안의 ⑥Render**에
  대한 진술이다. 현재 ⑥에 해당하는 구현체는 0개이므로, RR-4는 어떤
  기존 코드도 위반 상태로 만들지 않는다.
- **"그래도 훗날 Execution Layer를 Kernel에 맞출 때 같은 문제가
  돌아오지 않는가"** — 돌아온다. 그때 R-3 질문이 다시 열린다. **이
  ADC는 그 질문을 열지도 닫지도 않는다** — R-3은 ADC-0003 판단 5의
  상태 그대로 "Accept되지도 Reject되지도 않은" 채 남는다.
- **"RR-4가 없으면 무엇이 깨지는가"** — O-4가 깨진다. Render가 순서에
  관여하면 순서 규칙이 Ordering Policy와 Renderer 두 곳에 흩어지고,
  G-2(Stable Ordering)를 어느 한 곳에서 검증할 수 없게 된다.

### Decision

**Accept** (적용 범위를 한정하는 조건부)

1. **RR-4는 Kernel Reference Architecture의 ⑥Render에만 적용된다.**
2. **Execution Layer의 기존 Builder를 판정하지 않는다.** 이 ADC는
   `prompt_specification_builder.py`가 RR-4를 위반한다고 판단하지
   않는다 — 그것은 Kernel Renderer가 아니다.
3. **R-3의 상태를 변경하지 않는다.** ADC-0003 판단 5의 제외는 그대로
   유지된다.

### Decision Rationale

RR-4는 O-4의 직접적 귀결이다 — 순서 규칙이 두 곳에 흩어지면 O-4가
성립하지 않는다. 적용 대상이 존재하지 않는 것(Kernel Renderer 0개)이
문제가 아니라, **앞으로 만들어질 Renderer가 지켜야 할 조건을 미리
명시하는 것**이 Reference Architecture의 역할이다.

조건 2·3이 없으면 이 Accept는 ADC-0003 판단 5를 우회하는 것이 된다.
조건과 함께여야만 성립한다.

### Risks

Execution Layer가 훗날 Kernel Context를 사용하도록 정렬되면, 그
시점에 `RENDERING_MAP`이 RR-4와 충돌하는지를 판단해야 한다. 이 ADC는
그 시점을 정하지 않고, 그 판단을 예단하지도 않는다.

### Next Step

**ADR Required**

---

## 판단 6. Extension Flow (RFC-0005 §5)

### Evidence

- §14.5가 X-1~X-4를 확정했으나 **흐름상의 위치는 기록하지 않았다.**
- X-3 = ①의 입력: §13.2("어떤 Source를 볼지는 호출자가 정한다"),
  §14.5(X-3은 입력 경계).
- X-2 = ④의 입력: §13.2("Ordering Policy는 Builder의 입력").
- X-1 = ⑥의 자리: §13.4, §14.5.
- X-4 = 흐름 밖(Model): §14.5(X-4는 "확장이 들어올 자리의 표시").
- §5.1의 핵심 진술("확장 지점은 단계의 개수나 순서를 바꾸지 않는다")은
  위 4개 배치에서 도출된다 — 전부 입력이거나 자리이지 단계가 아니다.

### 검토한 반론 (기록)

- **"§5.2가 4-Layer를 언급하는 것이 B-2를 침식하는가"** — RFC-0005
  §5.2가 *"4-Layer는 여전히 Defer이며, 이 RFC는 그것이 확정될 것이라고
  말하지 않는다"*를 명시했다. §14.5의 X-4 서술("확장의 예고가
  아니다")과 같은 형태다. 침식하지 않는다.
- **"확장 메커니즘이 여전히 Defer인데 위치만 정하는 것이
  의미있는가"** — 있다. 위치는 계약의 일부(어느 단계의 입력인가)이고,
  메커니즘은 구현이다. 위치 없이 메커니즘을 논하는 것은 불가능하지만
  그 역은 가능하다.

### Decision

**Accept**

### Decision Rationale

4개 배치 전부 §13.2·§13.4·§14.5에서 도출되며 새 확장 지점을 만들지
않는다. §5.1의 진술(확장이 흐름을 바꾸지 않는다)은 Reference
Architecture의 안정성을 보장하는 성질이며, ADC-0003 판단 2가 Ordering
Policy를 Model 밖으로 꺼낸 결정의 귀결이다.

### Next Step

**ADR Required**

---

## 판단 7. Implementation Neutrality (RFC-0005 §6)

### Evidence

- KP-5(Implementation Agnostic), G-4(*"호출자의 Runtime·언어·저장소·
  실행 방식을 강제하지 않는다"*), `BASELINE.md` §3 "Everything is
  Replaceable"(v1.0부터 Frozen)이 이미 같은 요구를 하고 있다.
- IN-1~IN-5는 그 요구를 Reference Architecture에 적용했을 때의
  구체화다.
- §6.2의 3형태 시험(순수 함수 파이프라인 / 메시지 전달 / 서비스
  체인)은 **판정 기준**으로 제시되었고, RFC-0005가 세 형태 중 어느
  것도 채택하지 않았다.

### 검토한 반론 (기록)

- **"3형태 시험이 구현 방식을 3개로 제한하는가"** — 아니다. 시험은
  "이 셋 중 하나를 골라라"가 아니라 "셋 모두에서 성립하는가"다.
  셋에서 성립하면 그 셋에 한정되지 않는다는 근거가 된다.
- **"G-4는 관찰로 확인할 수 없다고 §14.3이 기록했는데, 3형태 시험이
  그 공백을 메우는가"** — 부분적으로 메운다. G-4 전체를 검증하지는
  못하지만, **적어도 세 실행 모델에서 계약이 유지되는지는 검토할 수
  있다.** 이는 §14.3이 "검토(Review)로만 지킬 수 있는 보장"이라고 한
  것에 실질을 부여한다.

### Decision

**Accept** (IN-1 ~ IN-5, 3형태 시험 포함)

3형태 시험은 **판정 기준**으로만 Accept한다 — 구현 계획이 아니며,
세 형태 중 어느 것도 채택되지 않는다.

### Decision Rationale

IN-1~IN-5는 KP-5·G-4·§3의 재진술이며 새 commitment가 없다. 3형태
시험은 G-4가 갖고 있던 "확인 방법 없음" 문제에 부분적 실질을 준다.

### Next Step

**ADR Required**

---

## 판단 8. Baseline 반영 범위

### Evidence

- `BASELINE.md` §Version 절: v1.3, Status Active, Architecture State
  **Frozen**.
- 판단 1이 §10 문언 변경을 Accept 조건으로 요구했다 — **이번 반영은
  새 절 추가만이 아니라 기존 절(§10) 변경을 포함한다.** ADR-0002·
  0003·0004는 전부 새 절 추가만 했으므로, 이는 선례와 다르다.
- ADR-0002 §2.1이 확립한 절 번호 정책(기존 절 번호 유지, 새 절은
  Version 앞에 삽입)은 여전히 적용 가능하다 — §10의 **번호가 아니라
  문언**만 바뀌기 때문이다.

### Decision

**Accept** (반영 범위를 한정하는 조건부)

Baseline에 반영할 것:

1. **§10 문언 변경** — "Kernel Architecture" → "Kernel Component
   Architecture", 그리고 무엇이 열렸는지를 §10 자체에 명시(판단 1
   조건 1·2)
2. Responsibility Flow ①~⑥과 각 단계의 책임(판단 2)
3. 순서 최소 진술 — "검증은 Assemble 이전에 완료"(판단 2b)
4. Kernel 경계선 배치(판단 3)
5. Data Flow와 조건 2건(판단 4)
6. Responsibility Relationship과 RR-1~RR-3(판단 5)
7. RR-4와 적용 범위 조건 3건(판단 5b)
8. Extension Flow 4개 배치(판단 6)
9. Implementation Neutrality IN-1~IN-5와 3형태 시험(판단 7)

Baseline에 반영하지 **않을** 것:

- 배선도의 ②Merge → ③Validate 구체 배치 — 예시로만(판단 2b)
- Kernel **Component** Architecture — §10에 남는다(B-4)
- Kernel API·클래스 구조·DI·Runtime — 다음 단계
- 확장 메커니즘 — ADC-0004 판단 5b Defer 유지
- §13.6·§14.7의 Defer 8건 — B-2, 그대로 유지
- RFC-0002 §15의 미결 3개 책임 — B-1
- R-3의 상태 변경 — 판단 5b 조건 3

### Decision Rationale

반영되는 것은 **이미 결정된 책임들의 연결**이며, 새 책임·Model 요소·
Component가 아니다(판단 2·4·5에서 개별 확인). §10 변경은 판단 1이
요구한 조건이며, 변경 후에도 Component Architecture는 Out of Scope로
남는다.

### Risks

- Baseline 버전 갱신(v1.3 → v1.4)이 필요하다.
- **§10 문언 변경은 이 프로젝트에서 Frozen 절의 기존 문장을 바꾸는
  첫 사례다.** ADR-0002·0003·0004는 새 절 추가만 했다. 이 선례가
  향후 "Frozen 문장도 바꿀 수 있다"는 논거로 오용될 수 있으며, ADR이
  변경 범위를 최소로 한정해야 한다.
- 이번 판단이 다시 8건의 "ADR Required"를 발생시킨다.

### Next Step

**ADR Required**

---

## 종합

| 판단 항목 | Decision | Next Step |
|---|---|---|
| **1 (Gating). §10 범위 한정** | **Accept** (조건 4건) | ADR Required |
| 2. Responsibility Flow ①~⑥ | **Accept** | ADR Required |
| 2b. 순서 진술 | **Accept** (최소 진술만) | ADR Required |
| 3. Kernel 경계선 배치 | **Accept** | ADR Required |
| 4. Data Flow | **Accept** (조건 2건) | ADR Required |
| 5. Responsibility Relationship, RR-1~RR-3 | **Accept** | ADR Required |
| 5b. RR-4 | **Accept** (적용 범위 조건 3건) | ADR Required |
| 6. Extension Flow | **Accept** | ADR Required |
| 7. Implementation Neutrality | **Accept** | ADR Required |
| 8. Baseline 반영 범위 | **Accept** (범위 한정) | ADR Required |

10개 판단 전부 Accept이며, 그중 5개가 조건부다. **이번 ADC에는 Defer가
없다** — 이는 이례적이므로 이유를 기록한다: RFC-0005는 새 결정을 거의
제안하지 않고 **이미 내린 결정들의 연결**을 제안했다. 연결할 대상이
이미 Accept된 것들이므로 Defer할 미결 요소가 적었다. 실제로 판단
2b·4·5b·8에서는 **Accept 범위를 축소**하는 방식으로 조정이 이루어졌다.

Reject나 Out of Authority로 분류된 항목은 없다. 다만 다음 3건은
Accept 범위에서 **제외**되었다.

- 배선도의 ②→③ 구체 배치(판단 2b) — 예시로만 남는다
- Execution Layer 기존 Builder에 대한 RR-4 적용(판단 5b)
- R-3의 상태 변경(판단 5b)

### 기준선 4건 최종 확인

| 기준선 | 확인 결과 |
|---|---|
| B-1 (RFC-0002 §15 미결 3개 책임) | **Pass.** 어떤 판단도 Task 전달·Capability 탐색·Engine 호출을 다루지 않았다. |
| B-2 (Defer 8건 유지) | **Pass.** 판단 6이 4-Layer Defer 유지를 확인했고, 판단 8이 확장 메커니즘 Defer를 반영 대상에서 제외했다. |
| B-3 (Kernel ADC-0001 Module 판단) | **Pass.** 판단 1이 §5의 Module Defer 3건을 근거로 인용하되 뒤집지 않았다. |
| B-4 (Component Architecture 비개방) | **Pass.** 판단 1 조건 1이 §10에 "Kernel Component Architecture"를 남기고, 판단 5가 Component 명명을 회피했다(명칭 변경). RFC-0005 C-3 충족을 판단 2·5에서 확인했다. |

## Self Review

- Evidence만 사용했는가 — **Pass**. GOVERNANCE-REVIEW-0001 §5의 근거
  6개, §10의 문언, ADC-0003 판단 5의 R-3 제외 근거,
  `prompt_specification_builder.py`의 입력 타입은 전부 원문·소스에서
  직접 확인했다.
- 일괄 승인했는가 — **아니오**. 10개 판단으로 분리했고, 5개가 조건부
  Accept이며 3건이 Accept 범위에서 제외되었다.
- **§10을 해석으로 우회했는가** — **아니오**. 판단 1이 "이것은 해석이
  아니라 범위 변경"임을 명시하고, ADR을 통한 문언 변경으로 처리하도록
  했다. RFC-0005 §0도 같은 인식을 문서 첫 절에 두었다.
- Kernel Readiness 평가를 무력화했는가 — **아니오**. 판단 1이 §5의
  근거 6개가 **전부 지금도 유효함**을 인정한 위에서, 그 6개가 Component
  수준 판단이라는 독해로 범위를 좁혔다. 그 독해가 틀렸다면 Accept가
  근거를 잃는다는 사실도 Risks에 기록했다.
- 다음 단계를 미리 허가했는가 — **아니오**. 판단 1 조건 3이 "이번
  Accept를 API 단계의 선례로 삼지 않는다"를 명시했다.
- 새 책임·Model 요소·Component가 생겼는가 — **아니오**. 판단 2가
  C-1을, 판단 4가 C-2를, 판단 1 조건 4와 판단 5가 C-3을 개별
  확인했다.
- 기존 제외 결정을 우회했는가 — **아니오**. 판단 5b가 R-3의 상태를
  변경하지 않는 것을 Accept 조건으로 삼았다.
- 요청과 다르게 처리한 것을 기록했는가 — **Pass**. 판단 5가 "Component
  Relationship → Responsibility Relationship" 명칭 변경의 이유와
  내용 동일성을 기록했다.
- 구현을 제안했는가 — **아니오**. 판단 7이 3형태 시험을 판정 기준으로만
  Accept하고 어느 형태도 채택하지 않았다.
- ADR을 작성했는가 — **아니오**. 이 ADC는 ADR이 필요하다는 판정만
  내렸다.
