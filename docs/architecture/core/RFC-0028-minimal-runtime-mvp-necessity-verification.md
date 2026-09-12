# RFC-0028: Minimal Runtime MVP 필요성 검증 (Phase E)

**Status**: Proposed (조사·실험 결과 기록, Baseline 결정 아님)
**Author**: Claude Code
**대상**: `docs/decisions/adc/ADC.md` ADC-02(Runtime 개념의 존폐, Open,
NOW), `docs/architecture/core/RFC-0024~0027`·`ADC-0032`·`ADC-0033`
(Phase A~D — 전부 Defer/Open 또는 "이미 Decided, 재정의 불필요"),
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`("Experimental
Implementation" 절, "ADC 채택 기준").

**Evidence**: `projects/multi-agent-handoff-mvp-v1/`(이 RFC를 위해 이번
세션에서 신설한 Experimental Implementation, `EVIDENCE.md` 참조),
`hqs/development/workflow.py`, `hqs/investment/teams/stock_team.py`.

> 이 RFC는 Phase A~D(`RFC-0024`~`RFC-0027`, `ADC-0032`, `ADC-0033`)의
> 결과를 **전제**로 삼는다. 이 RFC는 Runtime을 채택·구현하지 않으며,
> Agent Domain/Lifecycle/State/Message/Event/Agent Manager/Event Bus/
> Scheduler/Registry/Runtime Contract 중 어느 것도 Production Contract로
> 새로 확정하지 않는다.

---

## 0. 이 RFC가 열린 이유

Phase A~D는 전부 문서 조사만으로 "실제 소비자가 없다"는 결론에
도달했다. Phase E는 그 결론을 **실행 Evidence**로 한 번 더 검증하라는
사용자 지시다 — 문서상 소비자가 없다는 관찰과, 실제로 최소
시나리오조차 만들 수 없다는 관찰(혹은 그 반대)은 다른 수준의 증거다.
이 RFC는 격리된 Experimental Implementation을 실행해 그 차이를
메운다.

## 1. ADC-02 판단에 필요한 기존 조건 (조사 결과)

| 조건 | 근거 | 확인 |
|---|---|---|
| ADC-02 상태 | `docs/decisions/adc/ADC.md` | Open, 우선순위 NOW — 이 RFC로 변경되지 않음 |
| ADC-02를 대체 시도한 판정들 | `ADC-0008`(양쪽 Candidate 다 Accept 불가) · `ADC-0011`(Not Accepted) · `ADC-0012`(Defer) | 전부 미해소 확인(`RFC-0027` §2.1 재인용) |
| ADC 채택 기준 | `ARCHITECTURE_GOVERNANCE.md` | ①지금 결정 안 하면 상위 진행 불가, ②지연 시 되돌리는 비용 급증 — 둘 중 하나 필요 |
| Architecture Need 정의 | 同 문서 | "실제로 관찰된 문제/반복 요구" — 아이디어·선호는 Need 아님 |
| Experimental Implementation 허용 범위 | 同 문서 | `projects/` 격리, HQ production path 무단 연결 금지, Contract 보호, 성공/실패/폐기 기준 기록 |
| 기존 실행 단위 제공 현황 | `RFC-0027` §2·§3 | Execution Host(단일 unit dispatch)·Multi-Task(독립 동시 실행)·Workflow Adapter(고정 그래프 진행)·Engine Adapter(LLM 호출) — 4갈래 모두 Accept(Scoped), "Agent 동적 배분"만 미제공 |

## 2. 실험 전 판단 — 기존 Contract만으로 실험이 가능한가

`RFC-0027`의 결론(§2.1 이 RFC의 §1 재인용)에 따라, Execution Host나
Workflow Adapter를 "Multi-Agent Runtime"으로 간주하지 않았다. 대신
`hqs/development/workflow.py`(Stage 간 직접 함수 호출·값 기반 실패)와
`hqs/investment/teams/stock_team.py`(`ThreadPoolExecutor` 직접 사용)가
이미 Production에서 "역할 분리 + 전달 + 실패 처리 + 병렬"을 프레임워크
없이 수행하고 있음을 먼저 확인했다. 이 선례로 미루어, **기존
Contract(직접 함수 호출 + 표준 라이브러리)만으로 최소 시나리오를 만들
수 있는지가 이 실험의 첫 질문**이었다 — 새 Runtime 개념이 필요하다고
가정하지 않고 시작했다.

## 3. 실험 시나리오

`projects/multi-agent-handoff-mvp-v1/`(Experimental Implementation,
`EVIDENCE.md` 전문 참조):

- **Agent 역할 2개**: `domain/agents.py`의 `run_drafter`/`run_reviewer`
  — 순수 함수, Kernel/HQ 어떤 코드도 import하지 않음.
- **Task 전달**: `caller.py`의 `run_sequential_handoff` — Drafter 결과를
  Reviewer 입력으로 직접 전달하고 최종 값을 caller에 반환.
- **실패/종료**: Agent A 실패 시 Agent B 미호출(단축), Agent B 실패 시
  전파 — 둘 다 예외가 아닌 값으로 표현.
- **병렬**: `run_parallel_independent_agents` — 독립 Drafter 인스턴스를
  `ThreadPoolExecutor`로 동시 실행(§16.4 Multi-Task와 동형 패턴, 새
  추상화 없음).
- **명시적으로 배제**: LangGraph, 일반화된 Runtime API, Agent Domain/
  Lifecycle/State/Message/Event Production Contract, Agent Manager,
  Event Bus, Scheduler, Registry.

## 4. 실제 Multi-Agent 소비 증거

`/root/.local/bin/pytest projects/multi-agent-handoff-mvp-v1/tests/ -v`
→ **IN-1~IN-7 전부 PASS**(§EVIDENCE.md "실행 결과" 표). 핵심 관찰:

- IN-2가 "Agent A 결과 → Agent B 입력 → caller 반환"이라는 실제 소비
  사례를 프레임워크 없이 재현했다 — 이것이 사용자가 요구한 "하나의
  작업이 Agent A에서 Agent B로 전달되어 결과가 다시 상위 흐름으로
  반환되는 실제 소비 사례"다.
- IN-3·IN-4가 값 기반 실패/종료를 재현했다(§14.3 G-6과 동형이나, 이
  실험이 그 원칙을 새로 확정하는 것은 아니다 — 관찰상 자연스러운
  선택이었을 뿐).
- IN-5가 독립 병렬 실행을 §16.4 범위 밖 새 추상화 없이 재현했다.
- IN-6(정적 검사)이 LangGraph·Kernel/HQ production·Runtime/Scheduler/
  Registry/Agent Manager/Event Bus 어휘에 대한 의존이 **0건**임을
  확인했다.
- IN-7과 Production 회귀 기준선 재확인(`hqs/development/mvp/tests/` —
  186 passed, 6 skipped, 무변경)이 격리를 확인했다.

**이 실험 동안 "Scheduler/Registry/Runtime/Agent Manager가 있어야
가능하다"는 마찰은 한 번도 관찰되지 않았다.**

## 5. 현재 Architecture의 충분/부족 여부 — 판단

**충분하다.** 사용자가 요구한 최소 조건(독립 Agent 2개, Task 전달,
결과 반환, 실패/종료, 병렬)이 기존 Contract(직접 함수 호출 + 표준
라이브러리, §16.4 Multi-Task와 동형)만으로 마찰 없이 재현됐다. 이는
`hqs/development/workflow.py`·`stock_team.py`가 이미 Production에서
증명한 패턴과 정확히 같은 형태다 — 이 실험은 **새로운 사실을
발견했다기보다, Phase A~D가 문서로 확인한 "실제 소비자 부재"를 실행
수준에서 재확인**했다.

## 6. Runtime Candidate 발생 여부

**발생하지 않았다.** §5의 판단에 따라, ADC 채택 기준(①·②) 어느
것도 충족하지 않는다 — 오히려 이 실험이 "새 Runtime 없이도 충분하다"는
**반대 방향** Evidence를 추가했다. 사용자 지시("충분한 실제 소비
사례가 확보되지 않는다면 Runtime Adoption이나 Contract 확정을 하지
말고 ADC-02 Open 상태를 유지하라")에 따라, 이 RFC는 Minimal Runtime
책임 후보를 **정리하지 않는다** — 정리할 근거(부족함의 증거)가 반대로
나왔기 때문이다.

## 7. Out of Scope

- ADC-02 자체의 판정 — 이 RFC는 Open 상태를 유지할 뿐 대신 답하지
  않는다.
- Runtime/Scheduler/Registry/Event Bus/Agent Manager의 Production
  설계·구현.
- LangGraph 평가·채택·구현 — 이 실험은 의도적으로 사용하지 않았다.
- Agent Domain/Lifecycle(Phase A)·Agent State/Message/Event(Phase B)·
  Multi-Agent Workflow(Phase C)·Runtime Contract(Phase D)의 재정의.
- `projects/multi-agent-handoff-mvp-v1/`의 Production 경로 편입 — 이
  실험은 격리된 채로 남는다.
- `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md` 문언
  수정. Production Code 변경.

## 8. Non-goals

- 이 RFC는 "Multi-Agent Runtime이 필요 없다"고 **영구적으로**
  주장하지 않는다 — 지금 시점 Evidence로 필요성이 관찰되지 않았을
  뿐이며, 실제 Architecture Need가 나중에 관찰되면 재검토는 언제든
  가능하다(`ARCHITECTURE_GOVERNANCE.md` "Architecture Need" 원칙).
- 이 RFC는 `hqs/development/workflow.py`·`stock_team.py`의 기존 패턴을
  Kernel Contract로 승격하자고 주장하지 않는다.
- 이 RFC는 이 실험(`multi-agent-handoff-mvp-v1`)이 반복적 가치를 가진
  Component라고 주장하지 않는다 — Experimental Implementation 규칙대로
  필요 없어지면 RFC 없이 즉시 제거 가능한 상태로 남긴다.

## 9. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase E)** | ADC-02 판단에 필요한 실행 Evidence를 Experimental Implementation으로 확보. **Runtime Candidate를 열지 않는다** — Evidence가 충분성 방향으로 나왔다. |
| **ADC-02 자체 트랙** | 이 RFC와 무관하게 Open, NOW 우선순위 그대로 — `docs/decisions/adc/ADC.md`가 계속 소유. |
| **`projects/multi-agent-handoff-mvp-v1/`** | 폐기 대상(Experimental) — 반복적 가치가 추가로 관찰되지 않는 한 향후 세션에서 RFC 없이 제거 가능. |
| **후속 Governance Review** | 이 RFC가 Accept 대상으로 제안한 것이 없으므로 별도 ADC 필수는 아니다(Phase C/D와 동일 구조). |

## 10. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건, `projects/multi-agent-handoff-mvp-v1/`
  신규 디렉터리(EVIDENCE.md·caller.py·domain/·tests/) 외 무변경.
  `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·
  `docs/decisions/adc/ADC.md`·기존 Production Code(`core/`, `hqs/`,
  `dashboard/`) **무변경**.
- `docs/decisions/adc/ADC.md` ADC-02 원문 재조회 — "상태: Open ·
  우선순위: NOW" 확인, 이 RFC로 상태 변화 없음.
- `/root/.local/bin/pytest projects/multi-agent-handoff-mvp-v1/tests/ -v` —
  **7 passed**(§EVIDENCE.md).
- `/root/.local/bin/pytest hqs/development/mvp/tests/ -q` — **186
  passed, 6 skipped**, 이 실험 이전과 동일 — Production 회귀 없음
  확인.
- IN-6·IN-7 테스트 자체가 이 실험의 격리(LangGraph·Kernel/HQ·Runtime
  어휘 비의존, Production 경로 무변경)를 정적으로 검증.
- 이 RFC가 `RFC-0024~0027`/`ADC-0032`/`ADC-0033`의 Defer/Open 결론을
  뒤집지 않았는지 확인 — §7·§8에서 전부 재확인, 어떤 절도 Agent
  Domain/Lifecycle/State/Message/Event/Runtime을 Accept로 전환하지
  않았다.

## 11. Self Review

- Runtime을 채택·구현했는가 — **아니오**(§6, §7) — Candidate조차 열지
  않았다.
- Agent Domain/Lifecycle/State/Message/Event/Agent Manager/Event Bus/
  Scheduler/Registry를 Production Contract로 확정했는가 — **아니오**
  (§3 "명시적으로 배제", IN-6 정적 검증).
- Execution Host나 Workflow Adapter를 Multi-Agent Runtime으로
  간주했는가 — **아니오**(§2) — `RFC-0027`의 구분을 그대로 유지했다.
- LangGraph를 사용했는가 — **아니오**(§3, IN-6).
- 새로운 일반화된 Runtime API를 만들었는가 — **아니오** — `caller.py`는
  두 함수를 고정 순서로 직접 호출할 뿐 재사용 가능한 추상 인터페이스를
  두지 않았다.
- Production 경로를 변경했는가 — **아니오**(IN-7, §10 `git status`).
- 충분하지 않은 증거로 Runtime Adoption을 주장했는가 — **아니오**
  (§5, §6) — 오히려 증거가 반대 방향(충분함)으로 나왔음을 그대로
  기록했다.
- ADC-02를 이 RFC가 대신 판정했는가 — **아니오**(§9) — Open 상태를
  유지했다.
