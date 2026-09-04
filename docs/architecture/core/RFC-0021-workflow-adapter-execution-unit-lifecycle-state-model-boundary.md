# RFC-0021: Workflow Adapter가 소비하는 실행 단위·생명주기·State Model — Team/Division 부재 하의 v2 재설계 Boundary (ADC-0019 Next Step 5 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
§Decision 조건 5 · §Next Step 5가 후속 Architecture 절차로 이월한
v1 `ADR-0007` 결정 **2·5·11**의 v2 공백. `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md`
§8이 이를 **Gate (A)**로 명명하고 "구현·§14 승격의 hard gate"로 유지 중이다.
이 RFC는 그 세 공백 중 **Team/Division 부재에서 비롯된 것**만 정식
Boundary Question으로 연다.

**Evidence**: `archive/v1/docs/adr/0007-workflow-execution-model.md`(Accepted,
결정 2·5·11 원문), `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md`
§5(v1 12개 결정의 v2 재해석 표), `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
§Q7·§Decision 조건 5·§Next Step 5, `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md`
§Q-D (c)·§4.3(결정 11 결합 이연), `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md`
§3, `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md`
§8, `docs/architecture/baseline/BASELINE.md` §5·§6·§7·§16.6(v1.14),
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`hqs/investment/teams/stock_team.py`(v2에서 "team"이 실제로 어떻게
구성되는지의 관찰). **새로운 실험·프로토타입·측정은 수행하지 않는다** —
이미 병합·기록된 v1 Evidence와 v2 Governance 문서만 인용한다.

> 본 RFC는 v1 결정 2·5·11의 v2 대안을 **설계하지 않는다**. Team/Division을
> v2에 되살리자고 제안하지 않는다. `IWorkflowEngine` Port(결정 9)·§14
> Kernel Public Contract·"Task 전달 책임"을 다루지 않는다 — 그것은
> `ADC-0019` G3이 분리한 별개의 상위 트랙이다. LangGraph 채택·구현 전략·
> Production 구현·`IMPLEMENTATION_RULES.md` 해제를 제안하지 않는다. 병렬
> State 동시 쓰기 규약("(c)")의 규범 내용을 확정하지 않는다. 코드·Baseline·
> ADC·ADR·CLAUDE.md를 수정하지 않는다. 이 RFC가 여는 것은 좁은 질문
> 하나다: **"v2에서 Workflow Adapter(§16.6)가 입력으로 받는 '이미 구성된
> 실행 단위'와 그것이 진행시키는 실행의 생명주기·State Model은, Team/Division이
> 없는 v2 Meta Architecture 위에서 어떤 형태로 재정의되어야 하며, 그 일부는
> 이미 §16.6 A-IN/A-OUT이 흡수했는가?"**

---

## 0. 이 RFC가 열린 이유

`RFC-0019` §5는 v1 `ADR-0007`의 12개 결정을 v2로 옮길 수 있는지 검토하고,
대부분(1·3·4·6·8·10·12)은 이식 가능하나 **4개(2·5·9·11)는 재설계가
필요한 진짜 공백**이라고 정리했다. 그리고 그 4개의 공백 원인이 하나로
묶이지 않음을 명시했다.

- **결정 2·5·11**의 공백 원인은 **Team/Division 부재**다 — v2 §5 Meta
  Architecture에 Team/Division 대응물이 없어, Core가 소비할 생명주기
  (결정 2)·경계(결정 5)·State Model(결정 11)을 그대로 옮길 수 없다.
- **결정 9**(`IWorkflowEngine` Port)의 공백 원인은 Team 부재가 **아니다** —
  §14.1이 "Task 전달 책임"을 계약 범위 밖으로 두는 데서 온다. `ADC-0019`
  G3은 이것을 "이 RFC/ADC 범위보다 상위의, 별도로 이미 Open인 Kernel
  Public Contract 확장 질문"으로 규정했다.

`ADC-0019` §Decision 조건 5는 이 4개를 "Accept의 미해결 조건"으로 이월했고,
§Next Step 5는 "v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계는 후속 ADR 또는
별도 RFC로 순서를 정해 다룬다 — 완료 전 Public Contract 승격·구현 착수
불가"라고 지시했다. `ADC-0021` §8은 이 미해결 상태를 **Gate (A)**로
명명하고, `ADC-0021` §6 조건 4가 "이 ADC는 네 공백을 설계하지 않는다"고
재확인했다.

이 RFC는 그 지시를 따라 **공백 원인이 동일한 결정 2·5·11만 하나의
Boundary Question으로 묶어** 정식 절차에 올린다. 결정 9는 원인·해소
경로·닿는 문서(§14)가 다르므로 이 RFC에 포함하지 않는다(§7). "결정 2·5·11
↔ 결정 9"의 2분할은 이 RFC가 새로 판단하는 것이 아니라 `RFC-0019` §5와
`ADC-0019` §Q7이 이미 수행한 것을 그대로 계승한다.

## 1. Problem Statement

§16.6은 Workflow Adapter의 책임을 "**HQ가 이미 정의한 Workflow 그래프와
이미 구성된 실행 단위를 입력으로 받아**, 그 그래프가 기술하는 State 보유·
Node 진행·Conditional Edge·Loop·값 기반 Checkpoint/Resume을 진행시키는
것"으로 Accept(Scoped, Conditional)했다. 이 정의는 "이미 구성된 실행
단위"가 **무엇인지**를 전제로만 두고 정의하지 않는다.

v1에서 그 "실행 단위"는 `Team`이었고, v1 `ADR-0007`은 세 가지를 확정했다.

1. **결정 2** — `Team`/`TeamState`(FORMING→ACTIVE→COMPLETING→TERMINATED)는
   Core Domain 로직이며, Workflow Engine은 전이 규칙을 소유·재구현하지
   않고 정해진 순서로 `activate()`/`complete()`/`terminate()`를 호출하는
   조립자다.
2. **결정 5** — Division(반영구, Agent Catalog 보유)과 Team(Ephemeral,
   Workflow Engine이 조립)은 서로 다른 계층이며, Division Selection은
   Workflow Engine 개입 **이전** 단계다(HQ 책임).
3. **결정 11** — `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}`는 `TeamState`와
   **별개 축**(끝난 방식 vs 현재 단계)의 Core Domain State Model이며,
   `WorkflowResult`가 이를 반드시 포함한다.

v2 §5 Meta Architecture는 `Jarvis OS → HQ → Agent → Connector`만 계층으로
두고 "**Division과 Team은 HQ 내부에서 선택적으로 사용할 수 있는 구조이며,
Jarvis OS는 그 존재 여부를 알지 못한다**"고 명시한다. §7 System Boundary는
"HQ 내부 조직 구조(Division/Team의 존재 여부, 이름, 책임 분담)"를 Jarvis
OS가 책임지지 않는 것으로, "내부 조직 구조 결정"을 HQ의 책임으로 확정한다.

관찰로도 확인된다: `hqs/investment/teams/stock_team.py`는 v2에서 "team"이
`Team` 클래스·`TeamState` 상태 머신 없이 **평범한 함수 모듈 + `ThreadPoolExecutor`
+ `Checkpointer`**로 구성됨을 보인다. v2에는 Core가 소유하는 Team 생명주기가
실재하지 않는다.

따라서 §16.6이 전제하는 "이미 구성된 실행 단위"는 v2에서 **정의되지 않은
입력**이고, 결정 2(그 단위의 생명주기 소비)·결정 5(그 단위와 상위 조직
구조의 경계)·결정 11(그 실행의 결과·상태를 나타내는 Model)은 v2 대응물이
없다. 이 공백을 방치한 채 §16.6을 §14로 승격하거나 Production 구현에
착수하면, 어댑터가 "무엇을 받아 무엇의 상태를 진행시키는지" 규정되지 않은
계약이 된다(`ADC-0019` §Risks "빈 상자" 위험).

## 2. Evidence Summary — 이미 기록된 것만 인용

### 2.1 v1 결정 2·5·11 원문 (`archive/v1/docs/adr/0007-workflow-execution-model.md`)

- **결정 2**: "전이 순서 강제(`assert`로 위반 시 예외)는 Core에 남는다.
  Workflow Engine Adapter가 무엇이든 이 전이 규칙을 우회하거나 재구현할
  수 없다. Workflow Engine의 역할은 '언제 `activate()`를 호출하고, 언제
  `complete()`를 호출할지'의 타이밍과 순서를 그래프/노드로 표현하는
  것이다 — 상태값 자체를 새로 만들거나 전이 조건을 바꾸는 것이 아니다."
  대안 B(Adapter가 상태 전이 규칙을 자체 재구현) 기각.
- **결정 5**: "Division Selection(`HQ.select_division()`)은 Workflow Engine이
  개입하기 **이전** 단계다. Workflow Engine은 Division이 이미 선택된 뒤,
  그 Division의 `agent_catalog`를 바탕으로 Team을 조립하는 지점부터
  시작한다. … Workflow Engine은 Division을 생성/소멸시키지 않는다."
- **결정 11**: "`WorkflowStatus`는 '그 생명주기가 어떻게 끝났는가'를
  나타내고, `TeamState`는 '지금 어느 단계에 있는가'를 나타낸다. 두 개념은
  서로 다른 축이다. … 이 State Model 역시 HQ Lifecycle·Connector
  Lifecycle처럼 Core의 Domain 개념이며, 특정 Adapter(LangGraph)의 내부
  상태가 아니다."

### 2.2 v2 재해석 (`RFC-0019` §5 표 — 이 RFC가 확정하지 않음)

| v1 결정 | v2 재해석 (RFC-0019 §5) | v2에서 달라지는 점 |
|---|---|---|
| 결정 2 | Adapter가 소비할 대상은 HQ 내부에서 정의한 Agent/Task 단위의 전이이지 Kernel이 정의한 Team 상태 머신이 아니다 | "v2 Kernel에는 이 '소비할 생명주기'가 아직 없다 — HQ마다 다를 수 있음. **이 자체가 후속 Open Question**" |
| 결정 5 | v2에 대응 개념 없음(§5가 Division/Team을 Kernel이 모르는 HQ 내부 구조로 명시) | "이 결정 자체를 v2로 이식할 수 없다. Workflow Adapter는 **HQ가 이미 만든 실행 단위(내부에 Team/Division이 있든 없든)만 받는다**는 형태로 재정의해야 함" |
| 결정 11 | v2에 `TeamState` 대응 없음(결정 5와 동일 사유) | "**Team 대신 무엇의 상태를 나타낼지** 후속 절차 대상" |

### 2.3 이미 부분적으로 흡수된 것 (BASELINE v1.14 §16.6)

- **A-IN**: "HQ가 이미 정의한 Workflow 그래프와 **이미 구성된 실행 단위**를
  입력으로 받아", 개입 구간을 "HQ가 실행 단위를 구성한 이후 ~ 그 실행이
  모두 끝나는 시점"으로 한정. → 결정 5의 "Division Selection 이후부터
  개입"의 v2 등가물이 **이미 §16.6에 있다**.
- **A-OUT**: "HQ Routing/Registry, … Domain Lifecycle 전이 규칙(HQ/Agent의
  상태 전이 자체 — HQ가 소유하는 Domain 로직을 Adapter가 재구현하지
  않는다, v1 `ADR-0007` 결정 2·대안 B 기각과 동일 원칙)"을 명시 제외. →
  결정 2의 "전이 규칙을 재구현하지 않는다"의 v2 등가물이 **이미 §16.6에
  있다** — 단, "그렇다면 v2에서 소비할 생명주기가 존재하는가"의 긍정적
  답은 없다.
- **A-IN**: "실행 결과(성공/실패/취소에 준하는 상태)는 예외가 아닌 값으로
  표현한다(§14.3 G-6)" + Adapter Contract 부속 명세 **(b)**. → 결정 11의
  `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}` 축의 v2 등가물이 **부분적으로
  §16.6에 있다** — 단, "그 상태값이 무엇의 상태인가(A-IN(a) 공유 실행
  State와의 관계, `TeamState` 대체 축의 부재)"는 없다.

### 2.4 결정 11과 결합 대기 중인 항목 ((c) reducer 규약)

`ADC-0020` §Q-D는 후보 절 **(c)**(병렬 fan-out 노드의 disjoint key /
reducer 규약)를 **Defer**하며, §4.3·§Decision 4에서 그 이유를 "(c)는
§16.6에 없는 신규 표면이고, reducer 선언 위치(HQ 스키마 vs 어댑터 내부)가
**v1 `ADR-0007` 결정 11(State Model)의 v2 재설계와 얽힌다**"고 밝혔다.
`ADR-0009` §3은 "(c)의 (i) 계약화 여부, (ii) 배치, (iii) HQ State 설계
구속 여부는 후속 Implementation Strategy ADC 또는 별도 Governance 단계가
v1 `ADR-0007` 결정 11과 결합해 판정한다"고 기록했다. 즉 이 RFC가 결정
11의 v2 재설계를 정식 절차에 올리는 것은 (c)의 후속 판정이 걸려 있는
바로 그 전제 조건이다.

## 3. v1 개념과 v2의 불일치 정리

| v1 개념 | v1에서의 지위 | v2에서의 상태 | 이 RFC와의 관계 |
|---|---|---|---|
| **Team** | Core Domain Model(`packages/core/.../organization/entities.py`), Ephemeral | §5가 "HQ 내부 선택적 구조, Kernel은 존재 여부 모름"으로 배제 | Workflow Adapter의 입력 "실행 단위"를 v2에서 무엇으로 부를지 재정의 대상(B-2·B-5) |
| **TeamState** (FORMING→ACTIVE→COMPLETING→TERMINATED) | Core가 전이 규칙 소유, `assert` 강제 | v2 대응 없음. A-OUT이 "Domain Lifecycle 전이 규칙 재구현 금지"만 규정 | Adapter가 v2에서 소비하는 생명주기가 존재하는지, 존재하면 소유자가 누구인지(B-2) |
| **Division** | 반영구, Agent Catalog 보유, Selection은 HQ 책임 | §7이 "HQ 내부 조직 구조"로 명시, HQ 책임 | Adapter가 넘지 않는 경계를 §16.6 A-IN/A-OUT이 이미 그었는지 확인(B-5) |
| **WorkflowStatus** | Core Domain State Model, `TeamState`와 별개 축 | 결과-상태-값 부분은 §16.6 A-IN·Adapter Contract (b)에 흡수. 구조적 State Model·별개 축 프레이밍은 공백 | v2 Workflow 실행 State Model의 형태·소유·(c) 결합(B-11) |
| **WorkflowResult** | 결정 9의 반환 타입, `WorkflowStatus` 포함 | Port 자체가 §14.1 미결로 공백 | **이 RFC 범위 밖** — 결정 9 / §14 트랙(§7) |

## 4. 결정별 v2 공백 분석

### 4.1 B-2 — 결정 2 (Core 소유 Lifecycle 소비)

**v1이 확정한 것**: Workflow Engine은 Team 생명주기 전이 규칙의 소유자가
아니라 소비자다. 전이 규칙은 Core에, 호출 순서·타이밍은 Workflow Engine에.

**v2 공백**: v2에는 "Adapter가 소비할" Kernel/Core 소유 생명주기가 없다.
§16.6 A-OUT은 "Adapter가 Domain Lifecycle 전이 규칙을 재구현하지 않는다"는
**금지**만 명문화했다 — "그렇다면 Adapter는 무엇의 어떤 전이를 소비하는가,
그것을 소유하는 주체는 누구인가(HQ 공통? HQ마다 상이? 아예 없고 Adapter는
그래프 진행 상태만 다루는가?)"의 **긍정적 정의**가 비어 있다. `RFC-0019`
§5는 이를 "그 자체가 후속 Open Question"으로 남겼다.

**가능한 해소 형태(이 RFC가 고르지 않음)**: (i) v2 Adapter는 어떤 외부
생명주기도 소비하지 않고 A-IN(a) 그래프 진행 상태만 다룬다고 확정 — 이
경우 결정 2는 "v2에서 대응 의무 없음"으로 종결. (ii) HQ가 정의한 실행
단위 전이(HQ 도메인 로직)를 Adapter가 호출만 하고 재구현하지 않는다는
원칙을 A-OUT의 금지에 대응하는 긍정형으로 명문화. (iii) 둘의 조합.

### 4.2 B-5 — 결정 5 (Team/Division 경계)

**v1이 확정한 것**: Workflow Engine은 Division Selection 이후, 이미 선택된
Division의 Agent Catalog로 Team을 조립하는 지점부터 개입한다. Division을
생성/소멸시키지 않는다.

**v2 상태 — 대체로 흡수됨**: §16.6 A-IN("이미 구성된 실행 단위를 입력으로
받아") + 개입 구간 한정("HQ가 실행 단위를 구성한 이후 ~") + A-OUT("HQ
Routing/Registry" 제외) + §7(HQ 내부 조직 구조 = HQ 책임)이 결합하면,
결정 5의 관심사("Adapter가 실행 단위 구성·선택 경계를 넘지 않는다")는
**이미 v2 문언으로 표현되어 있다**. Team/Division이라는 이름만 사라졌을
뿐, "Adapter는 이미 만들어진 것을 받는다"는 경계는 살아 있다.

**잔여 공백**: 결정 5가 v2에서 **완전히 흡수되어 별도 의무가 남지 않는지**를
명시적으로 확정하는 서술이 없다. 후속 ADC가 "결정 5 = §16.6 A-IN/A-OUT +
§7로 완전 대체, 잔여 없음"으로 종결할 수 있는지, 아니면 (예: HQ 내부에
Team/Division 유무가 갈릴 때 Adapter 입력 계약이 그 차이에 영향받지 않아야
한다는) 잔여 불변조건이 필요한지가 판단 대상이다.

### 4.3 B-11 — 결정 11 (Workflow State Model)

**v1이 확정한 것**: `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}`는
`TeamState`와 별개 축의 Core Domain State Model이다.

**v2 상태 — 부분 흡수**: "실행 결과를 예외가 아닌 값으로"(§16.6 A-IN,
§14.3 G-6) + Adapter Contract **(b)**("실행 결과의 값 표현 = 어댑터
책임")가 `WorkflowStatus`의 **결과-상태-값** 측면을 담는다.

**잔여 공백 3가지**:
1. **구조적 State Model** — §16.6 A-IN(a)는 "공유 실행 상태(State)의
   보유"만 규정하고 그 State가 무엇을 담는 축인지 정의하지 않는다.
   `WorkflowStatus`(끝난 방식)에 대응하는 v2 개념이 A-IN(a) State 안의
   한 필드인지, 별도 축인지, HQ 도메인 내용(§7)이라 Kernel이 규정하지
   않는지가 미결이다.
2. **"별개 축" 프레이밍의 소실** — v1은 `WorkflowStatus`를 `TeamState`와
   대비해 정의했는데, `TeamState`가 v2에 없으므로 이 대비 자체가
   재구성되어야 한다.
3. **(c) reducer 규약의 결합 판정** — `ADC-0020` §Q-D·§4.3, `ADR-0009` §3이
   (c)를 "결정 11이 다뤄질 때 결합 판정"으로 이연했다. 이 RFC가 결정 11의
   v2 재설계를 절차에 올리면, 후속 ADC가 (c)의 (i) 계약화 여부·(ii) 배치·
   (iii) HQ State 설계 구속 여부를 결정 11과 함께 판정할 수 있게 된다.
   **이 RFC는 (c)의 규범 내용을 확정하지 않는다** — 결합 판정의 무대를
   여는 것까지만이다.

## 5. §16.6이 이미 부분적으로 메운 것 — 이 RFC가 새로 만들지 않는 것

| 결정 | §16.6/§7이 이미 담은 것 | 이 RFC가 여는 것 |
|---|---|---|
| 2 | A-OUT: "Domain Lifecycle 전이 규칙 재구현 금지" | 그 금지에 대응하는 **긍정적 정의**의 존재 여부 |
| 5 | A-IN "이미 구성된 실행 단위" + 개입 구간 한정 + §7 HQ 책임 | 그것으로 결정 5가 **완전 대체되어 잔여가 없는지**의 확정 |
| 11 | A-IN "결과를 값으로" + Adapter Contract (b) | 구조적 **State Model**, "별개 축" 재구성, (c) 결합 무대 |

이 표는 이 RFC의 범위를 **좁힌다**: 세 결정 모두 "완전 공백"이 아니라
"부분 흡수 + 명시되지 않은 잔여"이며, 이 RFC는 그 잔여만 Boundary
Question으로 올린다.

## 6. Boundary Question

**v2 Meta Architecture(§5)가 Team/Division을 Kernel 밖 HQ 내부 구조로
배제한 상태에서, §16.6 Workflow Adapter가 전제하는 "이미 구성된 실행
단위"와 그것이 진행시키는 실행의 생명주기·State Model은 어떤 형태로
재정의되어야 하며, v1 `ADR-0007` 결정 2·5·11 중 어느 부분이 이미 §16.6
A-IN/A-OUT·§7로 흡수되었고 어느 부분이 추가 확정을 요구하는가?**

세 하위 facet으로 나뉜다(후속 ADC가 각각 판정).

- **B-2 (결정 2)**: v2 Workflow Adapter가 소비하는 외부 생명주기가
  존재하는가. 존재한다면 소유 주체는 누구인가(HQ 공통 / HQ별 상이 /
  없음). A-OUT의 "전이 규칙 재구현 금지"에 대응하는 긍정형 명문이
  필요한가.
- **B-5 (결정 5)**: 결정 5의 경계 관심사가 §16.6 A-IN("이미 구성된 실행
  단위") + 개입 구간 한정 + §7(HQ 조직 구조 = HQ 책임)으로 **완전히
  대체되어 잔여 의무가 없는지**, 아니면 HQ 내부 Team/Division 유무와
  무관하게 성립해야 하는 입력 계약 불변조건이 남는지.
- **B-11 (결정 11)**: v2 Workflow 실행의 State Model이 (i) §16.6 A-IN(a)
  공유 State의 한 축인지, (ii) 별도 개념인지, (iii) §7에 따라 HQ 도메인
  내용이라 Kernel이 규정하지 않는지. `TeamState` 부재로 재구성이 필요한
  "끝난 방식 vs 현재 단계" 대비를 어떻게 다시 세우는가. (c) reducer 규약의
  결합 판정을 이 축에서 열 수 있는가.

### 이 Boundary Question이 명시적으로 제외하는 것

- **v1 결정 9(`IWorkflowEngine` Port)** — `ADC-0019` G3이 분리한 별개의
  상위 트랙. 공백 원인이 Team 부재가 아니라 §14.1 "Task 전달 책임"의
  계약 범위 밖 상태다. 이 RFC는 Port를 정의하지도, §14를 확장하지도
  않는다.
- **§14 Kernel Public Contract 승격** — `ADC-0019` §Decision 조건 5가
  "네 공백 해소 전 §14 승격 불가"로 유지. 이 RFC는 그 gate를 여는 것이
  아니라, 네 공백 중 세 개를 절차에 올려 **해소를 시작**할 뿐이다.
- **(c) 병렬 State disjoint key / reducer 규약의 규범 내용** — 이 RFC는
  (c)를 결정 11과 결합 판정할 수 있는 무대를 여는 것까지만이다. (c)가
  계약이 되는지, 어디에 배치되는지, HQ State 설계를 구속하는지는 후속
  ADC의 몫이다(`ADC-0020` §Q-D, `ADR-0009` §3).
- **LangGraph 채택 여부·구현 전략·Checkpointer 백엔드** — `ADC-0019`
  §Q8·`ADC-0021` §D2·§7. 이 RFC는 구현 중립이다.
- **명칭 재론** — §16.6 책임의 명칭은 `ADC-0020` §Q-B가 "Workflow
  Adapter"로 확정했다. 이 RFC는 그 이름을 쓰되 재론하지 않는다.
- **`hqs/investment/`·`hqs/development/`의 team 코드 재구성** — 관찰
  대상이지 변경 대상이 아니다.

## 7. Out of Scope

- v1 결정 2·5·11의 v2 대안 **설계**(구체 개념·필드·상태 목록·다이어그램).
  이 RFC는 Boundary Question만 연다.
- v1 결정 9의 v2 재설계, `IWorkflowEngine` Port, `WorkflowResult` 타입,
  §14.1 "Task 전달 책임"·"Engine 호출 책임"의 계약 편입.
- §14 Public Responsibilities/Guarantees/Extension Points 신설·수정.
- (c) reducer 규약의 규범화·배치·HQ 구속 판정.
- `ADC-0019` §Decision 조건 1~6, 재검토 조건 (c)(=Gate (B)), Reversibility
  필수 불변조건(=Gate (C) 트랙)의 재판단.
- Team/Division을 v2 Meta Architecture(§5)에 재도입하는 제안.
- `BASELINE.md` §5·§6·§7·§16.x 문언 수정, `IMPLEMENTATION_RULES.md`
  line 9/13/14/19의 전면·Scoped 해제.
- Production 코드 변경(`core/`, `hqs/`, `dashboard/`), 이 RFC 파일 자체를
  제외한 `docs/architecture/`·`docs/decisions/` 파일.
- Multi-HQ, 자연어 요청 분해(`ADC-0018`, Defer) 범위로의 확장.

## 8. Non-goals

- 이 RFC는 결정 2·5·11 중 어느 것도 "v2에서 불필요"라고 **미리 결론짓지
  않는다** — B-5가 "완전 흡수, 잔여 없음"으로 종결될 가능성을 §4.2·§6에서
  열어두지만, 그 판정은 후속 ADC의 몫이다.
- 이 RFC는 Governance v2 Rule B 충족을 주장하지 않는다 — 결정 2·5·11의
  v2 재설계는 Evidence 축적이 아니라 §5 Meta Architecture와의 정합
  문제이므로 Rule B와 직접 관계가 없다. `ADC-0019` 재검토 조건 (c)는
  Gate (B)로 별개 유지된다.
- 이 RFC는 결정 9를 "나중에" 다루겠다고 약속하지 않는다 — 결정 9는
  §14.1 트랙의 별개 RFC(또는 Kernel Public Contract 확장 절차)가 다룰
  사안이며, 그 착수 여부·시점은 이 RFC가 정하지 않는다.

## 9. Governance Chain / 번호 관계

- **선행**: `RFC-0019`→`ADC-0019`→`ADR-0008`(§16.6 존재 Accept, 조건 5로
  결정 2/5/9/11 이월) · `RFC-0020`→`ADC-0020`→`ADR-0009`(명칭 + Adapter
  Contract (a)(b)(d), (c) Defer·결정 11 결합) · `ADC-0021`(구현 전략
  프레이밍, §8이 결정 2/5/9/11을 Gate (A)로 명명).
- **이 RFC**: `ADC-0019` §Next Step 5 + `ADC-0021` §8 Gate (A) 중 **결정
  2·5·11**만 정식 Boundary Question으로 개설.
- **번호 관계 주의**: 이 저장소의 core 체인은 지금까지 RFC-N ↔ ADC-N으로
  1:1 짝을 이뤘으나, `ADC-0021`은 `RFC-0020` §8.2를 RFC pairing으로
  삼아 그 규칙을 이미 깼다(`ADC-0021` §1.4). 따라서 `RFC-0021`(이 문서)의
  후속 ADC는 **`ADC-0022`**가 되며, `ADC-0021`(Implementation Strategy)과는
  **주제가 다른 별개 문서**다. 혼동을 막기 위해 파일명·제목에 주제를
  명시했다.
- **후속**: 이 RFC가 Accept(개설 타당) 판정되면 → `ADC-0022`(신설)가
  B-2·B-5·B-11을 판정 → 필요 시 ADR → `BASELINE.md` §16.6(및 필요 시
  §5·§6·§7) Update. 이 RFC 자체는 그 판단을 내리지 않는다.

## 10. Next Step

후속 ADC(신설 예정, `ADC-0022`)에서 다음을 판단하도록 제안한다.

1. §6 Boundary Question(결정 2·5·11의 v2 잔여 공백)을 지금 정식 절차로
   여는 것이 타당한지, 아니면 더 상위의 결정(예: §16.6의 §14 승격 자체)이
   먼저여야 하는지.
2. 타당하다면 — **B-2**: v2 Adapter의 외부 생명주기 소비 여부와 소유
   주체를 확정하거나, "대응 의무 없음"으로 종결.
3. **B-5**: 결정 5가 §16.6 A-IN/A-OUT + §7로 완전 대체되는지, 잔여
   불변조건이 필요한지 확정.
4. **B-11**: v2 Workflow 실행 State Model의 형태·소유(Kernel 축 / 별도 /
   HQ 도메인)를 확정하고, (c) reducer 규약을 이 축에서 결합 판정할지 결정.
5. 각 facet의 판정이 `BASELINE.md` 어느 절(§16.6 본문 / §5 / §6 / §7)에
   어떤 granularity(Minor 문단 추가 / 별도 절)로 반영되는지, ADR이
   필요한지를 정한다.
6. 결정 9(§14 트랙)는 이 ADC가 다루지 않음을 재확인하고, 그 착수 경로를
   별도로 기록한다.

이 RFC 자체는 위 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 진행한다.

## 11. Self Review

- Evidence만 사용했는가 — **Pass**. v1 `ADR-0007`(Accepted 그대로 인용),
  `RFC-0019` §5, `ADC-0019`/`ADC-0020`/`ADR-0009`/`ADC-0021`, `BASELINE.md`,
  `ARCHITECTURE_GOVERNANCE.md`, `hqs/investment/teams/stock_team.py` 관찰만
  인용했다. 새 실험·프로토타입·측정은 없다.
- 결정 2·5·11의 v2 대안을 설계했는가 — **아니오**(§7). §4는 공백을
  기술하고 §6은 질문만 연다. §4.1·§4.3의 "가능한 해소 형태"는 예시이지
  선택이 아니다.
- 결정 9 / §14 / "Task 전달 책임"을 다뤘는가 — **아니오**(§6 제외 목록,
  §7, §8). `ADC-0019` G3의 2분할을 그대로 계승했다.
- (c) reducer 규약의 규범 내용을 확정했는가 — **아니오**(§4.3, §6 제외
  목록) — 결합 판정의 무대를 여는 것까지만.
- LangGraph 채택·구현 전략·`IMPLEMENTATION_RULES.md` 해제를 제안했는가 —
  **아니오**(§6 제외 목록, §8).
- Team/Division을 v2에 재도입하자고 했는가 — **아니오**(§8) — §5 배제를
  전제로 그 위에서 재정의를 묻는다.
- `ADC-0019` 조건 5·재검토 조건 (c), Gate (B)/(C)를 약화했는가 —
  **아니오**(§7, §8) — 결정 2·5·11의 해소를 **시작**할 뿐, §14 승격 gate는
  그대로다.
- §16.6이 이미 흡수한 부분을 중복 신설했는가 — **아니오**(§5) — 잔여만
  질문 대상으로 좁혔다.
- Production 코드·Baseline·ADC·ADR·CLAUDE.md를 수정했는가 — **아니오**.
  이 RFC 파일 하나만 신규 작성했다.
- 번호 관계(RFC-0021 ↔ ADC-0022, ADC-0021과 별개 주제)를 명시했는가 —
  **예**(§9).
