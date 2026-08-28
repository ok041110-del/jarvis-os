# ADC-0014: 단일 실행 단위 dispatch·격리 책임의 명칭 판단 (RFC-0014 후속)

## 목적

`docs/architecture/core/RFC-0014-execution-responsibility-naming.md`
§1 Boundary Question — **"`BASELINE.md` §16.3이 이미 존재를
Accept한 '단일 실행 단위 dispatch·격리' 책임을 어떤 Architecture
명칭으로 정의할 것인가?"** — 에 대해 판단한다.

근거는 RFC-0014와 그것이 인용한 Evidence(`ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`,
`ADC-0013-runtime-existence-scoped-reconsideration.md`,
`RFC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`§4,
`RFC-0012-dispatch-component-boundary.md`/`ADC-0012-dispatch-component-boundary.md`,
`BASELINE.md` §6/§16.3/§16.4, `docs/00_governance/GLOSSARY.md`)로만
한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Process/Thread/Subprocess 구현 전략 확정.
- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration 결정.
- `ADC-0008`(넓은 범위 Runtime 존폐, Not Accepted)의 재판단 — 그
  Decision은 이 ADC와 무관하게 유지된다.
- `ADC-0013`/`ADR-0003`이 이미 확정한 책임의 **존재**·**범위** —
  이 ADC는 명칭만 판단하고, 그 존재·범위를 넓히거나 좁히지 않는다.
- `RFC-0012`/`ADC-0012`(Dispatch Component, DEFER)의 재개.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  조항 해제 — 명칭이 정해져도 구현 전략이 미정인 한 그대로
  유효하다.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0014가 비교한 3개 명칭
후보(Runtime 유지 / Execution Dispatcher / Execution Host) 중
무엇을, `BASELINE.md` §16.3이 Accept한 좁은 책임의 공식 명칭으로
Accept할 것인가?**

---

## Q0. RFC-0014의 3개 후보 재대조

### 후보 A. Runtime (유지)

- **의미**: §6 Concept Model에 이미 등재된 이름을 그대로 쓴다.
- **충돌**: `docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`
  §4가 "MVP-0005가 요청한 'Pipeline Runtime'이... Jarvis OS Concept
  Model의 'Runtime'과 같은 것인지... 결정하지 않는다"고 이미 경계로
  남긴 바로 그 충돌이 지금도 미해소다. 더 근본적으로, `BASELINE.md`
  §6의 "Runtime" 정의(Workflow 참조, Multi-Task를 Agent에게 배분)는
  §16.3이 Accept한 것보다 **넓다** — 이름을 그대로 쓰면 "좁게만
  Accept됐다"는 사실이 이름 뒤에 가려질 위험이 크다.
- **재확인**: 이 충돌은 RFC-0014가 정확히 지적한 그대로이며, 이
  ADC가 다시 대조해도 해소되지 않는다.

### 후보 B. Execution Dispatcher

- **의미**: "dispatch" 책임을 이름에 직접 반영한다.
- **충돌**: `RFC-0012-dispatch-component-boundary.md`/`ADC-0012-dispatch-component-boundary.md`가
  "Dispatch Component"라는 이름을 Kernel Component Architecture(§10
  Out of Scope) 수준에서 이미 선점했고, `ADC-0012`는 그 RFC를
  **DEFER**했다(Trigger 미충족). "Execution Dispatcher"를 채택하면
  핵심 단어("Dispatch")를 공유하는 두 문서가 생겨, 향후 §10
  Out of Scope가 풀릴 때 "DEFER됐던 Dispatch Component가 다른
  이름으로 우회 승격됐다"는 오독을 유발할 실질적 위험이 있다. 또한
  격리(isolation) 책임이 이름에 전혀 드러나지 않는다 — §16.3
  "책임"의 절반이 이름 밖에 남는다.
- **재확인**: 이 충돌도 RFC-0014의 판단대로 유효하다.

### 후보 C. Execution Host

- **의미**: 단일 실행 단위가 시작되고(dispatch) 그 안에 격리되는
  경계를 가리킨다.
- **충돌**: 이 ADC 시점에도 `docs/architecture/core/`,
  `docs/00_governance/GLOSSARY.md`, `BASELINE.md` 전수 재검색 결과
  "Host"가 Concept·Component 이름으로 쓰인 사례가 없다(재확인 완료).
- **재확인**: RFC-0014 제출 이후 이 ADC 작성 시점까지 저장소에
  새로 추가된 문서 중 "Host"를 Concept 이름으로 선점한 것은 없다
  (`RFC-0014` 병합 이후 커밋 이력 확인).

### Q0 결론

RFC-0014의 비교는 재대조 결과에서도 그대로 유효하다 — 후보 A·B는
각각 독립적인 이유(§6 넓은 정의·`RFC-0004` 경고 / `RFC-0012`·
`ADC-0012` DEFER 대상과의 어휘 중복)로 충돌이 있고, 후보 C만
충돌이 없다.

---

## Q1. Execution Host를 Accept할 근거는 충분한가

### 검토

명칭 결정은 `ADC-0013`류의 "존재 Accept" 판단과 성격이 다르다 —
Evidence 반복 관찰(Rule B)이 필요한 것이 아니라, **기존 용어 체계와
충돌하지 않고 책임 범위를 정확히 표현하는가**가 판단 기준이다
(RFC-0014 §Boundary Question이 이미 이렇게 범위를 좁혔다). 이
기준으로 보면:

1. **충돌 없음**(Q0) — 유일하게 기존 Kernel/Core 용어와 충돌이 없다.
2. **범위 정확성** — §16.3 "책임"(dispatch + isolation, Multi-Task
   제외)을 과장도 축소도 없이 반영한다. "Dispatcher"(과소 —
   isolation 누락)나 "Runtime"(과대 — Multi-Task/Workflow 연상)과
   달리, "Host"는 "그 안에서 실행이 시작되고 격리되는 경계"라는
   중립적 이미지만 전달한다.
3. **구현 전략 중립성** — Process인지 Thread인지 규정하지 않는다.
4. **잔여 위험**(RFC-0014 §3 스스로 인정) — "Host"라는 단어가
   저장소 밖 일반적 의미(배포 인프라의 "host")와 혼동될 여지는
   있으나, 이는 저장소 내부 Concept과의 **충돌**이 아니라 일반
   어휘와의 근접성일 뿐이다 — 이 판단 기준(§Boundary Question)이
   요구하는 "기존 Kernel/Core 용어와의 충돌"에는 해당하지 않는다.
   §Risks에 기록하되 Accept를 막을 근거로 삼지 않는다.

### Q1 결론

Execution Host는 §Boundary Question이 요구하는 세 기준(충돌 없음,
범위 정확성, 구현 중립성)을 모두 충족한다. **Accept한다.**

---

## Q2. §6 Concept Model의 "Runtime"과 Execution Host는 재명명 관계인가, 별개 책임인가

### 검토

두 가지 선택지가 있다.

- **재명명**: §6의 "Runtime" 항목 자체를 "Execution Host"로 바꾼다.
- **별개 병존**: §6의 "Runtime"은 그대로 두고(넓은 정의, ADC-02 여전히
  Open), "Execution Host"를 §16.3 전용의 **새로운, 더 좁은**
  Concept으로 별도 등재한다.

`ADR-0003` §3이 이미 이 질문의 답을 예비적으로 판단해 두었다 —
"§6의 이름·표를 이 ADR이 건드리면 '이 책임 = Runtime'이라고
암묵적으로 확정하는 효과를 낳는다... §6의 Runtime 각주는 수정하지
않는다." 이 ADC는 그 판단을 뒤집을 근거가 없다:

1. §6의 "Runtime" 정의(Workflow 참조, Multi-Task를 Agent에게 배분)는
   §16.3이 Accept한 범위보다 **훨씬 넓다** — `ADC-0013` 자신이
   "이 6개 관찰은... Multi-Task 조합이나 Workflow 수준 배분은 어떤
   Prototype도 다루지 않았다"고 명시했다. 좁은 범위만 Accept된
   책임의 이름을, 넓은 정의를 가진 기존 Concept 항목에 덮어씌우면
   "넓은 정의도 Accept됐다"는 근거 없는 확장 해석을 낳는다.
2. `docs/decisions/adc/ADC.md`의 ADC-02("Runtime 개념의 존폐")는
   여전히 Open·NOW다 — 이 ADC가 §6의 "Runtime" 항목을 재명명하면,
   Jarvis OS 수준 ADC-02가 아직 열려 있는 그 "Runtime" 자체의 존폐
   질문에 사실상 답하는 효과를 낳는다. 이는 이 ADC의 권한 밖이다
   (`docs/decisions/adc/ADC.md`는 별도 트랙이며, `ADR-0001`·
   `ADR-0002`·`ADR-0003` 선례가 이미 이 트랙을 건드리지 않기로
   결정했다).
3. §16.3 "이 Accept가 결정하지 않는 것"이 "§6 Concept Model의
   'Runtime' 항목과의 관계"를 명시적으로 Open 항목에 포함시켰다 —
   이 ADC가 그 관계를 "재명명"으로 판단하는 것은 §16.3 자신이 이미
   유보한 것을 이 ADC가 임의로 확정하는 셈이 된다.

### Q2 결론

**별개 책임(별개 병존)으로 판정한다.** "Execution Host"는 §6의
"Runtime" 항목을 대체하거나 재명명하는 것이 아니라, §16.3이 이미
좁게 Accept한 책임만을 가리키는 **새로운, 더 좁은 범위의 Concept**
이다. §6의 "Runtime" 항목(Service 분류, 넓은 정의, ADC-02 Open)은
이 ADC로 전혀 변경되지 않는다.

---

## Decision

**A. Accept — 명칭: Execution Host**

`BASELINE.md` §16.3이 Accept한 "단일 실행 단위 dispatch·격리"
책임의 공식 명칭을 **Execution Host**로 확정한다. 이 명칭은 §6
Concept Model의 "Runtime" 항목과 **별개의, 더 좁은 범위의 Concept**
이다(§Q2) — Runtime 항목을 재명명하지 않으며, ADC-02(Jarvis OS
수준, Runtime 존폐)의 Open 상태에도 영향을 주지 않는다.

### Reason

- Q0 재대조 결과 후보 A(Runtime 유지)·B(Execution Dispatcher)는
  각각 실질적 이름 충돌이 있고, 후보 C(Execution Host)만 충돌이
  없다.
- Q1 — Execution Host는 명칭 판단 기준(충돌 없음, 범위 정확성,
  구현 중립성) 세 가지를 모두 충족한다.
- Q2 — 이 명칭은 §6의 "Runtime"을 재명명하지 않고 별개로 병존한다
  — 넓은 정의(§6)와 좁은 정의(§16.3)를 하나의 이름으로 뭉뚱그리지
  않음으로써, `ADC-0013`이 신중하게 지켜온 "좁은 범위만 Accept"
  원칙이 명칭 단계에서도 그대로 유지된다.

### Decision Rationale

이 Decision은 `ADC-0008`(넓은 범위 Runtime 존폐, Not Accepted)을
전혀 건드리지 않는다 — §6의 "Runtime" 항목이 그대로 남으므로,
`ADC-0008`이 판단 대상으로 삼았던 그 Concept도 그대로 남는다. 이
Decision은 `RFC-0012`/`ADC-0012`(Dispatch Component, DEFER)도
재개하지 않는다 — "Dispatch"라는 단어를 쓰지 않는 이름을 선택함으로써
그 충돌 가능성 자체를 피했다.

---

## Baseline 반영 범위 (다음 ADR을 위한 지침, 이 ADC가 직접 반영하지 않음)

### §16.3 명칭 반영 범위

`BASELINE.md` §16.3 본문에서 "이 책임"을 가리키는 표현("단일 실행
단위 dispatch·격리 책임")을 유지하되, 이제 명칭이 확정됐음을
반영해 절 제목과 본문에 **"Execution Host"**를 병기한다. 다음
후속 ADR이 수행할 구체적 갱신 범위(제안, 확정 아님):

- 절 제목: "16.3 단일 실행 단위 Dispatch·격리 (Accept, Scoped)" →
  "16.3 Execution Host — 단일 실행 단위 Dispatch·격리 (Accept,
  Scoped)".
- "**이 Accept가 결정하지 않는 것**" 문단의 "이 책임의 명칭(§6
  Concept Model의 'Runtime' 항목과의 관계 포함)" 문구를, 명칭은
  더 이상 Open이 아니므로 "Execution Host는 §6의 'Runtime' 항목과
  별개의 Concept이다(`ADC-0014` §Q2)"로 대체한다.
- **§6 Concept Model 표 자체는 건드리지 않는다** — Q2 판정에 따라
  "Runtime" 항목은 그대로 유지되고, "Execution Host"를 §6 표에
  새 행으로 추가할지는 이 ADC가 결정하지 않는다(§Out of Scope) —
  §6은 Jarvis OS 수준 넓은 Concept Model이고, Execution Host는
  Kernel Module(§16) 수준의 더 좁은 책임이기 때문에, 반드시 §6에
  등재되어야 하는 것은 아니다. 이 판단이 필요하다면 별도 절차로
  넘긴다.

### GLOSSARY.md 신규 용어 정의

**필요하다.** `docs/00_governance/GLOSSARY.md`의 "Concept Model
용어" 표는 현재 "Runtime"만 등재하고 있다. Execution Host가 별개
Concept으로 Accept됐으므로, 정합성을 위해 새 행이 필요하다(제안,
후속 ADR이 확정):

| 분류 | Concept | 정의 |
|---|---|---|
| (미정 — ADR에서 결정) | Execution Host | 단일 실행 단위의 dispatch·격리를 담당하는 책임. Command(불변)·Task(identity/lifecycle) 어느 쪽에도 속하지 않는다. §6 "Runtime"과 별개 Concept(`ADC-0014` §Q2) |

이 표 행의 정확한 분류(Service/Process/Interface 등)는 이 ADC가
결정하지 않는다 — §6 분류 체계와의 정합성은 후속 ADR이 판단한다.

---

## Out of Scope

- Process/Thread/Subprocess 구현 전략.
- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration.
- `ADC-0008`의 재판단, `ADC-0013`/`ADR-0003`이 확정한 존재·범위의
  재론.
- `RFC-0012`/`ADC-0012`(DEFER)의 재개.
- `docs/decisions/adc/ADC.md`의 ADC-02(Jarvis OS 수준, Runtime
  존폐) 항목 수정 — 이 ADC는 그 항목을 갱신하지 않는다.
- §6 Concept Model 표에 "Execution Host"를 실제로 추가할지 여부의
  최종 확정 — 방향만 제시했다(§Baseline 반영 범위).
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  해제 — **명칭 결정만으로는 해제하지 않는다.** 구현 전략
  (Process/Thread/Subprocess)이 별도로 확정되기 전까지 그 조항은
  실질적으로 유효하다. 다만 그 조항이 가리키는 대상이 이제
  "Execution Host"로 더 명확해졌으므로, 이유 문구 정밀화는 구현
  전략 확정 시점에 함께 반영하는 것을 계속 권고한다(`ADR-0003` §5와
  동일한 타이밍 판단).
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.

## Risks

- "Host"라는 단어가 배포 인프라의 일반적 의미("host machine")와
  혼동될 여지가 있다 — 저장소 내부 Concept과의 충돌은 아니지만,
  향후 GLOSSARY.md 항목 작성 시 정의를 명확히 해 둘 필요가 있다.
- Execution Host를 §6 표에 추가할지 여부를 이 ADC가 미결로 남긴
  것이, "Kernel Module(§16)에는 있지만 Concept Model(§6)에는 없는"
  비일관 상태로 오래 남을 위험이 있다 — 후속 ADR이 이 공백을
  방치하지 않도록 명시적으로 판단해야 한다.
- 명칭 Accept가 "구현 착수 가능"으로 오독될 위험 — 그런 뜻이 아니다
  (§Out of Scope, IMPLEMENTATION_RULES.md 조항 유지).

**재검토 조건**: 향후 Multi-Task/Workflow 범위로 책임이 확장
Accept된다면, "Execution Host"라는 이름이 그 확장된 범위까지
정확히 표현하는지 다시 판단해야 한다 — 이 ADC는 그 시점의 재검토
필요성을 미리 인정해 둔다.

## Next Step

**ADR Required** — 이 Decision은 `BASELINE.md` §16.3 본문에 명칭을
반영해야 한다.

1. ADR을 작성해 `BASELINE.md` §16.3 본문에 "Execution Host" 명칭을
   반영한다(§Baseline 반영 범위의 제안을 참고, 최종 문구는 ADR이
   확정).
2. 같은 ADR 또는 별도 절차로 `docs/00_governance/GLOSSARY.md`에
   Execution Host 항목을 추가한다.
3. §6 Concept Model 표에 Execution Host를 추가할지는 그 ADR이
   명시적으로 판단한다(추가하지 않기로 결정하는 것도 유효한 결론).
4. `hqs/development/IMPLEMENTATION_RULES.md`는 이 ADC·후속 ADR
   어느 것으로도 갱신되지 않는다 — 구현 전략 확정 RFC/ADC 이후로
   계속 이연한다.
5. 구현 전략(Process/Thread/Subprocess) 확정은 별도 RFC로, 이
   ADC·ADR 완료 이후 진행한다.

## Governance Chain 검증

`RFC-0014`(Proposed, 명칭 후보 비교와 권고만 — Decision 아님) → 이
ADC(Accept — Execution Host, §6과 별개 Concept으로 판정) → 후속
ADR(예정 — Baseline 반영). RFC-0014가 제시하지 않은 것(§6과의
관계 최종 판정, GLOSSARY 반영)을 이 ADC가 추가로 판단했으나, 이는
RFC-0014 §Next Step 3번이 "이 RFC는 판단하지 않는다"며 명시적으로
후속 ADC에 위임한 항목이므로 범위 위반이 아니다. 이 ADC가 RFC-0014의
Out of Scope(구현 전략·Scheduler·Multi-Task·`ADC-0008`·`ADC-0012`
재론)를 하나도 건드리지 않았음을 §Out of Scope에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오** — 이미 Accept된
  책임(§16.3)에 이름을 부여했을 뿐, 새 책임을 추가하지 않았다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **좁은 의미로
  그렇다** — "Execution Host"라는 이름이 붙은 Concept이 생겼으나,
  그 책임 범위는 §16.3이 이미 확정한 것과 동일하다(확장 없음).
- Contract Change — **없음** — 공개 Interface를 정의하지 않았다.
- Baseline 문서(`BASELINE.md`, `GLOSSARY.md`)를 이 ADC가
  변경했는가 — **아니오** — 인용·방향 제시만 했다. 실제 변경은
  ADR의 몫이다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- ADR이 필요한가 — **예**(§Next Step).

## Self Review

- Evidence만 사용했는가 — **Pass**. `RFC-0014`와 그것이 인용한
  `ADR-0003`, `ADC-0013`, `RFC-0013`, `RFC-0004`, `RFC-0012`/
  `ADC-0012`, `BASELINE.md`, `GLOSSARY.md`만 인용했다. 새 실험은
  하지 않았다.
- 3개 후보를 독립적으로 재대조했는가 — **Pass**(§Q0) — RFC-0014의
  결론을 그대로 베끼지 않고 충돌 근거를 다시 확인했다.
- RFC 권고(Execution Host)를 그대로 수용했는가, 판단 없이 — **아니오**
  (§Q1) — 판단 기준(충돌·범위 정확성·구현 중립성)을 명시하고 그
  기준으로 재평가했다.
- §6 "Runtime"과의 관계를 판정했는가 — **Pass**(§Q2) — 별개
  Concept으로 명시적으로 판정했다.
- 구현 전략을 결정했는가 — **아니오**(§Out of Scope).
- Scheduler/Multi-Task를 다뤘는가 — **아니오**(§Out of Scope).
- `IMPLEMENTATION_RULES.md`의 금지를 해제했는가 — **아니오**
  (§Out of Scope에 명시적으로 "명칭 결정만으로는 해제하지 않는다").
- `ADC-0008`·`ADC-0012`를 재론했는가 — **아니오**.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- Production Code를 변경했는가 — **아니오**.
- Baseline·GLOSSARY를 직접 수정했는가 — **아니오** — 방향만
  제시하고 ADR로 위임했다.
