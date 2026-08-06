# ADC-0002: Kernel Definition 채택 판단 (RFC-0002 후속)

## 목적

`docs/architecture/core/RFC-0002-kernel-definition.md`가 제안한 4개
사안을 **개별적으로** 판단한다. 일괄 승인하지 않는다.

1. Kernel Design Principles(KP-1~KP-6) 채택 여부
2. Kernel Context Architecture(RFC-0002 §12) 채택 여부
3. Core → Kernel 용어 통합 여부
4. RFC-0002를 Baseline Proposal로 채택할지 여부

근거는 RFC-0002, 그리고 그 RFC가 인용한 기존 문서
(`docs/01_architecture/BASELINE.md`, `development-hq/BOUNDARY.md`,
`docs/governance/adc/ADC-0001`·`ADC-0004`,
`docs/architecture/core/RFC-0001`·`ADC-0001`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`docs/core/execution-layer/MVP-0001~0005-*`,
`docs/research/EVIDENCE-REVIEW-0001.md`,
`docs/governance/rt/RT-0001.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md`)에
실제로 기록된 사실로만 한정한다. 새로운 Evidence를 만들지 않는다.

각 판단의 Decision은 **Accept / Defer / Reject / Out of Authority**
중 하나다.

---

## 판단 1. Kernel Design Principles(KP-1~KP-6) 채택 여부

KP는 6개이므로, Kernel ADC-0001이 5개 Module을 개별 판단한 선례에 따라
각 원칙의 근거를 개별적으로 확인한 뒤 하나의 Decision을 낸다.

### Evidence (원칙별)

| 원칙 | 근거 확인 결과 |
|---|---|
| KP-1 Responsibility over Component | **기존 사실의 재진술.** `docs/governance/adc/ADC-0001.md`·`ADC-0004.md`가 Task Dispatcher/Engine Gateway/Registry/Context 4개 Candidate를 모두 "Keep in MVP"로 판단했다 — 즉 Scheduler/Registry/Runtime/Memory/Event Bus 없이 MVP가 실제로 동작했다. RFC-0002 §10과 동일한 진술이며, 새 commitment를 만들지 않는다. |
| KP-2 Deterministic Context Assembly | **기존 사실의 일반화.** Execution Layer MVP-0001~0005의 5개 Builder 전부에 결정론 테스트가 존재하고 통과한다(`test_transformation_is_deterministic` 4건, `test_rendering_is_deterministic` 1건 — 연구자가 소스에서 직접 확인). `ARTIFACT-STANDARD-v1.md`가 이를 5개 Artifact 전부의 Contract로 이미 고정했다. |
| KP-3 Stable Context Ordering | **부분적 근거 있음.** Execution Layer MVP-0002가 고정 배치표(`RENDERING_MAP`)로 절 순서를 고정했고, 그 결과 서로 다른 두 Case에서 구조 오버헤드가 정확히 동일(77 글자)했음이 실측되었다(`MVP-0002-artifact-mapping.md`). 즉 "고정 순서로 조립한다"는 실천은 이미 존재하며 검증되었다. 다만 그 실천은 단일 Artifact 내부의 절 순서였고, **계층화된 Context 간의 순서 보장은 관찰된 적이 없다** — 신규인 부분은 그 일반화다. (RFC-0002 §11 KP-3은 이 Consistency Review 결과를 반영해 같은 구분을 담도록 갱신되었다.) |
| KP-4 Stable Context by Design | **신규. 단, commitment는 방어적이다.** 이 원칙이 요구하는 것은 "결정론적이고 안정적이며 재사용 가능한 Context 구조"뿐이며, 특정 벤더 기능을 위해 무언가를 만들 것을 요구하지 않는다 — 오히려 Prompt Caching 같은 최적화를 **설계의 목적이 아니라 결과**로 못박는다. 이 원칙의 실질적 기능은 인과 방향을 고정해 벤더 종속을 차단하는 것이며, 이는 이미 Frozen인 `BASELINE.md` §3 "Engine Independent"와 같은 방향이다. (명칭은 Consistency Review 결과 `Cache-aware by Design` → `Stable Context by Design`으로 확정되었다.) |
| KP-5 Implementation Agnostic | **기존 사실의 재진술.** `BASELINE.md` §3 "Engine Independent"·"Everything is Replaceable"이 v1.0부터 Frozen이다. Execution Layer MVP-0003이 실제 코드로 이를 지켰다 — `target_engine`을 고정 placeholder로 두고 실제 모델명 부재를 테스트로 검증(`test_target_engine_is_a_placeholder_not_a_real_model_name`, 연구자가 소스에서 직접 확인). |
| KP-6 Stateless Responsibility Boundary | **기존 사실의 재진술.** `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` §6이 "Stateless Interface"를 이미 Design Principle로 명시했다. MVP-0003~0005는 `request_id`/`created_at`/`handle_id`/`submitted_at`/`state`/`changed_at`을 전부 호출자 주입으로 남겨 시계·난수·상태 결정 로직을 두지 않았다. |

### 검토한 반론 (기록)

- **KP-6 vs. Execution State(MVP-0005) 충돌 가능성**: Execution State는
  이름 그대로 상태 Artifact이므로 "Stateless" 원칙과 충돌하는 것처럼
  보일 수 있다. 실제로는 충돌하지 않는다 — KP-6이 금지하는 것은
  "Kernel이 구현체의 내부 상태를 강제하는 것"이고, Execution State는
  Kernel이 관리하는 내부 상태가 아니라 호출자가 값을 주입해 만드는
  Artifact다(MVP-0005는 `state`/`changed_at`/`handle_id` 셋 다 호출자
  주입으로 구현했다). 이 점을 확인했으므로 KP-6은 기존 구현과
  모순되지 않는다.
- **KP-2가 Working/Ephemeral Layer와 충돌하는가**: 충돌하지 않는다.
  KP-2는 "동일한 입력 → 동일한 Context"이며, 입력이 달라지는 Layer가
  있다는 사실과 양립한다.

### Decision

**Accept** (KP-1~KP-6 전부)

### Decision Rationale

6개 중 4개(KP-1·2·5·6)는 이미 Frozen된 Baseline 진술이거나 Execution
Layer에서 실측 검증된 성질의 재진술·일반화이며, 채택해도 새로운
commitment가 발생하지 않는다. KP-3은 RFC-0002가 "신규"로 표시했으나
MVP-0002의 고정 배치표 실측이 이미 그 실천을 뒷받침한다. KP-4는 유일한
순수 신규 항목이나, 그 문언 자체가 "특정 벤더 기능을 위해 설계하지
않는다"는 **제약**이지 무언가를 만들라는 **요구**가 아니므로, 이
프로젝트가 경계해 온 "필요할 것 같다는 이유로 구조를 미리 만드는
것"에 해당하지 않는다.

원칙 채택은 Component 구축과 다르다 — Kernel ADC-0001이 Workflow/Memory/
Event Bus를 Defer한 이유는 "그 Module을 지금 만들 근거가 없다"는
것이었지, "그 방향이 틀렸다"는 것이 아니었다. KP-1~KP-6은 어떤
Component도 만들지 않으며, 오히려 만들지 않을 조건(KP-1)과 만들 때
지켜야 할 제약(KP-2~KP-6)을 규정한다.

### Risks

KP-3·KP-4는 아직 실제 Model 호출을 한 번도 하지 않은 상태에서
채택된다(RFC-0005 §1: MVP-0005~0013 전 구간 LLM/ML 호출 없음). 실제
Engine 연동이 시작된 뒤 "안정적인 순서"가 실측상 무의미하거나 다른
형태여야 한다는 관찰이 나오면, 두 원칙은 재검토 대상이 된다. 이
Accept는 "이 원칙들이 영구히 옳다"가 아니라 "지금 하위 설계의 참조
기준으로 삼을 만하고, 채택 비용이 없다"는 판단이다.

### Next Step

**ADR Required** — 최상위 설계 원칙으로 채택하려면 Baseline에 기록되어야
한다.

---

## 판단 2. Kernel Context Architecture(RFC-0002 §12) 채택 여부

§12는 성격이 다른 두 내용을 담고 있으므로 분리해 판단한다.

- **2a**: 4개 Context 책임(Stable Prefix / Context Boundary / Context
  Assembly / Context Ordering)을 Kernel 책임 **후보**로 채택할지.
- **2b**: 4-Layer Context Model(Immutable / Stable / Working /
  Ephemeral)을 Kernel Context Model로 **확정**할지.

### 2a. 4개 Context 책임을 Kernel 책임 후보로 채택

#### Evidence

- RFC-0002 §15는 이 4개를 이미 "Kernel에 속하는지 아닌지를 RFC를 통해
  하나씩 판단할" 8개 책임 목록에 포함시켰다 — 즉 확정이 아니라 판단
  대상으로 제시했다.
- `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` §4.4는
  이미 "Context 전달 책임"을 Execution Layer/Kernel 책임으로 인용했고,
  Kernel ADC-0001은 Execution Layer를 **Accept**했다. 4개 책임은 그
  이미 Accept된 책임을 세분한 것이지, 새 책임 영역을 신설하는 것이
  아니다.
- §12.1은 이 4개 책임이 Prompt Cache에 한정되지 않고 Conversation
  Resume / Context Snapshot / Memory Restore 등에도 동일하게 쓰인다고
  기록했다 — 특정 벤더 기능에 종속된 책임이 아니다.

#### Decision

**Accept** (책임 후보 목록으로서만)

#### Decision Rationale

이 4개를 채택한다는 것은 "이것들이 향후 RFC로 판단될 Kernel 책임
후보다"라는 의미이며, 각 책임이 실제로 Kernel에 속하는지는 여전히
미결이다(RFC-0002 §15가 그렇게 설계했다). 이미 Accept된 Execution
Layer 책임의 세분이므로 새 Boundary를 만들지 않는다.

### 2b. 4-Layer Context Model 확정

#### Evidence

- `docs/research/EVIDENCE-REVIEW-0001.md` "Context 전달 방식": MVP-0005
  ~0008 네 건 모두 Context를 **단일 문자열에 이어붙이는 하나의 경로**
  로만 다뤘고, 함수 시그니처는 네 건 모두 변경되지 않았다. 계층화된
  Context가 실제로 존재한 적이 없다.
- `docs/governance/rt/RT-0001.md` Candidate 4의 재평가 Trigger("Context
  전달 경로 ≥ 2")는 EVIDENCE-REVIEW-0001 기준으로 **발동 여부조차
  확인되지 않은** 상태다.
- `docs/architecture/core/ADC-0001-core-baseline.md`는 Memory Module을
  바로 이 근거로 **Defer**했다 — "단일 경로가 Phase 1 전 구간에서 한
  번도 실패하지 않았고, 승격을 정당화할 두 번째 경로나 영속화 필요
  사례가 관찰된 적이 없다."
- RFC-0002 §14 Roadmap은 "Kernel Context Model"과 "Kernel Context
  Architecture"를 **각각 별도의 후속 RFC 단계**로 이미 배치했다 — 즉
  RFC-0002 자신도 §12를 최종 확정으로 제시하지 않았다.

#### Decision

**Defer**

#### Decision Rationale

Immutable / Stable / Working / Ephemeral이라는 특정 4단계 분류는 이
프로젝트에서 단 한 번도 관찰된 적이 없는 구조다 — 지금까지 관찰된
Context는 언제나 단일 경로의 단일 문자열이었다. 이 시점에 특정
taxonomy를 확정하는 것은 Kernel ADC-0001이 Memory Module을 Defer할 때
사용한 것과 정확히 같은 상황이며, 같은 판단이 적용되어야 한다.

RFC-0002 §14 Roadmap 자신이 "Kernel Context Model"을 별도 RFC 단계로
두었으므로, 이 Defer는 RFC-0002와 모순되지 않고 오히려 그 로드맵을
그대로 따르는 것이다. 4개 Layer는 그 RFC의 **출발 후보**로 문서에
남되, 이 ADC가 확정하지는 않는다.

#### Risks

Defer를 유지하는 동안 Kernel Context Model RFC가 열리지 않으면, 4개
책임(2a에서 Accept)은 채택되었으나 그 책임이 다룰 Context의 구조는
미정인 상태가 지속된다. 이 공백은 GOVERNANCE-REVIEW-0001 §1이 이미
기록한 "ADC는 통과했으나 후속 문서가 작성되지 않은 채 남는" 패턴과
같은 종류의 절차 부채가 될 수 있다.

#### Next Step

No ADR Required

---

## 판단 3. Core → Kernel 용어 통합 여부

### Evidence

- `development-hq/BOUNDARY.md`(Development HQ Baseline, Frozen)는
  **처음부터 "Kernel"을 사용했다**: "Kernel Scheduler의 책임",
  "Kernel Communication의 책임", "Kernel Engine Port/Adapter의 책임",
  "Kernel Registry의 책임", "Kernel Policy Engine의 책임",
  "Kernel Registry/Governance의 책임", "Kernel의 책임"(연구자가 원문
  7개 행에서 직접 확인).
- Development HQ 수준 Governance 문서 전체가 "Kernel"을 사용했다 —
  Dev HQ `RFC-0001`(제목 자체가 "Kernel Boundary"),
  `docs/governance/adc/ADC-0001.md`(제목: "Kernel Extraction Candidate
  승격 판단"), `RFC-0004`, `ADC-0004` 등.
- 반면 "Core"는 `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`
  에서 처음 도입되었다. 그 문서 §2는 Core의 위치를 "모든 HQ가 공유하는
  공통 계층"으로 정의했는데, 이는 `BOUNDARY.md`가 "Kernel"이라고
  부르던 자리와 동일하다.
- 두 용어가 서로 다른 것을 가리킨다고 명시한 문서는 존재하지 않는다.

### Decision

**Accept**

### Decision Rationale

이 통합은 새 개념을 만들거나 기존 개념을 병합하는 것이 아니라, **하나의
개념에 두 이름이 붙어 있던 상태를 원래 이름으로 되돌리는 것**이다.
"Kernel"은 Development HQ Baseline(Frozen)이 처음부터 사용한 용어이고,
"Core"는 이번 세션에서 나중에 도입된 이름이다. 더 오래되고 더 널리
쓰인 쪽, 그리고 이미 Frozen 문서에 박혀 있는 쪽을 공식 용어로 삼는
것이 문서 정합성 비용이 가장 낮다.

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 Single Source of
Truth 원칙에 비추어도, 같은 개념이 두 이름으로 추적되는 상태는
해소되어야 한다.

### Risks

용어 변경 대상 문서가 이미 커밋된 것을 포함한다
(`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`,
`ADC-0001-core-baseline.md`, 그리고 `docs/core/execution-layer/` 이하
MVP 문서 다수). 파일 경로(`docs/architecture/core/`,
`docs/core/execution-layer/`)에도 "core"가 들어 있어, 경로까지 바꿀지
문서 내용만 바꿀지 결정이 필요하다 — 이 ADC는 그 범위를 결정하지
않고 ADR에 위임한다.

### Next Step

**ADR Required**

---

## 판단 4. RFC-0002를 Baseline Proposal로 채택할지 여부

### Evidence

- `docs/01_architecture/BASELINE.md` **§Version 절**(판단 당시 §11):
  Architecture State = **Frozen**, Version = v1.0(판단 당시).
- 같은 문서 §10 Out of Scope: **"Kernel Architecture"**, "Component
  Design(Scheduler, Engine Gateway, Registry, Communication, Memory,
  Policy 등)"이 명시되어 있다.
- RFC-0002는 Kernel **Architecture**를 설계하지 않는다 — §12(아직
  결정하지 않는 것)가 Scheduler/Registry/Runtime/Memory/Event Bus/
  Engine Gateway 필요 여부를 전부 미결로 남겼고, §9의 Component 표는
  "예시일 뿐, 채택 여부 결정 아님"으로 명시했다.
- `docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md` §5
  (Kernel Readiness Assessment)는 "Kernel을 설계할 충분한 Evidence가
  아직 없다"고 평가했다. 그 근거는 Kernel Module 3개 Defer, ADC-02
  Open, Engine Gateway Trigger 미충족, Execution Result 부재였다 —
  모두 **Kernel Architecture 설계**에 대한 판단이지, **Kernel 정의**에
  대한 판단이 아니었다.
- `ARCHITECTURE_GOVERNANCE.md` Freeze 원칙: "Architecture Baseline은
  '모든 문제가 해결된 상태'가 아니라 '지금 결정할 것과 나중에 결정할
  것이 명확히 구분되고 추적되는 상태'를 의미한다."

### Decision

**Accept** (반영 범위를 한정하는 조건부)

Baseline에 반영할 범위는 다음으로 한정한다.

1. Kernel의 정의(RFC-0002 §8: Kernel은 Component가 아니라 공통 책임을
   담당하는 계층이다)
2. Kernel과 Component의 관계(§9·§10: 책임으로 정의하고 구현으로
   정의하지 않는다)
3. Kernel Design Principles KP-1~KP-6(판단 1에서 Accept)
4. Core → Kernel 용어 통합(판단 3에서 Accept)

다음은 Baseline에 반영하지 않는다.

- Kernel Architecture 및 Component Design — `BASELINE.md` §10 Out of
  Scope에 **그대로 유지**한다.
- 4-Layer Context Model — 판단 2b에서 Defer되었다.
- RFC-0002 §14 Roadmap — 순서 제안이며 확정 계획이 아니다.

### Decision Rationale

RFC-0002가 Baseline에 추가하려는 것은 "Kernel이 무엇인가(정의)"이지
"Kernel이 어떻게 생겼는가(Architecture)"가 아니다. §10 Out of Scope가
막고 있는 것은 후자이며, 전자는 오히려 §10이 무엇을 Out of Scope로
두고 있는지를 더 명확하게 만든다 — Freeze 원칙이 요구하는 "지금 결정할
것과 나중에 결정할 것의 명확한 구분"에 부합한다.

GOVERNANCE-REVIEW-0001의 "Kernel Readiness = 아직 아님" 평가와도
모순되지 않는다. 그 평가는 Kernel을 **설계**할 준비가 되었는지에 대한
것이었고, 이번 Accept는 Kernel을 **정의**하는 데 한정된다. 정의가 먼저
확정되어야 이후 "이 책임이 Kernel에 속하는가"를 하나씩 판단할 수 있다.

### Risks

- Baseline은 Frozen v1.0이므로, 이 반영은 버전 갱신(예: v1.1)을
  동반한다. 그 버전 정책은 이 ADC가 결정하지 않고 ADR에 위임한다.
- **절차 부채**: `GOVERNANCE-REVIEW-0001-post-adc-0001.md` §1이 이미
  기록했듯, Kernel ADC-0001이 "ADR Required"로 판정한 2개 Module
  (Governance, Execution Layer)의 ADR이 아직 작성되지 않은 채로 남아
  있다. 이번 판단 1·3·4가 다시 "ADR Required"를 발생시키므로, 미작성
  ADR이 누적될 수 있다. 이 ADC는 그 누적 자체를 해소하지 않는다 —
  사실로만 기록한다.

### Next Step

**ADR Required**

---

## 종합

| 판단 항목 | Decision | Next Step |
|---|---|---|
| 1. Kernel Design Principles KP-1~KP-6 | **Accept** | ADR Required |
| 2a. Context 4개 책임(후보로서) | **Accept** | No ADR Required |
| 2b. 4-Layer Context Model 확정 | **Defer** | No ADR Required |
| 3. Core → Kernel 용어 통합 | **Accept** | ADR Required |
| 4. RFC-0002 Baseline Proposal 채택 | **Accept** (범위 한정) | ADR Required |

RFC-0002 전체를 일괄 승인하지 않았다. 5개 판단 중 4개 Accept, 1개
Defer이며, Defer된 항목(4-Layer Context Model)은 RFC-0002 자신의
Roadmap이 이미 별도 단계로 배치한 것이다.

Reject나 Out of Authority로 분류된 항목은 없다 — 4개 판단 모두 Jarvis
OS Architecture 수준의 판단 권한 안에 있었고, 어느 항목도 명시적으로
"틀렸다"고 볼 근거는 없었다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0002와 그것이 인용한 기존
  문서에 실제로 기록된 사실만 사용했고, 인용한 테스트 이름·문서 절
  번호는 소스에서 직접 확인했다. 새 실험은 하지 않았다.
- 일괄 승인했는가 — **아니오**. 4개 사안을 5개 판단으로 분리했고,
  그중 1개는 Defer다.
- "필요할 것 같다"는 이유로 Accept했는가 — **아니오**. 판단 2b가 바로
  그 이유로 Defer되었다(관찰된 적 없는 taxonomy를 확정하지 않았다).
- 반론을 검토했는가 — **Pass**. KP-6 vs Execution State, KP-2 vs
  가변 Layer 두 건을 판단 1에 기록했다.
- Architecture Drift가 없는가 — **없음**. 새 Layer/Component/Concept를
  만들지 않았다. 판단 4는 `BASELINE.md` §10 Out of Scope(Kernel
  Architecture)를 그대로 유지하도록 범위를 한정했다.
- Kernel Leak가 없는가 — **없음**. Scheduler/Registry/Runtime/Memory/
  Event Bus 어느 것도 설계하거나 필요 여부를 판단하지 않았다.
- 구현을 제안했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**. 이 ADC는 ADR이 필요하다는 판정만
  내렸다.
- RFC-0002와 모순되지 않는가 — **Pass**. 판단 2b의 Defer는 RFC-0002
  §14 Roadmap이 "Kernel Context Model"을 별도 단계로 둔 것과 일치한다.
