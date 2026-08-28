# RFC-0013: Runtime Existence — Scoped Reconsideration (ADC-02 후속)

**Status**: Resolved — `ADC-0013-runtime-existence-scoped-reconsideration.md`
→ `ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`로
종결됨(Accept, Scoped). RFC 자체는 결정 문서가 아니며, 이 라벨은
절차 진행 상태만 반영한다.
**Author**: Claude Code
**대상**: `docs/decisions/adc/ADC.md` ADC-02("Runtime 개념의 존폐") — Open·NOW.
`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`가 Not
Accepted(based on current evidence)로 남긴 재검토 조건 2번("Runtime
미결정으로 인한 반복 관찰 축적")을 근거로 연다.
**Evidence**: `docs/architecture/baseline/BASELINE.md` §6, §12, §16.2,
`docs/decisions/adc/ADC.md` ADC-02, `docs/architecture/core/RFC-0008-runtime-existence-boundary.md`,
`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`,
`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`,
`hqs/development/IMPLEMENTATION_RULES.md`,
`docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
(7개 Experimental Prototype + Dev HQ Vertical Slice Evidence 종합)

> 본 RFC는 Runtime의 존폐를 결정하지 않는다. Scheduler/Engine
> Gateway 등 대체 구조를 설계하지 않는다. Runtime의 명칭을
> 확정하지 않는다. Process/Thread/Subprocess 구현 전략을 결정하지
> 않는다. 새 실험을 수행하지 않는다 — 이미 병합/기록된 Evidence만
> 인용한다. 이 RFC가 여는 것은 좁은 질문 하나다: **"Jarvis OS에
> Command와 Task로 환원되지 않는 독립적인 실행 dispatch·격리
> 책임이 실제로 필요한가?"**

## 0. 이 RFC가 열린 이유

`ADC-0008-runtime-existence-boundary.md`는 "유지"·"대체" 두 후보
모두 Not Accepted로 남기면서, 재검토 조건 두 가지를 명시했다.

1. "Core Component 검토" 원문 확보.
2. **"Runtime의 세부 구조가 실제로 문제를 일으켰다는 반복
   관찰"**(Governance v2 Rule B의 정신과 같은 종류).

1번은 여전히 충족되지 않았다. 이 RFC는 1번을 다루지 않는다.

2번과 관련해, ADC-0008 이후 다음이 저장소에 추가됐다.

- `ADC-0004-execution-result-consumer.md`(execution-layer) Q3의
  Blocking 관찰(1건, ADC-0008이 이미 인용).
- `projects/` 아래 6개 Experimental Prototype
  (`unified-dashboard` → `command-contract` → `async-command` →
  `inprocess-async-command` → `runtime-boundary` →
  `process-runtime-strategy`, 전부 `main`에 병합됨)과
  `dev-hq-vertical-slice` Prototype 1건이 남긴 Evidence. 특히
  `inprocess-async-command` Prototype은 동일 Target을 Thread로
  동시 실행했을 때 실행 상태(Task 결과)가 서로 오염되는 것을
  재현했다 — 이는 ADC-02가 원래 우려한 "Runtime 버그 보고의 소속
  불명확성"(순수 명명 문제)보다 강한 형태의 문제, 즉 **격리
  경계가 없을 때 실제로 정확성이 깨지는 사례**다.
- `docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md`
  (READ-ONLY Governance Review)가 이 Evidence를 종합해 "존재
  질문에 한해 Accept 방향 근거가 처음으로 갖춰졌다"고 판단했다.

이 RFC는 그 Review의 판단을 그대로 채택하지 않는다 — Review 자체가
Formal Decision이 아니라고 명시했다. 이 RFC는 그 Review가 정리한
Evidence를 근거로, ADC-02의 좁은 부분 집합("존재 여부")을 정식
Boundary Question으로 여는 절차다.

## 1. Problem Statement

`ADC-0008`은 Runtime "유지"(BASELINE §6 정의 그대로) 대 "대체"
(Scheduler + Engine Gateway)라는 두 개의 완성된 대안 사이에서
판단을 시도했고, 어느 쪽도 충분한 근거가 없어 Not Accepted로
남겼다. 이후 축적된 Evidence는 그 원래 질문 전체에 답하지 않는다
— BASELINE §6이 정의한 "Workflow를 참조해 Task를 Agent에게
배분"하는 넓은 책임(Multi-Task/Workflow 수준 분배)은 어떤
Prototype도 테스트하지 않았다. 대신 그보다 좁은 질문 하나에는
답할 만한 근거가 쌓였다: **Command(불변)도 Task(identity/lifecycle)
도 담당하지 않는, 단일 실행 단위의 dispatch·격리 책임이 필요한가?**

이 RFC는 원래 질문을 좁혀서, 이 좁은 질문만 다룬다. 원래의 넓은
질문(Multi-Task/Workflow 분배)과 명칭(Runtime vs 대체 구조)은 이
RFC의 범위 밖에 그대로 남긴다.

## 2. Evidence Summary — 이미 기록된 것만 인용

### 2.1 Architecture Intent — BASELINE이 이미 표시한 설계 의도

`BASELINE.md` §6 Concept Model은 Runtime을 `Service` 분류로 이미
등재해 두었다(Memory, Registry와 함께). §16.2(Execution Layer,
Accept)는 "Specification 기반 AI 실행"이라는 책임 경계(Model/Engine
선택·호출 경계)를 이미 Accept했으나, 그 Accept 자체가 "이 Accept는
ADC-01/ADC-02를 결정하지 않는다"고 스스로 한정했다. 즉 BASELINE은
"실행 관련 무언가가 필요하다"는 Intent는 이미 여러 곳에서 반복
표시했지만, 그 "무언가"의 정체(Runtime인지 다른 것인지)는 계속
미결로 남겨 왔다.

### 2.2 실제 필요성 — 6개 Prototype + Vertical Slice가 축적한 관찰

- `command-contract`: Command를 불변으로 유지하려면 실행 상태를
  보관할 다른 무언가가 필요함을 확인.
- `runtime-boundary`(`rtb_task.py`): Task가 Executor 참조를 전혀
  갖지 않고도 identity/lifecycle을 유지할 수 있음을 코드로 증명
  — 즉 Task 경계 확장 없이도 실행 책임을 분리할 수 있다는 것을
  보여줌.
- `inprocess-async-command`: 격리 책임이 없을 때(Thread 공유 상태)
  동일 Target 동시 실행이 실제로 결과를 오염시키는 것을 재현
  — 정확성이 깨지는 구체적 실패 사례.
- `process-runtime-strategy`: Process 격리로 위 오염이 해소되는
  것을 확인(구현 전략 자체는 이 RFC의 범위 밖).
- `dev-hq-vertical-slice`: Command → Task → (Runtime 역할의)
  Process 실행 → Dev HQ Adapter → Result 저장 → Dashboard 관찰
  전체 경로가 실제 Dev HQ 코드(mock 아님)로 동작함을 E2E로 확인
  (7 tests passed, 전체 Regression 355 passed).

이 다섯 관찰은 전부 **단일 실행 단위**(하나의 Command → 하나의
Task → 하나의 실행) 범위 안에서 얻어졌다. Multi-Task 조합이나
Workflow 수준 배분은 어떤 Prototype도 다루지 않았다.

### 2.3 남아 있는 공백 — 이 RFC가 채우지 않는 것

- BASELINE §6의 원래 정의(Workflow 참조, Multi-Task를 Agent에게
  배분)는 미검증 상태 그대로다.
- `RFC-0004`(Dev HQ, Resolved)가 이미 경고한 이름 충돌 위험 —
  Dev HQ의 Task Dispatcher/Pipeline을 "Runtime"이라 부르면 Jarvis
  OS Concept Model의 "Runtime"(ADC-02 소관)과 충돌한다 — 은 전혀
  해소되지 않았다.
- "Scheduler + Engine Gateway" 대체 구조와의 직접 비교는 어떤
  Prototype도 수행하지 않았다.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  조항은 ADC-02가 Open인 동안 그대로 유효하다 — 이 RFC가 스스로
  해제하지 않는다.

## 3. Pattern

- Architecture Intent(§2.1)는 "실행 관련 책임이 필요하다"는 신호를
  일관되게 남겼으나 그 정체를 스스로 미결로 유보해 왔다.
- 실제 필요성 관찰(§2.2)은 좁은 범위(단일 실행 단위 dispatch·격리)
  에 한해 반복·수렴됐다 — Governance v2 Rule B가 요구하는 "3건
  이상의 독립 관찰" 기준에는 못 미치지만(ADC-0004 Blocking 관찰 1건
  + 이번 세션의 Prototype 클러스터를 하나의 관찰 묶음으로 보면
  총 2묶음), ADC-0008이 "반복 관찰"이라 표현한 재검토 조건의 방향은
  충족하기 시작했다.
- 원래 질문(BASELINE §6 전체 정의)과 실제로 검증된 범위(단일 실행
  단위) 사이에는 여전히 간극이 있다 — 이 간극을 무시하고 원래
  질문 전체에 답하면 근거를 벗어난 결론이 된다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 좁은 질문만 제기한다.

**Jarvis OS는 Command·Task로 환원되지 않는, 단일 실행 단위의
dispatch·격리를 담당하는 독립 책임을 Kernel Concept으로 Accept
하는가?**

| 후보 | 근거 | 근거 성격 |
|---|---|---|
| Accept(좁은 범위) | §2.2의 5개 Prototype/Slice 관찰 | 실행 결과 기반, 반복·수렴 |
| Not Accepted(현행 유지) | §2.3 — Multi-Task 범위 미검증, Rule B 3건 미충족 | 범위·수량 부족 |

이 RFC는 이 중 어느 쪽이 맞는지 판단하지 않는다. 판단은 후속 ADC로
위임한다.

### 이 Boundary Question이 명시적으로 제외하는 것

- **명칭**: "Runtime"이라는 이름을 그대로 쓸지, `RFC-0004`가 경고한
  충돌을 피해 다른 이름(예: Execution Dispatcher)을 쓸지는 이
  RFC도, 후속 ADC도 이 범위에서 결정하지 않는다 — 별도 판단
  대상으로 명시적으로 남긴다.
- **구현 전략**: Process/Thread/Subprocess 중 무엇을 쓸지는 이미
  `process-runtime-strategy` Prototype이 Process를 Evidence 기반
  기본값으로 제시했으나, 그 채택 여부는 이 RFC의 존재 여부 판단과
  분리된 별도 절차(구현 단계)에서 다룬다.
- **Multi-Task/Workflow 수준 분배**: BASELINE §6의 원래 넓은 정의는
  이 RFC의 범위 밖이다 — 별도 Evidence 없이는 다루지 않는다.

## Out of Scope

- Runtime 존재 여부의 실제 판단(§4에 위임).
- Scheduler/Engine Gateway 등 대체 구조의 설계.
- Runtime의 명칭 결정.
- Process/Thread/Subprocess 구현 전략 결정.
- BASELINE §6 원래 정의(Multi-Task/Workflow 분배)의 검증 또는 수정.
- `RFC-0004`가 남긴 Dev HQ ↔ Jarvis OS 명칭 충돌의 해소.
- `ADC-0004-execution-result-consumer.md`(execution-layer)의
  재판단 — 그대로 유지된다.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정 — 전혀 하지
  않는다.
- 새로운 실험 — 이미 기록된 Evidence만 인용한다.

## Non-goals

- 이 RFC는 Runtime 개념의 존폐를 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 대체 구조나 명칭을 설계·확정하지 않는다.
- 이 RFC는 구현 전략을 결정하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 §4의 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §4 Boundary Question(좁은 범위의 dispatch·격리 책임 존재 여부)을
   지금 Evidence로 Accept할 수 있는지, 아니면 Governance v2 Rule B의
   3건 기준 미충족을 이유로 계속 Not Accepted로 남길지.
2. Accept된다면, 그 Decision이 Baseline Update(ADR)로 이어질 때
   무엇을 확정하고 무엇을 계속 Open으로 남길지 — 최소한 명칭과
   Multi-Task 범위는 이 RFC와 동일하게 후속 절차로 넘기도록 제안한다.
3. Accept되지 않는다면, ADC-0008이 이미 제시한 두 재검토 조건 중
   1번("Core Component 검토" 원문 확보)이 여전히 유일한 남은 경로임을
   재확인한다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `BASELINE.md`, `ADC.md`,
  `RFC-0008`/`ADC-0008`, `RFC-0004`(Dev HQ),
  `IMPLEMENTATION_RULES.md`, 그리고 이미 병합/기록된 7개
  Prototype과 Governance Review 문서만 인용했다. 새 실험은
  수행하지 않았다.
- Runtime 존폐를 결정했는가 — **아니오**. §4는 질문 형태로만
  남겼다.
- 대체 구조(Scheduler/Engine Gateway)를 설계했는가 — **아니오**.
- Runtime의 명칭을 확정했는가 — **아니오**. §4가 명시적으로
  제외했다.
- 구현 전략(Process/Thread/Subprocess)을 결정했는가 — **아니오**.
  §4가 명시적으로 제외했다.
- BASELINE §6의 원래 넓은 정의(Multi-Task/Workflow 분배)를
  검증했다고 주장했는가 — **아니오**. §2.3에서 미검증임을 명시했다.
- `RFC-0004`의 이름 충돌 경고를 해소했다고 주장했는가 — **아니오**.
  §2.3에서 미해소임을 명시했다.
- `ADC-0004-execution-result-consumer.md`의 Not Accepted 상태를
  뒤집었는가 — **아니오**. Out of Scope에 명시했다.
- Production Code를 수정했는가 — **아니오**.
- ADC, ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
