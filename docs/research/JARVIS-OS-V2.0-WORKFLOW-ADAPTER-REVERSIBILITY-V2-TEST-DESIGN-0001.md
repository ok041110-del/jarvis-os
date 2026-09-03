# JARVIS-OS-V2.0 — Workflow Adapter Reversibility v2 통합 테스트 설계 (0001)

## 문서 성격

이 문서는 **Research / Test Design 문서다. Governance 문서가 아니다.**

Architecture Decision을 포함하지 않는다. RFC/ADC/ADR/RT/Baseline을 수정하지
않는다. 새 Production 코드·Capability·Runtime·Adapter를 구현하지 않는다.
LangGraph를 채택하지 않는다. 이 문서는 `ADC-0021` §8이 첫 Gate-clearing
단계로 지정한 **(C) Reversibility 필수 불변조건의 v2 맥락 in-repo 통합
테스트**의 **검증 범위·불변조건·위치·산출물**을 구현 이전에 설계하고,
그 설계에 대한 Architecture/Governance Review와 "별도 Evidence/ADC 필요
여부" 판정을 기록한다.

**Owner**: Claude Code (세션 2026-09-03)
**입력**: `ADC-0019` §Q6·§Decision 조건 4·§Next Step 4, `ADC-0021` §D4·§8 (C), `ADC-0020` §Q-C·§Q-D·§Q-E-1, `BASELINE.md` v1.13 §16.6, E1(`archive/v1` `ADR-0007` + `archive/v1/tests/integration/test_workflow_adapter_reversibility.py`), E2(`.claude/docs/integrations/langgraph.md`), E3(`.claude/docs/integrations/langgraph-domain-poc.md`), `hqs/development/IMPLEMENTATION_RULES.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation", Execution Host 선례 `docs/research/JARVIS-OS-V2.0-*-PROTOTYPE-0001.md` + `ADC-0015`.

---

## Summary

- **(C)가 요구하는 것**: `ADC-0019` 조건 4는 "§16.6 책임의 어떤 구현체를 제거하고 다른 구현체(최소한 순차 함수 호출)로 교체해도 Kernel·HQ 코드 0 변경"을 **v2 맥락의 통합 테스트로 재현 검증**할 것을 후속 구현의 선행 요구로 명문화했다(Next Step 4). E1은 cross-architecture로 부분 할인되고(v1은 Team/Division을 Core에 가짐 — `ADC-0019` G2), E3는 저장소 밖 PoC다(E3 §9-7). (C)는 이 둘의 공백 — **v2 A-IN 범위 · in-repo · 실행 가능한 테스트** — 만 메운다.
- **테스트 대상**: 동일한 caller-facing seam 뒤의 두 Workflow Adapter 구현체 — `adapter_sequential`(Reference: 조건문/반복문/`ThreadPoolExecutor`/명시적 merge)와 `adapter_langgraph`(대조: `StateGraph`, `langgraph` import 1개 모듈로 한정). 고정 입력 = HQ가 정의한 도메인 형태 그래프(`hqs/investment/teams/stock_team.py` 의미 — 5-way 병렬 → Bull/Bear 토론 Loop → Trader Decision → 조건부 라우팅) + 결정론적 stub 노드 + 2개 시나리오(`clean`, `data_gap`).
- **검증하는 불변조건 5개**: IN-1 최종 State 동치, IN-2 실행 결과의 값 표현(예외 비전파, §14.3 G-6), IN-3 caller-owned 값 checkpoint의 phase-boundary resume(프로세스 종료 생존, adapter 파일 I/O 0), IN-4 어댑터 교체 시 caller/도메인/State 스키마 파일 해시 불변 + `core/`·`hqs/`에 `langgraph`/`langchain` import 0, IN-5 라이브러리 경계 격리.
- **명시적 비검증**: mid-node/임의 지점 resume(C2), 성능·재컴파일·wall-clock을 pass/fail gate로 삼는 것, 실제 엔진 호출·비결정성, Public Port/§14 표면, (c) reducer 규약의 규범화, phase 경계 선언 주체(Q-E-2) 확정.
- **위치**: `projects/workflow-adapter-reversibility-v2/` — `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" 범위(격리 venv, `hqs/` production path 무연결, Formal Contract·Frozen Boundary 무변경). Execution Host의 `projects/runtime-boundary` 등이 `ADC-0015` Evidence가 된 것과 동형.
- **산출물**: 테스트 실행 후 자립 Evidence 문서(**E4** — `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` + 이 `docs/research/` 문서의 결과 절 갱신). E4는 `ADC-0019` 조건 4가 요구한 재현 검증 자료이며, 그 **충분성 판정**(조건 4를 완전히 discharge하는지, 부분 할인인지)은 후속 ADR의 몫이다.
- **판정**: 이 테스트를 **수행하는 데** 새 RFC/ADC는 필요 없다(이미 Accept된 §16.6 책임의 불변조건 재현, `ADC-0019` Next Step 4가 명시 요구). **새 Evidence 문서(E4)는 필요하다** — (C)의 산출물이 곧 E4다. E4가 생긴 뒤 "조건 4 충족"을 `BASELINE.md` §16.6에 반영하는 것은 `ADC-0021` §8이 이미 예고한 후속 ADR 경로이지 새 ADC가 아니다.

---

## 1. (C) Gate가 요구하는 정확한 범위

### 1.1 근거 조항

| 출처 | 문언 | 함의 |
|---|---|---|
| `BASELINE.md` §16.6 "Reversibility — 필수 Architecture 불변조건" | "어떤 구현체를 제거하고 다른 구현체(최소한으로는 순차 함수 호출)로 교체해도, Kernel과 HQ가 정의하는 코드는 한 줄도 수정되지 않아야 한다. 구현체 고유 문법은 이 책임의 경계 안에서만 쓰인다. … 후속 절차는 v2 맥락의 통합 테스트로 이 불변조건을 재현 검증해야 한다." | 검증 대상 = (i) 교체 시 Kernel·HQ 코드 0 변경, (ii) 고유 문법의 경계 격리 |
| `ADC-0019` §Decision 조건 4 | "이 조건은 v1 `ADR-0007` 결정 4와 `test_workflow_adapter_reversibility.py`가 이미 실증한 선례를 근거로, 후속 ADR이 Baseline 반영 시 **v2 맥락의 통합 테스트 수준 검증 요구사항**으로 명문화한다." | v1 테스트가 template, v2 맥락으로 재현 |
| `ADC-0019` §Next Step 4 | "Reversibility 검증(조건 4)을 v2 맥락의 통합 테스트로 재현하는 것을 후속 ADR/구현 지침의 **선행 요구사항**으로 명시한다." | 구현 착수 전 선행 |
| `ADC-0021` §D4 | "검증 방법 = v2 맥락 in-repo 통합 테스트. **검증의 실행 시점**: 이 ADC의 결과가 아니다 — §5 D3 조건 3·4가 충족되고 구현이 열리는 단계의 선행 요구." + 교체점 = "호출자가 어느 adapter 모듈을 인자로 받느냐 한 곳"(E3 §7) | 교체점 1곳, in-repo, 구현 전 |
| `ADC-0021` §8 (C) | "Reversibility 필수 불변조건의 v2 맥락 in-repo 통합 테스트 설계·재현 검증" | 이 문서의 대상 |
| `ADC-0020` §Q-D (d) | "검증 방법이 v2 맥락의 통합 테스트임을 명문화하는 것뿐이며, 그 통합 테스트의 **실행**은 이 반영의 결과가 아니다(후속 Implementation Strategy)." | (C) = 그 "실행" 단계 |

### 1.2 E1/E2/E3가 이미 보인 것 / (C)가 메워야 할 공백

| | 보인 것 | 공백 (→ (C)의 대상) |
|---|---|---|
| **E1** (`archive/v1`, Accepted) | LangGraph↔Sequential Adapter 교체 시 `packages/core` 무수정. Contract Parity 3 + Reversibility 1 + Fail-Closed 3을 통합 테스트로 실증 | **cross-architecture 부분 할인**(`ADC-0019` G2) — v1은 `Team`/`Division`/`IWorkflowEngine` Port를 Core Domain Model로 가졌고, v2 §5는 Kernel이 이를 모른다. v1 테스트는 v2 A-IN 범위·v2 seam을 검증하지 않음 |
| **E2** (`langgraph.md`, toy) | `langgraph` 1.2.11 설치·실행, toy State→Node→Conditional→Loop, `MemorySaver` mid-graph resume | 도메인 형태 아님. **caller-owned 소유 모델 아님**(LangGraph 소유 `MemorySaver`). Reversibility 미검증. **저장소 밖** |
| **E3** (`langgraph-domain-poc.md`, domain) | 13-node 도메인 그래프에서 26/26: LangGraph `run_full` == 순차 `run_full` 최종 State 동치, 어댑터 교체 시 caller/domain 파일 해시 불변, caller-owned 값 checkpoint가 프로세스 종료 후 재개, 어댑터 격리(import 1파일, 타입 누출 0) | **저장소 밖 실행**(E3 §9-7 — "저장소 내 통합 테스트로의 승격은 별도 결정, `ADC-0019` Next Step 4"). 결정론적 stub(§9-5). 재컴파일 오버헤드 미측정(§9-6) |

→ **(C)의 정확한 범위**: E3가 저장소 밖에서 보인 것을 **v2 저장소 안의 실행 가능한 통합 테스트로 승격**하고, v2 A-IN 5항목 + Adapter Contract 부속 명세 (a)(b)(d)에 대응하는 불변조건만 assert한다. E3 대비 **추가 강화점**: (i) in-repo 실행(pytest), (ii) `core/`·`hqs/` 오염 0을 grep gate로 명시 검증, (iii) 프로세스 경계 넘는 resume을 별도 subprocess로 실측, (iv) 노드 stub이 예외를 raise하는 경로를 명시 포함(IN-2). E3 대비 **의도적으로 넓히지 않는 것**: 실제 엔진 호출, 성능, mid-node resume.

---

## 2. Test Design

### 2.1 검증 대상 구성

```
projects/workflow-adapter-reversibility-v2/
  domain/
    state.py        # State 스키마 (TypedDict + 평문 dict 직렬화 규약). langgraph 무의존
    nodes.py        # 13개 도메인 stub 노드 (결정론적, fixture 기반). langgraph 무의존
    fixtures.py     # clean / data_gap 시나리오 입력. langgraph 무의존
    graph_spec.py   # HQ가 "정의"하는 그래프 구조 선언 (노드 목록 + edge + 조건부 술어).
                    #   adapter-agnostic 데이터. 실행 로직 없음
  adapters/
    sequential.py   # Reference. 조건부=if/elif, Loop=while, 병렬=ThreadPoolExecutor,
                    #   reducer=명시적 merge. 외부 의존 0
    langgraph.py    # 대조. StateGraph/add_conditional_edges/compile. `langgraph` import
                    #   유일 모듈 (2줄). catch-and-encode 래핑 포함
  caller.py         # 호출자 역할 (HQ 자리). adapter 모듈을 인자로 받음. checkpoint 값의
                    #   파일 영속화를 소유. adapter 종류를 모름
  tests/
    test_reversibility_v2.py   # pytest — IN-1 ~ IN-5
    _resume_subprocess.py      # IN-3용 별도 프로세스 진입점
  EVIDENCE.md        # 실행 후 산출 (E4)
  README.md          # Owner, 성공/실패/폐기 기준, 격리 venv 절차
```

- **seam(교체점)**: `caller.run(graph_spec, inputs, adapter=<module>)` 한 곳. `caller.py`는 `adapter.run_full` / `adapter.run_phase1` / `adapter.run_phase2`를 호출하되 이 시그니처는 **이 프로토타입 harness의 로컬 관례**이며, Public Port·§14 표면·`ADC-0020` §Q-C가 규정한 "구현체 내부 의무" 계약의 확정 시그니처가 **아니다**(§6 Review 참조). 테스트는 seam의 구체 형태에 의존하지 않도록 작성한다 — "두 어댑터가 동일 관례를 만족하고 결과가 동치"만 본다.
- **고정 입력**: `graph_spec.py`가 선언하는 그래프는 `hqs/investment/teams/stock_team.py`의 Wave 병렬 구조 + `hqs/investment/trader.py`의 REPORT/DECISION 분리 의미를 **참조**하되 그 파일을 import·수정하지 않는다(E3 §2와 동일 출처, 복제 아님).
- **노드**: fixture 기반 순수 함수 stub. 엔진 호출 없음. 2개 시나리오 모두 결정론적.

### 2.2 검증하는 불변조건

| ID | 불변조건 | Assertion (요지) | 근거 |
|---|---|---|---|
| **IN-1** | **최종 State 동치** | 모든 시나리오에서 `run_full(sequential)`의 직렬화 State == `run_full(langgraph)`의 직렬화 State (caller-visible 값 deep-equal). `clean`→BUY→`final_report`→`COMPLETED`, `data_gap`→HOLD→`escalate`→`ESCALATED_DATA_GAP` 각각. Conditional 분기·Loop 3라운드가 두 어댑터에서 동일 결과 | §16.6 A-IN (a)~(d), `ADC-0019` 조건 4 "동일하게 동작", E3 §7, E1 Contract Parity |
| **IN-2** | **실행 결과의 값 표현 (예외 비전파)** | (i) 정상 경로: 두 어댑터 모두 terminal outcome을 State 값(`outcome ∈ {COMPLETED, ESCALATED_DATA_GAP}`)으로 반환. (ii) 노드 stub이 `RuntimeError`를 raise하는 fixture: 두 어댑터 모두 `run_full`/`run_phase*` **경계 밖으로 예외를 전파하지 않고** 실패를 State 값(`outcome`/`data_flags`)으로 인코딩. `pytest.raises` 없음 확인 | §16.6 "예외가 아닌 값으로"(§14.3 G-6), `ADC-0020` §Q-D (b) "catch-and-encode는 어댑터 책임", E3 §6-b, E1 Fail-Closed. **메커니즘(정적 분석/Conformance)은 규정하지 않음** — 두 특정 어댑터의 관측 동작만 assert |
| **IN-3** | **caller-owned 값 checkpoint의 phase-boundary resume** | `run_phase1`이 직렬화 가능한 평문 값(JSON round-trip 성공) 반환 → **caller(test harness)**가 temp 파일에 저장 → **별도 프로세스**(`_resume_subprocess.py`)가 그 파일을 로드해 `run_phase2(value)` 호출 → resume 결과 State == 단발 `run_full` 결과 State. 추가 assert: adapter가 파일 I/O 0회, checkpoint 값에 adapter/library 타입 0(전부 `dict`/`str`/`int`/`list`/`bool`), adapter 객체·in-memory saver 폐기 후에도 resume 성립, 두 어댑터에서 동일 | §16.6 A-IN (e) + Adapter Contract (a), `ADC-0020` §Q-E-1 C1(phase-boundary caller-owned), E3 §5·§6-a, `BASELINE.md` §15.2 |
| **IN-4** | **교체 시 Kernel/HQ 코드 0 변경** | `caller.py`·`domain/*.py`(state/nodes/fixtures/graph_spec)의 파일 해시가 두 실행(sequential / langgraph)에서 **동일**. seam은 인자 1개(`adapter=`). 추가 gate: `git grep -nE 'langgraph|langchain' core/ hqs/` == 0건(프로토타입이 production으로 누출되지 않음). `domain/`·`caller.py`에 `langgraph` import 0 | §16.6 Reversibility 문언, `ADC-0019` 조건 4, `ADC-0021` §D4, E3 §7·§8 |
| **IN-5** | **라이브러리 경계 격리** | `langgraph` import가 `adapters/langgraph.py` 정확히 1개 모듈에만 존재. `langgraph`를 차단한 subprocess(import hook)에서 `domain/*`·`adapters/sequential.py`·`caller.py`가 정상 import. State 값에 `langgraph.*`/`langchain_core.*` 타입 인스턴스 0 | §16.6 "구현체 고유 문법은 경계 안에서만", E3 §8 |

### 2.3 명시적 비검증 (범위 밖 — gate·Contract 침범 방지)

| 비검증 항목 | 이유 |
|---|---|
| mid-node / 임의 지점 resume (C2) | `ADC-0020` §Q-E-1이 C2를 Reversibility 위반으로 판정, `RFC-0020` §7 범위 밖. IN-3는 **phase 경계(C1)만** |
| 성능·재컴파일 오버헤드·wall-clock을 pass/fail gate로 | Reversibility는 불변조건이지 비용 기준이 아님(`ADC-0015` §Q2 유비). wall-clock은 **정보성 기록만** 허용, gate 아님 |
| 실제 엔진 호출·비결정성·부분 실패율 | E2/E3 공통 한계. 검증 대상 = 어댑터 경계·불변조건이지 분석 품질 아님 |
| Public Port / §14 표면 / 호출자 계약 확정 시그니처 | `ADC-0019` 조건 5, `ADC-0020` §Q-C, `ADC-0021` §D4. seam은 harness 로컬 관례 |
| phase 경계 **선언 주체**(HQ 정의 vs Adapter Contract) | `ADC-0020` §Q-E-2 Defer. 테스트는 phase 경계를 fixture 선택으로 고정(예: `collect` fan-in 직후)하되 이를 governance 선언으로 삼지 않음 |
| (c) 병렬 State disjoint key / reducer 규약의 규범화 | `ADC-0020` §Q-D (c) Defer, `ADR-0009` §3. 테스트는 disjoint 키 + 명시 reducer를 **사용**하되 그것이 규범이라고 assert하지 않음 — "두 어댑터의 병합 결과가 동치"만 봄 |
| `IMPLEMENTATION_RULES.md` 조항 해제 | 이 문서·이 테스트는 어떤 해제도 하지 않음. Scoped 해제는 별도 ADR |
| LangGraph 채택 | E1/E2/E3와 동일 — 대조 Evidence이지 채택 아님(`ADC-0021` §D2) |

### 2.4 위치·격리 (Experimental Implementation 준수)

`ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation"의 허용·금지에 대조:

| 요건 | 이 설계의 준수 |
|---|---|
| 명확한 목적·제한된 scope | (C) Reversibility 불변조건 재현. §2.2 5개 불변조건으로 한정 |
| 명시적 owner | `README.md`에 기록 (Claude Code, 세션 2026-09-03) |
| 테스트/검증 수행 | pytest harness, 성공/실패/폐기 기준 문서화 |
| 기존 Formal Component Contract 보호 | `core/`·`hqs/` 무수정. `stock_team.py` 등은 참조만, import·수정 없음 |
| Frozen Boundary 보호 | `BASELINE.md`·Structure v1.0 무변경 |
| HQ production path 무단 연결 금지 | `hqs/development/`·`hqs/investment/`에 어떤 배선도 없음. `projects/` 안에서만 실행 |
| 성공/실패/폐기 기준 기록 | `README.md` — 성공: IN-1~IN-5 전부 pass. 실패 시: E4에 실패 항목·원인 기록, 조건 4 미충족으로 보고. 폐기: 필요 없어지면 RFC 없이 삭제 가능 |
| **금지**: 새 Core 책임을 Experimental로 사실상 선언 | §16.6 Workflow Adapter는 **이미 Accept된**(Scoped, Conditional) Kernel Concept — 신규·Deferred 아님. 이 프로토타입은 그 불변조건을 재현할 뿐 새 책임을 선언하지 않음 |
| **금지**: Frozen/Deferred Boundary 우회 | 우회 없음 — `ADC-0019` Next Step 4가 **명시 요구한** 검증을 그 지시대로 수행 |

`IMPLEMENTATION_RULES.md`와의 관계: 이 문서는 `hqs/development/` MVP 구현 규칙의 적용 대상이 아니다(`projects/` Experimental). 그럼에도 안전 측면에서 확인: 이 프로토타입은 `hqs/development/mvp/`에 Workflow Parser/Scheduler/Workflow orchestration/Dynamic Routing/Stage 재진입/Event Bus를 **추가하지 않는다**. `projects/` 내 조건부 분기·Loop 코드는 Development HQ Production 경로가 아니며, Execution Host의 `projects/runtime-boundary`(조건부 실행·Failure/Retry 포함)가 `ADC-0015` Evidence가 되면서도 `IMPLEMENTATION_RULES.md`를 침범하지 않은 것과 동형이다.

### 2.5 Evidence 산출물 (E4)

테스트 실행 완료 시:

1. `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` — 자립 Evidence. 환경(격리 venv, Python·`langgraph` 버전), `graph_spec` 구조·2 시나리오, IN-1~IN-5 각각의 assertion + 결과(pass/fail 수), 커버리지 한계(§2.3 재확인), "LangGraph 채택 아님·구현 승인 아님" 명시.
2. 이 `docs/research/` 문서에 "§10. 실행 결과" 절 추가(E3가 `langgraph.md`에 결과를 추가한 방식).
3. 이 산출물 묶음을 **E4**로 명명 — `ADC-0019` 조건 4·Next Step 4가 요구한 "v2 맥락 통합 테스트 재현" 자료.

E4의 **충분성**("조건 4를 완전히 discharge하는가, E1처럼 부분 할인인가")은 이 문서가 선언하지 않는다 — 후속 ADR이 판정한다(E2가 "Evidence가 main에 존재 ≠ 충분"을 명시한 태도와 동일).

---

## 3. Architecture / Governance Review

### 3.1 범위 — 이 테스트가 무엇을 결정/확장하는가

| 점검 | 결과 |
|---|---|
| 이 테스트 설계가 Architecture Decision을 포함하는가 | **아니오** — 이미 Accept된 §16.6 책임의 불변조건을 재현. `ADC-0019` Next Step 4가 명시 요구한 작업 |
| 새 Public Interface / Port / §14 표면을 정의하는가 | **아니오** — seam(`run_full`/`run_phase1`/`run_phase2`)은 harness 로컬 관례. §2.1·§2.3에 "확정 계약 아님" 명시. `ADC-0020` §Q-C L2/L3 구분 유지 |
| 호출자 계약 시그니처(`ADC-0021` §D4가 확정 안 함)를 확정하는가 | **아니오** — 테스트는 seam 형태에 의존하지 않도록 작성. 어떤 시그니처든 두 어댑터가 만족하면 됨 |
| phase 경계 선언 주체(Q-E-2 Defer)를 결정하는가 | **아니오** — fixture로 phase 경계를 고정하되 governance 선언으로 삼지 않음(§2.3) |
| (b) 강제·검증 메커니즘(Q-G)을 확정하는가 | **아니오** — IN-2는 두 특정 어댑터의 관측 동작만 assert. 정적 분석/Conformance Test 중 무엇도 규정하지 않음 |
| (c) reducer 규약(Q-D (c) Defer)을 규범화하는가 | **아니오** — 사용하되 규범이라고 assert하지 않음(§2.3) |
| Checkpoint 입도를 재론하는가 | **아니오** — `ADC-0020` §Q-E-1 C1을 그대로 검증 대상으로 삼음. C2는 §2.3 비검증 |
| mid-node resume / HITL을 여는가 | **아니오** — §2.3 명시 비검증 |

### 3.2 기존 Governance chain 정합성

| 문서 | 관계 | 정합성 |
|---|---|---|
| `ADC-0019` §조건 4·5·6, 재검토 조건 (c), Next Step 4 | (C)의 직접 근거 | 조건 4가 요구한 재현 검증을 설계. 조건 5(§14 미승격·구현 착수 불가)·재검토 조건 (c)(다른 계보/프로덕션 관찰)는 **이 테스트로 충족되지 않으며**, 그대로 hard gate 유지(§4) |
| `ADC-0020` §Q-C·§Q-D·§Q-E-1 | 불변조건의 계약 언어 출처 | (a)(b)(d)에 대응하는 IN-3/IN-2/IN-1·IN-4만 검증. (c) Defer 존중 |
| `ADC-0021` §D1·§D2·§D4·§8 (C) | 이 테스트의 지정자 | D1(Sequential=Reference)·D2(LangGraph=대조 후보, 채택 아님)를 그대로 반영. D4 교체점 1곳 검증. §8 (C) 수행 |
| `BASELINE.md` v1.13 §16.6 | 검증 대상 문언 | A-IN 5항목 + Reversibility 불변조건 + "예외 아닌 값" + Adapter Contract (a)(b)(d)를 인용·검증만. 문언 무변경 |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | 위치·격리 근거 | §2.4에 허용·금지 전 항목 대조. "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다" — E4는 후속 ADR의 입력이지 자동 승격 아님 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 | 침범 여부 확인 대상 | §2.4 — `hqs/development/` production 경로에 어떤 orchestration도 추가하지 않음. `projects/` Experimental은 그 규칙의 대상 아님 |
| E1 `test_workflow_adapter_reversibility.py` | template | 3-assertion 구조(Contract Parity / Reversibility / Fail-Closed)를 v2 맥락으로 이식 + IN-3(caller-owned checkpoint, v2 A-IN(e) 추가분) 신설. v1의 `IWorkflowEngine` Port 의존은 제거(v2 §5) |
| E3 `langgraph-domain-poc.md` §9-7 | "저장소 내 통합 테스트 승격은 별도 결정" | (C)가 그 승격. E3 shape 재사용, 저장소 밖 → in-repo |
| Execution Host `docs/research/JARVIS-OS-V2.0-*-PROTOTYPE-0001.md` + `ADC-0015` | 선례 | `projects/` 프로토타입이 in-repo Evidence로 ADC에 인용된 형식 동형 |

### 3.3 위험

- **seam이 사실상 계약으로 굳는 위험** — harness 관례(`run_full`/`run_phase*`)가 후속 구현에서 "이미 정해진 인터페이스"로 오독될 수 있다. 완화: E4·테스트 코드 주석·이 문서에 "로컬 관례, `ADC-0020` §Q-C 확정 계약 아님"을 반복 명시. 후속 Implementation Strategy 세부 ADC가 계약 시그니처를 별도 판정.
- **결정론적 stub의 한계** — 실제 엔진 비결정성 하에서 IN-1 동치가 깨질 여지는 이 테스트가 답하지 않는다. E4에 명시 한계로 기록(E3 §9-5와 동일). 이는 조건 4의 "부분 할인" 사유가 될 수 있으며 후속 ADR이 판정.
- **LangGraph 계보 단일성** — 대조 어댑터가 LangGraph뿐이라 `ADC-0019` 재검토 조건 (c)(다른 계보)는 이 테스트로 진전되지 않는다. (C)와 (B)는 독립 gate이며, 이 사실을 E4에 명시.
- **`projects/` venv에 `langgraph` 설치** — 저장소 최상위 의존성(`pyproject.toml` 등)에 추가하지 않고 프로토타입 격리 venv에만. IN-4 grep gate가 누출 0을 강제.

### 3.4 자체 판정

**PASS** — 이 Test Design은 (1) 이미 Accept된 §16.6 불변조건만 검증 대상으로 삼고, (2) `ADC-0019`/`ADC-0020`/`ADC-0021`이 Defer·Out of Scope로 둔 항목(계약 시그니처, Q-E-2, Q-G, (c) 규범화, C2, §14)을 하나도 결정하지 않으며, (3) `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" 범위 안에 위치하고, (4) `IMPLEMENTATION_RULES.md` production 금지를 침범하지 않는다. 잔여 수정사항 없음. §3.3 위험은 완화책과 함께 E4에 이월한다.

---

## 4. 판정 — 별도 Evidence / ADC 필요 여부

| 질문 | 판정 | 근거 |
|---|---|---|
| 이 테스트를 **수행**하는 데 새 RFC가 필요한가 | **아니오** | `ADC-0019` §Next Step 4가 "선행 요구사항으로 명시"라고 이미 지시. `RFC-0020` §8.2·`ADC-0021` §8이 (C)를 Gate-clearing 단계로 예고. 새 Boundary Question 없음 |
| 새 ADC가 필요한가 | **아니오 (수행 단계에서는)** | 이미 Accept된 책임의 불변조건 재현. Architecture Decision 없음(§3.1). E4가 생긴 뒤 "조건 4 충족"을 `BASELINE.md` §16.6에 반영하는 것은 `ADC-0021` §8이 이미 예고한 **후속 ADR** 경로(Minor)이지 새 ADC 아님 |
| 새 Evidence 문서가 필요한가 | **예 — E4** | (C)의 산출물이 곧 Evidence다. E1(`test_workflow_adapter_reversibility.py` + `ADR-0007`), E2·E3와 같은 계보의 자료. `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` + 이 문서 결과 절 |
| E4가 `ADC-0019` 조건 4를 **완전히 discharge**하는가 | **이 문서가 선언하지 않음 → 후속 ADR 판정** | 결정론적 stub·LangGraph 단일 계보라는 한계가 있어 "부분 할인" 판정 여지 존재(E1이 cross-arch 부분 할인된 것과 유사). 충분성 판정은 Governance 단계의 몫 |
| 이 테스트가 `ADC-0021` §8의 다른 gate((A) v1 결정 2/5/9/11, (B) 재검토 조건 (c))를 진전시키는가 | **아니오** | 독립 gate. (C)만 대상. E4에 명시 |

**결론**: 구현 착수 전 산출물은 **E4(Evidence) 1건**이며, 새 RFC/ADC는 필요 없다. 단, E4를 `BASELINE.md`에 반영(조건 4 "Conditional" 완화 또는 충족 명문화)하려면 `ADC-0021` §8이 예고한 후속 ADR을 거친다.

---

## 5. 다음 구현 진입 조건 (갱신된 관점)

`ADC-0021` §8의 hard gate 중 이 문서가 다루는 것은 **(C)뿐**이며, (C)도 "설계 완료"이지 "검증 완료"가 아니다.

| Gate | 상태 (이 문서 이후) | 다음 행위 |
|---|---|---|
| ADC-0021 Accept + RFC pairing | **완료** (`RFC-0020` §8.2) | — |
| **(C)** Reversibility v2 in-repo 통합 테스트 | **설계 완료 (이 문서). 미구현·미실행** | `projects/workflow-adapter-reversibility-v2/` 프로토타입 구현 → pytest 실행 → E4 산출. 이후 후속 ADR이 조건 4 충족/부분 할인 판정 |
| **(A)** v1 `ADR-0007` 결정 2/5/9/11 v2 공백 해소 | **미착수** | 후속 ADR 또는 별도 RFC (`ADC-0019` 조건 5·Next Step 5) |
| **(B)** `ADC-0019` 재검토 조건 (c) — 다른 계보/프로덕션 관찰로 독립 3건 | **미착수** — 이 테스트로 진전 없음(LangGraph 단일 계보) | 별도 관찰 확보 또는 직접 구현 최소 그래프 실행기(`RFC-0020` §8.2 Q-I) |
| Scoped 해제 ADR (`IMPLEMENTATION_RULES.md` line 9/13/14/19) | **미착수** | (A)(B)(C) 충족 후 별도 ADR (`ADC-0015` Q4 대응) |
| §14 승격 없이 A-IN 범위 구현 | **미착수** | §14.1 "Task 전달 책임" 해소가 상위 선행 |

**(C) 자체의 구현 진입 조건** (다음 세션이 프로토타입을 실제로 만들 때):

1. 이 Test Design의 Architecture/Governance Review PASS 확인(§3.4) + 사용자 승인.
2. `projects/workflow-adapter-reversibility-v2/` 신규 디렉터리, 격리 venv, `README.md`(owner·성공/실패/폐기 기준) 선작성.
3. `core/`·`hqs/`·`dashboard/`·`docs/architecture/`·`docs/decisions/` **무수정** — `git status`로 확인. 변경은 `projects/` + 이 `docs/research/` 문서 결과 절에 한정.
4. `langgraph`는 프로토타입 격리 venv에만 설치, 저장소 의존성 매니페스트 무변경.
5. IN-1~IN-5 전부 pass 시 E4 산출·보고. 하나라도 fail 시 구현 착수 불가 사유로 기록하고 보고.
6. Commit/PR/Merge는 E4 산출·보고 후 사용자 지시로만.

---

## 6. Traceability

| 문서 / 절 | 이 문서와의 관계 | 정합성 |
|---|---|---|
| `ADC-0019` §Q6·조건 4·Next Step 4 | (C)의 근거 | 조건 4가 요구한 재현 검증을 설계. 조건 5·재검토 조건 (c)는 미충족 유지(§4·§5) |
| `ADC-0020` §Q-C·§Q-D (a)(b)(d)·§Q-E-1 | 검증 불변조건의 계약 언어 | IN-1~IN-4가 (a)(b)(d)에 대응. (c) Defer·C2·§14 미접촉(§3.1) |
| `ADC-0021` §D1·§D2·§D4·§8 (C) | 이 테스트의 지정자 | D1/D2/D4 그대로 반영. §8 (C) 수행. 다른 gate 미접촉 |
| `BASELINE.md` v1.13 §16.6 | 검증 대상 | 문언 인용·검증만, 무변경 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 | 침범 확인 | `hqs/development/` production 무변경(§2.4). `projects/` Experimental은 대상 밖 |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | 위치·격리 근거 | 허용·금지 전 항목 대조 PASS(§2.4). E4 자동 승격 없음 |
| E1 `archive/v1/tests/integration/test_workflow_adapter_reversibility.py` + `ADR-0007` | template | 3-assertion 구조 이식 + IN-3 신설. v1 Port 의존 제거 |
| E2 `.claude/docs/integrations/langgraph.md` | 대조 방식 출처 | caller-owned 아님·저장소 밖이라는 한계를 (C)가 메움 |
| E3 `.claude/docs/integrations/langgraph-domain-poc.md` §5~§9 | shape 재사용 | 저장소 밖 → in-repo 승격(E3 §9-7). 결정론적 stub 한계 계승·명시 |
| Execution Host `docs/research/JARVIS-OS-V2.0-*-PROTOTYPE-0001.md` + `ADC-0015` | 형식 선례 | `projects/` 프로토타입 → in-repo Evidence → ADC 인용 동형 |
| `hqs/investment/teams/stock_team.py` / `trader.py` / `checkpoint.py` | 도메인 형태 출처 | 참조만 — import·수정 없음 |

---

## 7. Self Review

- Architecture Decision을 포함했는가 — **아니오**(§3.1). 이미 Accept된 §16.6 불변조건 재현.
- 새 RFC/ADC가 필요하다고 결론냈는가 — **아니오**(§4). E4(Evidence)만 필요.
- LangGraph를 채택했는가 — **아니오** — 대조 Evidence(`ADC-0021` §D2).
- Public Port / §14 / 호출자 계약 시그니처를 확정했는가 — **아니오**(§3.1·§3.3) — seam은 harness 로컬 관례.
- Q-E-2 / Q-G / (c) 규범화 / C2 / mid-node를 결정했는가 — **아니오**(§2.3·§3.1).
- `ADC-0019` 조건 5·재검토 조건 (c), (A)/(B) gate를 약화했는가 — **아니오**(§4·§5) — (C)만 대상, 나머지 hard gate 유지.
- `core/`·`hqs/`·Baseline·Governance 문서를 변경하는가 — **아니오** — `projects/` + 이 `docs/research/` 문서에 한정.
- `IMPLEMENTATION_RULES.md`를 침범하는가 — **아니오**(§2.4) — `projects/` Experimental, production 경로 무연결.
- 결정론적 stub·LangGraph 단일 계보 한계를 숨겼는가 — **아니오**(§3.3) — E4 이월 한계로 명시, 조건 4 충분성은 후속 ADR 판정.
- Commit/PR/Merge를 했는가 — **아니오** — 설계·Review·판정만. 구현·산출은 다음 단계.

---

## 8. 실행 결과 (구현 후 갱신 — 2026-09-03)

이 설계를 `projects/workflow-adapter-reversibility-v2/`에 구현·실행했다. 상세 Evidence(E4) = `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`.

### 8.1 환경

Python 3.12.14 (uv 관리 격리 venv), `langgraph==1.2.11`, `langchain-core==1.6.1`, `langgraph-checkpoint==4.2.0`, `langgraph-prebuilt==1.1.0`, `langgraph-sdk==0.4.4`, `pytest==9.1.1` — **E2/E3와 동일 계보·버전**. 저장소 최상위 의존성 매니페스트 무변경(`langgraph`는 격리 venv에만). Production 경로(`core/`·`hqs/`·`dashboard/`·`docs/architecture/`·`docs/decisions/`) 무변경 — `git status`는 `projects/workflow-adapter-reversibility-v2/` 신규 디렉터리만 표시(`.venv`는 git-ignored).

### 8.2 결과 — 22/22 PASS

```
$ .venv/bin/pytest tests/ -p no:cacheprovider
platform darwin -- Python 3.12.14, pytest-9.1.1
collected 22 items
tests/test_reversibility_v2.py ......................                    [100%]
============================== 22 passed in 1.08s ==============================
```

| 불변조건 | 테스트 수 | 결과 |
|---|---|---|
| IN-1 최종 State 동치 (+ 전제 기록) | 3 (+3) | PASS |
| IN-2 실행 결과의 값 표현 · 예외 비전파 | 6 | PASS |
| IN-3 caller-owned checkpoint의 별도-프로세스 phase-boundary resume (+ 어댑터 영속화 IO 0) | 4 (+1) | PASS |
| IN-4 교체 시 caller/도메인 파일 해시 불변 + `core/`·`hqs/` import 0 | 2 | PASS |
| IN-5 `langgraph` import 1개 모듈 격리 + 차단 프로세스 import + 타입 누출 0 | 3 | PASS |

3개 시나리오(`clean` → BUY/COMPLETED, `data_gap` → HOLD/ESCALATED_DATA_GAP, `node_error` → catch-and-encode/COMPLETED)에서 Sequential Reference와 LangGraph 대조 어댑터의 최종 State가 dict deep-equal로 동치. 토론 Loop 본문 3회 실제 반복(`BULL r0/r1/r2`), 두 시나리오가 서로 다른 terminal 노드 도달.

### 8.3 (C) discharge 수준 (과장 없이)

- **재현했다**: (C)가 요구한 "v2 맥락 in-repo 통합 테스트"를 저장소 안의 실행 가능한 pytest로 재현. v2 A-IN 범위·도메인 형태 그래프.
- **완전 discharge 여부는 이 문서가 선언하지 않는다** → 후속 ADR 판정. 한계 3가지: (i) 노드가 결정론적 stub — 실제 엔진 비결정성 미검증(E3 §9-5 계승), (ii) 대조 어댑터가 여전히 LangGraph 단일 계보 — E1+E2+E3+E4 전부 동일 계보, (iii) seam(`run_full`/`run_phase*`)이 harness 로컬 관례 — `ADC-0020` §Q-C 확정 계약 아님.
- **Gate (B)(`ADC-0019` 재검토 조건 (c), 다른 계보/프로덕션 관찰)를 진전시키지 않는다.** (A)(v1 결정 2/5/9/11)와도 무관.
- LangGraph 채택·구현 착수·`IMPLEMENTATION_RULES` 해제·§14 승격 중 무엇도 발생시키지 않는다 — 전부 후속 절차(`ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence 자동 승격 없음").

### 8.4 §3.3 위험의 처리 결과

- **seam이 계약으로 굳는 오독** — `README.md`·테스트 docstring·EVIDENCE.md §2·§4에 "harness 로컬 관례, `ADC-0020` §Q-C 확정 계약 아님"을 반복 명시. `IN-4`가 `caller.py`·`domain/*`의 `adapters` 무의존을 강제.
- **결정론적 stub 한계** — EVIDENCE.md §4 한계 1로 명시. 후속 ADR 충분성 판정 입력.
- **LangGraph 계보 단일성** — EVIDENCE.md §4 한계 2·§5로 명시. (B) 미진전 확인.
- **격리 venv `langgraph` 설치** — `.venv`는 git-ignored, `IN-4`의 `git grep` gate가 production 누출 0을 강제(실측 0건).
