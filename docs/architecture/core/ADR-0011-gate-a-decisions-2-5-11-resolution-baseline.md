# ADR-0011: Gate (A) v1 `ADR-0007` 결정 2·5·11 Resolution의 Baseline 반영 (ADC-0022 후속)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0011` (`docs/decisions/adr/`에는 동명 문서 없음 — 네임스페이스로 구분) |
| 제목 | `ADC-0022`의 Decision(Gate (A) 중 Team/Division 부재에서 비롯된 v1 `ADR-0007` **결정 2·5·11**의 v2 Resolution + (c) reducer 규약의 **배치**)을 Architecture Baseline·GLOSSARY에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** — Architecture/Governance Review PASS 이후, 사용자 승인(2026-09-04)으로 §Migration Strategy 1~4를 실행했다: `BASELINE.md` §16.6에 "실행 단위(Execution Unit)"·"A-IN(a) 공유 State가 담는 정보"·"실행 단위 Lifecycle" 문단 신설 + A-IN 문단에 HQ 조직 비의존 문장 부기 + 기존 (c) 문단에 배치 문장 부기 + "미해결 v2 공백" 문단 재작성 + "Production 구현과의 관계" 문단 참조번호 정정, §17 Version v1.14 → v1.15, `GLOSSARY.md` "Workflow Adapter (Reference)" 절에 "실행 단위" 행 추가 + 결정 참조번호(2/5/9/11 → 9) 정정 두 곳. `hqs/development/IMPLEMENTATION_RULES.md`·§14·§16.6 Reversibility 2문단·Adapter Contract (a)(b)(d) bullet·§16.1~§16.5·§16.7·§6 Concept Model 표·`docs/decisions/adc/ADC.md`·`ADC-0008`·`ADC-0021`은 무변경. Commit/PR/Merge는 별도로 진행한다 |
| Context | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` — **Status: Decided — ADR Required**, Architecture/Governance Review PASS(§9). D-0(실행 단위 = 설명 용어), D-2(결정 2 Resolved), D-5(결정 5 Resolved), D-11(결정 11 Resolved), D-11c((c) 배치 = HQ 스키마), D-9(결정 9 = §14.1 트랙), D-Gate-A(Gate (A) 부분 해소) |
| 관련 RFC | `docs/architecture/core/RFC-0021-workflow-adapter-execution-unit-lifecycle-state-model-boundary.md` §6(B-2·B-5·B-11 Boundary Question) |
| 관련 ADC | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` |
| 선행 ADR | `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md`(§16.6 **존재** 등재 — 조건 5로 결정 2/5/9/11 이월), `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md`(명칭 + Adapter Contract (a)(b)(d) 반영, "명칭만 반영·`IMPLEMENTATION_RULES.md` 무변경" 층위 — 이 ADR이 계승; §3이 (c) 배치를 "결정 11이 다뤄질 때 후속 판정"으로 넘긴 문서), `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`(Gate (C) E4 "부분 충족" 반영, §16.6 내부 문단 추가 + §17 + GLOSSARY 한 문장 층위 — 이 ADR이 계승) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0019` §Decision 조건 1~6·재검토 조건 (c), `ADC-0020` §6 Conditions 1~8, `ADC-0021` §D1~D4·§6~§8, `ADR-0010` "부분 충족", `docs/decisions/adc/ADC.md` ADC-02(Open·NOW), `docs/architecture/core/ADC-0008`(Not Accepted) — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 `ADC-0022`가 이미 내린 Decision을 다시 논의하지 않는다. 새로운
철학·Architecture·Contract를 제안하지 않는다. `ADC-0022` §5 D-0~D-Gate-A
중 **결정 2·5·11의 v2 Resolution과 (c)의 배치**를 실제 `BASELINE.md`·
`GLOSSARY.md` 문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

| 단계 | 다루는 것 |
|---|---|
| `RFC-0021` | B-2·B-5·B-11 Boundary Question 개설 — 결정하지 않음 |
| `ADC-0022` | D-0(실행 단위 = 설명 용어) / D-2(결정 2) / D-5(결정 5) / D-11(결정 11) / D-11c((c) 배치, 독립 Decision 아님) / D-9(결정 9 = §14.1 트랙) / D-Gate-A(Gate (A) 부분 해소) |
| **이 ADR** | `ADC-0022` §8 지침 중 **D-0·D-2·D-5·D-11·D-11c·D-Gate-A**의 Baseline Governance 반영 — §16.6 본문 갱신, §17 v1.14 → v1.15, `GLOSSARY.md` "Workflow Adapter (Reference)" 절 정정. 잔여 정합성 2건(§16.6 "Production 구현과의 관계" 문단·`GLOSSARY.md` 참조번호)을 함께 정정 |
| 후속 별도 절차 | 결정 9(`IWorkflowEngine` Port / §14.1 "Task 전달 책임") / §14 승격 / Gate (B)·(C) / (c)의 계약화·HQ 구속 강화 / LangGraph 채택 / Implementation Strategy / `IMPLEMENTATION_RULES.md` Scoped 해제 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0022`가 Decision 범위에서 반영을 지시하지 않은 것, 그리고 사용자
지시가 명시적으로 배제한 것은 **하나도 반영하지 않는다**(`ADC-0022`
§1.2·§6·§7).

| 항목 | 근거 |
|---|---|
| **결정 9(`IWorkflowEngine` Port) / 결과 반환 타입(`WorkflowResult` 대응) / 입력 시그니처 / §14.1 "Task 전달 책임"·"Engine 호출 책임"의 계약 편입** | `ADC-0022` §D-9, `RFC-0019` §5, `ADC-0019` G3, `BASELINE.md` §14.1 — 별도 Track. 이 ADR의 §16.6 갱신은 결정 9를 "§14.1 트랙 pending"으로 **명시**하되 §14·§14.1 문언을 건드리지 않는다 |
| **§14 Kernel Public Contract 승격 / Public Responsibilities·Guarantees·Extension Points·Port·Surface·Interface 신설·수정** | `ADC-0019` §Q7·§Decision 조건 5, `ADC-0020` §Q-C L3, `ADC-0022` §6 조건 6 — §14 승격은 결정 9 해소 이후에만 가능. §14에 항목 추가 없음 |
| **Gate (B)** (`ADC-0019` 재검토 조건 (c) — 다른 계보 또는 v2 프로덕션 관찰) 진전·충족 선언 | `ADC-0021` §8, `ADC-0022` §6 조건 5 — E1~E4 전부 LangGraph 계보. hard gate로 존속 |
| **Gate (C)** (Reversibility 필수 불변조건의 v2 완전 discharge) / `ADR-0010` "부분 충족" 재판정 | `ADR-0010`, `ADC-0022` §6 조건 4 — §16.6 "Reversibility — 필수 Architecture 불변조건" 문단과 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단은 **문자 그대로 유지** |
| **Adapter Contract 부속 명세 (a)(b)(d) bullet 문언 재정의** | `ADC-0022` §9.2, `ADR-0009`/`ADR-0010` §Out of Scope — 인용만, verbatim 유지. 특히 (d)의 "그 통합 테스트의 실행은 이 반영의 결과가 아니다" 문장 verbatim |
| **(c)의 계약화 여부 ((i)) · HQ State 설계 구속 강화 ((iii))** | `ADC-0020` §Q-D Defer, `ADR-0009` §3 — 이 ADR은 (c)의 **배치 ((ii))**만 반영하며, (c)를 정식 Adapter Contract 절로 승격하지 않고 규범 효력을 부여하지 않는다 |
| **"실행 단위(Execution Unit)"의 §6 Concept Model 표 등재 / 새 Kernel Domain·Layer·Component 신설** | `ADC-0022` §D-0·§3.2 U-1, `ADR-0009` §Decision 4(Workflow Adapter를 §6에 넣지 않은 선례) — §16.6 본문 설명 용어에 한정 |
| **종료 disposition 축의 Kernel 규범 정의 (R11-b)** | `ADC-0022` §3.3 S-b Reject, §D-11 (4) — Kernel은 종료 disposition 축의 존재를 요구하지 않는다. §16.6 신설 문단은 "기술/서술"에 한정하고 enum·타입을 도입하지 않는다 |
| **LangGraph 최종 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 / Implementation Strategy 세부** | `ADC-0019` §Q8, `ADC-0020` §7, `ADC-0021` §D2·§7 |
| **`hqs/development/IMPLEMENTATION_RULES.md` line 9/13/14/19 전면·Scoped 해제** | `ADC-0020` §6 조건 4, `ADR-0009` §6·`ADR-0010` §4 선례 — `ADC-0015`류 부분 해제를 **하지 않는다** |
| **`docs/decisions/adc/ADC.md` ADC-02 / `docs/architecture/core/ADC-0008` / §16.7 Workflow Kernel Module Defer 재판단** | `ADC-0019` §Q8, §16.6 "Workflow Module Defer(§16.7)와의 구분" 문단 — 별도 축 |
| **`BASELINE.md` §16.1~§16.5·§16.7 문언, §6 Concept Model 표, §15.2** | `ADR-0009`/`ADR-0010` §Out of Scope 관행 — 참조만, 문자 그대로 유지 |
| **`BASELINE.md` H1 제목줄(현재 `v1.8` 표기)과 §17 Version 표의 불일치 정정** | `ADR-0008` §5·`ADR-0009`·`ADR-0010` §Out of Scope와 동일 관행 — §17 표만 갱신 |
| **`ADC-0021` 원문 편집** (§8 Gate (A) 라벨 자체) | 사용자 지시 — ADC/ADR 미수정. Gate (A)의 새 상태는 `BASELINE.md` §16.6의 cross-reference로만 반영한다 |
| **Production Code(`core/`, `hqs/`, `dashboard/`), `docs/research/`** | 전혀 수정하지 않는다 |
| **`RFC-0021` Status 전환 (Proposed → Accepted)** | 별도 Governance 판단 — 이 ADR은 `ADC-0022`가 그 Boundary Question을 이미 판정했음만 인용한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.6 본문에 **(2.1)** "실행 단위(Execution Unit)" 설명 용어 문단, **(2.4)** "A-IN(a) 공유 State가 담는 정보" 서술 문단, **(2.2)** "실행 단위 Lifecycle" 문단을 신설하고, **(2.3)** A-IN 문단에 HQ 조직 비의존 문장을, **(2.5)** 기존 (c) 문단에 배치 문장을 부기하며, **(2.6)** "미해결 상태로 유지되는 v2 공백" 문단을 재작성하고, **(2.7)** "Production 구현과의 관계" 문단의 결정 참조번호를 정정한다. §17 Version을 v1.14 → v1.15로 갱신하고 변경 이력 한 줄을 추가한다. §16.6의 다른 문단(책임·근거·§16.3~16.5 경계·Checkpoint 용어 구분·Reversibility 필수 불변조건·Reversibility v2 부분 충족(E4)·Workflow Module Defer 구분·명칭·Adapter Contract (a)(b)(d) bullet·이 Accept가 결정하지 않는 것)과 §1~§15·§16.1~§16.5·§16.7·§6 Concept Model 표·§14·§15.2는 **문자 그대로 유지**한다 |
| `docs/00_governance/GLOSSARY.md` | "Kernel Modules — Workflow Adapter (Reference)" 절 표에 "실행 단위 (Execution Unit)" 행을 추가하고, 절 주석 블록(`>` 인용)의 결정 참조번호(2/5/9/11 → 9) 두 곳을 정정한다. "Workflow Adapter"·"Adapter Contract" 표 행, "Concept Model 용어" 절은 무변경 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, `docs/architecture/core/ADC-0021`,
Kernel Public Contract(§14), Production Code는 이 ADR로 건드리지 않는다
(§Out of Scope·§4·§6).

### 2. `BASELINE.md` §16.6 갱신 내용

`ADC-0022` §5 D-0~D-Gate-A와 §8 지침이 이미 정리한 것만 옮긴다. 새 판단을
만들지 않는다.

#### 2.1 "실행 단위(Execution Unit)" 설명 용어 문단 신설

삽입 위치: **A-IN 문단 뒤, A-OUT 문단 앞**(`ADR-0009` §2.2가 "명칭"
문단을 앞/뒤 앵커로 삽입한 방식과 동일).

```markdown
**실행 단위(Execution Unit) — §16.6 A-IN 입력 경계 설명 용어**: 위 A-IN이
입력으로 받는 "이미 구성된 실행 단위"는 **HQ가 구성한 "무엇을·어떤 순서·
병렬성으로·어느 Agent가 수행하는가"의 묶음**이며, Workflow Adapter는 이를
**불투명한 입력**으로 받는다. Kernel은 그 내부 구조·생명주기·조직적
출처(Division/Team의 유무)를 정의하지 않는다(`ADC-0022` §D-0). 이 용어는
§16.3·§16.4·§16.6이 이미 정의 없이 써 온 "실행 단위"에 §16.6 맥락의
설명을 붙인 것이지 — **§6 Concept Model 항목이 아니고, 새 Kernel
Domain·Layer·Component가 아니며, §16.7이 Defer한 Workflow Kernel Module이
아니다**(`ADR-0009` §Decision 4가 "Workflow Adapter" 명칭을 §6에 등재하지
않고 §16.6 본문 용어로 둔 것과 동일 판단).
```

#### 2.2 "실행 단위 Lifecycle" 문단 신설

삽입 위치: **A-OUT 문단 뒤, "§16.3~16.5와의 경계" 문단 앞**. A-OUT의
기존 bullet 목록은 무변경.

```markdown
**실행 단위 Lifecycle — Adapter가 소비할 Kernel 소유 전이는 없다
(`ADC-0022` §D-2)**: Workflow Adapter의 개입 구간(위 A-IN, "HQ가 실행
단위를 구성한 이후 ~ 그 실행이 모두 끝나는 시점")에는 **Adapter가 소비할
Kernel/Core 소유 실행 단위 생명주기 전이가 존재하지 않는다.** v1
`ADR-0007` 결정 2가 전제한 `Team`/`TeamState`의 v2 대응물은 §5(Kernel이
Team/Division을 모른다)로 인해 구조적으로 부재하며, Investment/Development
HQ 코드에도 실행 단위 상태 머신이 없다. 이 "부재"는 **실행 단위 수준**에
한정된다 — §6 "HQ는 Lifecycle State를 가진다"와 §7 "HQ의 생명주기 관리
및 상태 전환 통제 = Jarvis OS"는 이 서술로 변경되지 않으며, HQ Lifecycle
State는 Adapter 개입 구간 **밖**에서 Jarvis OS가 통제하고 Adapter가
전이시키지 않는다. HQ가 구성한 실행 단위가 자체 도메인 전이 로직을
포함하는 경우, Workflow Adapter는 그 로직을 **호출만** 하고 전이 규칙을
재구현하거나 재정렬하지 않는다 — 이는 위 A-OUT "Domain Lifecycle 전이
규칙 재구현 금지"(v1 `ADR-0007` 결정 2·대안 B 기각 인용)의 **긍정형
재기술**이며 새 의무가 아니다. 현재 이 조건을 트리거하는 실행 단위 전이
로직은 어느 HQ에도 없다 — 이 조항은 미래 대비로 존속한다.
```

#### 2.3 A-IN 문단에 HQ 조직 비의존 문장 추가

기존:

```markdown
**A-IN (Kernel Module로서 다루는 것)**: State, Node, Conditional Edge,
Loop, 값 기반 Checkpoint/Resume — 위 "책임" 문단의 다섯 항목, 그리고
그 진행이 개입하는 구간("HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두
끝나는 시점")으로 한정된다(`ADC-0019` §Q3·§Decision 조건 1).
```

교체 후(문장 추가, 기존 문장은 문자 그대로 유지):

```markdown
**A-IN (Kernel Module로서 다루는 것)**: State, Node, Conditional Edge,
Loop, 값 기반 Checkpoint/Resume — 위 "책임" 문단의 다섯 항목, 그리고
그 진행이 개입하는 구간("HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두
끝나는 시점")으로 한정된다(`ADC-0019` §Q3·§Decision 조건 1). 이
입력("이미 구성된 실행 단위")은 HQ 내부 조직 구조(Division/Team의 존재
여부·이름·책임 분담)와 **독립적으로** 성립하며, Adapter는 그 구조를
관측하지도 그에 의존하지도 않는다 — 새 입력 계약 의무가 아니라 §5·§7이
이미 함의한 경계의 확인이다(`ADC-0022` §D-5, `hqs/development/BOUNDARY.md`가
"Division/Team 관례를 쓸지 말지 결정"을 HQ 책임으로 명시). 후속 Adapter
Contract 정련이나 Public Port 정의가 HQ 내부 조직 구조를 입력 스키마에
노출하면 이 경계 위반이다. 입력의 **구체 시그니처**(v1 `ADR-0007` 결정
9 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 이 Accept가 정하지
않는다 — §14.1 "Task 전달 책임" 트랙에 남는다.
```

#### 2.4 "A-IN(a) 공유 State가 담는 정보" 서술 문단 신설

삽입 위치: **위 2.1 "실행 단위" 문단 뒤, A-OUT 문단 앞**(A-IN(a)
인접). 결과 문단 순서: `… A-IN → [2.1 실행 단위 용어] → [2.4 A-IN(a)
State 서술] → A-OUT → [2.2 실행 단위 Lifecycle] → §16.3~16.5 경계 …`.

```markdown
**A-IN(a) 공유 State가 담는 정보 — Workflow Execution State ↔ HQ Domain
State (`ADC-0022` §D-11)**: A-IN(a) "공유 실행 상태(State)의 보유"가 담는
정보는 두 종류로 **기술된다**(규범 축을 정의하는 것이 아니라 서술이다) —
(i) **진행 정보**: 그래프의 어느 Node에 있는지, 무엇을 반복 중인지.
Adapter가 생산하는 값이며 호출자가 보관·반환한다(A-IN(e), Adapter
Contract (a)). (ii) **종료 disposition 정보**: 실행이 어떻게
끝났는가(성공/실패/취소에 준하는 상태). 이것이 값으로 표현되고 예외로
전파되지 않는 것은 §14.3 G-6 · 위 A-IN · Adapter Contract (b)가 이미
규정한 **형식 제약**이며, 그 **내용·어휘**(어떤 상태가 있고 무슨 뜻인지)는
§7상 **HQ 도메인 책임**이고 Kernel이 규정하지 않는다. Kernel은 v1
`ADR-0007` 결정 11의 `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}`
enum이나 `WorkflowResult` 타입을 v2에 도입하지 않으며, 종료 disposition
정보가 State에 명시 축으로 존재하도록 **요구하지 않는다**. v1이
`WorkflowStatus`를 `TeamState`와 대비해 정의했던 "별개 축" 구도는 v2에서
"진행 정보 vs 종료 정보"로 약하게 재기술되며, 둘은 A-IN(a) State가 함께
담을 수 있는 정보이지 Kernel이 강제하는 별도 State 축이 아니다. 실행
결과를 호출자에게 돌려주는 반환 타입(`WorkflowResult` 대응)은 이 Accept
밖이며 §14.1 "Task 전달 책임" 트랙에 남는다.
```

#### 2.5 기존 (c) 문단에 배치 문장 부기

기존:

```markdown
병렬 fan-out Node가 동일 State 키에 reducer 선언 없이 쓰는 경우의
동시 쓰기 규약("(c)")은 이 부속 명세에 **포함되지 않는다** — `ADC-0020`
§Q-D가 (c)를 정식화하지 않고 Defer했다. (c)는 문서화된 hazard로만
존재하며, 그 계약화·배치·HQ State 설계 구속 여부는 v1 `ADR-0007` 결정
11(State Model)이 다뤄질 때 후속 절차가 결합 판정한다. 이 절은 (c)에
어떤 규범 효력도 부여하지 않는다.
```

교체 후(마지막 문장 뒤에 2문장 부기, 기존 문장은 문자 그대로 유지):

```markdown
병렬 fan-out Node가 동일 State 키에 reducer 선언 없이 쓰는 경우의
동시 쓰기 규약("(c)")은 이 부속 명세에 **포함되지 않는다** — `ADC-0020`
§Q-D가 (c)를 정식화하지 않고 Defer했다. (c)는 문서화된 hazard로만
존재하며, 그 계약화·배치·HQ State 설계 구속 여부는 v1 `ADR-0007` 결정
11(State Model)이 다뤄질 때 후속 절차가 결합 판정한다. 이 절은 (c)에
어떤 규범 효력도 부여하지 않는다. 결정 11이 `ADC-0022`에서 다뤄진 결과,
(c)의 **배치**는 HQ의 State 스키마 설계 책임(§7 도메인 내용 / §13.3류
구조 불변식)으로 확정된다(`ADC-0022` §D-11c) — 어댑터의 의무는 HQ
스키마가 선언한 disjoint/accumulate 의미론을 **기계적·결정론적으로
이행**하는 것뿐이다. (c)의 **계약화 여부**와 **HQ 설계 구속 강화**는
여전히 `ADC-0020` §Q-D Defer·`ADR-0009` §3 그대로이며, (c)는 규범 효력
없는 hazard + 배치 원칙으로만 남는다(실제 HQ에 공유 키 병렬 쓰기 사례
없음).
```

#### 2.6 "미해결 상태로 유지되는 v2 공백" 문단 재작성

기존:

```markdown
**미해결 상태로 유지되는 v2 공백 (Conditional)**: v1 `ADR-0007` 결정
2(Core 소유 Lifecycle 소비)·5(Team/Division 경계)·9(`IWorkflowEngine`
Port)·11(State Model)의 v2 대응 부재는 이 Accept로 해소되지 않는다
(`ADC-0019` §Q7·§Decision 조건 5). 이 네 공백이 후속 Architecture
절차(ADR 또는 별도 RFC)로 다뤄지기 전에는, 이 책임을 Kernel Public
Contract(§14)로 승격하거나 Production 구현에 착수할 수 없다. 결정 9의
공백 원인은 §14.1이 "Task 전달 책임"을 계약 범위 밖으로 두는 것이며,
이는 이 책임보다 상위의, 별도로 이미 Open인 질문이다.
```

교체 후(문단 bold 라벨 포함 재작성 — 상태 갱신이지 새 Decision이 아님):

```markdown
**v2 공백의 현재 상태 (Conditional)**: v1 `ADR-0007` 결정 **2(Core 소유
Lifecycle 소비)·5(Team/Division 경계)·11(State Model)은 `ADC-0022`로
Resolved**다 — Team/Division 부재에서 비롯된 세 공백의 v2 재정의가
완료됐다(위 "실행 단위(Execution Unit)"·"실행 단위 Lifecycle"·"A-IN(a)
공유 State가 담는 정보" 문단, `ADC-0022` §D-2·§D-5·§D-11·§D-11c).
**결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처)는
미해결로 남는다** — 공백 원인이 Team 부재가 아니라 §14.1이 "Task 전달
책임"·"Engine 호출 책임"을 계약 범위 밖으로 두는 것이므로, 이 책임보다
상위의 별도 Kernel Public Contract 확장 절차(별도 RFC → ADC → ADR)가
다룬다. **이 책임을 Kernel Public Contract(§14)로 승격하는 것은 결정 9
해소 이후에만 가능하다**(`ADC-0019` §Q7·§Decision 조건 5). Production
구현 착수는 결정 9 + `ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2
프로덕션 관찰 — `ADC-0021` §8 Gate (B)) + Reversibility 필수 불변조건의
v2 완전 검증(위 "부분 충족(E4)" 문단, `ADC-0021` §8 Gate (C)) +
`hqs/development/IMPLEMENTATION_RULES.md`로 **계속 차단된다** — 결정
2·5·11의 해소는 이 중 어느 것도 해제하지 않는다. `ADC-0021` §8 Gate
(A)는 이 반영 이후 **"부분 해소(결정 2·5·11 Resolved / 결정 9 pending)"**로
읽힌다.
```

#### 2.7 "Production 구현과의 관계" 문단 참조번호 정정

기존(마지막 문장):

```markdown
... v1 `ADR-0007` 결정 2/5/9/11 공백 해소와 Reversibility의 v2 재현
검증 이후, 별도 ADR이 A-IN 범위에 한해 그 금지의 Scoped 해제 여부를
판단한다(`ADC-0019` §Next Step 2·5).
```

교체 후(참조번호만 정정 — 나머지 문장·문단은 문자 그대로 유지):

```markdown
... v1 `ADR-0007` 결정 9 공백 해소(결정 2·5·11은 `ADC-0022`로 해소됨)와
`ADC-0021` §8 Gate (B)·(C) 충족 및 Reversibility의 v2 완전 검증 이후,
별도 ADR이 A-IN 범위에 한해 그 금지의 Scoped 해제 여부를 판단한다
(`ADC-0019` §Next Step 2·5).
```

> §2.7은 §2.6이 문단 #9에서 확정한 상태(결정 2·5·11 Resolved / 결정 9
> pending)를 문단 #15에도 정합하게 만드는 **참조 정정**이다. 새
> Architecture Decision이 아니며, Scoped 해제 차단의 실질(결정 9 + Gate
> (B)·(C) + `IMPLEMENTATION_RULES.md`)은 그대로다.

### 3. (c)의 처리 — 배치만 반영

`ADC-0020` §Q-D는 (c)를 Defer했고, `ADR-0009` §3은 "(c)의 (i) 계약화
여부, (ii) 배치, (iii) HQ State 설계 구속 여부는 … 후속 Implementation
Strategy ADC 또는 별도 Governance 단계가 v1 `ADR-0007` 결정 11과 결합해
판정한다"고 넘겼다. `ADC-0022` §D-11c가 그 "결정 11이 다뤄질 때"에
해당하며, **(ii) 배치**만 "HQ State 스키마 설계 책임"으로 판정했다. 이
ADR은 그 판정만 §16.6 기존 (c) 문단에 **부기**한다(§2.5):

- (c)는 여전히 Adapter Contract 부속 명세로 **정식화되지 않는다** — (c)
  bullet을 (a)(b)(d)와 나란히 만들지 않는다.
- (c)의 **계약화 여부**와 **HQ 설계 구속 강화**는 `ADC-0020` §Q-D
  Defer·`ADR-0009` §3 상태 그대로다.
- §16.6 본문의 (c) 문단은 여전히 "이 절은 (c)에 어떤 규범 효력도
  부여하지 않는다"를 유지하며, 부기 문장은 배치 서술과 "규범 효력 없는
  hazard + 배치 원칙으로만 남는다"를 명시한다.
- (c)는 **독립 Decision이 아니다** — `ADC-0022` §D-11의 하위 조건으로만
  다뤄진다.

### 4. `BASELINE.md` §6 Concept Model 표 갱신 여부

**추가·수정하지 않는다.** `ADR-0009` §Decision 4가 "Workflow Adapter"에
대해 내린 판단("§6 Concept Model은 Jarvis OS 전체 수준의 넓은 어휘
기준선이고, Kernel Module(§16) 내부 책임·용어는 §6에 등재하지 않는다")이
"실행 단위(Execution Unit)"에도 그대로 적용된다.

- "실행 단위"는 §16 Kernel Module 내부의 입력 경계 설명 용어다 — §6에
  추가하면 이 선례와 어긋나고, §6의 "Process"("Task")·"Service"("Runtime")
  항목과의 관계를 §6 스스로 설명해야 하는 부담이 생긴다. 그 관계는 §16.6
  본문 "실행 단위(Execution Unit)" 문단(§2.1)이 명시한다.
- §6의 어떤 행도 이 ADR로 수정·삭제·추가되지 않는다.

### 5. `docs/00_governance/GLOSSARY.md` 갱신 내용

"Kernel Modules — Workflow Adapter (Reference)" 절만 변경한다. "Concept
Model 용어" 절(§6 미러링)은 무변경.

#### 5.1 표에 "실행 단위 (Execution Unit)" 행 추가

"Adapter Contract" 행 **뒤**에 다음 행을 잇는다:

```markdown
| 실행 단위 (Execution Unit) | `BASELINE.md` §16.6 A-IN이 입력으로 받는 "이미 구성된 실행 단위" — HQ가 구성한 "무엇을·어떤 순서·병렬성으로·어느 Agent가 수행하는가"의 묶음. Kernel은 그 내부 구조·생명주기·조직적 출처(Division/Team 유무)를 정의하지 않는다(`docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` §D-0). §16.3·§16.4·§16.6이 공유하는 용어이며 §6 Concept Model에 등재되지 않는다 |
```

#### 5.2 주석 블록의 결정 참조번호 정정 (2곳)

기존 주석 블록(`>` 인용) 중 두 문장을 정정한다.

기존 ①:

```markdown
> 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 2/5/9/11이 미해결인 동안 §14 승격·Production 구현
> 착수는 불가하다.
```

정정 후 ①:

```markdown
> 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 9(및 `ADC-0021` §8 Gate (B)·(C))가 미해결인 동안 §14
> 승격·Production 구현 착수는 불가하다 — v1 `ADR-0007` 결정 2·5·11은
> `ADC-0022`로 해소됐다.
```

기존 ②(`ADR-0010`이 덧붙인 문장):

```markdown
> ... `ADC-0019` 재검토 조건 (c)와 v1
> `ADR-0007` 결정 2/5/9/11은 그대로 미충족이다
> (`docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

정정 후 ②(번호만 정정 + 해소 사실 부기 — Gate (C) "부분 충족" 문구·상태는
불변):

```markdown
> ... `ADC-0019` 재검토 조건 (c)와 v1
> `ADR-0007` 결정 9는 그대로 미충족이다(결정 2·5·11은 `ADC-0022`로
> 해소; `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

표의 "Workflow Adapter"·"Adapter Contract" 행, 주석 블록의 나머지 문장,
"Concept Model 용어" 절은 무변경.

### 6. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADR-0009` §6·`ADR-0010` §4와 동일 판단 — 이 ADR은
결정 2·5·11의 v2 재정의(경계 서술)만 반영하며 구현 착수를 허용하지
않는다.

- `ADC-0019` §Decision 조건 5가 여전히 Production 구현 착수를 금지한다 —
  이번 반영은 결정 2·5·11만 해소하며, 결정 9·Gate (B)·Gate (C)는 미해소
  hard gate로 남는다.
- `IMPLEMENTATION_RULES.md` line 9/13/14/19(Workflow Parser / Scheduler·
  우선순위·Workflow orchestration·Dynamic Routing·§6 넓은 Runtime /
  Stage 재진입·조건부 Stage / Event Bus 구현 금지)는 전면 **유지**된다.

### 7. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.14 | **v1.15** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 `RFC-0021` → `ADC-0022` → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0010`의 선례와 동일하다.

**Minor 증가(v1.15) 근거**: 신설 최상위·하위 절이 없다. 기존 §16.6 절
내부에 문단 3개를 신설하고, 같은 절의 문단 2곳에 문장을 부기하고, 문단
1개를 재작성하며, 문단 1개의 참조번호를 정정할 뿐이다(§16.1~§16.5·§16.7·
§6 Concept Model 표·§14·§15.2 무변경, `IMPLEMENTATION_RULES.md` 무변경).
선행 `ADR-0004`(명칭 반영, v1.8)·`ADR-0009`(부속 명세, v1.13)·`ADR-0010`
(Gate (C) 부분 충족, v1.14)와 같은 granularity로 Minor 단위로 기록한다.
`ADC-0022` §8-8이 예상한 폭(v1.15, Minor)과 일치한다.

### 8. Migration Strategy

> 아래 1~4는 Architecture/Governance Review PASS + 사용자 승인(2026-09-04)
> 이후 **실행되었다**(Status: Accepted). 5(커밋)는 그 이후 별도로
> 진행한다 — 이 시점까지 Commit/PR/Merge는 없다.

1. `docs/architecture/baseline/BASELINE.md`:
   - §16.6 A-IN 문단 뒤에 §2.1 "실행 단위(Execution Unit)" 문단, 이어서
     §2.4 "A-IN(a) 공유 State가 담는 정보" 문단을 그 순서로 삽입한다.
   - §16.6 A-IN 문단을 §2.3대로 교체한다(문장 추가).
   - §16.6 A-OUT 문단 뒤에 §2.2 "실행 단위 Lifecycle" 문단을 삽입한다
     ("§16.3~16.5와의 경계" 문단 앞).
   - §16.6 기존 (c) 문단을 §2.5대로 교체한다(문장 부기).
   - §16.6 "미해결 상태로 유지되는 v2 공백" 문단을 §2.6대로 교체한다.
   - §16.6 "Production 구현과의 관계" 문단의 마지막 문장을 §2.7대로
     교체한다.
   - §16.6의 다른 모든 문단(책임·근거·§16.3~16.5 경계·Checkpoint 용어
     구분·Reversibility 필수 불변조건·Reversibility v2 부분 충족(E4)·
     Workflow Module Defer 구분·명칭·Adapter Contract (a)(b)(d) bullet·
     이 Accept가 결정하지 않는 것)과 §1~§15·§16.1~§16.5·§16.7·§6·§14·
     §15.2는 문자 그대로 유지한다.
   - §17 Version을 v1.14 → v1.15로 바꾸고 변경 이력 맨 위에 다음 한
     줄을 추가한다:

     > `| v1.15 | §16.6에 Gate (A) 결정 2·5·11 Resolution 반영(`ADC-0022`) — "실행 단위(Execution Unit)"를 §16.6 A-IN 입력 경계 설명 용어로 명시(§6 Concept Model 미등재, 새 Kernel Domain·Layer·Component 아님, D-0). D-2: Adapter 개입 구간에 소비할 Kernel 소유 실행 단위 생명주기 전이 부재 + HQ Lifecycle State(§6/§7) 2층 분리 무변경 + A-OUT 금지의 긍정형 조건형 불변조건("현재 트리거 없음"). D-5: 결정 5 = §16.6 A-IN/A-OUT+§7로 대체, 입력은 HQ 내부 조직 구조 비의존(확인용 서술 — 새 입력 계약 의무 아님, 구체 시그니처는 §14.1 트랙). D-11: Kernel `WorkflowStatus` enum·`WorkflowResult` 타입 미도입, A-IN(a) State가 담는 정보를 진행 정보/종료 disposition으로 **서술**(종료 disposition 내용·어휘 = HQ 도메인, Kernel은 축의 존재를 요구하지 않음). D-11c: (c) 병렬 State 동시 쓰기 규약의 **배치 = HQ State 스키마** — 계약화 여부·HQ 구속 강화는 ADC-0020 §Q-D·ADR-0009 §3 그대로, 규범 효력 없음, 독립 Decision 아님. **결정 9(`IWorkflowEngine` Port/결과 반환 타입/시그니처)는 §14.1 "Task 전달 책임" 트랙 pending — Gate (A) 부분 해소.** Gate (B)(재검토 조건 (c))·Gate (C)(Reversibility 완전 검증)·§14 승격·`IMPLEMENTATION_RULES.md` line 9/13/14/19 차단 유지. §5·§6·§7·§14·§16.1~§16.5·§16.7·§6 Concept Model 표·Adapter Contract (a)(b)(d) 문언·Reversibility 2문단 무변경. `GLOSSARY.md` "Workflow Adapter (Reference)" 절에 "실행 단위" 행 추가 + 결정 참조번호(2/5/9/11 → 9) 정정. 근거: `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md` |`

2. `docs/00_governance/GLOSSARY.md` — §5.1의 "실행 단위 (Execution
   Unit)" 행을 "Adapter Contract" 행 뒤에 추가하고, §5.2의 두 문장
   정정을 반영한다. 표의 다른 행·"Concept Model 용어" 절은 무변경.

3. `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
   `docs/architecture/core/ADC-0008`, `docs/architecture/core/ADC-0021`,
   `core/`·`hqs/`·`dashboard/`·`docs/research/` — 변경하지 않는다.

4. 검증:
   - `BASELINE.md` 최상위 절 번호가 §1~§17로 유지되는지(신설 절 없음,
     §16.6 번호 유지).
   - §16.6의 §2.1·§2.2·§2.4 신설 문단, §2.3·§2.5 부기, §2.6 재작성,
     §2.7 참조 정정 외의 모든 문단, 그리고 §16.1~§16.5·§16.7·§6·§14·
     §15.2가 문자 그대로인지(`git diff`가 `BASELINE.md` §16.6·§17 +
     `GLOSSARY.md` 1절 + 이 ADR 파일에만 국한).
   - §16.6 "Reversibility — 필수 Architecture 불변조건" 문단과
     "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단이 verbatim.
   - Adapter Contract (a)(b)(d) bullet과 그 도입부 문단이 verbatim,
     특히 (d)의 "그 통합 테스트의 **실행**은 이 반영의 결과가 아니다"
     문장이 verbatim.
   - §16.6 "명칭" 문단이 verbatim.
   - 신설·부기·재작성 문단에 "Port" / "Public" / "Guarantee" / "Interface"
     어휘가 없고, §14에 추가된 항목이 없는지.
   - §2.4 신설 문단에 "MUST" / "요구한다" / "강제한다" / "축을 정의한다"
     류의 규범 표현이 없고 enum·타입이 도입되지 않았는지("요구하지
     않는다"의 부정형은 허용).
   - (c) 규약이 §16.6에 규범 문언(계약 절)으로 들어가지 않았고 (c)
     bullet이 (a)(b)(d)와 나란히 만들어지지 않았는지 — 배치 서술만.
   - §2.6 재작성 문단에 결정 9의 §14.1 원인 서술과 Gate (B)·(C) "계속
     차단"이 명문으로 남아 있는지.
   - `GLOSSARY.md`의 "Workflow Adapter"·"Adapter Contract" 표 행,
     "Concept Model 용어" 절이 문자 그대로인지.
   - `IMPLEMENTATION_RULES.md`가 `git diff` 0줄인지.
   - `docs/architecture/core/ADC-0021`이 `git diff` 0줄인지.
   - `git status`로 `core/`·`hqs/`·`dashboard/`·`docs/decisions/`가
     무변경인지.

5. 커밋 — 이 ADR과 위 `BASELINE.md`·`GLOSSARY.md` 변경을 함께 커밋한다
   (승인 이후).

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.14 → v1.15가 되고, §16.6이
  전제하던 "이미 구성된 실행 단위"·그 Lifecycle·그 실행의 State Model이
  Team/Division 없는 v2 위에서 어떻게 성립하는지가 §16.6 본문에 서술된다.
  이는 새 책임·범위 추가가 아니라 기존 A-IN/A-OUT이 전제·함의한 것의
  경계 서술이다.
- **결정 2·5·11이 Resolved**로 기록된다: (2) Adapter가 소비할 Kernel 소유
  실행 단위 생명주기는 없고 A-OUT 금지가 긍정형으로 재기술되며, (5) 결정
  5는 §16.6 A-IN/A-OUT + §7로 대체되고 입력이 HQ 내부 조직 구조에
  비의존임이 확인되고, (11) Kernel은 `WorkflowStatus`/`WorkflowResult`를
  도입하지 않고 종료 disposition의 내용·어휘는 HQ 도메인 책임임이
  서술된다.
- **(c)의 배치**가 "HQ State 스키마 설계 책임"으로 §16.6 (c) 문단에
  부기된다 — (c)는 여전히 Adapter Contract 절이 아니고 규범 효력이 없다.
- **결정 9는 미해결로 남는다** — §16.6 "v2 공백의 현재 상태" 문단이 결정
  9를 §14.1 "Task 전달 책임" 트랙 pending으로 명시하고, §14 승격·Production
  구현 착수 차단이 결정 9 + Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md`로
  유지됨을 재확인한다.
- `ADC-0021` §8 **Gate (A)의 상태가 "부분 해소(결정 2·5·11 Resolved /
  결정 9 pending)"로 읽힌다** — `ADC-0021` 원문은 수정되지 않으며,
  BASELINE §16.6의 cross-reference가 그 상태를 반영한다.
- `docs/00_governance/GLOSSARY.md`에 "실행 단위 (Execution Unit)" 용어가
  추가되고, "Workflow Adapter (Reference)" 절 주석의 결정 참조번호가
  결정 9 기준으로 정정된다. 표의 Workflow Adapter·Adapter Contract 행,
  "Concept Model 용어" 절은 무변경.
- `hqs/development/IMPLEMENTATION_RULES.md`는 **무변경**이다 — 결정 9·Gate
  (B)·Gate (C)가 미해소이므로 Scoped 해제할 대상이 없다. line 9/13/14/19
  전면 유지.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface·Port·
  Guarantee를 정의하지 않았다. §14.1의 "Task 전달 책임" 미결 상태
  그대로다.
- §16.6 "Reversibility — 필수 Architecture 불변조건" 문단, "Reversibility
  v2 통합 테스트 재현 — 부분 충족 (E4)" 문단, Adapter Contract (a)(b)(d)
  bullet은 **문자 그대로 유지**된다 — Gate (C)·Adapter Contract는 이
  ADR의 범위 밖이다.
- Rule B는 여전히 미충족이다(`ADC-0019` §Q2, 재검토 조건 (c) = Gate
  (B)). 이 반영은 §14 승격·Implementation Strategy·`IMPLEMENTATION_RULES.md`
  Scoped 해제·(c) 계약화의 hard gate를 약화하지 않는다.
- 이 ADR은 **Accepted** 상태다. Architecture/Governance Review PASS +
  사용자 승인(2026-09-04) 이후 §Migration Strategy 1~4를 실행했다 —
  `BASELINE.md` v1.15(§16.6 문단 신설·부기·재작성 + §17), `GLOSSARY.md`
  "Workflow Adapter (Reference)" 절("실행 단위" 행 + 참조번호 정정).
  `IMPLEMENTATION_RULES.md`·§14·§16.6 Reversibility 2문단·Adapter
  Contract (a)(b)(d) bullet·§16.1~§16.5·§16.7·§6 Concept Model 표·
  `docs/decisions/adc/ADC.md`·`ADC-0008`·`ADC-0021`은 무변경. 커밋은
  별도로 진행한다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(제한적 — 기존 경계의 서술 확정)** — §16.6이
  가리키는 책임의 범위(A-IN/A-OUT)는 전혀 바뀌지 않는다. "이미 구성된
  실행 단위"라는 전제 입력이 v2에서 무엇인지(설명 용어), 그 Lifecycle을
  Adapter가 소비하지 않는다는 것, 그 실행의 State가 진행/종료 disposition
  정보를 담고 후자의 내용이 HQ 도메인이라는 것이 서술된다. Component
  설계(§10 Out of Scope)에는 영향이 없다 — Interface·구현 전략·Public
  Port는 여전히 미정이다.
- **Contract Impact**: **없음** — 공개 Interface·Public Port·Guarantee를
  정의하지 않았다. Kernel Public Contract(§14)는 무변경. Adapter Contract
  부속 명세 (a)(b)(d) 문언은 verbatim 유지. (c)는 배치 서술만 부기되고
  계약 절이 되지 않는다. §14.1 "Task 전달 책임" 미결 상태가 이 책임의
  §14 승격을 계속 막는다(결정 9).
- **Kernel Impact**: **없음(경계·상태 기록)** — 새 Kernel Concept·Layer·
  Component·enum·타입이 추가되지 않는다. Kernel이 아는 생명주기는 여전히
  HQ Lifecycle뿐이다(§6). "실행 단위"는 §16.6 본문 설명 용어이며 §6
  Concept Model에 등재되지 않는다.

## Governance Chain 검증

`RFC-0021`(Proposed — B-2·B-5·B-11 Boundary Question 개설, 판단은
`ADC-0022`에 위임) → `ADC-0022`(Decided — Architecture/Governance Review
PASS §9; D-0 설명 용어, D-2/D-5/D-11 Resolved, D-11c 배치, D-9 별도
트랙, D-Gate-A 부분 해소) → 이 ADR(Accepted — `ADC-0022` §8 지침 중
D-0·D-2·D-5·D-11·D-11c·D-Gate-A를 `BASELINE.md` §16.6·§17·`GLOSSARY.md`에
반영, 새 결정 없음).

- `RFC-0021`은 Boundary Question만 열고 `ADC-0022`에 위임했다 — 위반 없음.
- `ADC-0022`는 `RFC-0021` §4 "가능한 해소 형태"를 자동 채택하지 않고 §5
  D-2/D-5/D-11로 독립 판정했으며(§4.1~§4.6), 결정 9·§14 승격·Gate
  (B)·(C)·(c) 계약화·LangGraph 채택·`IMPLEMENTATION_RULES.md` 해제를
  범위 밖으로 명시했다(`ADC-0022` §1.2·§7) — 위반 없음.
- 이 ADR은 `ADC-0022` §5 Decision과 §8 지침만 Baseline 문서 변경으로
  옮겼을 뿐, `ADC-0022`가 Out of Scope로 둔 것(결정 9, §14 승격, Gate
  (B)·(C), Adapter Contract (a)(b)(d) 재정의, (c) 계약화·HQ 구속, R11-b
  규범 축, LangGraph 채택, `IMPLEMENTATION_RULES.md` 해제, §6 표 등재)을
  새로 결정하지 않았다(§Out of Scope·§3·§4·§6) — 위반 없음.
- `ADC-0019` §Decision 조건 1~6, Rule B 미충족(재검토 조건 (c) = Gate
  (B)), `ADC-0021` §D1~D4·§6~§8, `ADR-0010` "부분 충족"이 §Out of
  Scope·§Consequences에 그대로 재확인됨을 확인했다 — `ADC-0022` §6
  Conditions와 일치.
- §16.6에 추가·부기·재작성되는 문단이 §16.3~16.5·§14·§14.1의 문장을
  인용은 하되 수정·재정의하지 않음을 §2가 명시하고 §8 검증 절차가
  확인하도록 했다 — 충돌 없음.
- 잔여 정합성 정정 2건(§16.6 "Production 구현과의 관계" 참조번호,
  `GLOSSARY.md` 주석 참조번호)은 §2.6이 확정한 상태를 다른 위치에도
  정합하게 만드는 것이며 새 Architecture Decision이 아니다(§2.7 주석,
  §5.2) — `ADC-0022` §4.3 잔여 판단 옵션 A에 부합.

## Self Review

- `ADC-0022`가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of Scope에
  명시한 항목(결정 9 / §14.1 / §14 승격 / Gate (B) / Gate (C) / Adapter
  Contract (a)(b)(d) 재정의 / (c) 계약화·HQ 구속 / R11-b 규범 축 /
  LangGraph 채택 / `IMPLEMENTATION_RULES.md` 해제 / §6 표 등재 / H1
  제목줄 / `ADC-0021` 원문)은 손대지 않았다.
- 결정 2·5·11의 Resolution만 공식화했는가 — **예**(§2.1~§2.6, §Decision).
  결정 9는 §2.6에서 "§14.1 트랙 pending"으로 명시 분리했다.
- "실행 단위(Execution Unit)"를 새 Kernel Domain으로 만들었는가 —
  **아니오**(§2.1·§4) — §16.6 본문 설명 용어, §6 미등재, "새 Kernel
  Domain·Layer·Component 아님 / §16.7 Workflow Kernel Module 아님" 명문화.
- R11-a의 종료 disposition을 Kernel 규범 축으로 정의했는가 —
  **아니오**(§2.4) — "기술된다/서술이다" 어휘, "Kernel은 … 요구하지
  않는다" 명문, `WorkflowStatus` enum·`WorkflowResult` 타입 미도입.
  내용·어휘 = HQ 도메인 책임.
- (c)를 독립 Decision·Adapter Contract 절로 만들었는가 —
  **아니오**(§2.5·§3) — 기존 (c) 문단에 배치 서술만 부기, "규범 효력
  없는 hazard + 배치 원칙으로만", 계약화·HQ 구속은 `ADC-0020`/`ADR-0009`
  상태 유지.
- Gate (A) 상태를 정확히 반영했는가 — **예**(§2.6) — "결정 2·5·11
  Resolved / 결정 9 pending", §14 승격은 결정 9 이후, Gate (B)·(C) "계속
  차단" 명문.
- 결정 9 / Gate (B) / Gate (C)의 상태를 바꾸거나 약화했는가 —
  **아니오**(§Out of Scope·§2.6·§Consequences) — 결정 9 §14.1 원인 서술
  유지, Gate (B)·(C)는 §16.6 Reversibility 2문단 verbatim + "계속 차단"
  재확인.
- §14 / Public Port / Guarantee를 신설·우회했는가 — **아니오**(§2·§8
  검증) — "Port/Public/Guarantee/Interface" 어휘 불사용, §14 항목 추가
  없음.
- `BASELINE.md` §16.1~§16.5·§16.7·§6 Concept Model 표·§14·§15.2,
  §16.6의 Reversibility 2문단·Adapter Contract (a)(b)(d) bullet·명칭
  문단을 수정했는가 — **아니오**(§2·§4·§8 검증 절차).
- `hqs/development/IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  `ADC-0008`·`ADC-0021`을 변경했는가 — **아니오**(§1·§6·§8).
- Rule B 충족을 선언했는가 — **아니오**(§Consequences) — 미충족·재검토
  조건 (c)(Gate (B)) 유지.
- 새 최상위·하위 절을 신설했는가 — **아니오**(§7) — §16.6 내부 문단
  추가/부기/재작성만, §16.6 번호 유지.
- `BASELINE.md` / `GLOSSARY.md`를 실제로 수정했는가 — **예(승인 반영)** —
  Review PASS + 사용자 승인(2026-09-04) 이후 §Migration Strategy 1~4를
  실행했다: `BASELINE.md` §16.6 문단 신설(3)·부기(2)·재작성(1)·참조 정정(1)
  + §17 v1.15, `GLOSSARY.md` "실행 단위" 행 + 참조번호 정정 2곳.
  §16.6 Reversibility 2문단·Adapter Contract (a)(b)(d) bullet·명칭
  문단·§16.1~§16.5·§16.7·§6·§14·§15.2·`IMPLEMENTATION_RULES.md`·
  `ADC-0021`은 무변경. 커밋은 별도.
- Production Code를 변경했는가 — **아니오**.
- 반영 과정에서 `ADC-0022`가 이미 인지한 것 이상의 새 Architecture 결정
  지점이 나타났는가 — **아니오**. 잔여 정합성 정정 2건은 `ADC-0022`
  §4.3 옵션 A로 이미 예고됐고, 새 결정이 아니라 참조 정합화다.
