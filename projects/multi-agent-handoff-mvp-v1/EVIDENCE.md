# EVIDENCE — Multi-Agent Handoff MVP v1 (Phase E)

## 목적

`docs/decisions/adc/ADC.md` ADC-02(Runtime 개념의 존폐, Open, NOW) 판단에
필요한 **실제 실행 Evidence**를 확보한다. Runtime을 채택·구현하지
않는다 — 현재 Contract(직접 함수 호출)만으로 최소 Multi-Agent 실행
시나리오를 재현할 수 있는지만 관찰한다.

## Scope

- 최소 2개의 독립적인 Agent 역할(Drafter/Reviewer).
- Task 전달: Agent A(Drafter) 결과 → Agent B(Reviewer) 입력 → 결과가
  상위 흐름(caller)으로 반환.
- 실패/종료: Agent A 실패(단축), Agent B 실패(전파) — 예외가 아닌 값.
- 병렬: 독립 Agent 인스턴스 다중 동시 실행(관찰용, `ThreadPoolExecutor`
  직접 사용).
- **명시적으로 만들지 않은 것**: 일반화된 Runtime API, Agent Domain/
  Lifecycle/State/Message/Event Production Contract, Agent Manager,
  Event Bus, Scheduler, Registry, LangGraph 의존.

## Owner

Claude Code(이 세션) — Phase E 조사·실험 담당.

## 격리 확인 (`ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation")

- `projects/multi-agent-handoff-mvp-v1/`에만 존재 — `hqs/development/`·
  `hqs/investment/` production path에 연결되지 않음(IN-7 정적 검증).
- 표준 라이브러리(`concurrent.futures.ThreadPoolExecutor`)만 의존 —
  `langgraph`/`langchain`/`hqs.*` import 0건(IN-6 정적 검증).
- 기존 Formal Component(Execution Host/Multi-Task/Workflow Adapter/
  Engine Adapter)의 Contract를 수정하지 않았다 — 이 실험은 그 어떤
  §16 절의 코드도 import·수정하지 않는다.

## 실행 결과 (IN-1 ~ IN-7, 전부 PASS)

`/root/.local/bin/pytest projects/multi-agent-handoff-mvp-v1/tests/ -v`
→ **7 passed**.

| ID | 관찰 대상 | 결과 |
|---|---|---|
| IN-1 | 2개 독립 Agent 역할 존재 | PASS — `drafter`/`reviewer` 두 함수, 서로 다른 이름·책임 |
| IN-2 | Task 전달 A→B, 결과가 caller로 반환 | PASS — `run_sequential_handoff`가 draft를 review 입력으로 넘기고 최종 값을 반환 |
| IN-3 | Agent A 실패 시 단축, 값으로 반환 | PASS — Agent B 미호출, `{"status":"error","failed_at":"drafter"}` |
| IN-4 | Agent B 실패 시 전파 | PASS — `{"status":"error","failed_at":"reviewer"}` |
| IN-5 | 독립 Agent 동시 실행(표준 라이브러리만) | PASS — `ThreadPoolExecutor.map`, 3개 독립 결과 |
| IN-6 | LangGraph·Kernel/HQ·Runtime 어휘 의존 없음 | PASS — 정적 소스 검사 |
| IN-7 | Production 경로 무변경 | PASS — 실험 디렉터리가 `core/`·`hqs/`·`dashboard/` 밖에 위치 |

Development HQ Production 회귀 기준선 재확인:
`/root/.local/bin/pytest hqs/development/mvp/tests/ -q` → **186 passed,
6 skipped** — 이 실험이 Production 경로에 전혀 영향을 주지 않았음을
재확인(격리 원칙 준수).

## 관찰 — 현재 Architecture로 충분한가

**충분하다.** 이 실험이 재현한 시나리오(독립 Agent 2개, Task 전달, 값
기반 실패, 독립 병렬 실행)는 **새로운 추상화 없이** 순수 함수 호출 +
표준 라이브러리 `ThreadPoolExecutor`만으로 완전히 재현됐다. 이는
우연이 아니다 — `hqs/development/workflow.py`(Stage 01→05 직접 함수
호출·값 기반 실패 반환)와 `hqs/investment/teams/stock_team.py`
(`ThreadPoolExecutor` 직접 사용)가 이미 Production에서 쓰는 것과
**동형의 패턴**이다. 이 실험 동안 "이 시나리오를 만들려면 Scheduler/
Registry/Runtime/Agent Manager가 있어야 한다"는 마찰(friction)은 **한
번도 관찰되지 않았다** — Agent 배분은 caller 코드에 고정되어 있고
(`caller.py`), 동적 재배분·Capability 탐색·Agent 간 직접 통신 중 어느
것도 필요하지 않았다.

## 관찰 — 새로운 Runtime 책임이 필요한가

**필요성이 관찰되지 않았다.** 이 실험이 다룬 4가지 요구(역할 분리,
전달, 실패 종료, 병렬)는 전부 기존 Contract(직접 함수 호출, §16.4
Multi-Task와 동형의 `ThreadPoolExecutor` 패턴)로 충족됐다. `RFC-0024`~
`RFC-0027`이 이미 지적한 "실제 소비자 부재"가 이 실험에서도 뒤집히지
않았다 — 오히려 "소비자가 나타나도 현재 Contract로 충분할 가능성이
높다"는 **반대 방향의 Evidence**가 하나 추가됐다.

## 성공/실패/폐기 기준

- **성공 기준**(이 실험 자체에 대해): IN-1~IN-7 전부 PASS, Production
  회귀 기준선 무영향 — **충족**.
- **Architecture 승격 기준**(이 실험이 Runtime Contract Candidate를
  낳는가): ADC 채택 기준 ①(지금 결정 안 하면 진행 불가) 또는 ②(지연
  시 되돌리는 비용 급증) 중 하나 — **어느 것도 충족되지 않음**. 이
  실험 자체가 프레임워크 없이 완결됐다는 사실이 오히려 ①·②를
  약화시킨다.
- **폐기 기준**: 이 Experimental Component는 반복적 가치가 추가로
  확인되지 않는 한 RFC 없이 즉시 제거 가능하다(`ARCHITECTURE_GOVERNANCE.md`
  "Experimental Implementation"). 이 Evidence는 그 존재만으로 Formal
  Architecture Decision이나 ADC Accept를 발생시키지 않는다.
