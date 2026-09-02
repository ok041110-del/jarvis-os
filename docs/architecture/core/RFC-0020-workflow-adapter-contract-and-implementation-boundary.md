# RFC-0020: Workflow Adapter Contract와 구현체 경계 (§16.6 Scoped Workflow Graph Execution 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §16.6(Scoped Workflow Graph Execution, Accept·Scoped·Conditional)이 **"이 Accept가 결정하지 않는 것"**으로 남긴 항목 중 — 이 책임의 **명칭**과 **구현체 경계(Adapter Contract)**. `docs/architecture/core/ADC-0019` §Q8·§Decision 조건 6이 여는 후속 3단계(존재 완료 → **명명** → 구현 전략) 중 "명명" 단계를, E3가 산출한 구체 Findings를 근거로 계약 정식화와 함께 개설한다.

**Evidence**: E1 `archive/v1/docs/adr/0007-workflow-execution-model.md`(Accepted) + `archive/v1/adapters/workflow-langgraph/` + `test_workflow_adapter_reversibility.py`; E2 `.claude/docs/integrations/langgraph.md`(toy PoC, 검증일 2026-08-30, `main` Traceability 복원 2026-09-02); E3 `.claude/docs/integrations/langgraph-domain-poc.md`(Domain PoC, 2026-09-02, 26/26 check). 근거 문서: `BASELINE.md` §6·§7·§13.3·§14.1·§15.2·§16.3~16.7·§17, `docs/architecture/core/RFC-0019`·`ADC-0019`·`ADR-0008`, Execution Host 선례 `RFC-0013`·`ADC-0013`·`ADR-0003`(등재)·`RFC-0014`·`ADC-0014`·`ADR-0004`(명명)·`RFC-0015`·`ADC-0015`·`ADR-0005`(구현 전략), `docs/decisions/adc/ADC.md` ADC-02, `docs/architecture/core/ADC-0008`, `hqs/development/IMPLEMENTATION_RULES.md`, `hqs/investment/checkpoint.py`. **새로운 실험은 수행하지 않는다** — 이미 `main`에 병합·기록된 E1/E2/E3만 인용한다.

> 본 RFC는 §16.6 책임의 명칭을 확정하지 않는다. Adapter Contract 절을 확정하지 않는다. LangGraph 채택을 승인하지 않는다. Checkpoint 입도를 확정하지 않는다. §14 Kernel Public Contract를 확장하지 않으며 — 이 RFC가 말하는 **"Workflow Adapter Contract"는 §14 Kernel Public Contract가 아니고**, Public Port·Public Surface·Public Guarantee·Public Interface를 신설하지 않는다(§5 도입부·§7). `IMPLEMENTATION_RULES.md` 금지 조항을 해제하지 않는다. 코드·Baseline·RFC-0019·ADC-0019·ADR-0008·IMPLEMENTATION_RULES·CLAUDE.md를 수정하지 않는다. 이 RFC가 여는 것은 **"§16.6이 등재한 이름 없는 책임에 이름을 부여하고, 그 책임의 구현체가 지켜야 할 경계(계약)를 E1/E2/E3 근거로 후보 형태로 정식화할 수 있는가"**라는 좁은 질문 하나다.

---

### 0. 이 RFC가 열린 이유

`RFC-0019` → `ADC-0019` → `ADR-0008`은 "§16.3~16.5 너머의 조건부 분기·Loop·값 기반 Checkpoint/Resume 실행 책임"의 **존재만** `BASELINE.md` §16.6에 Accept(Scoped, Conditional)로 등재했다. 그 과정에서 세 문서 모두 다음을 명시적으로 후속 절차로 미뤘다(`ADC-0019` §Q8·§Decision 조건 6, `ADR-0008` §Out of Scope):

- 이 책임의 **명칭**(Workflow Adapter / Workflow Engine 등 — 두 후보 병기, 미확정)
- **구현체 선택**(LangGraph 채택 여부, v1처럼 순차 함수 호출 유지)
- **Public Port 정의**
- **구현 전략**

세 문서는 Execution Host의 선례 — 존재(`ADC-0013`) → 명명(`ADC-0014`) → 구현 전략(`ADC-0015`) 3단계 분리 — 를 그대로 따르도록 지시했다. **이 RFC는 그중 "명명" 단계를 개설한다.** 다만 Execution Host의 `RFC-0014`가 명칭만 다룬 것과 달리, 이 RFC는 명칭에 **Adapter Contract 후보 절 정식화**를 묶는다. 이유는 `ADC-0019` 판정 **이후** 산출된 E3(`langgraph-domain-poc.md`, 2026-09-02)가 RFC-0019 §7 Pseudo-Contract가 명명하지 못했던 구체적 경계 조건(예외 전파, 병렬 State 스키마, Checkpoint 소유 입도)을 실측으로 드러냈고, E3 §10이 이를 "`ADC-0019` 후속 Governance 판단 입력"으로 명시적으로 넘겼기 때문이다. 명칭을 정하는 자리가 곧 그 이름이 짊어질 계약을 정하는 자리다.

**이 번들링(명명 + 계약 후보 정식화)은 Execution Host `ADC-0014`(명명 단독) → `ADC-0015`(구현 전략) 분리 선례로부터의 이탈이다.** 이 RFC는 그 이탈을 사유와 함께 공시할 뿐이며, 번들링을 허용할지 계약 절을 별도 단계로 분리할지는 ADC-0020이 **먼저** 판정한다(§8.1 Q-A).

이 RFC는 `RFC-0013`/`RFC-0016`/`RFC-0017`이 반복한 절차적 선례(넓게 묻지 않고 좁게 묻는다)를 따른다 — "LangGraph를 도입할 것인가"가 아니라 "이 책임의 구현체 경계를 무엇으로 규정하고 무엇으로 부를 것인가"만 연다.

---

### 1. Context

- **§16.6 (BASELINE v1.12)**: `RFC-0019` → `ADC-0019` → `ADR-0008` 절차로 Scoped Workflow Graph Execution 책임의 **존재**가 Accept됐다. A-IN 5항목 = (a) State 보유, (b) Node 진행, (c) Conditional Edge, (d) Loop, (e) 값 기반 Checkpoint/Resume. Reversibility가 **필수 Architecture 불변조건**으로 등재. A-OUT(Routing/Registry·Policy·Discovery·Domain Lifecycle·Event Bus·§16.5 저장 게이트·Multi-HQ decomposition·Registry 일반화) 명시 제외. v1 `ADR-0007` 결정 2/5/9/11의 v2 공백은 **미해결(Conditional)**로 이월 — 해소 전 §14 Public Contract 승격·Production 구현 착수 불가. `IMPLEMENTATION_RULES.md` 금지 조항 전면 유지.
- **RFC-0019 §7 Pseudo-Contract**: 책임·불변조건·경계·Reversibility 조건을 "개념 수준, 실행 가능한 코드 아님"으로 서술. E3 이전에 작성됨. **명칭 "Workflow Adapter"는 `RFC-0019` §3·§7이 이미 비공식 작업 용어로 사용**했으나, `ADC-0019` §Q8·`ADR-0008` §Out of Scope가 이를 의도적으로 미확정 상태로 두고 두 후보("Workflow Adapter / Workflow Engine")를 병기했다.
- **§14.1**: "Task 전달 책임"은 여전히 "이 계약의 범위 밖". `ADC-0019` §Q7/G3은 이것이 v1 결정 9(`IWorkflowEngine` Port) 공백의 상위 원인이며 이 책임보다 상위의 별도 Open 질문이라고 정리했다. → RFC-0020은 Public Port를 제안하지 않는다.
- **§15.2**: "이 흐름에는 영속화 지점이 없다 … '보관한다'는 것은 **호출자가** 그 값을 들고 있는 것." §16.6 A-IN(e)와 `ADC-0019` §Q3가 이 패턴을 그대로 준용.
- **§7 System Boundary**: "Workflow의 도메인 내용"은 HQ 책임. 어댑터는 "무엇을 실행할지"를 정하지 않는다.
- **E3 (ADC-0019 이후 산출)**: Investment HQ Stock Team 의미(5-way 병렬 → Bull/Bear 토론 Loop → Trader Decision → 조건부 라우팅)를 담은 13-node 도메인 그래프에서 26/26 check. Reversibility(LangGraph ↔ 순차 최종 State 동치)를 **도메인 형태 그래프**에서 실측했고, RFC-0019 §7이 명명하지 않은 3건의 Findings를 산출했다(§3 Evidence).

**`ADC-0019` §Decision 조건 1~6은 이 RFC로 전부 무변경이다.** RFC-0020은 §16.6의 존재·A-IN·A-OUT·Reversibility 불변조건·Conditional gap 이월·구현 착수 금지 중 어느 것도 건드리지 않는다.

---

### 2. Problem

§16.6은 책임의 존재와 비공식 Pseudo-Contract만 등재했다. 그 결과:

1. **이 책임에 확정된 이름이 없다.** `RFC-0019`가 "Workflow Adapter"를 비공식으로 썼으나 `ADC-0019`가 미확정으로 두었고, 하위 문서는 `§16.6` 또는 절 제목 전체로 지칭해야 한다. Execution Host 선례(`ADC-0014`)는 명명이 별개 Governance 단계이며, 이름을 비워 두면 후속 문서가 암묵적으로 이름을 귀속시킬 위험이 있음을 보여준다.
2. **RFC-0019 §7 Pseudo-Contract는 E3보다 앞선다.** E3는 Pseudo-Contract가 명명하지 못한 구체 경계를 드러냈다 — (i) LangGraph는 노드 예외를 `graph.invoke` 밖으로 **그대로 전파**하며 이는 `ADC-0019` §Q3·§14.3 G-6("예외를 던지지 않고 값으로")과 정면 충돌한다, (ii) reducer 없는 공유 키 병렬 쓰기는 `InvalidUpdateError`로 **크래시**한다, (iii) caller-owned 값 Checkpoint는 **phase 경계에서만** 재개되고 임의 mid-node 재개는 그래프 소유 checkpointer를 요구한다. 이를 계약 후보 절로 정식화하지 않으면, 후속 구현 전략 ADC는 구현체를 평가할 **경계 있는 계약**을 갖지 못한다.
3. **구현체 경계가 정의돼 있지 않다.** `ADC-0019` §Q6는 Reversibility를 요구하고 "최소한으로는 순차 함수 호출"을 바닥으로 언급하지만, 어느 구현이 **기준(reference)**이고 어느 구현이 **선택(optional)**인지는 명시하지 않았다.
4. **"LangGraph 도입"이 계속 질문으로 오독된다.** `RFC-0019` Non-goals와 `ADC-0019` §Q8은 그것이 질문이 아니라고 명시했다. RFC 수준에서 프레이밍을 교정할 필요가 있다 — 질문은 **Adapter Contract와 구현체 경계**이며, LangGraph는 교체 가능한 구현체 하나, 순차 함수 호출이 Reference다.

---

### 3. Evidence — E1/E2/E3가 증명하는 것과 증명하지 못하는 것

| | 증명하는 것 | 증명하지 **못하는** 것 |
|---|---|---|
| **E1** — v1 `ADR-0007` (`archive/v1`, Accepted) | LangGraph를 `IWorkflowEngine` 구현체로 실사용 검증. `StateGraph`/Node/`START`/`END` 문법이 `adapters/workflow-langgraph` 내부에만 존재, Core는 5개 Phase 전체에서 LangGraph 무인지. **Adapter Reversibility를 통합 테스트로 증명**(`test_workflow_adapter_reversibility.py` — Contract Parity 3 + Reversibility 1 + Fail-Closed 3). Team 생명주기 전이는 Core에 잔류, 어댑터는 호출 순서만 조립. 병렬 fan-out/fan-in **구조** 구성. | v2 이식성 — v1은 Team/Division을 Core Domain Model로 가졌고 v2 §5는 Kernel이 이를 모른다고 명시 → 결정 2/5/11 직접 이식 불가(`ADC-0019` G2). 병렬 fan-out은 **구조만** 검증(동시성 미검증, v1 known gap). Cancellation 미구현. 그래프 재컴파일 오버헤드 gap. Reversibility 테스트는 **cross-architecture로 부분 할인**(`ADC-0019` G2). |
| **E2** — toy PoC (`langgraph.md`, 2026-08-30) | `langgraph` 1.2.11이 격리 venv에서 `langchain-core`에만 의존해 설치·실행. toy 카운터 State→Node→Conditional Edge→Loop이 목표값 도달 시 종료. `MemorySaver` 기반 mid-graph 중단/재개(동일 `thread_id`)가 동작(checkpoint 히스토리 6건). 핵심 API(`StateGraph`/`add_conditional_edges`/`compile()`)가 v1 대비 하위 호환. | 도메인 형태 아무것도 검증 안 함. **A-IN(e)의 caller-owned 소유 모델이 아님**(E2는 LangGraph 소유 `MemorySaver` 사용). v2 Reversibility 미검증. "병렬 + 조건부" 상호작용 미검증. Traceability 주의: E2 파일은 2026-09-02까지 `main`에서 orphan 상태였고, 복원은 traceability만 해소 — **"Evidence가 `main`에 존재" ≠ "Evidence가 충분"**. |
| **E3** — Domain PoC (`langgraph-domain-poc.md`, 2026-09-02) | Investment HQ Stock Team 의미의 13-node 그래프에서 26/26 check: Conditional Edge + Loop(3라운드) + 시나리오별 상이한 terminal 노드. **caller-owned 값 Checkpoint**(어댑터가 plain-JSON dict 반환, 호출자가 영속화)가 phase 경계에서 동작하고 **프로세스 종료 후에도 재개**됨 — E2의 in-memory `MemorySaver`는 재개 불가. 어댑터 격리(langgraph import 1개 파일, State에 타입 누출 0). **도메인 그래프에서 Reversibility 실측** — 두 시나리오 모두 LangGraph `run_full` == 순차 `run_full` 최종 State, 어댑터 교체 시 caller/domain 파일 해시 불변. 병렬: disjoint 키 안전 병합 / reducer 없는 공유 키 → `InvalidUpdateError` / `Annotated[list, operator.add]` → 결정론적 병합 / 노드 예외 → `graph.invoke` 밖 전파 / fan-out 5×0.4s → wall ~0.4s. | 노드는 **결정론적 stub** — 실제 엔진 비결정성·부분 실패율 미검증. caller-owned 모델에서 **임의 mid-node 재개 불가**(그래프 소유 checkpointer 요구). 재컴파일 오버헤드 미측정. **저장소 밖 실행** — 저장소 내 통합 테스트 승격은 별도 결정(`ADC-0019` Next Step 4). **여전히 전부 LangGraph 계보**, 프로덕션 트래픽 아님. |

**Rule B 상태 (미충족 유지).** E1 + E2 + E3 = 3건이나 **전부 LangGraph 계보**이고 프로덕션 트래픽이 아니다. `ADC-0019` §Q2는 이 대상에 대해 Rule B 형식 미충족을 이미 명시했고 `ADC-0013`/`ADC-0016`보다 무겁게 작용한다고 판정했다. `ADC-0019` 재검토 조건 (c)는 **다른 계보 또는 v2 프로덕션 관찰**로 독립 3건에 도달할 것을 요구하며, E3는 그것을 채우지 못한다. **RFC-0020은 Rule B 충족을 주장하지 않으며 `ADC-0019`의 Conditional 성격을 약화하지 않는다.** E3가 더한 것은 세 번째 독립 계보가 아니라 **계약의 정밀도** — 어떤 구현체가 채우든 어댑터 경계가 지켜야 할 절이 무엇인지를 알려준다.

---

### 4. Alternatives

#### 4.1 명칭 · 구현체 경계

| | 내용 | 비용 / 반대 근거 |
|---|---|---|
| **N-0** | 명명·계약 정식화를 후속 구현 ADC까지 더 미룬다 | 하위 문서가 절 제목 전체로 계속 지칭. E3 Findings 미반영 상태 방치. 후속 구현 ADC가 계약을 처음부터 재도출. Execution Host는 구현 전략(`ADC-0015`)보다 **먼저** `ADC-0014`에서 명명됨 — 선례에 어긋남 |
| **N-1 (권고)** | 명칭 = **Workflow Adapter**(`RFC-0019` §3·§7이 이미 비공식으로 쓴 용어, `ADC-0019` §Q8이 미확정으로 병기한 두 후보 중 전자). **Sequential 함수 호출 = Reference Implementation**(Reversibility 바닥이자 계약 준수 기준선). **LangGraph = 교체 가능한 Implementation 후보 하나**. RFC-0019 §7 Pseudo-Contract + E3 Findings를 Adapter Contract 후보 절로 정식화 | "Adapter"가 Reversibility 불변조건을 이름에 담는다(v1 용어, `ADC-0019` §Q5·§Q6). Sequential을 Reference로 두면 Reversibility 바닥이 구체적·테스트 가능해진다(v1 결정 12, `ADC-0019` §Q6 "최소한으로는 순차 함수 호출"). LangGraph를 구현체 하나로 두면 `ADC-0019` §Q8 구현 중립성 유지. **주의**: "Adapter"는 통상 기존 인터페이스 래핑을 함의하나 Sequential Reference는 아무것도 래핑하지 않는다. 명칭 확정 시 ADC-0020/ADR은 이 이름과 §16.6 Baseline 제목 "Scoped Workflow Graph Execution"의 대응을 명시해야 한다(`ADR-0004`가 "Execution Host" ↔ §16.3을 명시한 선례) |
| **N-2** | 명칭 = **Workflow Engine** (v1 `IWorkflowEngine` 계승) | "Engine"이 §16.2 Engine Adapter(Model/LLM)와 충돌 — `RFC-0019` §3이 한 절을 들여 둘을 분리했는데 "Engine"을 재사용하면 그 구분이 다시 흐려진다 |
| **N-3** | **LangGraph를 Reference Implementation**으로 | `ADC-0019` §Q8·Non-goals 위반(LangGraph를 정답으로 전제하지 않음). Reference를 서드파티 라이브러리 의미론에 묶는다(E3 §6-b: 예외 전파 기본값이 이미 G-6과 충돌). Rule B 미충족 |

#### 4.2 Checkpoint 입도 (E3 §6-a의 (i)/(ii)/(iii))

§5.3 (a)가 정하는 것은 **값 소유 모델**(어댑터는 값을 생산만, 호출자가 영속화)뿐이다. 그 위에서 **재개 지점을 어디로 한정할지**가 아래 C1/C2/C3의 문제이며, 이 선택은 ADC-0020의 몫이다.

| | 내용 | 평가 |
|---|---|---|
| **C1 (권고)** | **phase-boundary caller-owned checkpoint** — 어댑터가 선언된 phase 경계에서 직렬화 가능한 State 값을 반환, 호출자가 영속화 후 반환해 재개 | A-IN(e) 문언에 그대로 부합. 순차 어댑터로도 성립(라이브러리 무관). 프로세스 종료 후 재개됨(E3 블록 2). 한계: phase 경계에서만 재개, 임의 mid-node 불가 |
| **C2** | **LangGraph-native checkpointer + 직렬화 shim** — `get_state().values` 추출 + fresh saver + `update_state` 주입으로 호출자가 값을 보유하는 형태를 흉내 | 임의 mid-node 재개 획득. 비용: E3 §6-a가 shim을 "비관용적"으로 평가. 계약을 LangGraph checkpointer 내부에 결합. Reversibility 약화(순차 어댑터가 mid-node 재개를 복제 못 함). **mid-node resume 자체가 이 RFC 범위 밖**(§7) |
| **C3** | **순차 전용 값 반환** — 계약에 Checkpointer 개념을 아예 두지 않음. 어댑터는 최종/중간 State 값만 반환, "재개" = 호출자가 값으로 재호출 | 가장 단순·가장 reversible. 비용: phase 경계 "중단 후 나중에 이어서" 자체를 명명된 계약 능력에서 포기. A-IN(e)가 명시한 Checkpoint/Resume을 사실상 축소 제공 |

**권고: C1** — RFC 단계 권고이며 **최종 채택은 후속 ADC**의 몫. C1은 A-IN(e)의 해석 중 E3가 두 어댑터에서 동일하게 동작하고 프로세스 종료를 견딤을 보인 것이다. C2의 mid-node 능력은 범위 밖이고, C3는 A-IN이 명시한 능력 하나를 버린다.

---

### 5. Proposal (권고안 — 결정 아님)

**이 절의 지위 (반드시 먼저 읽을 것)**

- 아래 §5.3의 후보 절 (a)~(d)의 문구는 **ADC-0020이 채택·수정·기각할 초안 문언**이다. 이 RFC가 채택한 규칙이 아니다. 절 안의 "금지"·"책임"·"규약" 같은 표현은 후보 절이 확정될 경우의 예상 문언이지 현재 발효 중인 규칙이 아니다.
- **"Workflow Adapter Contract"는 `BASELINE.md` §14 Kernel Public Contract가 아니다.** 이 RFC는 Public Port·Public Surface·Public Guarantee·Public Interface를 신설하지 않는다. 후보 절 (a)~(d)는 §16.6 책임의 **구현체가 지켜야 할 내부 경계 조건**이며, `RFC-0019` §7 Pseudo-Contract("개념 수준, 실행 가능한 코드 아님")와 동일한 지위다. §14 승격은 `ADC-0019` §Q7·§Decision 조건 5가 계속 금지한다(§7). 이 "Adapter Contract"가 §16.6 A-IN의 부속 규약인지 별도 계층인지, §14와 표기상 어떻게 구분하는지는 ADC-0020이 정한다(§8.1 Q-C).
- **명칭 "Workflow Adapter"는 새 용어가 아니다.** `RFC-0019` §3·§7이 이미 비공식 작업 용어로 사용했다. 그러나 `ADC-0019` §Q8·`ADR-0008` §Out of Scope는 이 명칭을 의도적으로 미확정 상태로 두고 "Workflow Adapter / Workflow Engine" 두 후보를 병기했다. 이 RFC는 그 두 후보 중 전자를 **권고**할 뿐, 확정하거나 이미 정해진 것으로 취급하지 않는다.

**5.1** 이 RFC의 핵심 주제는 **"Workflow Adapter Contract와 구현체 경계"이며, "LangGraph 도입"이 아니다.** LangGraph는 교체 가능한 Implementation 후보 하나로만 등장한다.

**5.2 명칭 권고**: §16.6 책임의 이름 = **Workflow Adapter**. **Sequential 함수 호출 형태 = Reference Implementation** (Reversibility 바닥, 계약 준수 판정의 기준선). **LangGraph = 교체 가능한 Implementation 후보 하나** (채택 여부는 후속 ADC). 명칭 확정 시 §16.6 Baseline 제목 "Scoped Workflow Graph Execution"과의 매핑, `GLOSSARY.md` 등재 형태는 ADC-0020/ADR이 명시한다(§8.1 Q-B).

**5.3 Adapter Contract 후보 절 권고** (RFC-0019 §7 Pseudo-Contract의 정식화 — 위 "이 절의 지위" 참조, 후속 ADC가 채택·수정·기각):

- **(a) caller-owned checkpoint 값 소유 모델** — 진행 상태(중간/최종)는 직렬화 가능한 값으로 표현되며, 어댑터는 그 값을 **생산**만 하고 영속화·복원을 소유하지 않는다(`BASELINE.md` §15.2·§16.6 A-IN(e) 준용). **재개 입도(phase 경계 재개 / 임의 mid-node 재개)는 이 절이 정하지 않는다** — 그 선택은 §4.2의 C1/C2/C3 문제이며 ADC-0020의 몫이다(§8.1 Q-E).
- **(b) exception → state** — 실패·취소를 예외가 아닌 State 값으로 표현한다. LangGraph 등 구현체가 노드 예외를 실행 경계 밖으로 전파하더라도(E3 §6-b 실측), `ADC-0019` §Q3·§14.3 G-6("예외를 던지지 않고 값으로") 준수는 **구현체의 보장이 아니라 어댑터의 책임**으로 둔다. catch-and-encode 강제·검증 방법은 미정(§8.2 Q-G, 이연).
- **(c) parallel State의 disjoint key / reducer 규약** — 병렬 fan-out 노드가 동일 State에 쓸 때는 서로소(disjoint) 키에 쓰거나, 공유 누적이 필요하면 명시 reducer(`Annotated[list, operator.add]` 등)를 선언한다. reducer 없는 공유 키 병렬 쓰기는 비결정·오류를 유발한다(E3 §6-c: `InvalidUpdateError` 실측). **Carve-out**: 이 절은 **병렬 쓰기 안전 메커니즘만** 제약한다. Workflow State Model 자체(v1 `ADR-0007` 결정 11의 v2 재설계 대상, 미해결)를 정의하지 않으며, "무엇을 State에 담을지"는 `BASELINE.md` §7에 따라 HQ의 Workflow 도메인 책임으로 남는다. 이 규약이 §13.3 A-1~A-5류의 구조 불변식에 해당하는지, HQ State 설계에 구속력을 갖는지는 ADC-0020이 판단한다(§8.1 Q-D).
- **(d) Reversibility (기존 불변조건의 재확인)** — 이는 **신규 제안이 아니다.** `BASELINE.md` §16.6이 이미 "필수 Architecture 불변조건"으로 등재했다(`ADC-0019` §Q6). 이 RFC가 더하는 것은 그 불변조건을 Adapter Contract 절로 **명시적으로 재기술**하고 검증 방법을 붙이자는 것뿐이다: 어떤 구현체를 제거하고 다른 구현체(최소한 Sequential)로 교체해도 Kernel·HQ 코드 0 변경, 구현체 고유 문법은 어댑터 경계 안에서만, 그리고 `ADC-0019` §Q6·Next Step 4가 요구하는 **v2 맥락 통합 테스트로 재현 검증**. E1 `test_workflow_adapter_reversibility.py`는 cross-architecture로 부분 할인되고(`ADC-0019` G2), E3 §7은 도메인 그래프에서 실측했으나 저장소 밖 PoC이지 in-repo 통합 테스트가 아니다.

**5.4 Checkpoint 입도 권고**: **C1 (phase-boundary caller-owned)**. §5.3 (a)가 정한 값 소유 모델 위에서, 재개 지점을 어댑터가 선언한 **phase 경계**로 한정하는 선택지다. RFC 단계 권고로만 제시하며 C2/C3는 §4.2에 보존한다. 최종 채택은 ADC-0020.

**5.5** 이 RFC는 위 전부를 권고로만 제시한다. 명칭 확정, Adapter Contract 절 확정, 구현체 선택, C1 채택은 모두 **후속 ADC(ADC-0020, 신설 예정)**의 몫이다. 이 RFC는 그 판단을 내리지 않는다.

---

### 6. Consequences

- **후속 ADC가 Accept할 경우**: §16.6 책임에 "Workflow Adapter" 명칭이 부여되고(별도 ADR → `BASELINE.md`, Execution Host §16.3 명칭이 `ADR-0004`로 반영된 것과 동일 절차, `GLOSSARY.md` 절 추가 포함 가능). Adapter Contract 후보 절 (a)~(d)가 계약으로 확정되면 후속 구현 전략 ADC가 구현체를 평가하는 기준이 된다. **여전히** §14 Public Contract 승격 아님, `IMPLEMENTATION_RULES.md` 해제 아님, Production 구현 착수 아님.
- **후속 ADC가 Accept하지 않을 경우**: §16.6은 이름 없는 책임으로 남고 E3 Findings는 후속 구현 ADC가 재도출해야 한다. `ADC-0019`의 모든 조건은 그대로 유지된다.
- **`ADC-0019` §Decision 조건 1~6은 이 RFC로 전부 무변경이다** — Conditional 성격 유지. Rule B는 이 RFC로도 충족되지 않으며, 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰)는 계속 미충족.
- **명명·계약 후보 정식화는 구현을 앞당기지 않는다.** `ADR-0003`이 §16.3 "Execution Host"의 존재를 등재하고 `ADR-0004`가 명명하면서도 `IMPLEMENTATION_RULES.md` 구현 금지를 유지했으며, Scoped 해제는 구현 전략이 확정된 `ADR-0005`가 별도로 수행했다 — 명명·계약과 구현 금지는 **공존**한다. Sequential을 Reference Implementation으로 권고하는 것도 지금 그 코드를 저장소에 두는 것을 승인하지 않는다.
- 이 RFC는 `BASELINE.md`·`RFC-0019`·`ADC-0019`·`ADR-0008`·`IMPLEMENTATION_RULES.md`를 **수정하지 않는다.** 실제 Architecture 문언 무변경.

---

### 7. 명시적으로 범위 밖 (RFC-0020으로 변하지 않음)

| 항목 | 상태 유지 근거 |
|---|---|
| §14 Kernel Public Contract 승격 (Workflow Adapter Port를 Public으로) | `ADC-0019` §Q7·§Decision 조건 5 — §14.1 "Task 전달 책임"이 계약 범위 밖인 한 근거 없음. v1 결정 2/5/9/11 공백 해소 전 불가. **§5.3의 "Adapter Contract"는 §14 Public Contract가 아니다** — Public Port·Surface·Guarantee·Interface 신설 없음 |
| `IMPLEMENTATION_RULES.md` 금지 해제 (Workflow Parser line 9 / Scheduler·Dynamic Routing·§6 넓은 Runtime line 13 / Stage 재진입·조건부 Stage line 14 / Event Bus line 19) | `ADC-0019` §Decision 조건 5·`ADR-0008` §4 — 전면 유지. Scoped 해제는 조건 충족 후 별도 ADR |
| §16.6 책임의 명명·Adapter Contract 후보 정식화가 구현을 앞당기는지 | **앞당기지 않는다.** `ADR-0003` 등재 → `ADR-0004` 명명이 구현 금지와 공존했고 Scoped 해제는 `ADR-0005`가 별도로 수행한 선례. Sequential을 Reference로 권고하는 것도 지금 그 코드를 저장소에 두는 것을 승인하지 않음 — `ADC-0019` §Decision 조건 5 충족 전까지 line 9/13/14/19 금지 유지 |
| Scheduler / Runtime orchestration / Event Bus 구현 | A-OUT, `IMPLEMENTATION_RULES.md`, `ADC-0019` §Q4 |
| mid-node resume / Human-in-the-loop | E3 §6-a·§9 — caller-owned 모델에서 불가, 그래프 소유 checkpointer 요구. C2가 이를 열지만 이 RFC는 C1 권고이며 mid-node를 범위 밖으로 둔다 |
| v1 `ADR-0007` 결정 2(Core 소유 Lifecycle 소비) / 5(Team/Division 경계) / 9(`IWorkflowEngine` Port) / 11(State Model)의 v2 재설계 | `ADC-0019` §Q7·§Decision 조건 5 — 미해결(Conditional)로 유지. 이 RFC는 계약 **후보**만 정식화할 뿐 이 네 공백을 설계하지 않는다. 특히 후보 (c)는 병렬 쓰기 안전 메커니즘만 제약하고 결정 11(State Model)을 정의하지 않는다(§5.3 (c) Carve-out) |
| ADC-02(Runtime 존폐, Open·NOW) 재판단 / `ADC-0008`(Not Accepted) 전복 | `ADC-0019` §Q8 — §6 넓은 정의는 다루지 않는다 |
| §16.3~16.5 (Execution Host / Multi-Task / Result Store 게이트) 범위·명칭·구현 전략 | `ADC-0019` §Q5 — 무변경 |
| `hqs/investment/checkpoint.py` (§16.5 저장 전 검증 게이트) | `ADC-0019` §Q5 — 값 기반 Checkpoint/Resume과 계층이 다름, 대체 제안 없음 |

---

### 8. Open Questions

#### 8.1 ADC-0020에서 반드시 결정해야 할 항목

| # | 항목 | 왜 여기서 결정해야 하나 |
|---|---|---|
| **Q-A** | **후속 ADC의 형태 (먼저 판정)** — Execution Host 3단계(존재→명명→구현 전략) 중 "명명"에 대응하는가, 아니면 명명 + Adapter Contract 후보 절을 묶은 형태인가? `ADC-0014`(명명 단독) → `ADC-0015`(전략) 분리 선례로부터의 이탈을 허용하는가? | 이 답이 ADC-0020의 나머지 범위를 정한다. 번들링을 불허하면 계약 절은 별도 단계로 분리 |
| **Q-B** | **명칭** — "Workflow Adapter"로 확정/기각. 확정 시 §16.6 Baseline 제목 "Scoped Workflow Graph Execution"과의 매핑 명시(`ADR-0004`가 "Execution Host" ↔ §16.3을 명시한 선례), `GLOSSARY.md` 등재 형태, §16.2 Engine Adapter·v1 `IWorkflowEngine`과의 구분 | 이 RFC의 핵심 질문. 미결 시 하위 문서가 계속 절 제목으로 지칭 |
| **Q-C** | **Adapter Contract의 층위** — 후보 절 (a)~(d)는 §16.6 A-IN의 부속 규약인가, 별도 계층(`ADR-0009` Stage Data Contract처럼 Public/Hidden 구분을 갖는)인가? §14 Kernel Public Contract와 표기상 어떻게 구분하고, "Public 아님"을 어디에 명문화하는가? | (a)~(d)가 Baseline 구속 규칙인지 비공식 지침인지를 가름 |
| **Q-D** | **후보 절 (a)~(d) 채택 집합** — 각각 채택 / 수정 / 기각 + 확정 문언. 특히 (c)가 HQ State 설계에 구속력을 갖는지(§13.3류 구조 불변식 여부), 그리고 (d)를 §16.6 Reversibility 불변조건의 재기술 절로 둘지 아니면 별도 계약 절로 둘지 | 계약 정식화의 실체 |
| **Q-E** | **Checkpoint 입도** — C1(phase-boundary caller-owned) / C2(LangGraph-native + shim) / C3(순차 전용 값 반환) 중 택일. C1 채택 시 "phase 경계"를 누가 선언하나 — HQ의 Workflow 정의인가, Adapter Contract인가? | A-IN(e)의 해석을 확정 |
| **Q-F** | **Rule B 하에서 진행 가부** — E3는 세 번째 관찰이나 동일 LangGraph 계보다. 계약 정식화는 계보와 무관하므로 지금 진행 가능한가, 아니면 `ADC-0019` 재검토 조건 (c)를 먼저 요구하는가? `ADC-0019` §Q2 형식으로 명시 판정 | Conditional Accept의 성립 근거. `ADC-0019` §Q2가 이 대상에 이미 한 판정을 재확인/갱신 |

#### 8.2 Implementation Strategy ADC(ADC-0020 이후)로 이연

| # | 항목 | 이연 근거 |
|---|---|---|
| **Q-G** | **(b) 강제·검증 방법** — exception→state를 못박을 경우 catch-and-encode 강제를 무엇으로 검증하나(정적 분석 / 어댑터 계약 테스트) | 구현 관심사. 계약 절 채택 여부(Q-D)가 먼저 |
| **Q-H** | **Reference Implementation의 실체** — Sequential을 저장소 내 실제 코드로 두는가, 계약 문서상 기준선으로만 두는가? `ADC-0019` §Q6 v2 통합 테스트 요구와 결합 | `IMPLEMENTATION_RULES.md` 조건 5 게이트. 구현 전략 단계의 문제 |
| **Q-I** | **다른 계보 관찰의 적극적 확보** — 직접 구현한 최소 그래프 실행기 등으로 `ADC-0019` 재검토 조건 (c)를 채울지 | Rule B 트랙. 명명/계약 진행 자체를 막지 않음(진행 가부만 Q-F에서 판정) |
| **Q-J** | **mid-node resume / C2 재검토 경로** — mid-node resume이 실제로 필요해지는 관찰이 나오면 C2를 어떤 절차로 다시 여나 | 이 RFC 범위 밖(§7). 관찰 트리거 시 별도 |

---

### 9. Traceability — 기존 Governance와의 관계

| 문서 / 절 | RFC-0020과의 관계 | 정합성 |
|---|---|---|
| `RFC-0019` §3·§7 (명칭 "Workflow Adapter" 비공식 사용) | RFC-0020이 이를 명시하고 권고 지위임을 밝힘 | 무변경 — 확정은 ADC-0020(Q-B) |
| `RFC-0019` §7 Pseudo-Contract | RFC-0020이 이를 Adapter Contract **후보 절**로 정식화 | §7이 "개념 수준, 코드 아님"으로 남긴 것을 동일 지위의 후보 계약으로 재정식화 제안. §7 문언 무변경 |
| `RFC-0019` §8 Boundary Question / §Next Step 2·3 | §Next Step 3(명칭·구현 전략 별도 ADC)의 **앞단계** | RFC-0020이 "명명" 단계 개설. §8은 `ADC-0019`가 이미 답함 |
| `ADC-0019` §Q3 (값 표현·예외 없음, G-6) | → Adapter Contract 후보 (b) | E3 §6-b가 LangGraph 예외 전파 기본값이 §Q3와 충돌함을 실측 → 어댑터 책임으로 계약화 제안 |
| `ADC-0019` §Q4 A-OUT | → RFC-0020 §7 범위 밖 목록에 그대로 인용 | 무변경 |
| `ADC-0019` §Q6 Reversibility 필수 불변조건 | → Adapter Contract 후보 (d) | **신규 아님** — §16.6 기존 불변조건의 재확인 + v2 통합 테스트 검증 방법 명시 |
| `ADC-0019` §Q7 / §Decision 조건 5 (결정 2/5/9/11 조건 이월, Public Contract·구현 착수 불가) | RFC-0020 §7에서 범위 밖으로 명시 유지 | 무변경 — RFC-0020은 계약 후보만 정식화, 네 공백을 설계하지 않음. (c)는 결정 11(State Model)을 정의하지 않음 |
| `ADC-0019` §Q8 / §Decision 조건 6 (명칭·구현체·Port·구현 전략 미확정, 3단계 선례) | RFC-0020이 "명명" 단계를 개시. 명명+계약 번들링은 선례 이탈로 공시 | 위반 없음 — RFC-0020은 권고만 제시, 확정은 ADC-0020. 번들링 허용 여부는 Q-A |
| `ADC-0019` §Decision 조건 1~6 | 전부 무변경 | RFC-0020은 어느 조건도 건드리지 않음(§1·§6) |
| `ADC-0019` 재검토 조건 (c) | Rule B 계속 미충족 명시 | 무변경 — E3는 다른 계보/프로덕션 관찰이 아님 |
| `ADR-0008` §Out of Scope / §4 (`IMPLEMENTATION_RULES.md` 무변경) | RFC-0020 §7에서 그대로 유지 | 무변경 |
| Execution Host `ADR-0003`(등재)→`ADR-0004`(명명)→`ADR-0005`(구현 전략) | §6·§7의 "명명·계약이 구현을 앞당기지 않는다" 근거 | 선례 인용 |
| `BASELINE.md` §16.6 (A-IN/A-OUT/Reversibility/Conditional gaps) | RFC-0020이 지칭·정식화 대상으로 인용 | 문언 무변경 |
| `BASELINE.md` §16.7 (Workflow Module Defer, `ADC-0001` Module 2) | 별개 축 — RFC-0020은 Module 존재 여부를 다루지 않음 | 무변경 |
| `BASELINE.md` §14.1 ("Task 전달 책임" 미결) | Public Port 제안 불가의 상위 원인으로 인용 | 무변경 |
| `BASELINE.md` §15.2 (호출자가 값 보유 패턴) | Checkpoint 후보 (a) 값 소유 모델·C1의 근거 | 인용만 |
| `BASELINE.md` §13.3 (Assembly 구조 불변식 A-1~A-5) | 후보 (c)가 이 부류에 해당하는지의 판단 기준 | 인용만 — 판정은 Q-D |
| `BASELINE.md` §7 (Workflow 도메인 내용 = HQ) | Adapter Contract 불변조건("무엇을 실행할지 결정 안 함")·(c) Carve-out의 근거 | 인용만 |
| `docs/decisions/adc/ADC.md` ADC-02 (Open·NOW) / `ADC-0008` (Not Accepted) | RFC-0020 §7에서 범위 밖 | 무변경 — §6 넓은 정의 미접촉 |
| Execution Host: `RFC-0014`→`ADC-0014`→`ADR-0004` (명명), `RFC-0015`→`ADC-0015`→`ADR-0005` (구현 전략) | RFC-0020이 따르는 절차 패턴 (명명 단계 대응) | 선례 인용 |
| E1 `archive/v1` `ADR-0007` + `test_workflow_adapter_reversibility.py` / E2 `.claude/docs/integrations/langgraph.md` / E3 `.claude/docs/integrations/langgraph-domain-poc.md` | §3 Evidence | Accepted/기록 상태 그대로 인용, 새 실험 없음 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 | RFC-0020으로 해제되지 않음 | 무변경 |

---

### 10. Self Review

- Evidence만 사용했는가 — **Pass**. E1(Accepted 그대로), E2·E3(`main` 병합 기록 그대로), `BASELINE.md`·`RFC-0019`·`ADC-0019`·`ADR-0008`·`IMPLEMENTATION_RULES.md`·Execution Host 체인만 인용. 새 실험·PoC 없음.
- §16.6 책임의 명칭을 확정했는가 — **아니오**(§5.2는 권고, §8.1 Q-B).
- 명칭을 새 용어로 도입했는가 — **아니오**(§4.1·§5 도입부: `RFC-0019` §3·§7이 이미 비공식 사용, `ADC-0019` §Q8이 미확정으로 병기).
- Adapter Contract 절을 확정했는가 — **아니오**(§5 도입부·§5.3: "ADC-0020이 채택·수정·기각할 초안 문언", 확정은 후속 ADC).
- Adapter Contract를 §14 Kernel Public Contract로 승격·혼동했는가 — **아니오**(§5 도입부, §7 첫 행, §8.1 Q-C: Public Port·Surface·Guarantee·Interface 신설 없음, `RFC-0019` §7 개념 수준과 동일 지위).
- 후보 (c)가 Workflow State Model / HQ Workflow 도메인 책임을 침범했는가 — **아니오**(§5.3 (c) Carve-out: 병렬 쓰기 안전 메커니즘만 제약, 결정 11 미정의, §7 HQ 경계 유지).
- 후보 (d)를 신규 계약으로 제시했는가 — **아니오**(§5.3 (d): §16.6 기존 필수 불변조건의 재확인 + 검증 방법 명시).
- LangGraph 도입을 승인했는가 — **아니오**(§3 프레이밍, §4 N-3 기각, §5.1).
- Checkpoint 입도를 확정했는가 — **아니오**(§4.2 C1 "권고", §5.4 "RFC 단계 권고로만"). 후보 (a)는 값 소유 모델만 정하고 입도는 정하지 않음.
- §14 Kernel Public Contract를 확장했는가 — **아니오**(§7, §2, §9 §14.1 행).
- `IMPLEMENTATION_RULES.md` 금지를 해제했거나 구현을 앞당겼는가 — **아니오**(§6·§7: 명명·계약과 구현 금지는 공존, Sequential Reference 권고 ≠ 저장소 코드 승인).
- v1 결정 2/5/9/11을 재설계했는가 — **아니오**(§7, §5.5).
- `ADC-0019` §Decision 조건 1~6을 변경했는가 — **아니오**(§1, §6).
- Rule B 충족을 주장했는가 — **아니오**(§3 "Rule B 상태", §6).
- 실제 Architecture 문언 / `BASELINE.md`·`RFC-0019`·`ADC-0019`·`ADR-0008`·`IMPLEMENTATION_RULES.md`를 수정했는가 — **아니오**. 이 RFC 파일 하나만 신규 작성 대상이며, 저장소의 다른 Governance 문서·코드는 수정하지 않는다.
- E3 Findings를 Contract 후보로 명확히 포함했는가 — **Pass**(§5.3 (a)~(d), §9).
- Open Questions를 ADC-0020 필수 결정과 이후 이연으로 구분했는가 — **Pass**(§8.1 Q-A~Q-F / §8.2 Q-G~Q-J).
