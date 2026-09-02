# ADC-0020: Workflow Adapter 명명 + Adapter Contract 부속 명세 정식화 (RFC-0020 후속)

**Status**: Decided — ADR Required
**Author**: Claude Code
**후속 대상**: `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md` (Proposed)
**선행**: `RFC-0019` → `ADC-0019` → `ADR-0008` (BASELINE v1.12 §16.6 Accept·Scoped·Conditional)

> 이 ADC는 §16.6 책임에 **명칭**을 부여하고, `RFC-0019` §7 Pseudo-Contract 자료 중 **§16.6에 이미 존재하는 의무**를 A-IN 부속 명세로 정식화한다. §14 Kernel Public Contract를 승격하지 않고, LangGraph를 채택하지 않으며, 어댑터를 구현하지 않고, Implementation Strategy·Conformance Test를 확정하지 않으며, Baseline 문언을 편집하지 않는다. 실제 §16.6 개정은 후속 ADR이 수행한다.

---

## 1. Decision Question

| # | 질문 | 처리 |
|---|---|---|
| **Q-A** | 명명과 Adapter Contract 후보 정식화를 **한 ADC에서 함께** 다루는 것이 `ADC-0019` 조건 6의 3단계 선례(존재→명명→구현 전략)로부터 허용되는가? | 1차 판정 — 확정 |
| **Q-B** | §16.6 책임의 명칭 = "Workflow Adapter"인가? | 독립 Decision |
| **Q-C** | "Adapter Contract"의 층위 — §14 Public Contract와 어떻게 분리되는가? | 독립 Decision |
| **Q-D** | 후보 절 (a)~(d) 각각 Accept / Modify / Defer | 독립 Decision (절별) |
| **Q-E** | Checkpoint 입도 C1/C2/C3 + phase 경계 선언 주체 | 독립 Decision (2분할) |
| **Q-F** | Rule B 미충족 상태에서 이번 정식화를 진행할 수 있는가? | 독립 Decision |

---

## 2. Evidence

Q-A는 절차 선례로 판단한다. Q-B~Q-F는 아래를 근거로 하며 **RFC-0020 권고는 입력이지 결정이 아니다.**

| # | Evidence | 용도 |
|---|---|---|
| **P1** | `ADC-0014` — Execution Host 명명은 철저히 명명 단독(존재·범위 미접촉, 구현 전략 별도 RFC, `IMPLEMENTATION_RULES` 미해제) | Q-A 선례 |
| **P2** | `ADC-0015` — 3번째 단계 = 구현 전략 + `IMPLEMENTATION_RULES` 부분 해제. 명명과 전략 사이 "계약 ADC" 없음(§16.3에 계약 표면이 없었기 때문) | Q-A 선례 |
| **P3** | `ADC-0019` §Q8·조건 6 — "명칭·구현체·구현 전략은 각각 별도 ADC(3단계 선례)를 그대로 따른다". 계약 정식화 병행에 대한 명시적 허용·금지 **없음**(계약 정식화는 조건 6의 3단계 열거에 포함되지 않음) | Q-A |
| **P4** | `BASELINE.md` §16.6 본문 — "Checkpoint 값을 생산할 뿐 저장·복원은 호출자"(§15.2), "실행 결과는 예외가 아닌 값으로 표현"(§14.3 G-6), "Reversibility 필수 Architecture 불변조건"을 **이미 Baseline 문언으로 담고 있다** | Q-A, Q-D (a)(b)(d) |
| **P5** | `RFC-0019` §3 — "Workflow Adapter"(이 책임)와 "Engine Adapter"(§16.2, Model/LLM)를 한 절 들여 분리. §7 제목 "Workflow Adapter Port" | Q-B |
| **P6** | v1 `ADR-0007` — Port = `IWorkflowEngine`("Engine" 계보). v2 §5는 Team/Division을 Kernel이 모른다고 명시 → "Engine" 프레이밍의 Core-소유 함의 폐기(`ADC-0019` G2) | Q-B |
| **P7** | `BASELINE.md` §14.1 — "Task 전달 책임"이 계약 범위 밖 → v1 결정 9(Port) 공백의 상위 원인, §16.6의 §14 승격 차단(`ADC-0019` 조건 5) | Q-C |
| **P8** | E3 `langgraph-domain-poc.md` §5·§6-a·블록 2 — caller-owned 값 Checkpoint(plain-JSON dict 반환)가 phase 경계에서 동작, **프로세스 종료 후 재개**(6/6). in-memory `MemorySaver`는 재개 불가 | Q-D (a), Q-E |
| **P9** | E3 §6-b·블록 5-(e)(d) — LangGraph는 노드 예외를 `graph.invoke` 밖으로 **그대로 전파**(실측). 값 반환 시 하위 conditional 정상 반응 | Q-D (b) |
| **P10** | E3 §6-c·블록 5-(a)(b)(c) — disjoint 키 안전 / reducer 없는 공유 키 → `InvalidUpdateError`(결정론적 라이브러리 동작) / `Annotated[list, operator.add]` → 결정론적 병합 | Q-D (c) hazard 기록 |
| **P11** | E3 §7 — 두 시나리오 모두 LangGraph `run_full` == 순차 `run_full` 최종 State, 어댑터 교체 시 caller/domain 파일 해시 불변. E1 `test_workflow_adapter_reversibility.py`(cross-arch 부분 할인, `ADC-0019` G2) | Q-D (d), Q-E |
| **P12** | `RFC-0019` §5 — v1 `ADR-0007` 결정 11(State Model): "v2에서 Team 대신 무엇의 상태를 나타낼지 미결" | Q-D (c) 이연 결합 대상 |
| **P13** | `BASELINE.md` §7 — "Workflow의 도메인 내용"은 HQ. §13.3 A-1~A-5 — 조립 구조 불변식(내용이 아닌 형식 제약) | Q-D (c), Q-E-2 |
| **P14** | `ADC-0019` §Q2 — 이 대상에 Rule B 형식 미충족. 그럼에도 범위 극소화 + 조건 이월 + Reversibility 고정으로 Accept 가능하다고 판정 | Q-F |

---

## 3. Alternatives (Q-A)

| | 내용 | 판정 |
|---|---|---|
| **Alt-1** | 번들링 허용 + 엄격한 내부 분할 — 명명·계약을 한 ADC에서 다루되 각 실체 판정을 개별 Decision으로, 계약은 "후보 절 + 후속 ADR용 문언"까지만 | **Accept (§4·§5)** |
| **Alt-2** | 명명 단독 (`ADC-0014` 미러링), 계약은 이후 별도 ADC | Reject — (a)(b)(d)가 §16.6 재기술이라 별도 라운드 비용 과다, 무명 방치 위험 |
| **Alt-3** | 4단계 체인(존재→명명→**계약**→전략) | 보류 — (c)의 §7/결정 11 접촉을 다룰 후속 단계 형태로 §12에 유지 |
| **Alt-4** | Q-A 자체 Defer | Reject — §16.6 무명, E3 Findings 미소유 |

---

## 4. Analysis

**4.1 선례의 방어 대상 (Q-A)** — `ADC-0013`/`0014`/`0015` 분리의 목적은 **단계 간 함의 누수**(존재→명명→구현 착수가 "따라오는 것"으로 오독)를 막는 것이다(`ADC-0014` §Q1·Risks). "명명 ADC가 그 이름이 §16.6에서 이미 짊어진 불변조건을 계약 언어로 함께 문서화하는 것"은 그 방어 대상이 아니다.

**4.2 계약 후보 4개의 성격** —

| 절 | §16.6 Baseline에 이미 있는가 | 성격 |
|---|---|---|
| (a) caller-owned checkpoint 값 소유 | **있음**(P4: "생산할 뿐 저장·복원은 호출자", §15.2) | 재기술 |
| (b) exception → state | **있음**(P4: "예외가 아닌 값으로", §14.3 G-6) | 재기술 + 귀속 명확화 |
| (c) parallel disjoint key / reducer | **없음** | 신규 — 별도 검토(4.3) → **Defer** |
| (d) Reversibility | **있음**(P4: "필수 불변조건", `ADC-0019` §Q6·조건 4) | 재기술 + 검증 방법 명문화 |

→ 정식화 대상 3개((a)(b)(d))는 전부 §16.6 재기술. 번들링은 **확장이 아니라 정합화**. 선례가 계약 단계를 두지 않은 건 §16.3에 계약 표면이 없었기 때문이지(P2) 규칙이 있어서가 아니다(P3).

**4.3 (c) — 별도 검토 및 이연 결론** —

- **결정 11(State Model)**: 결정 11의 v2 공백은 "State가 **무엇의** 상태를 나타내는가"(P12). (c)는 State에 **무엇을 담을지**를 규정하지 않는다.
- **§7(도메인 내용 = HQ)**: (c)는 도메인 내용을 규정하지 않는다. "동시 쓰기의 기계적 형식"은 §13.3 A-1~A-5류 구조 불변식에 해당한다(P13).
- **그러나**: (c)는 §16.6에 없는 **신규 표면**이다(4.2). §13.3 불변식은 이미 Baseline-Accepted이지만 (c)는 아니다 — 유비만으로 "이미 승인된 범주"에 넣을 수 없다. 또한 E3 PoC에서 reducer 선언(`Annotated[list, operator.add]`)이 도메인 스키마 코드에 있었으므로, (c)를 계약 절로 정식화하면 "HQ가 State 스키마를 disjoint/reducer 규약에 맞춰 설계해야 한다"는 **HQ 설계 구속**이 파생될 수 있다.
- **Q-A 범위와의 관계**: Q-A Accept의 근거는 "후보 4개 중 3개가 §16.6 재기술 → 번들링 = 정합화"다. 신규 표면인 (c)는 그 근거가 덮지 못한다.
- **결론**: (c)는 이 ADC에서 **정식화하지 않는다(Defer)**. E3 §6-c가 실측한 **parallel State write hazard**로만 기록한다. (c)의 (i) 계약화 여부, (ii) 배치(§16.6 A-IN 부속 vs 별도 계층), (iii) HQ State 설계 구속 여부는 **후속 Implementation Strategy ADC 또는 별도 Governance 단계가 v1 `ADR-0007` 결정 11과 결합해 판정**한다.

**4.4 Q-B~Q-F를 RFC-0020 권고와 독립적으로 판정** — §5 각 Decision의 Reason 참조. 특히 Q-C는 RFC-0020 §8.1 Q-C가 대안으로 제시한 "별도 계층(ADR-0009 Stage Data Contract처럼 Public/Hidden)" 프레이밍을 **Reject**한다(공개 표면 함의 위험).

---

## 5. Decision

### Q-A. Accept — Alt-1: 번들링 허용 + 엄격한 내부 분할

ADC-0020은 §16.6 책임의 **명명**과 **Adapter Contract 부속 명세 정식화((a)(b)(d)에 한정)**를 하나의 ADC에서 다룰 수 있다.

**이 Accept의 성격**: Q-A Accept는 **"같은 ADC에서 다룰 수 있다"는 절차적 승인**일 뿐이다. Q-B~Q-F의 실체적 결정을 의미하지 않으며, 각 항목은 아래에서 독립 Decision으로 판정된다.

**전제 조건**:
1. Q-B~Q-F는 각각 독립 번호 Decision. 패키지 표결 아님.
2. 계약 후보 절은 "Accept / Modify + 후속 ADR용 확정 문언"까지만. 발효 규칙 아님. 이 ADC는 Baseline 문언을 편집하지 않는다.
3. ADC-0020 문서에 "(a)(b)(d)는 §16.6 기존 문언의 재기술, (c)는 신규이므로 Defer"임을 명시하고, **이 번들링은 §16.6이 이미 계약 표면을 가졌기 때문이며 §16.x 명명 ADC의 일반 규칙이 아님**을 Traceability에 못박는다.
4. Q-E의 "phase 경계 선언 주체"는 심의 중 §7 접촉이 과중하면 후속 단계로 분리 이연할 수 있다.

**Reason**:
- 선례의 방어 대상은 단계 간 함의 누수이지 계약 병행 문서화가 아니다(4.1). 정식화 대상 3개가 §16.6 재기술이므로 번들링은 정합화(4.2).
- **`ADC-0019` 조건 6은 문면상 "명명 단독"(=`ADC-0014` 미러링) 해석을 허용한다.** 조건 6이 열거한 3단계(존재→명명→구현 전략)에 "계약 정식화"는 포함되지 않으며, 엄격 문면 해석으로는 명명 ADC가 명명만 다뤄야 한다는 독법이 가능하다. 그러나 그 선례의 *의도*는 단계 간 함의 누수 차단이지(4.1) 명명 ADC가 그 이름이 §16.6에서 이미 짊어진 의무를 계약 언어로 재기술하는 것을 금하는 것이 아니다. 신규 표면인 (c)를 Defer로 배제함으로써, 이 ADC의 정식화는 전적으로 기존 §16.6 자료에 머문다 — Q-A Accept는 조건 6의 *문면*을 확장하되 *의도*에 부합한다는 판단이다.
- 분리 시 이미 근거된 재기술에 과도한 절차 비용 + 무명 방치 위험(§3, Alt-2). 오독 리스크는 Q-C 명시 판정 + 절별 분할 + Traceability 못박기로 통제(4.4).

---

### Q-B. Accept — 명칭: "Workflow Adapter"

§16.6 "Scoped Workflow Graph Execution" 책임의 Architecture 명칭을 **Workflow Adapter**로 Accept한다.

**Reason (Evidence 기반, RFC-0020 권고의 자동 채택 아님)**:
- `RFC-0019` §3이 이미 이 책임을 "Workflow Adapter"로, §16.2 Model/LLM 호출을 "Engine Adapter"로 한 절 들여 분리했다(P5). 두 경계 모두 Execution Layer의 교체 가능한 seam이며 "Adapter" 접미사는 이 저장소에서 이미 그 의미로 쓰인다 — 명칭 충돌이 아니라 **정합**이다.
- N-2("Workflow Engine"): §16.2 Engine Adapter와 실충돌 + v1 `IWorkflowEngine`의 "Engine" 프레이밍이 함의하던 Core-소유 Lifecycle을 v2가 명시적으로 폐기했으므로(P6), "Engine"을 계승하지 **않는** 것이 이점이다.
- Modify 후보("Workflow Runner/Executor"): "Adapter"가 담는 Reversibility-seam 함의(§16.6 필수 불변조건)를 잃고 "Engine Adapter"와의 짝을 깬다. "Adapter=래핑 함의 vs Sequential Reference는 무엇도 안 감쌈"은 **의미 긴장(Minor)**이지 채택을 막는 근거가 아니다.

**이 ADC의 범위 밖**: RFC-0020 §5.2가 명칭과 함께 권고한 **"Sequential = Reference Implementation"** 지정은 이 ADC에서 다루지 않는다. Reference의 실체(저장소 코드 vs 문서 기준선)와 지정 자체는 RFC-0020 §8.2 Q-H대로 **Implementation Strategy ADC 소유**다(§12 #2).

**Condition**: 후속 ADR은 이 명칭과 §16.6 절 제목 "Scoped Workflow Graph Execution"의 대응을 명시해야 한다(`ADR-0004`가 "Execution Host" ↔ §16.3을 명시한 선례). `GLOSSARY.md`에 "Workflow Adapter" 항목 추가(Engine Adapter §16.2와의 구분, v1 `IWorkflowEngine` 계보 관계 포함).

---

### Q-C. Accept (Modify) — Adapter Contract = §16.6 A-IN의 부속 명세. §14 Public Contract가 아니다.

**3계층 분리를 확정한다**:

| 계층 | 내용 | 상태 |
|---|---|---|
| **L1 — §16.6 책임 (Baseline, Accepted)** | *무엇을* — A-IN 5항목 + Reversibility 불변조건 + "예외가 아닌 값" | `ADR-0008`으로 확정됨 |
| **L2 — Adapter Contract (이 ADC가 (a)(b)(d) 후보 정식화)** | L1 구현체가 지켜야 할 **내부 의무의 정련**. **§16.6 A-IN의 부속 명세(sub-specification)**. `RFC-0019` §7 "개념 수준" 지위 계승. **Public Surface 아님, Interface 아님** | 후보 — Q-D에서 절별 판정 |
| **L3 — §14 Kernel Public Contract / Public Port (범위 밖, 차단)** | HQ·호출자가 의존하는 **공개 표면** + Public Guarantee | v1 `ADR-0007` 결정 2/5/9/11 해소 전 승격 불가(`ADC-0019` 조건 5). §14.1 "Task 전달 책임" 계약 범위 밖(P7) |

**Modify (RFC-0020 §8.1 Q-C 대안 대비)**: RFC-0020이 제시한 "별도 계층(HQ-level Contract 유사, `ADR-0009` Stage Data Contract처럼 Public/Hidden 구분)" 프레이밍을 **Reject**한다 — 공개 표면 함의를 만든다. Adapter Contract는 L1의 **부속**이지 L1 위의 새 계층이 아니다.

**(a)(b)의 호출자 관측 효과와 비-Guarantee 근거**: (a)는 호출자가 값을 보유하고 (b)는 호출자가 예외 아닌 값을 수신하므로 caller-observable 효과를 갖는다. 그럼에도 이들이 **Public Guarantee가 아닌** 이유는, Adapter Contract가 **§16.6의 비-§14 지위를 그대로 상속**하기 때문이다 — §16.6은 Accepted Kernel Module 절이지 §14 Kernel Public Contract가 아니며(`ADR-0008`), (a)(b)는 §16.6 본문에 이미 있는 caller-facing 동작의 재기술일 뿐 새 공개 표면을 만들지 않는다. §14 승격은 조건 5가 계속 차단한다.

**표기 규칙 (후속 ADR 구속)**:
- Adapter Contract 절에 "Port" / "Public" / "Guarantee" / "Interface" 어휘를 쓰지 않는다.
- 절 도입부에 "§16.6 A-IN 부속 — 구현체 내부 의무. Public Surface 아님. §14 Kernel Public Contract 아니며 그 선행물도 아니다(자동 승격 경로 없음)."를 명문화.
- §16.6 본문 안에 배치하고, §14에는 어떤 항목도 추가하지 않는다.

---

### Q-D. 후보 절 (a)~(d) — 개별 판정

**이 ADC가 후속 ADR용 후보 절로 정식화하는 집합 = (a)(b)(d). (c)는 Defer.**

#### (a) caller-owned checkpoint 값 소유 모델 — Accept (재기술)

진행 상태(중간/최종)는 직렬화 가능한 값으로 표현되고, 어댑터는 그 값을 **생산**만 하며 영속화·복원을 소유하지 않는다.

**Reason**: §16.6 본문("Checkpoint 값을 생산할 뿐 저장·복원은 호출자") + §15.2 + A-IN(e)의 재기술이다(P4). E3 블록 2가 이 모델이 프로세스 종료를 견딤을 실측했다(P8). 신규 표면 없음. **재개 입도는 이 절이 정하지 않는다 → Q-E.**

#### (b) exception → state — Accept (Modify: 강제 메커니즘 미확정)

어댑터 경계를 벗어나는 실행 결과는 예외가 아닌 State 값이어야 한다(§14.3 G-6). 구현체가 노드 예외를 실행 경계 밖으로 전파하면(P9 실측), 어댑터가 그것을 catch-and-encode 하여 값으로 변환하는 것은 **구현체의 보장이 아니라 어댑터의 책임**이다.

**Modify**: "모든 노드에서 강제"를 규범 문언에 넣지 않는다. 강제·검증 **메커니즘**(정적 분석 / Conformance Test)은 이 ADC가 확정하지 않는다 → §12, Implementation Strategy. 이 절은 **의무의 소재**("G-6 준수는 어댑터 책임")까지만 확정한다.

**Reason**: §16.6 "예외가 아닌 값으로" + `ADC-0019` §Q3의 재기술이나, E3 §6-b가 LangGraph 기본 동작이 이와 반대임을 실측했으므로 "누가 책임지는가"를 명확히 할 실익이 있다. 메커니즘은 구현 관심사이므로 분리.

#### (c) parallel State의 disjoint key / reducer — Defer

이 ADC는 (c)를 Adapter Contract 후보 절로 **정식화하지 않는다**. E3 §6-c가 실측한 **parallel State write hazard** — 병렬 fan-out 노드가 reducer 선언 없이 동일 State 키에 쓰면 `InvalidUpdateError`로 비결정·실패(P10) — 로만 기록한다.

**이연 사유**: (c)는 §16.6에 없는 신규 표면이며(§4.2), 병렬 노드 저작은 §7 HQ 도메인 영역이고, reducer 선언 위치(HQ 스키마 vs 어댑터 내부)가 v1 `ADR-0007` 결정 11(State Model)의 v2 재설계와 얽힌다(§4.3). Q-A Accept의 근거("후보 4개 중 3개가 §16.6 재기술 → 번들링 = 정합화")는 신규 표면인 (c)를 덮지 못한다.

**후속 판정**: (c)의 (i) 계약화 여부, (ii) 배치(§16.6 A-IN 부속 vs 별도 계층), (iii) HQ State 설계 구속 여부는 **후속 Implementation Strategy ADC 또는 별도 Governance 단계가 v1 `ADR-0007` 결정 11과 결합해 판정**한다. 그때까지 (c)는 문서화된 hazard로만 존재하며 어떤 규범 효력도 갖지 않는다.

#### (d) Reversibility — Accept (재기술, 신규 아님 명시)

어떤 구현체를 제거하고 다른 구현체(최소한 Sequential)로 교체해도 Kernel·HQ 코드 0 변경. 구현체 고유 문법은 어댑터 경계 안에서만.

**명시**: 이것은 **신규 제안이 아니다.** `BASELINE.md` §16.6이 이미 "필수 Architecture 불변조건"으로 등재했다(`ADC-0019` §Q6·조건 4). 이 절이 더하는 것은 그 불변조건을 계약 언어로 재기술하고, **검증 방법 = v2 맥락 통합 테스트**임을 명문화하는 것뿐이다.

**Condition**: v2 통합 테스트의 **실행**은 이 ADC의 결과가 아니다 → Implementation Strategy 단계(`ADC-0019` Next Step 4). E1은 cross-architecture 부분 할인(G2), E3 §7은 저장소 밖 PoC이지 in-repo 통합 테스트가 아님(P11).

---

### Q-E. Checkpoint 입도 — 2분할 판정

#### Q-E-1. Accept — C1 (phase-boundary caller-owned)

| | Evidence 기반 평가 |
|---|---|
| **C1** | A-IN(e) 문언에 그대로 부합. 순차 어댑터로도 성립(라이브러리 무관, P11). 프로세스 종료 후 재개됨(P8). **Reversibility 불변조건 통과** — 순차 어댑터가 동일 동작 복제(E3 §7). 한계: phase 경계에서만 재개 |
| **C2** | 임의 mid-node 재개 획득. 그러나 **Reversibility 불변조건 위반** — 순차 어댑터가 그래프 소유 checkpointer의 mid-node 재개를 복제 못 함. shim이 "비관용적"(E3 §6-a). **mid-node resume은 이 ADC 범위 밖** |
| **C3** | 가장 단순·reversible. 그러나 A-IN(e)가 **명시한** "값 기반 Checkpoint/Resume" 능력을 축소 제공 — Baseline이 Accept한 A-IN 항목을 미달 이행 |

**Reason**: C1은 RFC-0020 권고의 자동 채택이 아니라 **`ADC-0019` 조건 1(A-IN(e)) + 조건 4(Reversibility)의 결합이 강제하는 유일 선택**이다. C2는 조건 4를 깨고 범위 밖 mid-node에 진입한다. C3는 조건 1을 미달한다.

#### Q-E-2. Defer — phase 경계 선언 주체 (필요조건만 확정)

"phase 경계를 누가 선언하는가"(HQ Workflow 정의 vs Adapter Contract)는 **이 ADC가 확정하지 않는다.**

- **확정하는 것 (필요조건)**: phase 경계는 최소한 **State가 외부 일관성을 갖는 지점**이어야 한다. 이는 "쓰기 중간에는 checkpoint할 수 없다"는 **직렬화 일관성의 자명한 하한**이지 Governance 선택이 아니다.
- **미정으로 남는 것**: 그 지점을 **권위 있게 선언하는 주체**. §7은 "무엇을 실행할지 = HQ"라 하고 phase 경계는 워크플로 구조의 일부로 HQ 쪽으로 기울지만, "State 직렬화 일관 지점"은 어댑터가 판별 가능한 속성이기도 하다. → **Investment/Development HQ 관점 입력 필요**, Implementation Strategy 단계 또는 전용 후속에서 판정(§12 #3).

---

### Q-F. Accept — Rule B 미충족 상태에서 이번 정식화 진행 가능

**Rule B 충족을 선언하지 않는다.** E1+E2+E3 = 3건이나 전부 LangGraph 계보·프로덕션 트래픽 아님. `ADC-0019` §Q2의 Rule B 형식 미충족 판정, 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰)는 그대로 유효하다.

**진행 가능 판정의 근거**:
1. **명명(Q-B)은 계보 독립적이다** — 용어 결정이며 근거는 저장소 용어 충돌 검사이지 관찰이 아니다.
2. **정식화 대상 (a)(b)(d)는 Rule B 하중을 새로 지지 않는다** — §16.6 기존 문언의 재기술이고, 그에 대한 Rule B 판단은 `ADC-0019`의 Accept에 이미 흡수됐다(P14).
3. **신규 표면인 (c)는 이 ADC에서 Defer이므로 Rule B 판단 대상에서 빠진다** — (c)의 계보 근거 충분성은 후속 단계가 결정 11과 함께 다룰 때 평가한다.
4. 이 ADC는 `ADC-0019`보다 **적게** 한다 — 경계를 확장하지 않고, §14로 승격하지 않으며, 구현을 승인하지 않는다.

**유지되는 hard gate**: `ADC-0019` 재검토 조건 (c)는 **다음 단계**(§14 승격, Implementation Strategy, `IMPLEMENTATION_RULES` Scoped 해제, (c) hazard의 계약화)의 차단 조건으로 그대로 유효하다. 이 ADC는 그 gate를 건드리지 않는다.

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6 전부 무변경** — 범위(A-IN)·명시적 제외(A-OUT)·§16.3~16.5 불가침·Reversibility 필수·조건 이월·미확정 항목.
2. **Rule B 미충족 유지** — 재검토 조건 (c) 미충족. Q-F는 "진행 가부"만 판정.
3. **v1 `ADR-0007` 결정 2(Core 소유 Lifecycle)·5(Team/Division 경계)·9(Port)·11(State Model) 미해결(Conditional) 유지** — 해소 전 §14 승격·Production 구현 착수 불가. 이 ADC는 계약 후보((a)(b)(d))만 정식화하며 네 공백을 설계하지 않는다. (c)는 결정 11과 결합해 후속 판정(§5 Q-D (c)).
4. **`IMPLEMENTATION_RULES.md` 금지 유지** — Workflow Parser / Scheduler·우선순위·Workflow orchestration·Dynamic Routing / §6 넓은 Runtime / Stage 재진입·조건부 Stage / Event Bus 구현 금지. 이 ADC는 `ADC-0015`류 부분 해제를 **하지 않는다**.
5. **§14 Kernel Public Contract 미승격 유지** — Public Port·Public Surface·Public Guarantee 신설 없음(Q-C).
6. **Baseline 문언 무변경** — §16.6 개정은 후속 ADR. 이 ADC는 지침만 남긴다.
7. **Reversibility 필수 불변조건 유지** — v2 통합 테스트 재현 검증 요구 그대로, 수행은 Implementation Strategy 트랙.
8. **정식화 범위** — 이 ADC가 후속 ADR용 후보 절로 정식화하는 Adapter Contract 집합은 **(a)(b)(d)에 한정**된다. (c)는 §5 Q-D (c)대로 Defer이며 정식화 대상이 아니다.

---

## 7. Out of Scope (이 ADC의 자동 결과가 아닌 것)

| 항목 | 근거 |
|---|---|
| **LangGraph 최종 채택** | (b)·(c) hazard는 LangGraph 동작을 Evidence로만 인용. `ADC-0019` §Q8 |
| **Implementation Strategy** (어댑터 래핑 방식, Checkpointer 백엔드, Sequential 저장소 코드화·Reference 실체) | `ADC-0015` 대응 단계 |
| **실제 Adapter 구현** | `IMPLEMENTATION_RULES` + `ADC-0019` 조건 5 |
| **Conformance Test / (b) 강제 메커니즘 / (d) v2 통합 테스트 실행** | Implementation Strategy 트랙 |
| **(c) hazard의 계약화·배치·HQ 구속 여부** | 후속 Implementation Strategy ADC 또는 별도 Governance 단계 + 결정 11 결합 |
| **§14 승격 / Public Port 정의** | `ADC-0019` §Q7·조건 5, §14.1 |
| **mid-node resume / HITL / C2 경로** | Q-E-1, RFC-0020 §7 |
| **Scheduler / Runtime orchestration / Event Bus** | A-OUT, `ADC-0019` §Q4 |
| **v1 결정 2/5/9/11 재설계** | `ADC-0019` §Q7·조건 5 |
| **ADC-02(Runtime 존폐) / `ADC-0008` 재판단** | `ADC-0019` §Q8 |
| **§16.3~16.5 무엇이든 / §16.7 Workflow Kernel Module Defer 재판단** | `ADC-0019` §Q5, §16.6 "불가침"; 별개 축(`ADC-0001` Module 2) |
| **Baseline 문언 편집** | → 후속 ADR |
| **Rule B 재판단(충족 선언)** | `ADC-0019` §Q2 유지 |
| **Q-E-2 phase 경계 선언 주체 확정** | HQ 입력 필요, 이연 |

---

## 8. 후속 ADR에서 반영할 사항 (Baseline 지침 — 이 ADC가 직접 반영하지 않음)

1. **§16.6 절 제목·본문에 명칭 부여**: "16.6 Workflow Adapter — Scoped Workflow Graph Execution (…)". 명칭 ↔ 기존 제목 대응 문장 명시(`ADR-0004` 선례).
2. **`GLOSSARY.md`**: "Workflow Adapter" 항목 추가 — §16.2 Engine Adapter와의 구분, v1 `IWorkflowEngine` 계보 관계, Reversibility 함의.
3. **§16.6 본문에 Adapter Contract 부속 명세 추가** — **(a)·(b)·(d)** 확정 문언. 도입부에 "§16.6 A-IN 부속 / 구현체 내부 의무 / Public Surface·§14 아님 / 자동 승격 경로 없음 / `RFC-0019` §7 개념 수준 지위" 라벨. "Port/Public/Guarantee/Interface" 어휘 불사용.
4. **(c)는 후속 ADR에 반영하지 않는다** — (c)는 E3에서 확인된 parallel State write hazard로만 남는다. 그 계약화 여부·배치·HQ 구속 여부는 후속 Implementation Strategy ADC 또는 별도 Governance 단계가 v1 `ADR-0007` 결정 11과 결합해 판정한 뒤, 필요 시 그 단계의 ADR이 반영한다.
5. **명시적 비변경 재확인**: §14 미승격, `IMPLEMENTATION_RULES` 무변경, v1 결정 2/5/9/11 미해결, §16.3~16.5·§16.7 무변경, ADC-02/ADC-0008 불변.
6. **Version**: v1.12 → v1.13 (Minor 예상), Architecture State = Frozen 유지.

---

## 9. Traceability

| 문서 / 절 | ADC-0020과의 관계 | 정합성 |
|---|---|---|
| `RFC-0020` §8.1 Q-A | 이 ADC의 1차 Decision Question | RFC가 "ADC-0020이 먼저 판정"으로 위임 → 완료(Q-A Accept Alt-1) |
| `RFC-0020` §5 권고 (명칭 / Sequential=Reference / (a)~(d) / C1) | 입력이지 결정 아님 | **Q-B** Accept(명칭 "Workflow Adapter", 독립 Evidence P5·P6) / **Sequential=Reference** 범위 밖(→ Impl Strategy) / **Q-C** Accept·Modify(3계층, RFC "별도 계층" 대안 Reject) / **Q-D (a)** Accept 재기술 · **(b)** Accept·Modify(메커니즘 이연) · **(c)** Defer(결정 11 결합) · **(d)** Accept 재기술 / **Q-E-1** Accept C1(조건 1+4 강제, 권고와 결론 동일하나 근거 독립) · **Q-E-2** Defer / **Q-F** Accept(진행 가부만, Rule B 미선언) |
| `RFC-0019` §3 (Workflow Adapter ↔ Engine Adapter 분리) / §7 (Pseudo-Contract) | Q-B 근거 / L2 계약의 출처·지위 | §7 문언 무변경, "개념 수준" 지위 계승. §7 자료 중 §16.6에 없는 (c)는 정식화 제외 |
| `ADC-0019` §Q8 / 조건 6 (3단계 선례) | Q-A가 해석·판정하는 대상 | 조건 6은 "명명 단독" 문면 해석을 허용(§5 Q-A Reason). Q-A Accept는 문면 확장 + 의도 부합. 번들링은 §16.6 기존 계약 표면 때문이며 **일반 규칙 아님** |
| `ADC-0019` §Decision 조건 1~5 | 전부 무변경 | §6에 재확인 |
| `ADC-0019` §Q2 / 재검토 조건 (c) | Q-F가 준용, Rule B 미충족 유지 | 무변경 — 다음 단계(§14 승격·Impl Strategy·(c) 계약화) hard gate로 존속 |
| `ADC-0019` §Q6 / 조건 4 (Reversibility) | Q-D (d)·Q-E-1의 판정 기준 | 재기술만, 검증 실행은 이연 |
| `ADC-0013`→`ADC-0014`→`ADC-0015` (+`ADR-0004`/`ADR-0005`) | Q-A 선례 | `ADC-0014` 명명 단독이었음. ADC-0020 번들링은 예외적, Traceability에 못박음 |
| `BASELINE.md` §16.6 | 명명 대상 + (a)(b)(d) 재기술 출처 | 문언 무변경 — 개정은 후속 ADR |
| `BASELINE.md` §14 / §14.1 | Q-C L3 — 승격 차단, "Task 전달 책임" 계약 범위 밖 | 무변경, §14에 항목 추가 없음 |
| `BASELINE.md` §7 / §13.3 | Q-D (c)·Q-E-2 경계 판단 기준 | 무변경 — (c)는 Defer, 도메인 내용 미규정 |
| `BASELINE.md` §15.2 | Q-D (a) 근거 | 인용만 |
| v1 `ADR-0007` 결정 11 (State Model) | **Q-D (c) Defer의 결합 대상** | 미해결 유지 — (c) hazard의 계약화·배치·HQ 구속 여부는 결정 11이 다뤄질 때 후속 단계에서 함께 판정. 이 ADC는 (c)를 정식화하지 않음 |
| v1 `ADR-0007` 결정 2/5/9 | §6 조건 3 | 미해결 유지 |
| `ADR-0008` §Out of Scope / §4 | 명칭·구현체·Port·전략 미반영, `IMPLEMENTATION_RULES` 무변경 | ADC-0020도 유지 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 | §6 조건 4 | 해제 없음 |
| RFC-0020 Final Review (PASS) | 이 ADC의 입력 전제 | 번들링을 "공시된 이탈, Q-A 위임"으로 처리한 것이 PASS 근거 |

---

## 10. Self-Review (Architecture / Governance Review 관점)

| 점검 | 결과 |
|---|---|
| Q-A Accept가 Q-B~Q-F 실체 결정을 선행했는가 | **아니오** — §5 Q-A가 "절차적 승인일 뿐"임을 명시, Q-B~Q-F는 개별 Decision + 각자 Reason |
| Q-A가 조건 6 엄격 해석을 은폐했는가 | **아니오** — §5 Q-A Reason이 "명명 단독" 문면 해석 가능성을 인정하고, 의도(함의 누수 차단)와 구분하여 정당화 |
| RFC-0020 권고를 자동 채택했는가 | **아니오** — Q-B는 P5·P6로 독립 지지; Q-C는 RFC 대안 Reject; Q-D (b) Modify·(c) Defer; Q-E-1은 조건 1+4가 C1을 강제; Sequential=Reference는 범위 밖으로 명시 |
| Adapter Contract가 §14/Public Port를 우회 생성하는가 | **아니오** — Q-C 3계층 분리, (a)(b)의 caller-observable 효과도 §16.6 비-§14 지위 상속으로 비-Guarantee, "Port/Public/Guarantee/Interface 어휘 금지", §14 항목 추가 없음, "자동 승격 경로 없음" 명문화 |
| (c)가 v1 결정 11 / §7 / HQ State 설계를 몰래 결정하는가 | **아니오** — (c)는 이 ADC에서 **정식화하지 않고 Defer**. E3 hazard로만 기록. 계약화·배치·HQ 구속은 결정 11과 결합해 후속 단계 판정(§5 Q-D (c), §8-4, §12 #1). 규범 효력 없음 |
| Q-E-1 C1이 A-IN(e)+Reversibility를 동시 만족하는 논리가 Evidence로 충분한가 | **예** — A-IN(e) 문면 부합 + E3 블록 2(프로세스 종료 후 재개 6/6) + E3 §7(순차 어댑터 동일 동작, 해시 불변). C2는 조건 4 위반, C3는 조건 1 미달 |
| Q-E-2 Defer가 적절한가 | **예** — 필요조건(직렬화 일관성 하한, Governance 선택 아님)만 확정, 선언 주체는 HQ 입력 필요로 미정 |
| Q-F가 Rule B 충족을 암묵 선언하거나 hard gate를 약화하는가 | **아니오** — "Rule B 충족을 선언하지 않는다" 명시, 재검토 조건 (c)를 다음 단계 hard gate로 재확인. (c) Defer로 Rule B 계산에서 제외 |
| LangGraph 채택 / Impl Strategy / 실제 구현 / Conformance Test / §14 승격 / `IMPLEMENTATION_RULES` 해제를 자동 결과로 만들었는가 | **아니오** — §7 Out of Scope에 전부 명시. §6 조건 4가 `ADC-0015`류 부분 해제 배제 |
| `ADC-0019` 조건 1~6 / v1 결정 2/5/9/11 / `IMPLEMENTATION_RULES` / §14 미승격 유지 | **예** — §6 Conditions 1~8에 전부 재확인 |
| Baseline을 수정했는가 | **아니오** — §8에 후속 ADR 지침만 |
| 새 Architecture / Contract를 확장했는가 | **아니오** — §16.6 존재는 `ADC-0019` Accept 완료. 이 ADC는 명명 + 기존 §16.6 자료((a)(b)(d))의 계약 언어화. 신규 표면 (c)는 Defer |
| ADR이 필요한가 | **예** — 명칭 + (a)(b)(d) 부속 명세가 §16.6 본문에 들어가려면 Baseline 개정 필요 |

---

## 11. Next Step

**ADR Required** — §8 지침으로 §16.6에 (1) "Workflow Adapter" 명칭 + 제목 매핑, (2) `GLOSSARY.md` 항목, (3) Adapter Contract 부속 명세 **(a)(b)(d)**를 반영. Baseline v1.12 → v1.13, Frozen 유지. **(c)는 이 ADR에 포함하지 않는다.**

**그다음 — Implementation Strategy ADC** (`ADC-0015` 대응): LangGraph 채택 여부, 어댑터 구현 전략, Checkpointer 백엔드, Sequential Reference 실체, (b) 강제 메커니즘, **(c) hazard의 계약화·배치·HQ 구속 여부(+ 결정 11 결합, Alt-3 분리 판단)**, (d) v2 통합 테스트, Q-E-2 phase 경계 선언 주체, `IMPLEMENTATION_RULES` Scoped 해제 여부. **차단 조건**: `ADC-0019` 재검토 조건 (c)(다른 계보 / v2 프로덕션 관찰) + v1 결정 2/5/9/11 해소.

---

## 12. Open Issues

1. **(c) hazard의 계약화·배치·HQ 구속 여부** — E3 §6-c가 실측한 parallel State write hazard(reducer 없는 공유 키 → `InvalidUpdateError`)를 (i) Adapter Contract 절로 계약화할지, (ii) §16.6 A-IN 부속으로 둘지 별도 계층으로 둘지, (iii) HQ State 스키마 설계를 구속할지 — 이 셋을 v1 `ADR-0007` 결정 11(State Model)이 다뤄질 때 후속 Implementation Strategy ADC 또는 별도 Governance 단계에서 결합 판정. Alt-3(4단계 체인)의 실질 트리거.
2. **"Sequential = Reference Implementation"** — 이 지정은 ADC-0020 범위 밖이며(§5 Q-B), Reference의 실체(저장소 코드 vs 문서 기준선)는 RFC-0020 §8.2 Q-H대로 **Implementation Strategy ADC 소유**.
3. **Q-E-2 phase 경계 선언 주체** — HQ Workflow 정의 vs Adapter Contract. Investment/Development HQ 관점 입력이 필요한지, 전용 후속 문서가 필요한지.
4. **(b) exception→state 강제·검증 메커니즘** — catch-and-encode를 정적 분석으로 검증할지 Conformance Test로 검증할지. Implementation Strategy 단계.
5. **4단계 체인의 장기 정합성** — Traceability의 "일반 규칙 아님" 못박기가 §16.x 확장 시 충분한 방어인지, Alt-3이 구조적으로 더 깨끗한지.
6. **후속 ADR의 Version 폭** — (a)(b)(d) 부속 명세 추가가 Minor(v1.13)로 충분한지.
