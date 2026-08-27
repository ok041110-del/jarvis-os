# JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001: ADC-02 Runtime Existence Boundary — Reconsideration Review

**문서 성격**: READ-ONLY Governance Review(작업 지시 §8). Formal
Architecture Decision이 아니다 — `docs/decisions/adc/ADC.md`의
ADC-02 상태, `BASELINE.md`, Structure v1.0을 이 문서가 직접
변경하지 않는다. Production `core/`, `hqs/`, `dashboard/`도
무수정이다. 이 문서는 **재검토를 제안**할 뿐, ADC-02를 대신
결정하지 않는다 — 실제 결정은 별도 RFC → ADC → ADR 절차를 통해서만
유효하다.

**질문(작업 지시 §1로 한정)**: "Jarvis OS에 독립적인 Runtime 책임이
실제로 필요한가?" — Process/Thread/Subprocess 등 구현 전략은 이
질문에서 분리한다(작업 지시 §2).

**결론**: **재검토 개시를 권고한다 — "존재" 질문에 한해 Accept
방향의 근거가 처음으로 갖춰졌지만, 그 범위는 BASELINE §6의 원래
Runtime 정의보다 좁다.** 7개 Prototype과 Dev HQ Vertical Slice는
"단일 실행 단위를 비동기로 시작하고 격리하는 책임"이 Command(불변)
에도 Task(identity/lifecycle)에도 속할 수 없다는 것을 반복적으로,
기능적 오류(결과 오염)까지 동반해 실증했다. 이는 ADC-02가 원래
우려한 "이름이 가리키는 대상이 불분명하다"는 문제보다 **더 강한
형태의 문제**(실제 정확성 결함)다. 그러나 이 Evidence가 실증한
책임은 BASELINE §6의 "Runtime은 Workflow를 참조하여 Task를
Agent에게 배분한다"는 **Workflow 수준의 넓은 정의보다 훨씬 좁다**
(단일 실행 단위의 비동기 시작·격리일 뿐, Multi-Task 분배·Workflow
참조는 검증한 적이 없다). 따라서 이 문서는 **"Runtime 존재"를
지금 이 자리에서 Accept로 확정하지 않는다** — 대신 이 Evidence를
근거로 새 RFC를 열어, 범위를 좁게 한정한 "존재" 질문만 다시
대조할 것을 권고한다(§7).

---

## 1. 기존 Decision 재확인(구현 전 재검토, 작업 지시 서두)

- **`docs/decisions/adc/ADC.md` ADC-02**: "Runtime 개념의 존폐" —
  **Open, 우선순위 NOW**(변경 없음, 이 문서가 갱신하지 않음). "충돌
  내용": Concept Model은 Runtime을 Service로 유지하나, "Core
  Component 검토"는 폐기하고 Scheduler + Engine Gateway로 대체할
  것을 권고. "미결정 시 문제": **"Runtime 버그"라는 보고가 어느
  Component를 가리키는지 구분 불가**(순수 용어/귀속 문제로 기술됨).
- **`ADC-0008-runtime-existence-boundary.md`**(RFC-0008 후속): Q0
  ("유지" 후보)와 Q1("대체" 후보) 모두 **Not Accepted** — "유지"
  근거(BASELINE §6)는 원문이 스스로 미결정임을 명시해 확정 근거가
  못 되고, "대체" 근거("Core Component 검토")는 결론 문구만 있고
  추론 과정이 저장소 어디에도 없어 채택 불가. **재검토 조건**: (1)
  "Core Component 검토" 원문 확보, 또는 (2) "Runtime 미결정으로
  인한 반복 관찰" 축적 — 둘 중 하나가 채워지면 **새 RFC**로 재검토.
- **`BASELINE.md` §6**: "Runtime은 Workflow를 참조하여 Task를
  Agent에게 배분한다." — 다른 Concept(Task→Engine Port 실제 연산,
  HQ→Registry 등)과 나란히, **Workflow 그래프 순회·Multi-Task
  분배**라는 넓은 정의로 기술되어 있다. 같은 절 각주가 이 상태를
  "세부 구조는 Open Decision(ADC-02)"이라고 스스로 유보한다.
- **`BASELINE.md` §16.2**(Execution Layer, Accept): 책임은
  "Specification 기반 AI 실행"(코드 생성·실행·테스트, Model/Engine
  선택·호출까지)이다. 그 Accept가 **"결정하지 않는 것"**으로
  ADC-01·ADC-02를 명시적으로 남겨둔다 — 즉 Execution Layer의
  Accept는 "무엇을 하는가(경계)"만 확정했고, "그 실행을 어떻게
  dispatch·격리하는가(내부 구조)"는 여전히 미정이다.
- **`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`**
  (Dev HQ 수준, Resolved): MVP-0005가 "Stage 객체 + 이를 순회
  실행하는 Runtime" 구조를 요구했을 때, 이 RFC는 **그 결과물을
  "Runtime"이라 부르는 것이 Jarvis OS Concept Model의 "Runtime"과
  이름이 겹치는 문제를 일으킬 수 있다**는 것을 명시적으로 경계로
  남겼다(§4, "Development HQ ADC는 ADC-02를 해결할 권한이 없다").
  이번 재검토에서도 동일한 이름 충돌 위험이 반복된다(§6).
- **`hqs/development/IMPLEMENTATION_RULES.md`**: "Runtime 구현 금지
  — Runtime 개념 자체가 Open Decision(ADC-02)이다." (Production Dev
  HQ MVP 범위에 적용, 이번 문서가 변경하지 않음.)

---

## 2. 검토한 Evidence(7개 Prototype + Vertical Slice)

작업 지시 §4가 핵심 근거로 지정한 Vertical Slice를 포함해, 관련된
6개 Experimental Prototype 전부를 다시 대조했다(모두 main에 병합
완료, Production 무수정 확인된 상태).

| Prototype | Runtime 관련 핵심 발견 |
|---|---|
| `unified-dashboard` | (직접 관련 없음 — Dashboard Observe 원칙만) |
| `command-contract` | Command 불변, Task 불필요(이 범위) — Runtime 질문 자체가 아직 제기되지 않음 |
| `async-command`(subprocess) | Task=CANDIDATE(Command 불변성 보호). **Runtime=NOT REQUIRED**(subprocess가 이미 비동기·격리를 공짜로 제공) |
| `in-process-async-command`(Thread) | 동일 실제 대상을 Thread로 동시 실행하면 `monkeypatch` 상태가 실제로 섞여 **진짜 테스트 실패가 재현됨**(`assert 2 == 1` 등, 단순 카운트 오류 아님). **Runtime=CANDIDATE로 격상** |
| `runtime-boundary`(Sequential/Thread/Process) | Process는 동일 대상 동시 실행에서 항상 정확·안정, Thread는 결과 오염뿐 아니라 대상 코드 내부 ThreadPoolExecutor와 중첩되어 실행 시간이 예측 불가능해짐(0.03초→최대 43초). **Task(identity/lifecycle)와 Runtime(scheduling/isolation)이 코드로 실제 분리 가능함을 실증**(`rtb_task.py`가 Executor를 전혀 참조하지 않고 동작) |
| `process-runtime-strategy` | Process가 필요한 조건은 "동시 실행 자체"가 아니라 **"동일 Target 동시 실행"**로 좁혀짐 — 다른 대상은 Thread로도 3회 반복 전부 정확(Dev HQ 내부 파일 간에도 재확인) |
| `dev-hq-vertical-slice`(E2E) | Command→Task→Runtime→Dev HQ Adapter→Result 저장→Dashboard 전체 경로가 실제로 관통 연결됨을 확인. **단, 이 Slice 자체는 "동일 Target 동시 실행" 조건을 만들지 않아 Process가 이 Slice 안에서 필수임을 새로 증명하지는 못했다**(해당 Evidence 문서 §8이 이미 정직하게 기록) |

**일관되게 재확인된 것**: Command는 실행 상태를 담으면 불변성이
깨진다 → 실행 상태는 Command 밖에 있어야 한다. Task가 그 실행
상태(identity/lifecycle)를 담을 수 있다 → 그러나 Task는 "어떻게
실행할 것인가(dispatch·격리)"까지 담당하면 Executor를 직접
참조하게 되어 §Task/Runtime 분리 원칙이 깨진다(실제로
`rtb_task.py`가 Executor를 전혀 모른 채 세 전략 모두에서 정상
동작한 것으로 반증됨). **따라서 Command도 아니고 Task도 아닌 제3의
책임이 실행 dispatch·격리를 맡아야 한다는 것이, 5개 Prototype에
걸쳐 서로 다른 실행 대상·전략으로 반복 관찰됐다.**

---

## 3. Q0 — Architecture Intent(작업 지시 §3, "Evidence 부족으로 중단하지 않는다")

`ADC-0008`은 BASELINE §6의 "Runtime은 Concept으로서 Baseline에
유지되나..."라는 원문을, "적극적 근거가 아니라 현상 유지 서술"로
판단해 Accept 근거로 인정하지 않았다. 이 판단 자체는 뒤집지
않는다 — 그러나 Architecture Intent를 "그 원문 하나"로만 보지
않고 Kernel 전체 설계 원칙과 함께 보면 다른 그림이 보인다.

- `BASELINE.md` §12 Kernel Design Principles(KP-1): "Kernel은
  Component가 아니라 Responsibility"라는 원칙 자체가, 어떤 책임이
  실제로 존재한다면 그것을 담을 Concept이 있어야 한다는 것을
  전제한다.
- §6 Concept Model은 Runtime을 Memory/Registry와 나란히 **Service**
  분류에 이미 배치해 두었다 — Workflow(Definition)나 Task(Process)
  와는 다른 분류다. 이는 "실행을 조율하는 무언가"가 Concept
  Model의 설계 당시부터 이미 상정되어 있었다는 의도의 흔적이다.
- 이 Intent는 (ADC-0008이 옳게 지적했듯) 단독으로 Accept 근거가
  되지 못한다. 그러나 §2의 새 기능적 Evidence와 **결합**하면
  의미가 달라진다: Intent가 "그런 책임이 있을 것"이라고 예상해 둔
  자리에, 이제 그 책임이 실제로 필요하다는 기능적 반증이
  더해졌다.

---

## 4. Q1 — 실제 구현 필요성(작업 지시 §3)

§2의 Evidence가 답하는 것은 "Runtime이라는 이름의 Concept이
필요한가"가 아니라 **"Command와 Task 둘 다로 환원되지 않는 제3의
실행 dispatch·격리 책임이 실제로 필요한가"**다. 이 질문에는
Evidence 기반으로 **예**라고 답할 수 있다:

1. Command에 담으면 불변성이 깨진다(Case A, 5개 Prototype에서
   반복 재현).
2. Task에 담으면(Executor를 직접 참조하게 하면) Task의 "identity/
   lifecycle만" 원칙이 깨지고, 실제로 `rtb_task.py`는 그렇게 하지
   않고도 동작해 이 책임이 Task 밖에 있어야 함을 반증했다.
3. 이 책임을 아예 두지 않고 "그냥 Thread로 부르면 된다"고
   가정하면, 동일 대상 동시 실행에서 **실제 정확성 결함**이
   재현된다(§2, `in-process-async-command`) — 이것은 ADC-02가
   원래 우려한 "이름 혼동" 수준을 넘어서는, 실제로 틀린 결과를
   만드는 문제다.
4. Dev HQ Vertical Slice(§4 지정 핵심 근거)는 이 책임을 Command/
   Task와 분리해 별도 모듈(`rtb_runtime.py`)에 둔 구조가, 실제
   E2E 경로(사용자 입력→Command→Task→Dev HQ 실행→Result 저장→
   Dashboard 관찰)에서 **아무 문제 없이 동작함**을 보여줬다 —
   분리된 구조가 실제로 작동한다는 긍정적 Evidence다.

---

## 5. Q2 — 이 Evidence가 답하지 못하는 것(정직한 범위 한정)

- **Multi-Task 분배는 검증된 적이 없다.** BASELINE §6의 Runtime
  정의("Workflow를 참조하여 Task를 Agent에게 배분한다")는 하나의
  Workflow 안에서 여러 Task를 여러 Agent에게 나누는 것을 말한다.
  7개 Prototype 전부 **단일 실행 단위**(pytest 대상 하나)를
  비동기로 시작·관찰한 것이지, Workflow 그래프를 순회하며 여러
  Task를 여러 Agent에 분배한 적은 없다.
- **"Scheduler + Engine Gateway로 대체" 후보를 직접 비교하지
  않았다.** ADC-02의 원래 두 후보("유지" vs "대체")에서, 이 Evidence
  는 "유지"(Runtime을 Concept으로 둔다)를 뒷받침하는 쪽에 가깝지만,
  "대체" 구조(Scheduler + Engine Gateway로 나눴을 때도 같은 문제가
  해결되는지)를 실제로 실험한 적은 없다 — `rtb_runtime.py`가
  "Scheduler"에 더 가까운지 "Runtime"에 더 가까운지는 이름의
  문제이지 이 Evidence가 결정한 것이 아니다.
- **RFC-0004(Dev HQ)가 이미 경고한 이름 충돌이 그대로 반복된다.**
  "그 결과물을 'Runtime'이라 부르는 것이 Jarvis OS Concept Model의
  'Runtime'과 겹치는 것을 피해야 하는가?"라는 질문에 이 문서도
  답을 주지 못한다 — `rtb_runtime.py`라는 이름을 그대로 Jarvis OS
  Concept Model의 "Runtime"으로 승격해도 되는지는 별도 판단이
  필요하다.
- **반복 관찰의 "반복" 성격이 완전하지 않다.** `ADC-0008`의 재검토
  조건 2번("Runtime 미결정으로 인한 반복 관찰")은 서로 다른
  독립적 계기에서 여러 번 관찰되는 것을 뜻한다. 이번 Evidence는
  전부 **같은 저자(Claude Code)가 같은 세션 안에서 설계한 연속
  Prototype**에서 나왔다 — `ADC-0004-execution-result-consumer.md`
  가 남긴 1건(Execution Result Consumer 판단이 막힘)과 합치면
  최소 2개의 서로 다른 계기가 있지만, Governance v2 Observation
  Layer의 Rule B(3건 이상)에는 아직 못 미친다.

---

## 6. 판단 — 재검토는 열되, Accept를 이 자리에서 확정하지 않는다

작업 지시 §5·§6은 "필요하다고 판단되면 Decision을 제안"하고
"RFC→ADC→ADR 절차를 제시"하라고 요구한다. §4의 실제 필요성
Evidence는 충분히 강하지만, §5의 범위 불일치(Multi-Task 분배
미검증)와 이름 충돌 위험(RFC-0004가 이미 경고)이 남아 있으므로,
이 문서가 직접 "Runtime 존재 = Accept"를 선언하는 것은 근거를
넘어서는 것이다(ADC-0008이 "억지로 결론 내리지 않는다"고 정한
원칙과 같은 이유). 대신 **다음 절차로 넘긴다**:

**권고 Decision 방향**(제안일 뿐, 확정 아님): "Command와 Task로
환원되지 않는 단일 실행 단위의 dispatch·격리 책임은 **존재해야
한다**(Accept, 좁은 범위)" — 단, (a) 이 책임을 "Runtime"이라는
이름으로 Jarvis OS Concept Model에 그대로 편입할지, 별도 이름
(예: "Execution Dispatcher")으로 둘지, (b) BASELINE §6의 넓은
Multi-Task 분배 책임까지 같은 Concept이 흡수할지는 **이 재검토가
결정하지 않고 새 RFC로 넘긴다.**

---

## 7. Next Step — RFC → ADC → ADR 절차 제안(작업 지시 §6)

구현 전략(Process/Thread/Subprocess)은 이 절차 어디에서도
확정하지 않는다.

1. **새 RFC 개설**: 제목(가칭) "Runtime Existence — Scoped
   Reconsideration(ADC-02 후속)". Evidence로 이 문서와 7개
   Prototype Evidence 문서 전체를 인용한다. **범위를 명시적으로
   좁힌다** — "단일 실행 단위의 dispatch·격리 책임 존재 여부"만
   다루고, Multi-Task 분배·Workflow 참조·구현 전략(Process/Thread/
   Subprocess)·이름(Runtime vs Scheduler+Engine Gateway vs
   Execution Dispatcher)은 각각 별도 Open Question으로 명시만
   하고 이 RFC의 결정 범위에서 제외한다.
2. **ADC 재판단**: 새 RFC의 Evidence를 근거로 ADC-02를 다시
   대조한다(`ADC-0008`을 대체하는 것이 아니라, 그 문서가 예고한
   "재검토 조건 충족 시" 절차를 따르는 후속 ADC). 가능한 Decision:
   "존재 Accept(좁은 범위) / 이름과 넓은 범위는 Open으로 유지."
3. **ADR**: ADC가 "존재 Accept"로 판단되는 경우에만 필요 — Baseline
   Update(§16에 새 Kernel Module 절 추가 또는 §6 각주 갱신)가
   뒤따른다. 이 ADR은 구현 전략이나 이름을 확정하지 않는다(§6
   Decision 범위 그대로).
4. **이름 충돌 해소는 별도 Decision**: RFC-0004(Dev HQ)가 이미
   제기한 "Runtime 이름 재사용 문제"를 이 RFC가 함께 다룰지, 별도
   RFC로 분리할지도 그 RFC 자신이 스코프 결정 시 명시해야 한다.

이 문서는 이 절차를 **제안**할 뿐 개시하지 않는다 — RFC 개설은
사용자 승인 이후의 별도 작업이다.

---

## 8. Architecture / Contract / Kernel 영향

- **Architecture Change**: 없음 — `ADC.md`의 ADC-02 상태(Open,
  NOW)를 이 문서가 변경하지 않는다.
- **Contract Change**: 없음.
- **Kernel Impact**: 없음(직접) — 재검토를 권고했을 뿐, Kernel
  Module을 추가하거나 확정하지 않았다. `BASELINE.md` §16.3("미결
  항목")과 §6 각주는 그대로 유효하다.
- **Production Code**: 무수정(READ-ONLY Review, 작업 지시 §8).

---

## 9. Self Review

- Evidence만 사용했는가 — Pass. 7개 Prototype Evidence 문서,
  `ADC.md`, `ADC-0008`, `BASELINE.md` §6/§12/§16, `RFC-0004`(Dev
  HQ), `IMPLEMENTATION_RULES.md`만 인용했다. 새 실험은 하지
  않았다.
- Evidence 부족을 이유로 중단했는가 — 아니오(작업 지시 §3 준수).
  Architecture Intent(§3)와 실제 필요성(§4)을 함께 평가해 "재검토
  개시"라는 구체적 판단까지 내렸다 — `ADC-0008`처럼 "Not Accepted"
  로만 멈추지 않았다.
- Runtime 존재와 구현 전략을 분리했는가 — Pass(§1 원칙, §6·§7
  전체가 전략을 명시적으로 제외).
- Vertical Slice를 핵심 근거로 썼는가 — Pass(§2 표, §4-4).
- 억지로 Accept를 선언했는가 — 아니오(§6) — 범위 불일치(§5)를
  근거로 "재검토 권고"에서 멈췄다. 이는 회피가 아니라, §5가 실제로
  답하지 못하는 질문(Multi-Task 분배, 이름 충돌)이 남아 있기
  때문이다.
- Production Code를 변경했는가 — 아니오.
- RFC/ADC/ADR을 이 문서가 직접 만들었는가 — 아니오(§7에서 제안만).

---

Architecture Change: 없음(ADC-02 상태 Open·NOW 유지, 이 문서가 변경하지 않음)
Contract Change: 없음
Production Code Change: 없음
Tests: 해당 없음(코드 변경 없음, 기존 7개 Prototype 테스트 355 passed 상태 그대로 재인용)
E2E: 해당 없음(신규 실행 없음, `dev-hq-vertical-slice` Evidence의 기존 E2E 결과를 인용)
RFC: 없음(§7에서 신규 RFC 개설을 제안, 이 문서가 개설하지 않음)
ADC: 없음(ADC-02는 Open·NOW 그대로, 이 문서가 갱신하지 않음)
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (커밋 예정)
Branch: `claude/adc-02-runtime-existence-reconsideration`(계보: `claude/dev-hq-vertical-slice-prototype`에서 분기 — 핵심 근거로 인용하는 Vertical Slice Evidence 문서가 아직 main에 병합되지 않았기 때문)
Next Implementation Candidate: §7의 "Runtime Existence — Scoped Reconsideration" RFC 개설 여부 — 사용자 결정 필요(승인 시 새 RFC 문서 작성이 다음 작업)
