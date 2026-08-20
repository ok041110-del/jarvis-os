# RFC-0004: Task Dispatcher → Runtime 승격 Boundary (Governance v2, Rule A)

**Status**: Resolved — `docs/governance/adc/ADC-0004.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (MVP-0005 요청에 대한 Governance v2 절차 적용)
**대상 Candidate**: Task Dispatcher (단 하나)
**Governance v2 근거**: Rule A(RT Trigger 충족 → RFC), `docs/governance/observations/OBS-0001.md`,
`docs/governance/observations/OBS-0002.md`

> 본 RFC는 Kernel의 구현 방법을 제안하지 않는다.
> 본 RFC는 MVP에서 관찰된 Kernel Extraction Candidate의 Boundary만 논의한다.

## 0. 이 RFC가 열린 절차 (Governance v2 Rule A)

이 RFC는 새로운 코드 실행 없이, 이미 존재하는 두 OBS 문서만으로 Rule A를
충족해 열렸다.

- `OBS-0001`: MVP-0002에서 하드코딩된 Task 호출 체인이 2개가 된 사실
  (RT-0001 Task Dispatcher Trigger "체인 수 ≥ 2" 충족)
- `OBS-0002`: MVP-0004에서 그 체인이 5단계짜리 3번째 체인으로 늘어난 사실

`docs/governance/rt/RT-0001.md`의 Task Dispatcher Trigger("Workflow
Branch 발생, 또는 하드코딩된 Task 호출 체인 수 ≥ 2")는 이 두 OBS만으로
이미 충족된다. Rule A는 "RT Trigger 충족 → RFC"이므로, 이 RFC는 그
조건 충족 확인만으로 열렸다. 두 OBS 모두 Status를 `Absorbed into
RFC-0004`로 갱신했다.

## 1. Background — 이번 RFC를 지금 여는 이유

Development HQ의 다음 목표로 "MVP-0005: Development HQ Runtime"이
제시되었다. 요청 원문의 핵심은 다음과 같다.

> Pipeline Runtime — 각 Stage는 실행 가능한 객체(`run()`)로 표현하고,
> Stage를 순차 실행하는 최소 Runtime을 구현한다.

이는 지금까지의 Task Dispatcher 구현 형태(파일마다 하드코딩된 함수 호출
나열: `workflow.py`, `workflow_0002.py`, `workflow_hello_sdlc.py`)와
질적으로 다르다. 지금까지는 "무엇을 호출할지"가 코드에 직접 쓰여 있었고,
요청된 형태는 "실행 가능한 객체 목록을 순회하며 호출하는 일반화된
실행기"다. `development-hq/IMPLEMENTATION_RULES.md`는 이를 다음과 같이
명시적으로 금지한다.

> Runtime 구현 금지 — Runtime 개념 자체가 Open Decision(ADC-02)이다.

또한 `docs/03_adc/ADC.md`의 ADC-02("Runtime 개념의 존폐")는 Jarvis OS
수준에서 아직 Open 상태(우선순위 NOW)다: "Concept Model은 Runtime을
Service로 유지하나, Core Component 검토에서는 Runtime을 폐기하고
Scheduler + Engine Gateway로 대체할 것을 권고함."

즉 이번 요청은 (a) 이미 RT-0001이 충족된 Task Dispatcher Candidate의
재평가와, (b) "Runtime"이라는 이름 자체가 걸린 Jarvis OS 수준의 미해결
결정(ADC-02) 두 가지를 동시에 건드린다. 이 RFC는 그중 (a)만 Development
HQ ADC 대상으로 다루고, (b)는 §4에서 별도로 경계만 기록한다.

## 2. Observation (OBS-0001, OBS-0002에서 그대로 인용)

- 하드코딩된 Task 호출 체인은 MVP-0001(2-Task) → MVP-0002(조건 분기
  포함 2-Task) → MVP-0004(5단계, 5개 함수 호출)로 이어지며 개수와
  길이가 늘어났다.
- 각 체인에서 Implementation Stop Trigger(조건문이 파서/설정 파일로
  대체되려는 순간)는 한 번도 발생하지 않았다.
- 지금까지 세 체인 모두 "각 Stage를 실행 가능한 객체로 표현"하지 않고,
  함수를 직접 순서대로 호출하는 형태였다.
- MVP-0005 요청은 이 형태를 "Stage 객체 + 이를 순회 실행하는 Runtime"
  구조로 바꿀 것을 요구한다. 이 구조 변경은 아직 코드로 존재하지 않는다
  (이 RFC 시점 기준).

## 3. Boundary Question (Task Dispatcher, Development HQ ADC 대상)

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

1. 하드코딩된 Task 호출 체인이 3개(MVP-0001/0002/0004)로 늘어난 지금도
   Task Dispatcher는 "각 파일에 하드코딩된 순차 호출을 반복해서 쓰는"
   현재 형태로 계속 남아야 하는가, 아니면 이 반복 자체가 승격을
   재검토할 시점을 의미하는가?
2. "Stage를 실행 가능한 객체(`run()`)로 표현"하는 것과, "그 객체들을
   순회 실행하는 최소 Runtime을 두는" 것은 서로 다른 결정인가, 하나가
   다른 하나를 자동으로 요구하는가?
3. 만약 Task Dispatcher가 승격된다면, 그 결과물을 "Runtime"이라는
   이름으로 부르는 것이 맞는가, 아니면 Jarvis OS Concept Model의
   "Runtime"(§4 참조)과 이름이 겹치는 것을 피해야 하는가?

## 4. Boundary Risk — Jarvis OS 수준 ADC-02와의 경계 (기록만, 해결하지 않음)

`docs/01_architecture/BASELINE.md` §6 Concept Model은 Runtime을 다음과
같이 정의한다: "Runtime은 Workflow를 참조하여 Task를 Agent에게
배분한다." 이 개념 자체의 존폐가 `docs/03_adc/ADC.md`의 ADC-02로 아직
Open 상태다.

MVP-0005가 요청한 "Pipeline Runtime"이 만약 승격된다면, 그 구현체가
Jarvis OS Concept Model의 "Runtime"과 같은 것인지, Development HQ 내부의
별개 개념(예: 단순 "Stage Executor")인지는 이 RFC가 결정하지 않는다.
Development HQ ADC는 ADC-02를 해결할 권한이 없다(Jarvis OS Architecture
Baseline은 Frozen이며, ADC-02는 Jarvis OS `docs/03_adc/ADC.md` 소관이다).
이 경계는 RFC-0003 §4.2·§14가 Engine Gateway/Multi-Model에 대해 이미
남긴 것과 같은 종류의 경계다: Development HQ가 자체적으로 결정할 수
있는 범위(Task Dispatcher 승격 여부)와, Jarvis OS 수준 결정이 선행되어야
하는 범위(그 결과물이 "Runtime" Concept과 같은 것인지)를 분리해 둔다.

## Non-goals

- 이 RFC는 Task Dispatcher나 Runtime을 어떻게 구현할지 논의하지 않는다.
- 이 RFC는 Stage 객체의 인터페이스(`run()` 시그니처 등)를 설계하지
  않는다.
- 이 RFC는 ADC-02(Jarvis OS 수준 Runtime 개념 존폐)를 해결하지 않는다.
- 이 RFC는 Engine Gateway, Registry, Context 전달 메커니즘을 다루지
  않는다.
- 이 RFC는 Architecture Baseline이나 Development HQ Baseline을 변경하지
  않는다.
- 이 RFC는 위 질문에 답하지 않는다.
- 이 RFC는 MVP-0005의 코드를 구현하지 않는다. MVP-0005 구현은 이 RFC의
  다음 절차(ADC-0004)가 끝난 뒤에만 진행된다.

## 다음 절차

ADC-0004에서 다음을 판단한다.

1. Task Dispatcher 승격 여부(Promote to Kernel / Keep in MVP / Defer) —
   Development HQ ADC의 권한 범위.
2. "Stage를 실행 가능한 객체로 표현하는 것"과 "Runtime을 구현하는 것"이
   같은 결정 단위인지, 분리 가능한지.
3. §4의 Jarvis OS 경계(ADC-02)를 Development HQ가 넘지 않도록, 승격이
   결정되더라도 그 결과물의 명칭·범위를 어떻게 한정할지.

이 RFC 자체는 위 3개 중 어느 것도 결정하지 않는다.
