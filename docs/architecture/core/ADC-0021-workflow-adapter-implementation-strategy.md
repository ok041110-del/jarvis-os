# ADC-0021: Workflow Adapter Implementation Strategy — Sequential Reference와 LangGraph 구현체의 역할·선택 기준·교체 가능성 (ADC-0020 후속)

**Status**: Decided — Strategy Framing Accepted. Architecture/Governance Review PASS (§9). Commit/PR/Merge 대기(사용자 보고 후 진행), ADR 미착수.
**Author**: Claude Code
**선행 체인**: `RFC-0019` → `ADC-0019` → `ADR-0008` (BASELINE v1.12 §16.6 존재 Accept·Scoped·Conditional) → `RFC-0020` → `ADC-0020` → `ADR-0009` (BASELINE v1.13 §16.6 명칭 = **Workflow Adapter** + Adapter Contract 부속 명세 (a)(b)(d))
**대응 단계**: Execution Host의 존재(`ADC-0013`) → 명명(`ADC-0014`) → **구현 전략(`ADC-0015`)** 3단계 중 **구현 전략** 단계. `ADC-0020` §11 "그다음 — Implementation Strategy ADC", `RFC-0020` §8.2 Q-G~Q-J가 이 단계로 이연한 항목의 일부.

> 이 ADC는 §16.6 Workflow Adapter 책임의 **구현 전략만** 판단한다. 구체적으로 (1) Sequential Reference Implementation과 LangGraph 구현체의 **역할**, (2) 둘 사이의 **선택 기준**, (3) **교체 가능성(Reversibility)**이 이 전략 결정에서 갖는 위치 — 이 셋만 결정한다. §14 Kernel Public Contract를 승격하지 않고, Public Port/Surface/Guarantee/Interface를 정의하지 않으며, Rule B 충족을 선언하지 않고, Scheduler/Runtime orchestration/Event Bus를 다루지 않으며, mid-node resume/HITL을 열지 않는다. `IMPLEMENTATION_RULES.md`의 어떤 금지 조항도 해제하지 않는다(`ADC-0015`류 Scoped 부분 해제를 **하지 않는다**). Production Code를 구현하지 않고, `BASELINE.md`를 편집하지 않는다. 이 전략 결정은 §16.6이 이미 Accept한 범위 위에만 서며, Architecture나 Contract를 **선행 확장하지 않는다**.

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (셋으로 한정)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D1** | Sequential Reference Implementation의 **역할** — §16.6 Reversibility 필수 불변조건의 바닥이자 Adapter Contract 부속 명세 (a)(b)(d) 준수 판정의 기준선 | `RFC-0020` §5.2·§8.2 Q-H, `ADC-0020` §Q-B "범위 밖 → Implementation Strategy ADC 소유", `ADR-0009` §Out of Scope("'Sequential = Reference' 지정 및 Reference의 실체" = 후속 별도 결정) |
| **D2** | LangGraph 구현체의 **역할** — Reference도 채택된 구현체도 아닌, 교체 가능한 Implementation 후보 하나. E2/E3가 실측한 특정 능력의 후보로만 인용 | `ADC-0019` §Q8·조건 6, `ADC-0020` §7("LangGraph 최종 채택" = Out of Scope) |
| **D3** | Reference와 LangGraph 사이의 **선택 기준** — 어떤 조건이 동시에 성립할 때 LangGraph 평가가 열리는가 | `RFC-0020` §4.1·§8.2 Q-I, `ADC-0019` 재검토 조건 (c) |
| **D4** | **교체 가능성(Reversibility)**이 이 전략 결정에서 갖는 위치 — 교체점, 검증 방법, 그 검증의 실행 시점 | `BASELINE.md` §16.6 "Reversibility — 필수 Architecture 불변조건", `ADC-0019` §Q6·조건 4, `ADC-0020` §Q-D (d) |

### 1.2 이 ADC가 판단하지 않는 것 (경계 — 선행 확장 방지)

아래는 이 ADC의 자동 결과가 아니며, 이 전략 결정으로 인해 앞당겨지거나 열리지 않는다. 근거는 §7에 항목별로 재확인한다.

- §14 Kernel Public Contract 승격 / Public Port·Surface·Guarantee·Interface 정의
- Rule B 충족 선언 (미충족 유지, 재검토 조건 (c)는 다음 단계 hard gate로 존속)
- Scheduler / Runtime orchestration / Dynamic Routing / Event Bus / §6 넓은 Runtime
- mid-node resume / Human-in-the-loop / `RFC-0020` §4.2 C2 경로
- Checkpoint 입도 재론 (C1은 `ADC-0020` §Q-E-1이 이미 Accept — 이 ADC는 재론하지 않는다), phase 경계 선언 주체 (`ADC-0020` §Q-E-2 Defer 유지)
- (b) 예외→상태값 변환의 **강제·검증 메커니즘** 확정 (`RFC-0020` §8.2 Q-G) — 의무의 소재는 §16.6이 이미 "어댑터 책임"으로 확정, 이 ADC는 메커니즘을 확정하지 않는다
- (c) 병렬 State 동시 쓰기(disjoint key / reducer) 규약의 계약화·배치·HQ State 설계 구속 (`ADC-0020` §Q-D (c) Defer 유지, v1 `ADR-0007` 결정 11 결합)
- (d) Reversibility v2 통합 테스트의 **실행**
- Checkpointer 백엔드 선택 (`MemorySaver` / `PostgresSaver` 등)
- `IMPLEMENTATION_RULES.md` line 9/13/14/19의 전면·Scoped 해제
- Reference Implementation을 저장소 내 실제 코드로 두는지 (`RFC-0020` §8.2 Q-H의 "실체" 부분 — Scoped 해제 선행 필요)
- v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계
- `docs/decisions/adc/ADC.md` ADC-02 / `docs/architecture/core/ADC-0008` 재판단
- `BASELINE.md` §16.1~§16.5·§16.7 문언, §14, §15.2 무엇이든
- `BASELINE.md` 문언 편집 — 이 ADC는 지침만 남긴다. 지정을 §16.6/`GLOSSARY.md`에 반영할지는 후속 ADR의 판단(§8)

### 1.3 새 실험 없음

이 ADC는 `main`에 이미 병합·기록된 Evidence(E2 `.claude/docs/integrations/langgraph.md`, E3 `.claude/docs/integrations/langgraph-domain-poc.md`)와 Governance 문서(`BASELINE.md` v1.13, `RFC-0019`/`RFC-0020`, `ADC-0019`/`ADC-0020`, `ADR-0008`/`ADR-0009`, `IMPLEMENTATION_RULES.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`)만 인용한다. 새 PoC·프로토타입·측정을 수행하지 않는다.

### 1.4 RFC pairing 근거 (확정)

이 ADC의 RFC-level 개설은 **`RFC-0020` §8.2 (Open Questions — Implementation Strategy ADC로 이연)**가 수행한다. 별도의 `RFC-0021`을 새로 작성하지 않는다.

- `RFC-0020` §8.2는 Q-G(§Q-D (b) 강제·검증 방법)·Q-H(Reference Implementation의 실체)·Q-I(다른 계보 관찰의 적극적 확보)·Q-J(mid-node resume / C2 재검토 경로) 네 항목을, 각각의 이연 근거와 함께 "Implementation Strategy ADC(ADC-0020 이후)"로 명시 위임했다. `ADC-0020` §11도 "그다음 — Implementation Strategy ADC (`ADC-0015` 대응)"로 이 단계를 예고하고 §12 Open Issues에 동일 항목을 열거했다.
- 이 ADC가 결정하는 D1(Reference 역할)·D3(선택 기준)은 각각 `RFC-0020` §8.2 Q-H·Q-I가 연 질문의 부분집합이며, 새 Boundary Question이나 새 규범 표면을 열지 않는다 — Execution Host에서 `RFC-0015` §1 Boundary Question 하나가 `ADC-0015` Q0~Q4로 전개된 것과 같은 관계다.
- `RFC-0020` §8.2가 다루지 않은 항목은 이 ADC도 다루지 않는다: Q-G(b 메커니즘)·Q-J(mid-node/C2)는 §7 Out of Scope로 그대로 이연한다. 이 ADC는 §8.2가 위임한 범위를 넘지 않는다.
- 따라서 "core ADC는 짝 RFC를 갖는다"는 선례는 `RFC-0020`(§8.2)로 충족된다. 이 판단은 사용자 지시(2026-09-03)로 확정됐고 §10 R1은 해소(ACTIONED)됐다.

---

## 2. Evidence

`ADC-0020`이 사용한 P1~P14 중 이 ADC의 판단에 직접 쓰이는 것과, E2/E3에서 구현 전략에 관계된 관찰만 추린다. **RFC-0020 §5의 권고는 입력이지 결정이 아니다.**

| # | Evidence | 이 ADC에서의 용도 |
|---|---|---|
| **S1** | `BASELINE.md` §16.6 "Reversibility — 필수 Architecture 불변조건" — "어떤 구현체를 제거하고 다른 구현체(**최소한으로는 순차 함수 호출**)로 교체해도 Kernel·HQ 코드는 한 줄도 수정되지 않아야 한다. 구현체 고유 문법(`StateGraph`/`START`/`END`/Checkpointer API 등)은 이 책임의 경계 안에서만." | D1(Reference = 이 문언의 "순차 함수 호출" 구체화), D4 |
| **S2** | `BASELINE.md` §16.6 Adapter Contract 부속 명세 (d) — Reversibility 재확인, "검증 방법이 v2 맥락의 통합 테스트임을 명문화하는 것뿐이며, 그 통합 테스트의 **실행**은 이 반영의 결과가 아니다(후속 Implementation Strategy)" | D4(검증 방법과 실행 시점의 분리) |
| **S3** | E3 §7 (Reversibility 결과) — `adapter_sequential.py`가 동일 호출자 계약을 langgraph 없이 제공(Conditional = `if/elif`, Loop = `while`, 병렬 = `ThreadPoolExecutor`, reducer = `_merge()`). 두 시나리오(`clean`·`data_gap`) 모두 LangGraph `run_full` == 순차 `run_full` **최종 State 동치**. 어댑터 교체 시 `caller.py`·`domain/*` **파일 해시 불변**, 교체점은 "어느 adapter 모듈을 넘기느냐" **한 곳** | D1(순차 구현이 실재 가능·동치 실측), D4(교체점 1곳) |
| **S4** | E3 §6-d·블록 5-(f) — LangGraph 1.2.11은 super-step 내 동기 노드를 내부 thread pool로 **실제 wall-clock 병렬** 실행(fan-out 5노드 × 0.4s → wall ~0.4s, 순차 2.0s). 단 threads/GIL이므로 **I/O 바운드 노드에만** 유효, CPU 바운드는 이득 없음 | D2(LangGraph 고유 능력 1 — 조건부), D3 |
| **S5** | E3 §6-a·§9-1 — caller-owned 값 Checkpoint는 **phase 경계에서만** 재개. 임의 mid-node 재개는 LangGraph checkpointer(그래프 소유, `thread_id` 키)를 요구하며, A-IN(e)를 만족시키려면 "비관용적 shim"을 어댑터가 얹어야 함 | D2(LangGraph 고유 능력 2 — mid-node, 단 범위 밖), D3 |
| **S6** | E3 §6-b·§9-2 — LangGraph는 노드 예외를 `graph.invoke` 밖으로 그대로 전파(`RuntimeError` propagated 실측). §14.3 G-6 준수(catch-and-encode)는 **어댑터 책임**이지 LangGraph 보장이 아님. 실패를 값으로 반환한 경우(`NO_DATA`)는 하위 conditional 정상 반영·값 기반 종료 | D2(LangGraph 채택 시 감수 비용), D3 |
| **S7** | E3 §8 — 저장소 `core/`·`hqs/` 활성 `*.py`에 `langgraph`/`langchain` import 0건. PoC 내부 `langgraph` import = `adapter_langgraph.py` **1개 파일 2줄**. domain State 값에 `langgraph`/`langchain_core` 타입 누출 0 | D2(고유 문법의 경계 격리 실측), D4 |
| **S8** | E3 §9-6 — 재컴파일 오버헤드 미측정(`run_full`마다 `StateGraph` 재조립·`compile()`, v1 known gap 그대로). E3 §5-6 노드는 결정론적 stub — 실제 엔진 비결정성·부분 실패율 미검증 | D3(LangGraph 채택 시 미해소 gap) |
| **S9** | E2 §2.3·§Summary — `langgraph` 1.2.11은 `langchain-core`에만 의존(전체 `langchain` 불요). 핵심 API(`StateGraph`/`add_conditional_edges`/`compile()`)가 v1 PoC 시점 대비 하위 호환. E2의 Checkpoint는 **caller-owned 모델이 아님**(LangGraph 소유 `MemorySaver`), in-memory saver는 프로세스 종료 후 재개 불가 | D2(LangGraph의 의존성·안정성), D3 |
| **S10** | E2 §복원 노트·E3 §10 / `ADC-0019` §Q2·재검토 조건 (c) — E1 + E2 + E3 = 3건이나 **전부 LangGraph 계보**·프로덕션 트래픽 아님. Rule B(3건 이상 독립 관찰) 형식 미충족. 재검토 조건 (c) = 다른 계보 또는 v2 프로덕션 관찰 | D3(선택이 열리는 gate), §7 |
| **S11** | `ADC-0020` §Q-E-1 — Checkpoint 입도 C1(phase-boundary caller-owned) Accept. C2(LangGraph-native + shim)는 **Reversibility 불변조건 위반**(순차 어댑터가 그래프 소유 checkpointer의 mid-node 재개를 복제 못 함), mid-node resume은 범위 밖 | D2(LangGraph mid-node 능력이 범위 밖인 이유), D3 |
| **S12** | Execution Host `ADC-0015` §Q2·§Decision — 비용 미측정이 Accept 자체를 막지 않으나, "유일·영구 전략 Freeze"는 정당화하지 않는다(Conditional). 구현 착수는 후속 ADR 이후에만(§Next Step 3) | D3(선택 기준의 비대칭 형태), §5 Decision 형태 |
| **S13** | `ADR-0009` §6 / `ADC-0020` §6 조건 4 — 명칭·부속 명세 반영이 `IMPLEMENTATION_RULES.md`를 해제하지 않았다. `ADC-0015`류 부분 해제를 **하지 않는다**. `ADR-0004`(명칭만 반영, `IMPLEMENTATION_RULES.md` 무변경) 선례 | §5(이 ADC도 동일), §7 |

---

## 3. Alternatives

### 3.1 이 ADC의 형태

| | 내용 | 판정 |
|---|---|---|
| **F-0** | 구현 전략 전체(`RFC-0020` §8.2 Q-G~Q-J + `ADC-0020` §11 열거 전부: LangGraph 채택 여부, 어댑터 래핑 방식, Checkpointer 백엔드, (b) 강제 메커니즘, (c) 계약화, (d) 통합 테스트, Q-E-2, `IMPLEMENTATION_RULES` Scoped 해제)를 한 ADC에서 결정 | **Reject** — `ADC-0019` 재검토 조건 (c) + v1 결정 2/5/9/11이 hard gate로 미충족(S10). Gate가 닫힌 상태에서 채택·구현 착수·Scoped 해제를 결정하면 `ADC-0019`/`ADC-0020` 조건을 우회하게 된다 |
| **F-1 (채택)** | **역할·선택 기준·교체 가능성만** 결정. Gate에 걸린 항목(채택, 구현 착수, Scoped 해제, 계약 메커니즘)은 전부 §7로 이연하고, 이 ADC는 그 위에 서는 전략 프레이밍만 확정 | **Accept (§5)** — 사용자 지시 범위와 일치. `ADC-0015`가 "존재→명명" 확정 위에 "전략"만 얹은 것과 같은 층위이나, Gate 미충족으로 `ADC-0015`의 Scoped 해제 부분까지는 가지 않는다 |
| **F-2** | 이 단계 자체를 Defer — Gate가 열릴 때 한 번에 | **Reject** — Reference/LangGraph의 역할과 선택 기준이 미정이면 후속 Gate-clearing 절차(결정 2/5/9/11 RFC/ADR, 통합 테스트 설계)가 "무엇을 향해" 준비하는지 기준이 없다. 프레이밍은 Gate와 무관하게 지금 확정 가능(§4.1) |

### 3.2 Reference Implementation의 지정

| | 내용 | 비용 / 반대 근거 |
|---|---|---|
| **R-1 (권고 계승)** | **Sequential 순차 함수 호출 = Reference Implementation** (§16.6 "최소한으로는 순차 함수 호출"의 구체화, Reversibility 바닥, (a)(b)(d) 준수 판정 기준선). LangGraph = 교체 가능한 후보 하나 | `RFC-0020` §5.2 권고, E3 §7이 도메인 그래프에서 순차↔LangGraph 최종 State 동치 실측(S3). "Adapter"가 통상 래핑을 함의하나 Sequential Reference는 아무것도 안 감쌈 — 이는 의미 긴장(Minor)이지 채택을 막지 않음(`ADC-0020` §Q-B와 동일 판단) |
| **R-2** | **LangGraph = Reference** | `ADC-0019` §Q8·`RFC-0020` §4.1 N-3 위반. Reference를 서드파티 의미론에 묶음(예외 전파 기본값이 이미 G-6과 충돌 — S6). Rule B 미충족(S10). C2 경로가 Reversibility 약화(S11) |
| **R-3** | Reference를 지정하지 않고 "둘 다 동등 후보"로 | Reversibility 불변조건의 **바닥**이 구체화되지 않는다. §16.6이 "최소한으로는 순차 함수 호출"을 이미 명문화했으므로 바닥은 이미 순차 쪽 — 지정 회피는 그 문언과 어긋남 |

---

## 4. Analysis

### 4.1 프레이밍은 Gate와 독립적으로 확정 가능하다

`ADC-0019` 재검토 조건 (c)와 v1 `ADR-0007` 결정 2/5/9/11은 **§14 승격·Production 구현 착수·`IMPLEMENTATION_RULES` Scoped 해제**를 차단한다(S10, `ADC-0019` 조건 5). 그러나 이 ADC가 결정하는 세 가지 — Reference/LangGraph의 역할, 선택 기준, 교체 가능성의 위치 — 는 그 gate 뒤의 행위가 아니다.

- **역할 지정**은 용어·기준선 결정이다. §16.6 "최소한으로는 순차 함수 호출"(S1)과 `RFC-0019` §3의 "Workflow Adapter" 비공식 용법(`ADR-0009` §2.2로 공식화)이 이미 있는 자리에 "Sequential = Reference / LangGraph = 후보 하나"라는 층위를 못박을 뿐, 새 표면을 만들지 않는다.
- **선택 기준**은 "어떤 조건이 성립해야 LangGraph 평가가 열리는가"를 적는 것이다 — gate를 여는 것이 아니라 gate의 목록을 명시하는 것이며, `ADC-0019` 재검토 조건 (c)·`RFC-0020` §8.2 Q-I를 재기술한다.
- **교체 가능성**은 §16.6 필수 불변조건의 재확인이다(`ADC-0020` §Q-D (d)와 동일 성격). 검증 방법(v2 통합 테스트)은 이미 §16.6에 명문, 그 **실행**은 이 ADC가 하지 않는다(S2).

따라서 F-1은 `ADC-0019`/`ADC-0020`의 조건을 약화하지 않는다 — `ADC-0020`이 §16.6보다 "적게" 한 것처럼, 이 ADC는 `ADC-0020`보다 적게 한다: 경계를 확장하지 않고, §14로 승격하지 않으며, 구현·Scoped 해제를 승인하지 않는다.

### 4.2 Reference를 Sequential로 두는 것의 실측 근거 (D1)

E3 §7(S3)은 `ADC-0019` 이후 산출된 Evidence로서, `adapter_sequential.py`가 **langgraph 없이** 동일 호출자 계약을 제공하고 두 도메인 시나리오에서 LangGraph와 최종 State가 동치임을 실측했다. 조건부 분기는 `if/elif`, Loop는 `while`, 병렬은 `ThreadPoolExecutor`(= `hqs/investment/teams/stock_team.py`의 wave 모델과 동일 패턴), reducer 규칙은 `_merge()`로 재현됐다. 즉 §16.6 A-IN 5항목 전체가 서드파티 라이브러리 없이 순차 코드로 표현 가능함이 도메인 형태 그래프에서 확인됐다.

이것이 Reference로서의 요건을 채운다:
- **Reversibility 바닥** — "다른 구현체로 교체해도 Kernel·HQ 코드 0 변경"(S1)에서 그 "다른 구현체"의 최소 형태가 Sequential이며, E3 §7이 교체점이 1곳(호출자가 adapter 모듈을 인자로 받음)임을 실측했다(S3).
- **(a)(b)(d) 준수 판정 기준선** — 어떤 구현체든 Reference가 산출하는 최종 State와 동치여야 하고, (b) catch-and-encode는 Reference에서는 자명하게 성립한다(순차 함수가 예외를 값으로 반환). LangGraph는 이를 어댑터 코드로 강제해야 성립한다(S6).
- **라이브러리 비의존** — Reference는 `langchain-core` 등 어떤 외부 의존도 요구하지 않는다.

### 4.3 LangGraph의 역할을 "후보 하나"로 한정하는 근거 (D2)

E2/E3가 실측한 LangGraph의 능력 중 Sequential Reference가 제공하지 못하는 것은 둘뿐이다:
1. **super-step 내 실제 wall-clock 병렬**(S4) — 단 threads/GIL이라 I/O 바운드 노드(Jarvis 엔진 호출 계열)에만 유효. Sequential의 `ThreadPoolExecutor` wave 모델도 동일 제약 아래 동일 이득을 낸다(E3 §7이 순차 어댑터도 `ThreadPoolExecutor`를 씀) — 즉 이 능력은 LangGraph **고유가 아니다**.
2. **임의 mid-node 재개**(S5) — 그래프 소유 checkpointer 요구. 이는 `ADC-0020` §Q-E-1이 C1을 Accept하고 C2(LangGraph-native + shim)를 Reversibility 위반으로 판정한 그 경로이며(S11), **mid-node resume 자체가 `ADC-0019`·`ADC-0020`·`RFC-0020` §7의 범위 밖**이다.

LangGraph를 채택하면 감수해야 하는 비용은 명확하다: 예외 전파 기본값이 G-6과 충돌해 어댑터가 전 노드 catch-and-encode를 강제해야 하고(S6), 재컴파일 오버헤드가 미측정이며(S8), Rule B가 미충족이다(S10). 이 비용을 정당화할 **LangGraph 고유의, Sequential로 대체 불가능한** 능력 필요가 아직 관찰되지 않았다. 따라서 LangGraph는 "채택된 구현체"도 "Reference"도 아닌, **평가 대기 후보**로만 기록한다(`ADC-0019` §Q8, `ADC-0020` §7).

### 4.4 선택 기준의 형태 (D3)

`ADC-0015` §Q2가 "비용 미측정이 Accept를 막지 않으나 영구 Freeze도 정당화하지 않는다"는 비대칭을 취한 것과 유사하게(S12), 이 ADC도 비대칭을 취한다: **Sequential Reference가 기본이며, LangGraph는 영구 배제가 아니라 조건부 평가 대상**이다. 다만 `ADC-0015`와 달리 이 ADC는 구현 착수를 승인하지 않으므로(gate 미충족), "지금 Sequential로 구현을 시작한다"고 말하지 않는다 — "구현이 열릴 때 Sequential이 기본선이고 LangGraph는 §5 D3 조건이 모두 충족될 때만 후속 절차로 평가된다"고 말한다.

---

## 5. Decision

**A. Accept (Strategy Framing Only) — Sequential Reference를 기본선으로, LangGraph를 조건부 평가 후보로 확정. 구현 착수·Scoped 해제·계약 메커니즘은 결정하지 않는다.**

### D1. Sequential Reference Implementation의 역할

§16.6 Workflow Adapter 책임의 **Reference Implementation**은 **순차 함수 호출 형태**다 — 조건부 분기는 조건문, Loop는 반복문, 병렬 fan-out은 `ThreadPoolExecutor`(HQ가 이미 쓰는 wave 패턴), 공유 누적은 명시적 merge 함수. 그 역할은 셋이다:

1. **Reversibility 필수 불변조건(§16.6)의 바닥** — "최소한으로는 순차 함수 호출로 교체해도 Kernel·HQ 코드 0 변경"(S1)에서 그 "순차 함수 호출"의 지정된 형태.
2. **Adapter Contract 부속 명세 (a)(b)(d) 준수 판정의 기준선** — 어떤 구현체든 동일 입력에 대해 Reference가 산출하는 최종 State와 동치여야 하며(E3 §7 실측 방식, S3), (b) 실행 결과의 값 표현은 Reference에서 자명하게 성립한다.
3. **라이브러리 비의존 기준점** — 외부 의존 없이 A-IN 5항목 전체를 표현한다(E3 §7이 도메인 그래프에서 확인, S3).

**이 D1이 결정하지 않는 것**: Reference를 저장소 내 실제 코드로 두는지, 계약 문서상 기준선으로만 두는지(`RFC-0020` §8.2 Q-H의 "실체" 부분). 저장소 코드화는 `IMPLEMENTATION_RULES.md` line 9/13/14/19의 Scoped 해제를 선행 요구하며, 그 해제는 이 ADC의 범위 밖이다(§7, S13). D1은 **역할의 지정**까지만 확정한다.

### D2. LangGraph 구현체의 역할

LangGraph는 §16.6 Workflow Adapter의 **교체 가능한 Implementation 후보 하나**이며, Reference도 채택된 구현체도 아니다. 그 역할은 다음으로 한정된다:

- E2/E3가 실측한 능력 — (i) super-step 내 I/O 바운드 노드의 실제 wall-clock 병렬(S4, 단 Sequential의 `ThreadPoolExecutor`도 동일 제약 아래 동일 이득), (ii) 그래프 소유 checkpointer 기반 임의 mid-node 재개(S5, 단 이는 `ADC-0020` §Q-E-1 C2 = Reversibility 위반 경로이자 범위 밖) — 을 제공하는 **평가 대기 후보**로만 인용된다.
- LangGraph 고유 문법(`StateGraph`/`START`/`END`/Checkpointer API)은 Workflow Adapter 경계 안에서만 쓰인다(§16.6 Reversibility 문언, E3 §8 실측 — import 1개 파일·State 타입 누출 0, S7).

**LangGraph를 채택하지 않는다.** 최종 채택은 `ADC-0019` §Q8·`ADC-0020` §7이 Out of Scope로 둔 항목이며, §5 D3 네 조건이 모두 충족되기 전에는 선택 자체가 열리지 않는다. 이 ADC의 지위에서 확정 기록: **LangGraph는 현재 "평가 대기 후보"이고, D3 네 조건이 동시에 충족되어 그 평가를 수행하는 별도 ADC가 Accept하기 전까지 어떤 형태로도 채택되지 않는다** — 저장소 의존성 추가, 어댑터 코드 배선, `IMPLEMENTATION_RULES` 해제 신청 중 무엇도 이 ADC를 근거로 진행할 수 없다.

### D3. 선택 기준 — Sequential Reference vs LangGraph

**Sequential Reference가 기본선(default)이다.** LangGraph는 아래 네 조건이 **모두 동시에** 성립할 때에만 후속 절차(별도 RFC → ADC → ADR)로 평가 대상이 된다:

1. **Sequential Reference로 충족 불가능한, LangGraph 고유의 구체적 능력 필요가 반복 관찰됨** — 1회 관찰은 Evidence로 인정하지 않는다(`ADC-0019`·`IMPLEMENTATION_RULES.md` 재검토 Trigger와 동일 기준). §4.3에 따라 wall-clock 병렬은 Sequential도 제공하므로 이 조건을 단독으로 채우지 못한다.
2. **`ADC-0019` 재검토 조건 (c) 충족** — LangGraph와 다른 계보 또는 v2 프로덕션 맥락의 조건부 분기·Loop 실행 관찰이 추가되어 독립 관찰 3건에 도달(S10). E1/E2/E3는 전부 LangGraph 계보이므로 이를 채우지 못한다.
3. **v1 `ADR-0007` 결정 2/5/9/11(Core 소유 Lifecycle 소비·Team/Division 경계·`IWorkflowEngine` Port·State Model)의 v2 공백이 후속 Architecture 절차로 해소됨**(`ADC-0019` 조건 5).
4. **Reversibility 필수 불변조건이 v2 맥락 in-repo 통합 테스트로 재현 검증됨**(`ADC-0019` §Q6·조건 4·Next Step 4). E1 `test_workflow_adapter_reversibility.py`는 cross-architecture 부분 할인(`ADC-0019` G2), E3 §7은 저장소 밖 PoC — 둘 다 이 조건을 채우지 못한다.

**기준의 방향성**: Reversibility 위험이 최소인 것은 Sequential Reference다. LangGraph는 그 대비 (a) 서드파티 의미론 결합(예외 전파 기본값이 G-6과 충돌 — S6), (b) mid-node resume 경로가 Reversibility 약화(S11), (c) 재컴파일 오버헤드 미측정(S8)을 감수한다. 이 비용을 상쇄할 LangGraph 고유 능력 필요가 위 조건 1로 확인되지 않으면 Sequential Reference를 유지한다.

**AND 게이트임을 명시**: 네 조건은 OR가 아니라 AND다. 조건 1(고유 능력 필요의 반복 관찰)이 충족되어도 조건 2·3·4 중 하나라도 미충족이면 LangGraph 평가 ADC를 열 수 없다. 역으로 조건 2·3·4가 모두 충족되어도(예: 다른 계보 관찰 확보 + v1 결정 해소 + 통합 테스트 통과) 조건 1이 없으면 Sequential Reference를 유지하는 것이 기본 결론이며, LangGraph로의 전환을 강제하지 않는다. 현재 네 조건 중 충족된 것은 **없다**.

### D4. 교체 가능성(Reversibility)의 위치

- Reversibility는 §16.6 필수 Architecture 불변조건이며, 이 ADC가 새로 만들지 않는다 — 재확인만 한다(`ADC-0020` §Q-D (d)와 동일 성격).
- **교체점**: 구현체 교체는 "호출자가 어느 adapter 모듈을 인자로 받느냐" 한 곳에서 일어난다(E3 §7 실측, S3). 두 구현체는 동일 호출자 계약을 제공하고, 교체 시 호출자·도메인 파일은 해시 불변이다. (호출자 계약의 구체 시그니처는 이 ADC가 확정하지 않는다 — `RFC-0020` §5.3, `ADC-0020` §Q-C가 규정한 "구현체 내부 의무" 층위에 머문다.)
- **검증 방법**: v2 맥락의 in-repo 통합 테스트(`ADC-0019` 조건 4, `ADC-0020` §Q-D (d), `BASELINE.md` §16.6 (d)). 
- **검증의 실행 시점**: 이 ADC의 결과가 **아니다**(S2). §5 D3 조건 3·4가 충족되고 구현이 열리는 단계의 선행 요구사항이다. 이 ADC는 그 통합 테스트를 설계·실행하지 않는다.

### Decision 형태 — 왜 "Strategy Framing Only"인가

`ADC-0015`는 "존재→명명" 확정 위에 구현 전략을 Conditional Accept하면서 `IMPLEMENTATION_RULES.md`를 Scoped 해제했다. 이 ADC는 그 마지막 단계(Scoped 해제·구현 착수)까지 가지 않는다 — `ADC-0019` 재검토 조건 (c)와 v1 결정 2/5/9/11이 hard gate로 미충족이기 때문이다(S10, S13). 따라서 이 ADC는 `ADC-0015`의 Q0~Q3(전략 판단)에 대응하는 부분만 수행하고, Q4(`IMPLEMENTATION_RULES` 해제)에 대응하는 부분은 §7로 이연한다. `ADR-0004`가 명칭만 반영하고 `IMPLEMENTATION_RULES.md`를 건드리지 않은 선례, `ADR-0009` §6이 이를 계승한 선례와 같은 층위다(S13).

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6 전부 무변경** — 범위(A-IN)·명시적 제외(A-OUT)·§16.3~16.5 불가침·Reversibility 필수·조건 이월·미확정 항목.
2. **`ADC-0020` §6 Conditions 1~8 전부 무변경** — 특히 조건 4(`IMPLEMENTATION_RULES.md` 금지 유지, `ADC-0015`류 부분 해제 없음), 조건 5(§14 미승격), 조건 8(Adapter Contract 정식화 범위 = (a)(b)(d), (c) Defer).
3. **Rule B 미충족 유지** — E1+E2+E3 전부 LangGraph 계보. `ADC-0019` §Q2 판정과 재검토 조건 (c)는 §5 D3의 조건 2로, 그리고 이후 모든 단계(채택·구현 착수·Scoped 해제)의 hard gate로 그대로 유효하다. 이 ADC는 Rule B 충족을 선언하지 않는다.
4. **v1 `ADR-0007` 결정 2/5/9/11 미해결(Conditional) 유지** — 해소 전 §14 승격·Production 구현 착수 불가. 이 ADC는 네 공백을 설계하지 않는다.
5. **§14 Kernel Public Contract 미승격 유지** — Public Port·Surface·Guarantee·Interface 신설 없음. §14.1 "Task 전달 책임" 계약 범위 밖 상태 그대로. Adapter Contract 부속 명세의 비-§14 지위(`ADC-0020` §Q-C) 계승.
6. **`IMPLEMENTATION_RULES.md` 금지 유지** — line 9(Workflow Parser) / line 13(Scheduler·우선순위·Workflow orchestration·Dynamic Routing·§6 넓은 Runtime) / line 14(Stage 재진입·조건부 Stage) / line 19(Event Bus). 이 ADC는 `ADC-0015`류 Scoped 부분 해제를 **하지 않는다**.
7. **`BASELINE.md` 문언 무변경** — §16.6 개정 여부는 후속 ADR. 이 ADC는 전략 지침만 남긴다.
8. **Reversibility 필수 불변조건 유지** — v2 통합 테스트 재현 검증 요구 그대로, 실행은 gate 충족 후 구현 단계.
9. **Checkpoint 입도 C1 무변경** — `ADC-0020` §Q-E-1이 Accept한 C1을 이 ADC는 재론하지 않는다. phase 경계 선언 주체(§Q-E-2)는 Defer 유지.

---

## 7. Out of Scope (이 ADC의 자동 결과가 아닌 것 — 경계 재확인)

| 항목 | 상태 유지 근거 |
|---|---|
| **LangGraph 최종 채택** / 어댑터 래핑 방식 | `ADC-0019` §Q8, `ADC-0020` §7. §5 D3 네 조건 미충족 |
| **Production Adapter 구현 착수** (`core/`·`hqs/` 코드) | `IMPLEMENTATION_RULES.md` line 9/13/14/19, `ADC-0019` 조건 5, `BASELINE.md` §16.6 "Production 구현과의 관계" |
| **Reference Implementation의 저장소 코드화** | `RFC-0020` §8.2 Q-H "실체" 부분 — Scoped 해제 선행 필요. D1은 역할 지정까지만 |
| **`IMPLEMENTATION_RULES.md` line 9/13/14/19 Scoped 해제** | `ADC-0020` §6 조건 4, `ADR-0009` §6. `ADC-0015` Q4 대응 단계는 gate 충족 후 별도 ADR |
| **§14 Kernel Public Contract 승격 / Public Port 정의** | `ADC-0019` §Q7·조건 5, §14.1, `ADC-0020` §Q-C L3 |
| **Rule B 충족 선언 / `ADC-0019` §Q2 재판단** | S10 — 재검토 조건 (c) 미충족. §5 D3 조건 2로 재기술만 |
| **Checkpointer 백엔드 선택** (`MemorySaver`/`PostgresSaver` 등) | 구현 관심사, gate 후 구현 전략 세부 |
| **(b) 예외→상태값 강제·검증 메커니즘** (정적 분석 / Conformance Test) | `RFC-0020` §8.2 Q-G, `ADC-0020` §Q-D (b) "메커니즘은 후속 Implementation Strategy가 다룬다" — 이 ADC는 **의무의 소재를 재확인만** 하고 메커니즘을 확정하지 않는다 |
| **(c) 병렬 State disjoint key / reducer 규약의 계약화·배치·HQ State 설계 구속** | `ADC-0020` §Q-D (c) Defer 유지, `ADR-0009` §3. v1 `ADR-0007` 결정 11 결합 후속 판정 |
| **(d) Reversibility v2 통합 테스트의 실행** | `BASELINE.md` §16.6 (d), `ADC-0019` Next Step 4 — gate 후 구현 단계의 선행 요구 |
| **mid-node resume / HITL / C2 경로** | `ADC-0020` §Q-E-1, `RFC-0020` §7 |
| **phase 경계 선언 주체 (Q-E-2)** | `ADC-0020` §Q-E-2 Defer — Investment/Development HQ 관점 입력 필요 |
| **Scheduler / Runtime orchestration / Event Bus / §6 넓은 Runtime** | A-OUT, `IMPLEMENTATION_RULES.md`, `ADC-0019` §Q4 |
| **v1 `ADR-0007` 결정 2/5/9/11 재설계** | `ADC-0019` §Q7·조건 5 |
| **`docs/decisions/adc/ADC.md` ADC-02 / `ADC-0008` 재판단** | `ADC-0019` §Q8 |
| **`BASELINE.md` §16.1~§16.5·§16.7 / §14 / §15.2 문언** | 참조만, 문자 그대로 유지 |
| **`BASELINE.md` 문언 편집** | → 후속 ADR (§8) |

---

## 8. Next Step

**ADR 필요 여부 — 조건부.**

- **§16.6 / `GLOSSARY.md`에 "Sequential = Reference Implementation" 지정을 반영하려면**: Minor ADR 1건이 필요하다(`ADR-0004`가 명칭을, `ADR-0009`가 부속 명세를 반영한 것과 같은 granularity). 그 ADR은 §16.6 "Reversibility — 필수 Architecture 불변조건" 문단의 "최소한으로는 순차 함수 호출"을 "Reference Implementation(§16.6 구현 전략 기준선, `ADC-0021`)"으로 명시하고, `GLOSSARY.md`에 "Reference Implementation" 항목을 추가하는 데 그친다. `IMPLEMENTATION_RULES.md`·§14·§16.1~§16.5는 무변경(`ADR-0009` §6 선례).
- **전략 기록만으로 충분하다고 판단되면**: 이 ADC가 `ADC-0021`로 존속하고 `BASELINE.md` 변경은 없다. §16.6이 이미 "최소한으로는 순차 함수 호출"을 담고 있으므로 지정은 그 문언의 해석 확정에 해당한다.

권고: **후자(전략 기록만)**. §16.6 문언이 이미 순차 함수 호출을 Reversibility 바닥으로 명문화했고, "Reference"라는 라벨은 이 ADC와 `GLOSSARY.md`가 참조 가능한 형태로 보유하면 충분하다. Minor ADR은 gate-clearing 절차와 함께 묶어도 늦지 않다.

### 이 ADC 이후의 진입 순서 (구현은 이 목록의 맨 끝)

```
ADC-0021 (이 문서) Accept  ← RFC pairing = RFC-0020 §8.2 (확정, §1.4). RFC-0021 신규 작성 안 함
  ↓
[선택] Minor ADR — "Sequential = Reference" 지정을 §16.6/GLOSSARY에 반영 (§8 권고: 이연 가능)
  ↓
━━━ 이하 hard gate (현재 하나도 충족되지 않음) ━━━
  ↓
(A) v1 ADR-0007 결정 2/5/9/11 v2 공백 해소 — 후속 ADR 또는 별도 RFC (ADC-0019 조건 5·Next Step 5)
(B) ADC-0019 재검토 조건 (c) 충족 — 다른 계보 또는 v2 프로덕션 맥락의 조건부 분기·Loop 실행 독립 관찰로 3건 도달 (RFC-0020 §8.2 Q-I)
(C) Reversibility 필수 불변조건의 v2 맥락 in-repo 통합 테스트 설계·재현 검증 (ADC-0019 조건 4·Next Step 4)
  ↓
Implementation Strategy 세부 ADC — LangGraph 채택 가부(B·C 결과 입력), (b) 강제 메커니즘(Q-G), (c) 계약화(Q-D (c)+결정 11), Checkpointer 백엔드, phase 경계 선언 주체(Q-E-2)
  ↓
Scoped 해제 ADR — IMPLEMENTATION_RULES.md line 9/13/14/19를 A-IN 범위에 한해 Scoped 해제 (ADC-0015 Q4 대응, ADC-0019 Next Step 2)
  ↓
Workflow Adapter Production 구현 착수 (Sequential Reference 기본선)
```

**정확한 진입 조건 — 다음 "구현" 단계는 아래가 모두 참일 때에만 열린다:**

1. 이 ADC가 Accept됨(RFC pairing = `RFC-0020` §8.2, 확정 — §1.4). 선택적 Minor ADR(§8)은 이연 가능.
2. **(A)** v1 `ADR-0007` 결정 2(Core 소유 Lifecycle 소비)·5(Team/Division 경계)·9(`IWorkflowEngine` Port)·11(State Model)의 v2 대응 부재가 후속 Architecture 절차(ADR 또는 별도 RFC)로 해소됨 — 미해결 시 §14 승격·구현 착수 불가(`ADC-0019` 조건 5).
3. **(B)** `ADC-0019` 재검토 조건 (c) 충족 — LangGraph 계보가 아닌 관찰 또는 v2 프로덕션 맥락 관찰이 추가되어 독립 관찰 3건에 도달. E1/E2/E3(전부 LangGraph 계보, 프로덕션 트래픽 아님)는 이를 채우지 못한다. LangGraph 채택을 평가하려는 경우에 한해 필수이며, Sequential Reference만으로 구현하는 경우에도 `ADC-0019` Conditional 성격상 (c)는 Reversibility 재현 검증(C)과 함께 요구된다.
4. **(C)** Reversibility 필수 불변조건이 v2 맥락 in-repo 통합 테스트로 재현 검증됨(`ADC-0019` §Q6·조건 4·Next Step 4). E1 `test_workflow_adapter_reversibility.py`(cross-arch 부분 할인)·E3 §7(저장소 밖 PoC)은 대체하지 못한다.
5. **Scoped 해제 ADR**이 `IMPLEMENTATION_RULES.md` line 9/13/14/19를 §16.6 A-IN 범위에 한해 Scoped 해제함(Scheduler/orchestration/Event Bus/§6 넓은 Runtime 구현 금지는 계속 유지 — `ADC-0013` Q4·`ADC-0016` §Next Step 2 패턴).
6. 위 전 과정에서 §14 승격 없이 A-IN 범위 구현만 진행 — Public Port 정의는 여전히 별도(§14.1 "Task 전달 책임" 해소가 상위 선행).

현재 2·3·4·5 중 **충족된 것은 없다.** 따라서 이 ADC 직후의 다음 단계는 구현이 아니라 위 (A)·(B)·(C)를 향한 Gate-clearing 절차이며, 그 착수 순서(어느 것을 먼저)는 이 ADC가 정하지 않는다.

---

## 9. Architecture / Governance Review

`RFC-0019`→`ADC-0019`→`ADR-0008`, `RFC-0020`→`ADC-0020`→`ADR-0009`, `BASELINE.md` v1.13 §16.6, E2/E3, `IMPLEMENTATION_RULES.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`를 기준으로 이 ADC의 범위·Traceability·기존 RFC/ADC/ADR 정합성을 검증한다(최종 Review — 사용자 지시 2026-09-03).

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 이 ADC가 선행 체인(`ADC-0019`/`ADC-0020`/`ADR-0008`/`ADR-0009`)이 확정한 것을 뒤집거나 재론하는가 | **아니오** — §16.6 존재·A-IN·A-OUT·Reversibility·명칭·부속 명세 (a)(b)(d)·(c) Defer·C1·조건 이월을 모두 전제로만 사용(§6 Conditions 1·2·9). |
| 이 ADC가 `ADC-0020` §11·`RFC-0020` §8.2가 예고한 "Implementation Strategy ADC" 단계에 대응하는가 | **예** — `ADC-0020` §11 "그다음 — Implementation Strategy ADC (`ADC-0015` 대응)", `RFC-0020` §8.2 Q-H(Reference 실체)·Q-I(다른 계보 확보)에 부분 대응. Q-G(b 메커니즘)·Q-J(mid-node/C2)는 명시적으로 Out of Scope(§7). |
| **RFC pairing** — 이 ADC에 선행하는 RFC가 필요한가 | **충족 (확정).** RFC-level 개설 = `RFC-0020` §8.2 (Q-G~Q-J를 이연 근거와 함께 "Implementation Strategy ADC"로 명시 위임). `ADC-0020` §11·§12도 동일 항목을 이 단계로 예고. 이 ADC의 D1·D3은 §8.2 Q-H·Q-I의 부분집합이며 새 Boundary Question을 열지 않는다(§1.4). 별도 `RFC-0021`을 새로 만들지 않는다(사용자 지시 2026-09-03). `RFC-0015` 단일 Boundary Question이 `ADC-0015` Q0~Q4로 전개된 것과 같은 관계 — 선례 위반 없음. → §10 R1 ACTIONED. |
| `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준"(① 지금 결정 안 하면 상위 Architecture 진행 불가 / ② 늦어질수록 되돌리는 비용 큼)을 만족하는가 | **①에 해당** — Reference/LangGraph의 역할·선택 기준이 미정이면 후속 Gate-clearing 절차((A)(B)(C))가 "무엇을 향해" 준비하는지 기준선이 없다(§4.1). 프레이밍 확정은 그 상위 절차의 진입 전제다. |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다"를 준수하는가 | **예** — E2/E3는 저장소 밖 PoC이며(E3 §9-7), 이 ADC는 그것으로 채택·구현을 발생시키지 않는다. 프레이밍 판단에만 인용. |

### 9.2 경계 — Architecture/Contract 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임을 추가했는가 | **아니오** — §16.6 책임은 `ADC-0019`가 Accept 완료. 이 ADC는 그 구현 전략의 역할·기준만 판단. |
| 새 Layer/Component/Concept을 추가했는가 | **아니오** — "Reference Implementation"은 §16.6 "최소한으로는 순차 함수 호출" 문언에 붙는 라벨이지 새 Concept이 아니다(§4.1). |
| Contract Change가 있는가 | **없음** — 공개 Interface·Public Port·Guarantee 정의 없음. §14 무변경(§6 조건 5). Adapter Contract 부속 명세((a)(b)(d))의 문언도 건드리지 않음 — (b) "메커니즘"은 확정하지 않고 의무 소재만 재확인. |
| §16.6 A-IN/A-OUT 범위를 넓혔거나 좁혔는가 | **아니오** — 인용만. |
| Checkpoint 입도(C1) / phase 경계 선언 주체(Q-E-2)를 건드렸는가 | **아니오** — C1 무변경, Q-E-2 Defer 유지(§6 조건 9). |
| `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`를 이 ADC가 변경하는가 | **아니오** — §8이 후속 ADR 지침만 남기고, 권고는 "전략 기록만, Baseline 변경 없음"이다. |
| 이 전략 결정이 구현·Scoped 해제·§14 승격 중 무엇이든 앞당기는가 | **아니오** — §5 Decision 형태·§7·§8 진입 조건이 (A)(B)(C)+Scoped 해제 ADR을 전부 hard gate로 유지. `ADR-0004`/`ADR-0009`가 명칭·명세만 반영하고 `IMPLEMENTATION_RULES.md`를 유지한 선례와 동일 층위(S13). |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| BASELINE v1.13, RFC/ADC/ADR 0019·0020, E2/E3 기준으로 **구현 전략만** 결정 | **준수** — §5 D1~D4가 역할·선택 기준·교체 가능성만. |
| Public Contract·§14 승격·Rule B 충족·Scheduler/Runtime/Event Bus·mid-node/HITL은 **결정하지 않음** | **준수** — §1.2·§6·§7에 전부 명시적 제외. |
| Governance 허용 범위·`IMPLEMENTATION_RULES` 금지 준수, Architecture/Contract 선행 확장 금지 경계 설정 | **준수** — §9.2, §6 조건 6, §7. `ADC-0015`류 Scoped 해제를 하지 않음을 §5 Decision 형태에서 명시. |
| Production Code·Commit/PR/Merge 없음 | **준수** — 이 파일 1건만 작성(미커밋). 코드 무변경. Commit/PR/Merge는 사용자 보고 후 별도. |
| 다음 구현 단계의 정확한 진입 조건 제시 | **준수** — §8 "정확한 진입 조건" 1~6, 현재 충족된 것 없음 명시. |
| RFC-0020 §8.2를 RFC pairing으로 인정, RFC-0021 신규 미작성 | **준수** — §1.4·§9.1. |
| D1~D4 유지 + Sequential=Reference / LangGraph=평가 대기 후보 / 4조건 동시 충족 전 채택 불가 | **준수** — §5 D1~D4, D2 확정 기록, D3 "AND 게이트임을 명시". |
| §8 A·B·C + Scoped 해제/§14 선행조건을 hard gate로 유지, 구현·Contract 승격·`IMPLEMENTATION_RULES` 해제 미선행 | **준수** — §6·§7·§8. §5 Decision 형태가 `ADC-0015` Q4(Scoped 해제) 대응 단계를 이연으로 명시. |

### 9.4 판정

**PASS (무조건).** §10 R1(RFC pairing)이 ACTIONED로 해소되어 잔여 조건이 없다. 이 ADC는:

- `ADC-0019` §Decision 조건 1~6, `ADC-0020` §6 Conditions 1~8, v1 `ADR-0007` 결정 2/5/9/11 미해결, Rule B 미충족, `IMPLEMENTATION_RULES.md` line 9/13/14/19 금지를 하나도 약화하지 않는다(§6).
- 새 Architecture 책임·Layer·Component·Concept·Public Interface를 추가하지 않고, §14를 승격하지 않으며, `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`를 변경하지 않는다(§9.2).
- `RFC-0020` §8.2가 위임한 범위(Q-H·Q-I) 안에서만 결정하고, §8.2가 이연 상태로 둔 Q-G·Q-J는 그대로 Out of Scope로 유지한다(§1.4·§7).
- 구현·Contract 승격·`IMPLEMENTATION_RULES` Scoped 해제를 선행하지 않으며, 그 전부를 §8의 hard gate((A)(B)(C) + Scoped 해제 ADR)로 유지한다.

Status를 **Decided — Strategy Framing Accepted**로 확정한다. Commit/PR/Merge는 사용자 보고 후 진행한다(§Next Step 아님 — 절차 유보).

---

## 10. 수정사항 (Review 결과)

| ID | 항목 | 조치 |
|---|---|---|
| **R1** | **RFC pairing** — 선례상 모든 core ADC는 짝 RFC를 가진다. `RFC-0020` §8.2가 Q-G~Q-J를 이연 근거와 함께 "Implementation Strategy ADC"로 명시 위임했는지, 그것이 별도 `RFC-0021`을 대체하는지. | **ACTIONED (2026-09-03)** — 사용자 지시로 `RFC-0020` §8.2를 이 ADC의 RFC-level 개설로 인정한다. `RFC-0021`을 새로 만들지 않는다. §1.4 신설, §9.1 RFC pairing 행 "충족(확정)"으로 갱신, Status Draft → Decided. 이 ADC의 D1·D3이 §8.2 Q-H·Q-I의 부분집합이고 새 Boundary Question을 열지 않음을 §1.4에서 입증. |
| **R2** | **§8 ADR 필요 여부** — "Sequential = Reference" 지정의 `BASELINE.md` §16.6 반영은 Minor ADR 대상이나, §16.6 기존 문언("최소한으로는 순차 함수 호출")이 이미 이를 담고 있어 이연 가능. | **반영 완료** — §8 권고대로 **전략 기록만**으로 두고, Minor ADR은 Gate-clearing 절차와 묶어 후속 판단. 이 ADC로 `BASELINE.md` 변경 없음. |
| **R3** | **§5 D3 조건 (B)의 적용 범위** — 재검토 조건 (c)가 "LangGraph 평가"에만 필요한지, "Sequential만으로 구현"하는 경우에도 필요한지. | **반영 완료** — §8 진입 조건 3에 명시: `ADC-0019` Conditional 성격상 (c)는 Reversibility 재현 검증(C)과 함께 Sequential 단독 구현에도 요구된다. |

**잔여 수정사항 없음.** R1 ACTIONED, R2·R3 문언 반영 완료. §9.4 판정 = PASS(무조건).

---

## 11. Traceability

| 문서 / 절 | ADC-0021과의 관계 | 정합성 |
|---|---|---|
| `RFC-0020` §8.2 (Open Questions — Implementation Strategy ADC로 이연) | **이 ADC의 RFC-level 개설 (RFC pairing 확정)** | 별도 `RFC-0021` 미작성. D1·D3이 §8.2 Q-H·Q-I 부분집합, 새 Boundary Question 없음(§1.4). `RFC-0015`→`ADC-0015` Q0~Q4 전개와 동형 |
| `RFC-0020` §5.2 (Sequential = Reference 권고) / §8.2 Q-H | D1의 입력(권고), 확정은 이 ADC | 권고를 자동 채택이 아니라 E3 §7(S3) 실측으로 독립 지지. "실체"(저장소 코드화)는 Q-H대로 이연(§7) |
| `RFC-0020` §8.2 Q-I (다른 계보 관찰 확보) | D3 조건 2·§8 진입 조건 (B) | 재기술만 — `ADC-0019` 재검토 조건 (c) 원문 유지 |
| `RFC-0020` §8.2 Q-G (b 강제 메커니즘) / Q-J (mid-node/C2) | 명시적 Out of Scope | §7 — 이 ADC가 다루지 않음 |
| `ADC-0020` §Q-B ("Sequential = Reference"는 범위 밖 → Implementation Strategy ADC 소유) | 이 ADC가 그 소유 단계 | D1이 지정을 수행. `ADC-0020`이 유보한 자리를 채움 |
| `ADC-0020` §Q-C (Adapter Contract = §16.6 A-IN 부속, 비-§14) | §6 조건 5 | 무변경 — 이 ADC는 호출자 계약 시그니처를 확정하지 않음(§5 D4) |
| `ADC-0020` §Q-D (b) (메커니즘은 후속 Implementation Strategy) / (c) Defer | §7 | (b) 의무 소재만 재확인, 메커니즘 미확정. (c) Defer 유지 |
| `ADC-0020` §Q-E-1 C1 Accept / §Q-E-2 Defer | §6 조건 9 | C1 재론 안 함, Q-E-2 Defer 유지 |
| `ADC-0020` §7 (LangGraph 채택·Impl Strategy·§14 승격 = Out of Scope) / §11 Next Step | 이 ADC가 §11이 예고한 단계 | §7 목록을 이 ADC도 그대로 Out of Scope로 유지 |
| `ADC-0019` §Decision 조건 1~6 / 재검토 조건 (c) / Next Step 2·4·5 | §6 조건 1·3·4·§8 진입 조건 | 전부 무변경. (c)는 §5 D3 조건 2로 재기술, hard gate 존속 |
| `ADR-0009` §Out of Scope ("'Sequential = Reference' 지정 및 Reference의 실체" = 후속 별도 결정) / §6 (`IMPLEMENTATION_RULES.md` 무변경) | D1이 그 "후속 별도 결정"에 대응 | 지정만 수행, 실체(코드화)는 이연. `IMPLEMENTATION_RULES.md` 무변경 계승(S13) |
| `BASELINE.md` §16.6 "Reversibility 필수 불변조건" / Adapter Contract (a)(b)(d) / "Production 구현과의 관계" | D1·D4의 근거, §6·§7 | 문언 인용만, 무변경 |
| `BASELINE.md` §14 / §14.1 / §15.2 / §16.1~§16.5 / §16.7 | §6 조건 5·7·§7 | 무변경, 참조만 |
| E2 `.claude/docs/integrations/langgraph.md` | S9·S10 | 기록 상태 그대로 인용, 새 실험 없음 |
| E3 `.claude/docs/integrations/langgraph-domain-poc.md` §6·§7·§8·§9·§10 | S3~S8 | 기록 상태 그대로 인용. E3 §10이 "후속 Governance 판단 입력"으로 넘긴 것을 이 ADC가 부분 수용(역할·기준), 나머지(계약 메커니즘)는 이연 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 / "Dynamic Workflow 재검토 Trigger" | §6 조건 6·§7·§8 | 무변경. D3 조건 1의 "1회 관찰 불인정"은 이 문서의 재검토 Trigger 기준과 동일 |
| `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준" / "Experimental Implementation" | §9.1 | ①에 해당, Experimental Evidence 자동 승격 금지 준수 |
| Execution Host `ADC-0015` (구현 전략 단계) / `ADR-0004` (명칭만 반영) | 대응 선례 | `ADC-0015` Q0~Q3에 대응(전략 판단), Q4(Scoped 해제)는 gate 미충족으로 이연. `ADR-0004`류 "명칭·전략만, `IMPLEMENTATION_RULES.md` 유지" 층위 |

---

## 12. Self-Review

- `ADC-0019`/`ADC-0020`이 결정하지 않은 것을 새로 결정했는가 — **역할·선택 기준·교체 가능성만**. 채택·구현 착수·Scoped 해제·계약 메커니즘·§14 승격·Rule B·mid-node/HITL·Scheduler/Event Bus는 §7에 전부 Out of Scope.
- "Sequential = Reference"를 지정했는가(RFC-0020 권고의 자동 채택이 아니라) — **예**(D1) — E3 §7 실측(S3)으로 독립 지지, "실체"(저장소 코드화)는 Q-H대로 이연.
- LangGraph를 채택했는가 — **아니오**(D2) — "평가 대기 후보"로만. §5 D3 네 조건은 AND 게이트이며 현재 충족된 것 없음. 저장소 의존성·어댑터 배선·`IMPLEMENTATION_RULES` 해제 신청 중 무엇도 이 ADC를 근거로 불가.
- RFC pairing을 어떻게 처리했는가 — **`RFC-0020` §8.2로 확정**(§1.4·§9.1·§10 R1 ACTIONED) — `RFC-0021` 신규 미작성.
- 선택 기준이 gate를 여는가, 아니면 gate를 명시하는가 — **명시**(D3·§4.1) — `ADC-0019` 재검토 조건 (c)·v1 결정 2/5/9/11·Reversibility 통합 테스트를 재기술.
- Reversibility 검증을 실행했거나 실행을 이 ADC의 결과로 만들었는가 — **아니오**(D4·S2) — 검증 방법(v2 통합 테스트)은 §16.6에 이미 명문, 실행은 gate 후 구현 단계.
- §14 / Public Port / Guarantee를 신설·우회했는가 — **아니오**(§6 조건 5·§9.2) — Adapter Contract 부속 명세의 비-§14 지위 계승, (b) 메커니즘 미확정.
- `IMPLEMENTATION_RULES.md`를 변경했거나 Scoped 해제를 결정했는가 — **아니오**(§6 조건 6·§9.2) — `ADC-0015`류 부분 해제 없음, `ADR-0004`/`ADR-0009` 선례 계승.
- `BASELINE.md`·`GLOSSARY.md`·`ADC.md`를 변경했는가 — **아니오**(§8·§9.2) — 후속 ADR 지침만, 권고는 "전략 기록만".
- Checkpoint 입도(C1)·phase 경계 선언 주체(Q-E-2)·(c) Defer를 건드렸는가 — **아니오**(§6 조건 9·§7).
- Rule B 충족을 선언했는가 — **아니오**(§6 조건 3) — 미충족 유지, 재검토 조건 (c)를 다음 단계 hard gate로 재확인.
- 새 실험/PoC를 수행했는가 — **아니오**(§1.3) — `main` 병합 Evidence(E2/E3)와 Governance 문서만 인용.
- Production Code를 변경했는가 — **아니오**.
- 이 전략 결정이 Architecture나 Contract를 선행 확장하는가 — **아니오**(§9.2) — §16.6 이미 Accept된 범위 위에만 서고, 새 책임·Layer·Component·Concept·Interface 없음.
- 다음 구현 단계의 정확한 진입 조건을 제시했는가 — **예**(§8) — (A)(B)(C) + Scoped 해제 ADR, 현재 충족된 것 없음을 명시.
- ADR이 필요한가 — **조건부**(§8·§10 R2) — 지정을 `BASELINE.md`에 반영하려면 Minor ADR, 전략 기록만이면 불요(권고: 후자, 이연 가능).
- 미해소 절차 항목이 있는가 — **아니오**(§10) — R1 ACTIONED, R2·R3 반영 완료. §9.4 판정 = PASS(무조건). Status = Decided.
- Commit/PR/Merge를 했는가 — **아니오** — PASS 이후에도 사용자 보고를 먼저 하고 다음 Gate-clearing 단계로 넘어간다(사용자 지시 2026-09-03).
