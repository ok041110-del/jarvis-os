# RFC-0014: 단일 실행 단위 dispatch·격리 책임의 명칭 (ADR-0003 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §16.3("단일 실행
단위 Dispatch·격리, Accept Scoped")가 "이 Accept가 결정하지 않는
것"으로 명시적으로 남긴 항목 중 **명칭**만.
**Evidence**: `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`,
`docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`§4,
`docs/architecture/core/RFC-0012-dispatch-component-boundary.md`/`ADC-0012-dispatch-component-boundary.md`,
`docs/architecture/baseline/BASELINE.md` §6/§16.3/§16.4,
`docs/00_governance/GLOSSARY.md`. 새로운 실험·Evidence를 만들지
않는다.

> 본 RFC는 이 책임의 구현 전략(Process/Thread/Subprocess)을 결정하지
> 않는다. Scheduler·Engine Gateway 대체 구조나 Multi-Task/Workflow
> orchestration을 설계하지 않는다. Runtime의 존폐 자체(넓은 범위)를
> 다시 열지 않는다 — `ADC-0008`(Not Accepted, 넓은 범위)과
> `ADC-0013`(Accept, Scoped)이 이미 내린 판단은 그대로 유지된다. 이
> RFC가 여는 것은 명칭 하나뿐이다: **§16.3이 이미 존재를 Accept한
> 책임을 어떤 Architecture 명칭으로 부를 것인가?**

## 0. 이 RFC가 열린 이유

`ADR-0003`은 `BASELINE.md` §16.3에 "단일 실행 단위 dispatch·격리"
책임을 등재하면서, 그 명칭을 §6 Concept Model의 "Runtime" 항목과
의도적으로 연결하지 않았다(ADR-0003 §3: "§6의 이름·표를 이 ADR이
건드리면 '이 책임 = Runtime'이라고 암묵적으로 확정하는 효과를
낳는다"). `ADC-0013` §Implementation Boundary "제외"도 명칭을 별도
절차로 명시적으로 위임했다. 이 RFC는 그 위임을 받는다.

명칭이 미정인 채로 남으면 §16.3 본문 스스로가 "이 책임의 명칭(§6
Concept Model의 'Runtime' 항목과의 관계 포함)"이라는 조건부 표현을
써야 하고, `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime
구현 금지" 조항도 "무엇을 구현 금지하는지조차 확정할 수 없는
상태"(`ADR-0003` §5)로 남는다. 명칭을 정하는 것은 구현 착수와
무관하게, 문서 자체의 정합성을 위해 필요하다.

## 1. Boundary Question

**§16.3이 이미 존재를 Accept한 "단일 실행 단위 dispatch·격리"
책임을 어떤 Architecture 명칭으로 정의할 것인가?**

이 질문은 다음을 전제로 한다 — 전제 자체는 이 RFC가 다시 열지
않는다.

- 책임의 **존재**는 이미 Accept됐다(`ADC-0013`, `ADR-0003`). 이
  RFC는 존재 여부를 재론하지 않는다.
- 책임의 **범위**는 이미 좁게 확정됐다(§16.3 "책임" 문단) — 명칭
  후보를 고를 때 그 범위보다 넓게 들리는 이름은 감점 요인이다.
- 구현 전략(Process/Thread/Subprocess), Scheduler/Engine Gateway
  비교, Multi-Task/Workflow 확장은 이 RFC의 범위 밖이다(§Out of
  Scope).

## 2. 명칭 후보

### 후보 A. Runtime (유지)

**의미**: §6 Concept Model에 이미 등재된 이름을 그대로 쓴다.
`BASELINE.md` §6은 "Runtime은 Workflow를 참조하여 Task를 Agent에게
배분한다"고 정의한다.

**기존 문서 충돌**:
- `RFC-0004-task-dispatcher-runtime-boundary.md` §4가 정확히 이
  상황을 경고했다 — "MVP-0005가 요청한 'Pipeline Runtime'이 만약
  승격된다면, 그 구현체가 Jarvis OS Concept Model의 'Runtime'과 같은
  것인지... 이 RFC가 결정하지 않는다"는 경계가 지금도 미해소다. 이
  후보를 선택하면 Dev HQ 수준에서 등장할 수 있는 유사 이름의
  구조물과 계속 혼동 위험을 안고 간다.
- 더 근본적인 문제: §6의 "Runtime" 정의는 Workflow 참조·Multi-Task
  배분까지 포함하는 **넓은** 정의인데, `ADC-0013`이 Accept한 것은
  그보다 훨씬 **좁은** 범위다. 이름을 그대로 유지하면, 이 책임이
  실제로는 좁게만 Accept됐다는 사실이 이름 뒤에 가려질 위험이 크다
  — 독자가 "Runtime = §6 전체 정의가 이미 Accept됨"으로 오독하기
  쉽다.

**확장성**: 향후 Multi-Task/Workflow 범위까지 확장 Accept된다면
이름을 다시 바꿀 필요가 없다는 것이 유일한 장점이다.

**구현 적합성**: 이름 자체는 구현 전략에 중립적이다.

### 후보 B. Execution Dispatcher

**의미**: "실행을 dispatch한다"는 책임을 이름에 직접 반영한다. 이번
Accept된 책임의 핵심 동사(dispatch)를 그대로 명사화한 이름이다.

**기존 문서 충돌**:
- `RFC-0012-dispatch-component-boundary.md`/`ADC-0012-dispatch-component-boundary.md`가
  이미 "Dispatch Component"라는 이름을 Kernel Component
  Architecture(§10 Out of Scope) 수준에서 선점하고 있다 —
  `ADC-0012`는 이 RFC를 **DEFER**했다(Trigger 미충족). "Execution
  Dispatcher"라는 이름을 새로 채택하면, 표면적으로는 다른 문서지만
  "Dispatch"라는 핵심 단어를 공유하게 되어 독자가 "DEFER됐던
  Dispatch Component가 다른 이름으로 우회 승격됐다"고 오독할 위험이
  있다 — `ADC-0013` §Q2가 이미 "판단 대상의 폭이 다르다"고 구분해
  둔 것을, 명칭 단계에서 다시 흐릴 수 있다.
- 격리(isolation) 책임은 이름에 드러나지 않는다 — §16.3 "책임"의
  절반(동시 실행 시 상태 오염 방지)이 이름만으로는 보이지 않는다.

**확장성**: "Dispatcher"는 여러 Task를 여러 대상에 배분하는
뉘앙스를 자연스럽게 허용해, 향후 Multi-Task 확장 시 이름이 자연스럽게
따라올 수 있다 — 그러나 이는 동시에 지금 Accept된 범위보다 넓게
들린다는 단점과 같은 원인이다.

**구현 적합성**: 이름 자체는 구현 전략에 중립적이다.

### 후보 C. Execution Host

**의미**: "단일 실행 단위가 그 안에서 시작되고 격리되는 경계"를
가리킨다. dispatch(시작)와 isolation(격리, "host" 경계 안에
가두는 것) 두 책임을 모두 이름에 담되, 어느 쪽도 과장하지 않는다.

**기존 문서 충돌**: 저장소 전수 검색 결과(`docs/architecture/core/`,
`docs/00_governance/GLOSSARY.md`, `BASELINE.md`) "Host"라는 단어가
Concept·Component 이름으로 쓰인 사례가 없다 — Runtime(§6)·Dispatch
Component(RFC-0012)·Scheduler/Engine Gateway(ADC-02 대체 후보) 중
어느 것과도 어휘가 겹치지 않는다.

**확장성**: "Host"는 "무엇을 담고 있는가"에 열려 있는 이름이라,
향후 격리 단위가 Process 하나인지 여러 개인지와 무관하게 쓸 수
있다. 다만 Multi-Task/Workflow 수준 분배까지 자연스럽게 확장되는
이름은 아니다 — 오히려 "단일 실행 단위"라는 좁은 범위에 이름 자체가
못박혀 있다는 점이, 지금 Accept된 범위를 정확히 반영한다는 장점과
향후 넓히려면 새 이름이 또 필요할 수 있다는 단점을 동시에 갖는다.

**구현 적합성**: 이름 자체는 구현 전략에 중립적이다("Host"가
Process인지 Thread인지 규정하지 않는다).

## 3. 비교표

| 기준 | A. Runtime (유지) | B. Execution Dispatcher | C. Execution Host |
|---|---|---|---|
| 책임 범위를 정확히 표현하는가 | 아니오 — §6 넓은 정의를 연상시킴 | 부분적 — dispatch만 드러나고 격리는 안 드러남 | 예 — dispatch·격리 둘 다 중립적으로 포함 |
| 기존 Kernel/Core 용어와 충돌 | 있음(`RFC-0004` 경고, §6 넓은 정의와 혼동) | 있음(`RFC-0012`/`ADC-0012` "Dispatch Component"와 어휘 중복) | 없음(전수 검색 결과 미사용 어휘) |
| 확장성(Multi-Task/Workflow로 확장 시) | 이름 유지 가능(장점) = 동시에 현재 오독 위험(단점) | 자연스럽게 확장 가능하나 현재도 넓게 들림 | 확장 시 새 이름 필요 가능성 있으나, 현재 범위는 가장 정확히 반영 |
| 구현 전략에 대한 중립성 | 중립 | 중립 | 중립 |
| Baseline/GLOSSARY 갱신 범위 | 없음(이름 유지) — 그러나 §6 각주의 "세부 구조는 Open" 표현을 §16.3의 Scoped Accept와 어떻게 정합시킬지는 여전히 남는 문제 | §16.3 본문·GLOSSARY 신규 항목 추가 필요 | §16.3 본문·GLOSSARY 신규 항목 추가 필요 |

## 4. Decision Candidate (권고, 확정 아님)

**권고: 후보 C. Execution Host**

- 유일하게 기존 Kernel/Core 용어와 충돌이 없다(§3) — 후보 A는
  `RFC-0004`가 이미 경고한 충돌을 그대로 안고 가고, 후보 B는
  `RFC-0012`/`ADC-0012`의 DEFER된 "Dispatch Component"와 어휘가
  겹친다.
- §16.3이 Accept한 좁은 범위(dispatch + isolation, Multi-Task
  제외)를 이름 하나로 가장 정확하게 반영한다 — 과장도, 과소평가도
  없다.
- 구현 전략(Process/Thread/Subprocess)에 대해 어느 쪽으로도
  기울지 않는다.

이 권고는 **Decision이 아니다.** 최종 채택 여부, 그리고 GLOSSARY·
§16.3 본문에 실제로 반영할지는 후속 ADC로 위임한다(§Next Step).

## Out of Scope

- Process/Thread/Subprocess 구현 전략 결정.
- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration 결정.
- `ADC-0008`(넓은 범위 Runtime 존폐, Not Accepted)의 재판단.
- `ADC-0013`/`ADR-0003`이 이미 확정한 책임의 **존재**·**범위**
  재론.
- `RFC-0012`/`ADC-0012`(Dispatch Component, DEFER)의 재개.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  조항 해제 — 명칭이 확정되고 구현 전략까지 정해지기 전까지 그대로
  유효하다.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.
- 새로운 실험.

## Non-goals

- 이 RFC는 명칭을 확정하지 않는다 — 권고만 한다.
- 이 RFC는 구현 전략을 결정하지 않는다.
- 이 RFC는 Scheduler나 Multi-Task/Workflow를 설계하지 않는다.
- 이 RFC는 `ADC-0008`·`ADC-0013`의 기존 판단을 뒤집지 않는다.
- 이 RFC는 Architecture Baseline을 직접 변경하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §4의 권고(Execution Host)를 그대로 Accept할지, 후보 A/B 중
   하나를 대신 채택할지, 아니면 이 RFC가 제시하지 않은 새 이름을
   요구할지.
2. Accept된다면, 그 결정이 Baseline Update(ADR)로 이어질 때 무엇을
   갱신할지 — 최소한 `BASELINE.md` §16.3 본문의 명칭 표기,
   `docs/00_governance/GLOSSARY.md` 신규 항목 추가 여부.
3. `BASELINE.md` §6 Concept Model의 "Runtime" 항목과 새 명칭의
   관계 — 같은 Concept의 재명명인지, 별개 Concept으로 병존하는지는
   그 ADC가 명시적으로 판단해야 한다(이 RFC는 판단하지 않는다).
4. `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
   조항 이유 문구 갱신 필요 여부 — 명칭이 확정되면 그 문구가 가리키는
   대상이 명확해지므로, 이 시점에 함께 정리하는 것을 권고한다
   (`ADR-0003` §5가 이미 이 타이밍을 제안했다).

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADR-0003`, `ADC-0013`,
  `RFC-0013`, `RFC-0004`, `RFC-0012`/`ADC-0012`, `BASELINE.md`,
  `GLOSSARY.md`만 인용했다. 새 실험은 하지 않았다.
- 책임의 존재·범위를 재론했는가 — **아니오**. §16.3이 이미 Accept한
  것을 그대로 전제로 삼았다(§1).
- 구현 전략을 결정했는가 — **아니오**(§Out of Scope).
- Scheduler/Multi-Task를 다뤘는가 — **아니오**(§Out of Scope).
- 명칭을 확정했는가 — **아니오**. §4는 권고이지 Decision이 아니다.
- 기존 Kernel/Core 용어와의 충돌을 후보마다 확인했는가 — **Pass**
  (§2·§3, 전수 검색 기반).
- `ADC-0008`·`ADC-0013`의 기존 판단을 뒤집었는가 — **아니오**.
- `RFC-0012`/`ADC-0012`(DEFER)를 재개했는가 — **아니오** — 오히려
  그 DEFER 상태를 후보 B의 충돌 근거로만 인용했다.
- Production Code를 수정했는가 — **아니오**.
- ADC, ADR을 작성했는가 — **아니오**.
