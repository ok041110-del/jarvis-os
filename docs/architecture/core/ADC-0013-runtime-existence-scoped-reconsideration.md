# ADC-0013: 단일 실행 단위 dispatch·격리 책임 존재 여부 — Scoped Reconsideration (RFC-0013 후속)

## 목적

`docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md`
§4 Boundary Question — **"Jarvis OS는 Command·Task로 환원되지
않는, 단일 실행 단위의 dispatch·격리를 담당하는 독립 책임을 Kernel
Concept으로 Accept하는가?"** — 에 대해 판단한다.

근거는 RFC-0013과 그것이 인용한 Evidence(`BASELINE.md` §6/§12/§16.2,
`docs/decisions/adc/ADC.md` ADC-02,
`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`/`ADC-0008-runtime-existence-boundary.md`,
`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`,
`hqs/development/IMPLEMENTATION_RULES.md`,
`docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
및 그것이 종합한 5개 Prototype/Vertical Slice Evidence 문서)로만
한정한다. 새로운 Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Runtime(또는 대체 명칭)의 실제 Interface·위치 설계.
- Process/Thread/Subprocess 구현 전략 확정 — `process-runtime-strategy`
  Prototype이 Process를 Evidence 기반 후보로 제시했으나, 채택 여부는
  이 ADC의 범위 밖이다(RFC-0013 §4 제외 항목, 그대로 유지).
- Runtime의 명칭 확정 — "Runtime"을 그대로 쓸지, `RFC-0004`가 경고한
  이름 충돌을 피해 다른 이름을 쓸지는 결정하지 않는다.
- `BASELINE.md` §6의 원래 넓은 정의(Workflow 참조, Multi-Task를
  Agent에게 배분)의 검증 또는 채택 — 이 ADC는 그 정의를 다루지
  않는다.
- `ADC-0004-execution-result-consumer.md`(execution-layer)의
  재판단 — Not Accepted 상태는 이 ADC의 결과와 무관하게 유지된다.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0013 §4가 좁힌 범위 —
단일 실행 단위의 dispatch·격리 책임의 존재 여부 — 를 지금 Evidence로
Accept할 수 있는가?**

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가?

### Evidence

- `BASELINE.md` §6: Runtime을 `Service` 분류로 Memory/Registry와
  나란히 이미 등재해 두었다. 같은 절 각주는 "세부 구조는 Open
  Decision(ADC-02)"이라고 스스로 유보한다.
- `BASELINE.md` §12 Kernel Design Principles(KP-1): "Kernel은
  Component가 아니라 Responsibility"라는 원칙 — 실제로 존재하는
  책임에는 그것을 담을 Concept이 있어야 한다는 것을 전제한다.
- `BASELINE.md` §16.2(Execution Layer, Accept): "Specification 기반
  AI 실행" 책임 경계를 Accept하면서도, 그 Accept가 ADC-01·ADC-02를
  "결정하지 않는 것"으로 명시적으로 남겼다.

### Q0 결론

`ADC-0008`이 이미 판단했듯, 이 Intent는 단독으로 Accept 근거가 되지
못한다 — 원문 스스로 미결정임을 명시하기 때문이다. 이 판단은 뒤집지
않는다. **Architecture Intent만으로는 지금 판단할 수 없다.**

---

## Q1. §2(Evidence)와 결합하면 무엇이 달라지는가 — 실제 필요성

### Evidence

`docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
§2·§4가 종합한 5개 관찰(전부 main에 병합, 서로 다른 실행 대상·전략):

1. `command-contract`: Command에 실행 상태를 담으면 불변성이
   깨진다 — 실행 상태는 Command 밖에 있어야 한다.
2. `async-command`(subprocess): Task=CANDIDATE(Command 불변성 보호),
   subprocess가 이미 비동기·격리를 제공하므로 이 범위에서
   Runtime=NOT REQUIRED.
3. `in-process-async-command`(Thread): 동일 대상 동시 실행 시 상태가
   실제로 오염되어 테스트가 실패하는 것이 재현됐다(`assert 2 == 1`
   등) — 이름 혼동 수준이 아니라 **정확성 결함**.
4. `runtime-boundary`(`rtb_task.py`): Task가 Executor를 전혀 참조하지
   않고도 identity/lifecycle을 유지한 채 Sequential/Thread/Process
   세 전략 모두에서 동작 — Task(identity/lifecycle)와 실행
   dispatch·격리가 코드로 실제 분리 가능함을 실증. 동시에 Thread는
   대상 코드 내부 ThreadPoolExecutor와 중첩되어 실행 시간이
   예측 불가능해짐(0.03초→최대 43초).
5. `process-runtime-strategy`: Process 격리가 "동일 Target 동시
   실행" 조건에서 오염을 해소함을 확인 — 조건은 "동시 실행"이 아니라
   "동일 Target 동시 실행"으로 좁혀졌다.
6. `dev-hq-vertical-slice`(E2E): Command → Task → (dispatch·격리
   역할의) Process 실행 → Dev HQ Adapter → Result 저장 → Dashboard
   관찰까지, 이 책임을 Command/Task와 분리한 별도 모듈로 둔 구조가
   실제 Dev HQ 코드 경로에서 문제없이 동작함을 확인(7 tests passed,
   전체 Regression 355 passed).

### Q1 결론

이 6개 관찰이 답하는 질문은 "Runtime이라는 이름의 Concept이
필요한가"가 아니라, RFC-0013 §4가 정확히 좁혀 놓은 질문 그대로다:
**"Command와 Task 둘 다로 환원되지 않는, 단일 실행 단위의 dispatch·
격리 책임이 실제로 필요한가."** 서로 다른 실행 대상·전략에 걸쳐
반복적으로, 그리고 부재 시 실제 정확성 결함(관찰 3)까지 동반하며
같은 답에 수렴했다. **이 좁은 질문에 한해서는 Evidence가 존재를
지지한다.**

---

## Q2. Rule B(3건 이상 독립 관찰) 미충족과 Multi-Task 범위 미검증은 Accept를 막는가

### 검토

`docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
§5가 정직하게 남긴 공백은 두 가지다.

1. **형식적 관찰 건수**: Governance v2 Rule B(3건 이상 독립 관찰)
   기준으로 보면, 이번 5개 관찰은 "같은 저자가 같은 세션에서 설계한
   연속 Prototype"이라는 하나의 계기이고, `ADC-0004-execution-result-consumer.md`(Q3)의
   Blocking 관찰 1건과 합쳐도 서로 다른 계기는 2개뿐이다 — 3건에
   못 미친다.
2. **범위 불일치**: `BASELINE.md` §6의 원래 정의(Workflow 참조,
   Multi-Task를 Agent에게 배분)는 어떤 Prototype도 검증하지 않았다.

이 작업의 작업 지시 §2는 "Evidence 부족만으로 Accept를 금지하지
않는다"고 명시한다. 이 지시는 Rule B를 무시하라는 뜻이 아니라,
**Rule B가 겨냥하는 대상과 이 ADC가 판단하는 대상이 같은 범위인지**를
먼저 확인하라는 뜻으로 읽는다.

- `ADC-0012`가 Phase 6 Evidence에 Rule B를 엄격히 적용해 DEFER한
  대상은 **Kernel Component Architecture(§10) 전체 설계 착수** —
  Multi-Task/Workflow 수준까지 포괄하는 넓고 돌이키기 어려운
  결정이었다. 그 경우 형식적 관찰 건수 부족이 Accept를 막을
  합당한 이유였다.
- 이 ADC가 판단하는 대상은 그보다 훨씬 좁다 — RFC-0013이 스스로
  Multi-Task/Workflow 분배, 명칭, 구현 전략을 전부 범위 밖으로
  제외했기 때문에(§4 "명시적으로 제외하는 것"), **범위 불일치
  공백(위 2번)은 애초에 이 ADC의 판단 대상이 아니다** — RFC-0013이
  이미 그 공백을 질문에서 들어냈다.
- 남는 것은 형식적 관찰 건수(위 1번)뿐이다. 그러나 이 5개 관찰은
  단일 계기 안에서도 **서로 다른 실행 대상·전략**(subprocess,
  Thread, Process, 3가지 병렬 전략, 실제 Dev HQ E2E)에 걸쳐
  독립적으로 재현됐고, 그중 하나(관찰 3)는 이름 문제가 아니라
  실제 정확성 결함이다 — Rule B가 형식적 "3건"을 요구하는 근본
  이유(우연·저자 편향이 아님을 확인하는 것)를, 다른 방식으로
  이미 충족한다.

### Q2 결론

Rule B의 형식적 건수 미충족은, **RFC-0013이 스스로 좁힌 범위** 안에서는
Accept를 막을 만큼 결정적이지 않다. 범위 불일치 공백은 이 ADC의
판단 대상 밖으로 이미 제외되어 있다. `ADC-0012`와 결론이 다른 이유는
Rule B를 다르게 적용해서가 아니라, **판단 대상의 폭이 다르기
때문**이다.

---

## Decision

**A. Accept (Scoped)**

RFC-0013 §4의 좁은 Boundary Question — "Command와 Task로 환원되지
않는, 단일 실행 단위의 dispatch·격리를 담당하는 독립 책임" — 의
**존재**를 Accept한다. 이 Accept는 다음을 확정하지 않는다: 명칭,
Process/Thread/Subprocess 구현 전략, `BASELINE.md` §6의 넓은
Multi-Task/Workflow 분배 책임. 이 세 항목은 RFC-0013이 이미 명시적
Open Question으로 분리했고, 이 ADC도 그 분리를 그대로 유지한다.

### Reason

- Architecture Intent(Q0)는 단독으로는 부족하지만, "실행 관련
  책임이 있을 것"이라는 신호를 설계 당시부터 일관되게 남겨 왔다
  (Runtime을 Service로 분류, KP-1 원칙).
- 실제 필요성 Evidence(Q1)는 서로 다른 실행 대상·전략에 걸쳐
  반복·수렴했고, 부재 시 실제 정확성 결함까지 재현했다 — 이는
  ADC-02가 원래 우려한 "이름 혼동" 문제보다 강한 형태의 근거다.
- Rule B 형식 미충족(Q2)은 RFC-0013이 스스로 좁힌 범위 안에서는
  Accept를 막지 못한다 — 그 형식 기준이 겨냥하는 위험(범위가 넓고
  돌이키기 어려운 결정에서 우연한 관찰로 성급히 결론 내리는 것)은
  이 ADC가 판단 범위를 좁게 유지함으로써 이미 회피됐다.

### Decision Rationale

이 Decision은 `ADC-0008`의 Not Accepted를 뒤집지 않는다 — `ADC-0008`은
BASELINE §6의 **넓은** 정의("유지" 대 "대체")를 판단 대상으로
삼았고, 그 범위에서는 지금도 Evidence가 부족하다(Multi-Task 분배
여전히 미검증). 이 ADC는 그보다 훨씬 좁은, RFC-0013이 새로 연
질문만 판단했다 — 두 Decision은 서로 다른 질문에 대한 것이므로
모순이 아니다. `ADC-0012`의 DEFER와도 모순이 아니다 — `ADC-0012`는
Kernel Component Architecture 전체 설계 착수 여부를 판단했고, 이
ADC는 그보다 훨씬 좁은 존재 질문 하나만 판단한다.

---

## Implementation Boundary (다음 Production 구현을 위한 최소 책임 범위)

이 Accept는 Production 구현을 지금 승인하지 않는다 — 아래는 향후
ADR·Baseline Update가 이 책임을 등재할 때 참고할 **최소 책임
경계**이며, 이 ADC가 직접 구현을 지시하지 않는다.

**포함(이번에 존재를 Accept한 것)**:

- 이미 형성된 단일 Task(identity/lifecycle은 Task가 그대로 소유)를
  받아 실행을 시작하는 책임.
- 그 실행이 Command를 변경하지 않는다는 것(Command 불변성 보존)을
  보장하는 책임.
- 동일 대상에 대한 동시 실행에서 상태 오염이 발생하지 않도록 격리를
  제공하는 책임 — 최소한 `process-runtime-strategy` Prototype이
  실증한 수준(동일 Target 동시 실행에서 정확성 보장).
- Task가 Executor(이 책임의 구현체)를 직접 참조하지 않고도 동작할
  수 있어야 한다는 제약(`rtb_task.py`가 이미 반증한 원칙) — 즉 이
  책임은 Task로부터 호출되는 쪽이지, Task가 이 책임의 내부 구현을
  알아야 하는 쪽이 아니다.

**제외(이번 Accept가 결정하지 않는 것 — 후속 절차로 위임)**:

- 명칭(Runtime 그대로 사용할지, `RFC-0004`가 경고한 충돌을 피해
  다른 이름을 쓸지).
- 구현 전략(Process/Thread/Subprocess) — `process-runtime-strategy`
  Prototype의 결과는 근거로 인용 가능하나, 채택은 별도 판단.
  `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  조항은 이 ADC가 해제하지 않는다 — ADC-02가 Baseline 수준에서
  실제로 갱신되기 전까지 그대로 유효하다.
- Multi-Task/Workflow 수준 분배(BASELINE §6의 원래 넓은 정의) —
  별도 Evidence 없이는 이 책임의 확장 대상이 아니다.
- Scheduler/Engine Gateway 등 대체 구조와의 비교 — 수행된 적 없다.

---

## Risks

- 이 Decision은 "존재" 질문만 Accept했을 뿐, `docs/decisions/adc/ADC.md`의
  ADC-02 항목(Open, 우선순위 NOW) 자체는 이 ADC가 갱신하지 않는다 —
  그 항목의 실제 갱신은 ADR·Baseline Update 단계에서 다룬다(§Next
  Step).
- "존재는 Accept됐다"는 것이 "Runtime 구현을 지금 시작해도 된다"로
  오독될 위험이 있다 — 그런 뜻이 아니다. `IMPLEMENTATION_RULES.md`의
  금지 조항은 Baseline이 실제로 갱신되기 전까지 유효하다(§Implementation
  Boundary).
- Rule B 형식 미충족을 이 ADC가 "범위를 좁혀서" 우회했다는 비판이
  가능하다 — 그러나 그 범위 좁히기는 이 ADC가 아니라 RFC-0013이
  이미 수행했고, 이 ADC는 그 좁힌 범위에 대해서만 판단했다(§Q2).
  넓은 범위(Multi-Task/Workflow)에 대해서는 여전히 Rule B 기준을
  그대로 적용해 미충족으로 남긴다.
- 5개 관찰이 전부 같은 세션·같은 저자에서 나왔다는 사실은 그대로
  남는다 — 향후 이 Decision이 재검토될 경우, 서로 다른 계기의
  독립 관찰이 추가로 쌓이는 것이 이 Decision을 더 견고하게 만든다.

**재검토 조건**: 이 Decision 이후 다음 중 하나가 확인되면 재검토
대상이 된다 — (a) 이 Accept가 실제 Production 맥락에서 부적절했다는
반증 관찰, (b) Multi-Task/Workflow 범위로 확장을 시도했으나 이번
책임 경계로는 부족하다는 관찰.

## Next Step

**ADR Required** — 이 Decision은 `ADC-0008`과 달리 Boundary를
이동시킨다(Not Accepted → Accept, 좁은 범위). 따라서 Baseline
Update가 필요하다.

1. ADR을 작성해 `BASELINE.md`를 갱신한다 — §6 각주 또는 §16에 새
   절을 추가해, "단일 실행 단위 dispatch·격리 책임"의 존재를
   등재하되, §Implementation Boundary의 제외 항목(명칭, 구현 전략,
   Multi-Task 범위)은 계속 Open으로 명시한다.
2. ADR 승인 이후에만 `docs/decisions/adc/ADC.md`의 ADC-02 항목
   상태를 이 Decision을 반영해 갱신한다 — 이 ADC 자신은 그 문서를
   수정하지 않는다.
3. ADR 승인 이후에만 `hqs/development/IMPLEMENTATION_RULES.md`의
   "Runtime 구현 금지" 조항의 재검토가 가능해진다 — 이 ADC는 그
   조항을 지금 해제하지 않는다.
4. 명칭 충돌(`RFC-0004`가 경고) 해소, 구현 전략(Process/Thread/
   Subprocess) 확정, Multi-Task/Workflow 범위 판단은 각각 ADR 이후
   별도 RFC로 다룬다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **좁은 범위에서 그렇다**:
  단일 실행 단위의 dispatch·격리 책임의 "존재"만 Accept했다. 실제
  Baseline 반영은 ADR을 거쳐야 한다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오** —
  Concept의 명칭·위치·Interface는 확정하지 않았다.
- Contract Change — **없음** — 공개 Interface를 정의하지 않았다.
- Baseline 문서(`BASELINE.md`, `docs/decisions/adc/ADC.md`)를
  변경했는가 — **아니오** — 이 ADC 자신은 인용만 했다. 변경은 ADR의
  몫이다.
- ADR이 필요한가 — **예**(§Next Step).

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0013과 그것이 인용한
  `BASELINE.md` §6/§12/§16.2, `ADC.md` ADC-02, `RFC-0008`/`ADC-0008`,
  `RFC-0004`(Dev HQ), `IMPLEMENTATION_RULES.md`,
  `JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
  및 그것이 종합한 5개 Prototype/Vertical Slice 문서만 인용했다.
  새 실험은 하지 않았다.
- Evidence 부족을 이유로 판단을 회피했는가 — **아니오**(작업 지시
  §2 준수). Rule B 형식 미충족과 범위 불일치를 각각 분리해 검토한
  뒤(§Q2), 판단 대상의 범위가 다르다는 것을 근거로 Accept까지
  나아갔다.
- Runtime 존재와 명칭·구현 전략·Multi-Task 범위를 분리했는가 —
  **Pass**(§Implementation Boundary 전체가 이 분리를 명시).
- `ADC-0008`의 Not Accepted를 뒤집었는가 — **아니오**(§Decision
  Rationale) — 서로 다른 범위의 질문에 대한 별개 Decision이다.
- `ADC-0012`의 DEFER와 모순되는가 — **아니오**(§Decision Rationale)
  — `ADC-0012`는 Kernel Component Architecture 전체 착수를,
  이 ADC는 존재 질문 하나만 판단했다.
- `docs/decisions/adc/ADC.md`를 수정했는가 — **아니오**(§Next Step
  2번, ADR 이후로 위임).
- `IMPLEMENTATION_RULES.md`의 금지 조항을 해제했는가 — **아니오**
  (§Implementation Boundary, §Next Step 3번).
- Production Code를 변경했는가 — **아니오**.
- 구현 전략(Process/Thread/Subprocess)을 확정했는가 — **아니오**.
- Runtime의 명칭을 확정했는가 — **아니오**.
- `BASELINE.md` §6의 넓은 정의(Multi-Task/Workflow 분배)를
  Accept했다고 주장했는가 — **아니오**(§Implementation Boundary
  제외 항목에 명시).
