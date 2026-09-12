# RFC-0027: Multi-Agent Runtime — Contract Candidate 조사 및 Boundary (Phase D)

**Status**: Proposed (조사·판단 결과 기록, Baseline 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §6(Concept Model:
Runtime/Resource)·§16.2(Execution Layer)·§16.3(Execution Host)·§16.4
(Multi-Task)·§16.6(Workflow Adapter), `docs/decisions/adc/ADC.md`
ADC-02(Runtime 개념의 존폐, Open, NOW), `docs/architecture/core/ADC-0008`
(Runtime 존폐, Not Accepted)·`ADC-0011`(Standalone Execution Location
Boundary, Not Accepted)·`ADC-0012`(Dispatch Component Boundary, Defer)·
`ADC-0027`~`ADC-0031`/`ADR-0015`~`ADR-0017`(OmniRoute Thin Engine Caller,
Production Adopted, Scoped), `hqs/development/IMPLEMENTATION_RULES.md`
(Scheduler/Registry/Event Bus/넓은 Runtime 구현 금지), `RFC-0024/ADC-0032`·
`RFC-0025/ADC-0033`·`RFC-0026`(Phase A/B/C — 전부 Defer/Open 또는 "이미
Decided, 재정의 불필요").

**Evidence**: 위 문서 전체, `hqs/development/mvp/execution_host.py`
(§16.3 Production 구현), `hqs/development/mvp/omniroute_engine.py`
(Engine Adapter/OmniRoute Production 구현), Production 코드 전체에서
`Runtime`/`Scheduler`/`AgentManager`/`Registry` 클래스 부재를 grep으로
확인. **새로운 실험·프로토타입·측정은 수행하지 않는다.**

> 이 RFC는 Phase A~C(`RFC-0024`/`ADC-0032`, `RFC-0025`/`ADC-0033`,
> `RFC-0026`)의 결과를 **전제**로 삼는다 — Agent Domain/Lifecycle/State/
> Message/Event 전부 Defer/Open, §16.6 Workflow Adapter의 Task 그래프
> 구성 요소는 이미 Decided(Scoped, Conditional, Production 차단). 이
> RFC는 이들을 재확정하지 않으며, 특히 **ADC-02(Runtime 존폐)를 이
> Phase가 대신 판정하지 않는다.**

---

## 0. 이 RFC가 열린 이유

사용자가 지정한 Phase D는 "Runtime Contract"를 후보로 정의하라는
것이다. 조사 결과, 이 질문은 이 저장소에서 **이미 살아 있는 최우선
Open Decision과 문자 그대로 같은 질문**이다 — `docs/decisions/adc/ADC.md`
ADC-02 "Runtime 개념의 존폐"는 **상태 Open, 우선순위 NOW**로 지금도
등록되어 있다. 이 RFC가 새로 "Runtime Candidate"를 정의하면, 그것은
새 질문을 여는 것이 아니라 **이미 Open인 ADC-02를 별도 이름으로
재상정하는 것**이 된다. 따라서 이 RFC의 실질 임무는 Phase C와
동형이다 — "Runtime"이라는 한 단어 아래 실제로는 여러 층위가 섞여
있으므로, 이미 Accept(Scoped)된 조각과 여전히 ADC-02 하나로 수렴하는
미결 조각을 정확히 가르는 것이다.

## 1. Problem Statement

`BASELINE.md` §6은 Runtime을 "Workflow를 참조하여 Task를 Agent에게
배분하는 서비스(세부 구조는 ADC-02, Open)"로 정의한다. 그러나 실제로는
이 한 문장이 가리키는 책임이 최소 4갈래로 이미 쪼개져 각자 다른
Governance 상태를 갖고 있다.

1. 단일 실행 단위의 dispatch·격리 → **Execution Host**(§16.3, Accept
   Scoped) — Runtime 항목의 **재명명이 아니라 별개의 더 좁은 개념**
   (`ADC-0014` §Q2가 명시).
2. 독립 실행 단위의 동시 실행·결과 수집 → **Multi-Task**(§16.4, Accept
   Scoped Conditional).
3. 이미 고정된 그래프의 조건부 분기·Loop 진행 → **Workflow
   Adapter**(§16.6, Accept Scoped Conditional).
4. 외부 Model/LLM Provider 호출 → **Engine Adapter**(§16.2 내부 갈래,
   OmniRoute Thin Engine Caller Case A로 Production Adopted, `ADR-0017`).

이 네 조각을 다 더해도 §6 원문의 "Task를 **Agent에게 배분**"이라는
핵심 동사는 여전히 채워지지 않는다 — **어느 Agent가 무엇을 수행할지
동적으로 결정하는 책임**(Scheduler/Dynamic Routing)은 네 조각 모두가
명시적으로 제외한 영역이며, 그것이 바로 ADC-02가 미결로 남겨 둔
정확한 나머지다. 이 RFC는 이 사실을 근거를 대며 확인한다.

## 2. Evidence Summary — 이미 결정된 네 조각

| 조각 | Governance 근거 | 상태 | Runtime 전체와의 관계 |
|---|---|---|---|
| Execution Host(§16.3) | `RFC-0013`/`ADC-0013`/`ADC-0014`/`ADC-0015` | Accept(Scoped) — Production 구현 존재(`execution_host.py`) | §6 "Runtime" 항목의 **재명명 아님**(`ADC-0014` §Q2) — 별개의 더 좁은 Concept |
| Multi-Task(§16.4) | `RFC-0016`/`ADC-0016` | Accept(Scoped, Conditional) | "Agent 동적 선택은 포함하지 않는다"(§16.4 원문) — Runtime의 "배분" 동사 제외 |
| Workflow Adapter(§16.6) | `RFC-0019`~`0021`/`ADC-0019`~`0026`/`ADR-0008` 등 | Accept(Scoped, Conditional), Production 차단(Gate B/C 미충족) | A-OUT이 "HQ Routing/Registry" 명시 제외 — Node의 Agent 배정은 HQ가 실행 단위 구성 시점에 이미 고정(불투명 입력) |
| Engine Adapter/OmniRoute(§16.2 내부 갈래) | `ADC-0027`~`0031`/`ADR-0015`~`0017` | Production Adopted(Scoped, Thin Engine Caller Case A) — Production 구현 존재(`omniroute_engine.py`) | Model/LLM **호출**(§14.1 #3 "Engine 호출 책임")이며 Agent **실행 배분**과는 별개 seam(`ADC-0023` §D-9b가 명시적으로 구분) |

### 2.1 ADC-02와 그 대조 판정들 — 전부 미해소, 이 RFC가 재조사하지 않음

| 판정 | 결론 | 재확인 |
|---|---|---|
| `ADC-0008`(RFC-0008 후속) | "유지" 후보 — 근거 부족, "대체"(Scheduler+Engine Gateway) 후보도 근거 부족 → **양쪽 다 Accept 불가**, ADC-02 Open 유지 | 원문 재조회로 확인 |
| `ADC-0011`(Standalone Execution Location Boundary) | **Not Accepted (based on current evidence)** | 원문 재조회 — "Not Accepted는 그런 위치가 영원히 있을 수 없다는 뜻이 아니다"라는 단서까지 확인 |
| `ADC-0012`(Dispatch Component Boundary) | **Defer** — 선행 조건(Kernel Module 3건 Defer, ADC-01·02 Open, Engine 수 ≥2 미충족) 다수 미충족 | 원문 재조회 |

**세 판정 모두 ADC-02를 Open 상태로 그대로 남겨 두었다.** 이 RFC는 이
판정들을 다시 조사하지 않고 그 결론만 인용한다(사용자 지시 "직접
재검증하여... 우회하지 않는지 확인" — 재검증은 "결론을 다시 읽고
원문과 대조"하는 것이지 "새로 판단"하는 것이 아니다).

## 3. Evidence Summary — 실제 Production Runtime 소비자 존재 여부

| 대상 | 확인 결과 |
|---|---|
| `hqs/development/mvp/execution_host.py` | Execution Host(§16.3, Accept Scoped)의 Production 구현. `run_isolated` — 단일 실행 단위 dispatch·격리만. Agent 동적 배분 없음. |
| `hqs/development/mvp/omniroute_engine.py` | Engine Adapter/OmniRoute(Production Adopted, Scoped)의 Production 구현. 단일 endpoint 호출만(`ADC-0031` "Thin Engine Caller 범위"). |
| `Runtime`/`Scheduler`/`AgentManager`/`Registry` 클래스 | grep 결과 Production 경로(`core/`, `hqs/`, `dashboard/`) **0건**(`hqs/investment/checkpoint.py`는 §16.5 저장 전 검증 게이트이며 이름만 유사, 무관). |
| Multi-HQ/여러 Agent 간 동적 실행 배분 경로 | 코드 전수 조사 결과 **없음** — Development HQ는 4개 고정 Agent를 `workflow.py`가 순서대로 직접 호출, Investment HQ는 `stock_team.py` 내부 병렬 함수 호출뿐. |

**결론**: "Runtime"이라는 이름의 통합 Component는 물론, §6 원문이
정의하는 "Task를 Agent에게 배분"하는 실제 동작을 수행하는 코드가
Production 어디에도 없다. 이미 Accept된 네 조각(§2)만 각자의 좁은
경계 안에서 개별적으로 구현되어 있을 뿐이다.

## 4. Runtime Contract Candidate별 판단

> 사용자가 지정한 6개 후보 각각을 "지금 확정해야 하는가"로 판단한다.
> ADC 채택 기준(①지금 결정하지 않으면 상위 Architecture 진행 불가,
> ②지연 시 되돌리는 비용 급증)을 그대로 적용한다.

| Candidate | 이미 결정된 부분 | 남는 것 | 판단 |
|---|---|---|---|
| Agent 실행 요청 | 없음 — §14.1 #1 "Task 전달 책임"이 이 계약의 범위 밖으로 **이미 명시**(§14.1 표) | 어느 Agent가 요청을 받는지 결정하는 것 자체가 Scheduler/Dynamic Routing(구현 금지) | **Not Accept — Defer**(ADC-02와 동일 질문, ①·② 미충족 — 소비자 없음, §3) |
| 실행 상태 | §16.6 A-IN(a) — Workflow **그래프 진행 상태**(Task 그래프 층위, Accept Scoped)로 이미 부분 커버 | Agent 단위의 실행 상태(=Phase B "Agent State", `RFC-0025`§4)는 Defer 그대로 | **재정의하지 않음** — §16.6은 재확인, Agent State는 Phase B Defer 인용만 |
| 결과 전달 | §16.6 A-IN(e)·Adapter Contract (b) — Workflow 그래프의 caller-owned 값 반환(Task 그래프 층위)은 이미 Accept | Agent↔Agent 결과 전달(=Phase B Message/Event, `RFC-0025`§6)은 Open 그대로; §14.1 #1 Task 전달 책임도 계약 범위 밖 | **재정의하지 않음** — 둘 다 기존 Defer/Open 인용만 |
| 실패/취소 | §14.3 G-6(예외 아닌 값 표현) — Kernel 전역 원칙, 이미 결정됨. §16.6 A-IN(a)(ii) 종료 disposition(Task 그래프 층위)도 Accept | Runtime 수준의 취소(예: 실행 중인 Agent를 외부에서 중단)는 대응 개념 자체가 없음 — Runtime 미존재이므로 취소 대상도 없음 | **Not Accept — Defer**(대상 부재) |
| 동시 실행 | §16.4 Multi-Task — 독립 고정 실행 단위 동시 실행은 이미 Accept(Scoped, Conditional) | "Agent 동적 선택"을 포함하는 동시 실행(진짜 Multi-Agent 병렬 협업)은 §16.4가 명시적으로 제외 | **재정의하지 않음** — §16.4 재확인, 확장분은 ADC-02 영역 |
| 외부 Engine 호출 | §16.2/Engine Adapter/OmniRoute — Production Adopted(Scoped, Thin Engine Caller) | Runtime과 **다른 seam**(Model/LLM 호출 vs Agent 실행 배분, `ADC-0023` §D-9b가 이미 구분) — 혼동 방지가 이 RFC의 역할(§5) | **재정의하지 않음, 계층 구분만 재확인** |

**공통 결론**: 6개 후보 중 이미 부분적으로 다루어진 4개(실행 상태·
결과 전달·실패/취소 절반·동시 실행·외부 Engine 호출)는 기존 Accept를
재확인할 뿐 새로 정의하지 않는다. 나머지(Agent 실행 요청, 그리고
"실행 상태/결과 전달/실패-취소"의 **Agent 동적 배분과 결합된 나머지
절반**)는 전부 **ADC-02 Open 하나로 수렴**한다 — 별도 이름의 새
Candidate를 만들 실익이 없다. 소비자도 없다(§3).

## 5. Engine Adapter와 Runtime의 계층 구분 — 혼동 방지 확인

사용자가 명시적으로 요구한 구분이다. `ADC-0023` §D-9b가 이미 다음을
확정했다: v1 `IWorkflowEngine`의 "Engine"(Workflow 그래프 실행)과
§16.2 Engine Adapter(Model/LLM Provider 호출)는 **별개 seam**이며,
Engine Adapter/OmniRoute는 §14.1 #3 "Engine 호출 책임" 트랙, Runtime의
"Task를 Agent에게 배분"은 §14.1 #1 "Task 전달 책임" 트랙으로 **처음부터
분리되어 있다.** 이 RFC는 이 구분을 유지한다:

- **Engine Adapter**: "무엇으로 실행할 것인가"(어떤 LLM/Model을 어떻게
  호출하는가) — 이미 좁은 범위에서 Production Adopted.
  - `hqs/development/mvp/omniroute_engine.py`가 이 seam의 유일한
    Production 구현이며 단일 endpoint 호출로 극도로 제한됨을
    재확인했다(§3).
- **Runtime**: "누가(Agent) 무엇을(Task) 수행할지 배분·조정하는가" —
  ADC-02 Open, 미존재.

두 seam을 하나로 묶어 "Runtime Contract"라는 이름으로 함께 정의하면
`ADC-0023`의 기존 구분을 흐리게 되므로, 이 RFC는 §4의 어떤 행에서도
Engine Adapter의 확장으로 Runtime을 정의하지 않았다.

## 6. LangGraph의 취급 — Runtime의 전제나 설계 기준이 아님

`ADC-0021`~`ADC-0026`의 축적 판단(§16.6 트랙, Phase C `RFC-0026` §6이
이미 재확인)을 그대로 따른다 — LangGraph는 §16.6 A-IN(Task 그래프
층위) 구현 후보 중 하나일 뿐이며, "Runtime"(§6 원문의 넓은 배분 책임)의
설계 기준으로 쓰인 적이 없고 이 RFC도 그렇게 쓰지 않는다. Runtime
Candidate가 실제로 Accept되는 시점이 오더라도, 그 검증에 LangGraph를
쓸지는 §16.6과 별개로 그때 판단할 문제이며 지금 전제하지 않는다.

## 7. Out of Scope

- ADC-02(Runtime 개념의 존폐) **자체의 판정** — 이 RFC는 그 질문을
  대신 답하지 않는다. Open 상태를 재확인만 한다.
- Execution Host(§16.3)·Multi-Task(§16.4)·Workflow Adapter(§16.6)·
  Engine Adapter(§16.2 내부 갈래)의 **재정의·재판정** — 각자의
  Governance Chain 소관.
- Scheduler, Agent Manager, Registry, Event Bus, Workflow Engine의
  설계·구현.
- LangGraph 평가·채택·구현.
- Agent Domain/Lifecycle(Phase A)·Agent State/Message/Event(Phase B)의
  재정의.
- `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md` 문언
  수정. Production Code 변경.

## 8. Non-goals

- 이 RFC는 "Multi-Agent Runtime Contract가 필요하다"고 주장하지
  않는다 — 조사 결과 그 이름이 가리키는 대부분이 이미 네 조각으로
  나뉘어 Accept(Scoped)되어 있거나, 나머지가 ADC-02 하나로 수렴하며
  실제 소비자가 없다.
- 이 RFC는 ADC-02·ADC-0008·ADC-0011·ADC-0012의 기존 판정을 강화·
  약화하지 않는다.
- 이 RFC는 Engine Adapter를 Runtime의 대체물이나 선행물로 주장하지
  않는다(§5).

## 9. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase D)** | Runtime이라는 이름 아래 이미 Accept된 네 조각(Execution Host/Multi-Task/Workflow Adapter/Engine Adapter)과, 여전히 ADC-02 하나로 수렴하는 미결 나머지를 구분해 확인. **새 Candidate를 Accept 대상으로 제안하지 않는다.** |
| **ADC-02 자체 트랙** | Runtime 존폐 여부는 이 RFC와 무관하게 그 트랙(`docs/decisions/adc/ADC.md`)에서 계속 Open — NOW 우선순위 그대로. |
| **§16.3/16.4/16.6/16.2 각 트랙** | 각자의 Production 개시 조건(예: §16.6 Gate B/C)은 이 RFC와 무관하게 진행. |
| **후속 Governance Review(신설 예정, 필요 시)** | 사용자가 별도로 요청하는 경우, 이 RFC가 새로 Accept 대상으로 제안한 것이 없으므로 판정할 새 사안이 없다 — Phase C와 동일 구조. |

## 10. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건 추가만 존재. `BASELINE.md`·
  `GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  Production Code **무변경**.
- `docs/decisions/adc/ADC.md` ADC-02 원문 재조회 — "상태: Open ·
  우선순위: NOW" 확인, 이 RFC로 상태 변화 없음.
- `docs/architecture/core/ADC-0008/0011/0012` 원문 재조회 — 결론(Q0/Q1
  둘 다 Accept 불가 → Open 유지; Not Accepted; Defer) 인용이 원문과
  일치함을 확인.
- `BASELINE.md` §16.3 "Execution Host는 §6 Concept Model의 'Runtime'
  항목을 재명명한 것이 아니다" 원문 재대조 — §2 표의 인용과 일치.
- `ADC-0023` §D-9b(Engine Adapter/§14.1 #3 vs Task 전달/§14.1 #1의
  별개 seam 구분) 원문 재대조 — §5의 인용과 일치.
- `grep -rn "class.*Runtime\|class.*Scheduler\|class.*AgentManager\|class.*Registry\b"` —
  Production 경로 0건(`checkpoint.py` 제외 무관 확인).
- `hqs/development/mvp/execution_host.py`·`omniroute_engine.py` 존재
  및 책임 범위(§16.3/§16.2 Scoped) 확인 — §3 인용과 일치.
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다. `pytest`
  모듈은 이번 세션 환경에 없으며(Phase A~C에서 이미 확인), 코드 diff
  0줄이므로 재실행 결과가 달라질 여지가 없다.

## 11. Self Review

- ADC-02를 이 RFC가 대신 판정했는가 — **아니오**(§2.1, §7, §9) — Open
  상태를 재확인만 했다.
- Execution Host/Multi-Task/Workflow Adapter/Engine Adapter를 재정의
  했는가 — **아니오**(§2, §4) — 각 원문을 인용해 이미 Decided임을
  확인했을 뿐이다.
- ADC-0008/0011/0012의 결론을 다시 판단했는가 — **아니오**(§2.1) —
  "재조사하지 않는다"고 명시하고 결론만 인용했다.
- Engine Adapter를 Runtime의 일부로 흡수시켰는가 — **아니오**(§5) —
  `ADC-0023` §D-9b의 기존 구분을 그대로 유지했다.
- Scheduler/Agent Manager/Registry/Event Bus/LangGraph를 구현·설계
  했는가 — **아니오**(§6, §7).
- Phase A/B/C의 Defer/Open을 우회했는가 — **아니오**(§4 표의 "실행
  상태"·"결과 전달" 행이 각각 Phase B 항목을 그대로 인용만 했다).
- 실제 소비자 존재 여부를 코드로 검증했는가 — **예**(§3) — grep과
  파일 원문 확인.
- 새 Kernel Concept·Public Contract 항목을 추가했는가 — **아니오**
  (§7, §10 `git status` 0 diff).
- Production Code를 변경했는가 — **아니오**(§10).
