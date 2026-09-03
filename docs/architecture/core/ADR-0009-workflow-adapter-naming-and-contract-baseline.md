# ADR-0009: Workflow Adapter 명명 + Adapter Contract 부속 명세((a)(b)(d))의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0009` (`docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md`와 다른 문서 — 네임스페이스로 구분) |
| 제목 | `ADC-0020`의 Decision(§16.6 책임의 명칭 = **Workflow Adapter**, Adapter Contract 부속 명세 (a)(b)(d)의 정식화)을 Architecture Baseline·GLOSSARY에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** — Architecture/Governance Review PASS 이후, §Decision·§Migration Strategy가 정의하는 `BASELINE.md` 변경(§16.6에 **명칭**·**Adapter Contract 부속 명세((a)(b)(d))** 문단 추가, "이 Accept가 결정하지 않는 것" 문단 정정, §17 Version v1.12 → v1.13)과 `GLOSSARY.md` 변경("Kernel Modules — Workflow Adapter (Reference)" 절 신설)이 반영되었다. `IMPLEMENTATION_RULES.md`·§6 Concept Model 표·§14·§16.1~§16.5·§16.7·`docs/decisions/adc/ADC.md`·`ADC-0008`은 무변경. Commit/PR/Merge는 별도로 진행한다 |
| Context | `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` — **Status: Decided — ADR Required**. Q-B Accept(명칭 "Workflow Adapter"), Q-C Accept·Modify(3계층 분리), Q-D (a)(b)(d) Accept·(c) Defer, Q-E-1 Accept(C1)·Q-E-2 Defer, Q-F Accept(진행 가부) |
| 관련 RFC | `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md` §5(Proposal)·§8.1(Q-A~Q-F) |
| 관련 ADC | `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` |
| 선행 ADR | `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md`(§16.6 **존재** 등재 — 이 ADR이 이름을 붙이는 대상), `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`(명칭만 Baseline·GLOSSARY에 반영하고 §6·`IMPLEMENTATION_RULES.md`는 건드리지 않은 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0013`→`ADC-0014`→`ADC-0015`(Execution Host 존재→명명→구현 전략 3단계 분리), `ADC-0019`(§16.6 Accept, Scoped·Conditional), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW), `docs/architecture/core/ADC-0008`(Not Accepted) — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 `ADC-0020`이 이미 내린 Decision을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. 그 Decision 중 **명칭 부여**와
**Adapter Contract 부속 명세 (a)(b)(d)** 두 가지를 실제 Baseline·GLOSSARY
문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

| 단계 | 다루는 것 |
|---|---|
| `RFC-0020` | Workflow Adapter 명칭·Adapter Contract 후보 절 (a)~(d)·Checkpoint 입도·Open Questions(Q-A~Q-F) 제기 — 결정하지 않음 |
| `ADC-0020` | Q-A(번들링 허용) → Q-B(명칭 Accept) / Q-C(3계층 분리) / Q-D((a)(b)(d) Accept, **(c) Defer**) / Q-E-1(C1) · Q-E-2(Defer) / Q-F(Rule B 미충족 상태에서 진행 가부) |
| **이 ADR** | `ADC-0020` §8 지침 중 **명칭 + (a)(b)(d)**의 Baseline Governance 반영 — §16.6 본문 갱신, `GLOSSARY.md` 절 신설, v1.12 → v1.13 |
| 후속 별도 결정 | (c) hazard의 계약화·배치·HQ 구속, Checkpoint 입도 C1의 문언화, phase 경계 선언 주체, "Sequential = Reference", LangGraph 채택, 구현 전략, Conformance Test, §14 승격, `IMPLEMENTATION_RULES.md` Scoped 해제 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0020`이 Decision 범위에서 반영을 지시하지 않은 것은 **하나도 반영하지
않는다**(`ADC-0020` §7·§8).

| 항목 | 근거 |
|---|---|
| **(c) 병렬 State 동시 쓰기(disjoint key / reducer)의 계약화·배치·HQ State 설계 구속** | `ADC-0020` §Q-D (c) **Defer**·§8-4 — 후속 ADR에 반영하지 않는다. E3 PoC가 실측한 parallel State write hazard로만 존재하며, v1 `ADR-0007` 결정 11(State Model)이 다뤄질 때 후속 Implementation Strategy ADC 또는 별도 Governance 단계가 결합 판정 |
| Checkpoint 입도 C1(phase-boundary caller-owned)의 Baseline 문언화 | `ADC-0020` §Q-E-1이 C1을 결정했으나 §8·§11의 "후속 ADR 반영 사항"에서 제외 — C1의 Baseline 반영(필요 시)은 Implementation Strategy 트랙 |
| phase 경계 선언 주체(HQ Workflow 정의 vs Adapter Contract) | `ADC-0020` §Q-E-2 **Defer** — Investment/Development HQ 관점 입력 필요 |
| "Sequential = Reference Implementation" 지정 및 Reference의 실체 | `ADC-0020` §Q-B "이 ADC의 범위 밖"·§12 #2 — Implementation Strategy ADC 소유 |
| LangGraph 최종 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 | `ADC-0020` §7, `ADC-0019` §Q8·§Decision 조건 6 |
| Conformance Test / (b) exception→state 강제·검증 메커니즘 / (d) v2 통합 테스트 **실행** | `ADC-0020` §7·§Q-D (b)(d) — Implementation Strategy 트랙 |
| §14 Kernel Public Contract 승격 / Public Port·Interface 정의 | `ADC-0019` §Q7·§Decision 조건 5, §14.1 "Task 전달 책임" 계약 범위 밖; `ADC-0020` §Q-C L3 |
| v1 `ADR-0007` 결정 2(Core 소유 Lifecycle)·5(Team/Division 경계)·9(`IWorkflowEngine` Port)·11(State Model)의 v2 재설계 | `ADC-0019` §Decision 조건 5 — 미해결로 유지 |
| `hqs/development/IMPLEMENTATION_RULES.md`의 Workflow Parser / Scheduler·우선순위·Workflow orchestration·Dynamic Routing / §6 넓은 Runtime / Stage 재진입·조건부 Stage / Event Bus 구현 금지 조항의 전면·Scoped 해제 | `ADC-0020` §6 조건 4 — `ADC-0015`류 부분 해제를 **하지 않는다** |
| `BASELINE.md` §6 Concept Model 표의 "Runtime"·"Adapter" 행 수정·삭제, "Workflow Adapter" 신규 행 추가 | `ADR-0004` §3과 동일 판단 — §6은 Jarvis OS 수준 넓은 어휘 기준선이고, Kernel Module(§16) 내부 책임은 §6에 등재하지 않는다(§Decision 4) |
| `BASELINE.md` §16.1~§16.5·§16.7 문언, §14, §15.2 | `ADC-0020` §6 조건 1·6·§7 — 참조만 하고 문자 그대로 유지 |
| `ADC-0019` §Decision 조건 1~6, Rule B 미충족(재검토 조건 (c)) | `ADC-0020` §6 조건 1·2·§Q-F — 무변경, hard gate 존속 |
| `docs/decisions/adc/ADC.md` ADC-02, `docs/architecture/core/ADC-0008`, §16.7 Workflow Kernel Module Defer(`ADC-0001` Module 2) | `ADC-0019` §Q8·`ADR-0008` §Out of Scope와 동일 — 별도 축, 별도 절차 |
| `BASELINE.md` H1 제목줄(현재 `v1.8` 표기)과 §17 Version 표의 불일치 정정 | `ADR-0008` §5와 동일 관행 — §17 표만 갱신, 제목줄은 이 ADR 범위 밖(별도 사항으로 남김) |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.6 절 제목에 "Workflow Adapter" 명칭을 접두하고(재배치·신설 절 없음), 본문에 **명칭** 문단과 **Adapter Contract 부속 명세((a)(b)(d))** 문단을 추가한다. 기존 "이 Accept가 결정하지 않는 것" 문단에서 명칭을 Open으로 서술하던 부분을 확정 서술로 교체한다. §17 Version을 v1.13으로 갱신하고 변경 이력 한 줄을 추가한다 |
| `docs/00_governance/GLOSSARY.md` | "Kernel Modules — Execution Host (Reference)" 절 뒤에 "Kernel Modules — Workflow Adapter (Reference)" 절을 신설한다. "Concept Model 용어" 절(§6 미러링, "Runtime"·"Adapter" 행 포함)은 무변경 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, Kernel Public Contract(§14), Production
Code는 이 ADR로 건드리지 않는다(§Out of Scope·§5·§6).

### 2. `BASELINE.md` §16.6 갱신 내용

`ADC-0020` §Q-B·§Q-C·§Q-D와 §8이 이미 정리한 것만 옮긴다. 새 판단을
만들지 않는다. §16.6의 기존 문단(책임·근거·A-IN·A-OUT·§16.3~16.5 경계·
Checkpoint 용어 구분·Reversibility·미해결 v2 공백·Workflow Module Defer
구분·Production 구현 관계)은 **문자 그대로 유지**한다.

#### 2.1 절 제목 교체

기존:

```markdown
### 16.6 Scoped Workflow Graph Execution — 조건부 분기·Loop·값 기반 Checkpoint/Resume (Accept, Scoped, Conditional)
```

교체 후(명칭 접두 + 뒤 서술을 괄호로 묶어 em-dash 1중 유지 — `ADR-0004`가
§16.3에 "Execution Host — "를 접두한 선례, `ADC-0020` §8-1 예시 형식과
동일):

```markdown
### 16.6 Workflow Adapter — Scoped Workflow Graph Execution (조건부 분기·Loop·값 기반 Checkpoint/Resume) (Accept, Scoped, Conditional)
```

#### 2.2 **명칭** 문단 신설

삽입 위치: "**Workflow Module Defer(§16.7)와의 구분**" 문단 **뒤**, "**이
Accept가 결정하지 않는 것**" 문단 **앞**(`ADR-0004`가 §16.3에서 "명칭"
문단을 "이 Accept가 결정하지 않는 것" 앞에 둔 배치와 동일).

```markdown
**명칭**: 이 책임의 공식 명칭은 **Workflow Adapter**다
(`docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md`
§Q-B). 이는 §16.6이 기술하는 책임 — 절 제목 "Scoped Workflow Graph
Execution"의 그 책임 — 에 붙는 이름이며, 절 제목은 위와 같이 "Workflow
Adapter —" 접두로 갱신된다(`ADR-0004`가 §16.3 제목에 "Execution Host —"를
접두한 선례와 동일). `RFC-0019` §3이 이미 이 책임을 "Workflow Adapter"로, §16.2 Model/LLM
Provider 호출 책임을 "Engine Adapter"로 구분해 온 비공식 용법을
공식화한 것이다 — 두 경계 모두 Execution Layer의 교체 가능한 seam이며,
"Adapter" 접미사는 이 저장소에서 이미 그 의미로 쓰인다. Workflow Adapter는
§16.2 Engine Adapter를 재명명하거나 흡수한 것이 아니라 그와 별개의
책임이다. v1 `archive/v1` `ADR-0007`의 `IWorkflowEngine` Port("Engine"
계보)가 함의하던 Core 소유 Lifecycle 소비는 v2 §5(Kernel이 Team/Division을
모른다)가 이미 폐기했으므로, 이 명칭은 "Engine" 프레이밍을 의도적으로
계승하지 않는다(`ADC-0019` G2, `ADC-0020` §Q-B). §6 Concept Model의
"Runtime"·"Adapter" 항목은 이 명칭 반영으로 변경되지 않으며, `docs/decisions/adc/ADC.md`
ADC-02(Runtime 존폐, Open)도 그대로다.
```

#### 2.3 **Adapter Contract — §16.6 A-IN 부속 명세** 문단 신설

삽입 위치: 위 **명칭** 문단 **뒤**, "**이 Accept가 결정하지 않는 것**"
문단 **앞**.

```markdown
**Adapter Contract — §16.6 A-IN 부속 명세 (구현체 내부 의무)**: 아래
(a)·(b)·(d)는 §16.6 A-IN이 이미 짊어진 의무를 계약 언어로 정련한 것이다
(`ADC-0020` §Q-C·§Q-D). **§16.6 A-IN의 부속 명세(sub-specification)이며,
그 위의 새 계층이 아니다.** 구현체 내부 의무를 서술할 뿐 Public Surface가
아니고, `RFC-0019` §7의 "개념 수준" 지위를 그대로 계승한다. 이 명세는
§14 Kernel Public Contract가 아니며 그 선행물도 아니다 — §14로 이어지는
자동 승격 경로는 없다(§14 승격은 위 "미해결 상태로 유지되는 v2 공백"
문단이 계속 차단한다). 이 명세에는 "Port" / "Public" / "Guarantee" / "Interface"
어휘를 쓰지 않으며, §14에는 어떤 항목도 추가되지 않는다.

- **(a) caller-owned Checkpoint 값 소유 모델**: 진행 상태(중간·최종)는
  직렬화 가능한 값으로 표현되고, 어댑터는 그 값을 **생산**만 하며
  영속화·복원을 소유하지 않는다(§15.2, §14.3 G-6, A-IN(e)의 재기술).
  재개 입도(어느 지점에서 이어서 진행하는가)는 이 절이 정하지 않는다.
- **(b) 실행 결과의 값 표현 — 어댑터 책임**: 어댑터 경계를 벗어나는 실행
  결과(성공/실패/취소에 준하는 상태)는 예외가 아닌 State 값이어야 한다
  (§14.3 G-6). 구현체가 단계(Node) 예외를 실행 경계 밖으로 전파하는 경우,
  그것을 catch-and-encode 하여 값으로 변환하는 것은 구현체의 보장이
  아니라 **어댑터의 책임**이다. "모든 Node에서 강제"의 강제·검증
  메커니즘(정적 분석 / Conformance Test)은 이 절이 확정하지 않는다 —
  이 절은 **의무의 소재**까지만 확정하며, 메커니즘은 후속 Implementation
  Strategy가 다룬다.
- **(d) Reversibility — 재확인 (신규 계약 아님)**: 어떤 구현체를 제거하고
  다른 구현체(최소한 순차 함수 호출)로 교체해도 Kernel·HQ가 정의하는
  코드는 한 줄도 수정되지 않는다. 이것은 **신규 계약이 아니라** 위
  "Reversibility — 필수 Architecture 불변조건" 문단의 재기술이며, 더하는
  것은 검증 방법이 v2 맥락의 통합 테스트임을 명문화하는 것뿐이다. 그
  통합 테스트의 **실행**은 이 반영의 결과가 아니다(후속 Implementation
  Strategy, `ADC-0019` §Next Step 4).

병렬 fan-out Node가 동일 State 키에 reducer 선언 없이 쓰는 경우의
동시 쓰기 규약("(c)")은 이 부속 명세에 **포함되지 않는다** —
`ADC-0020` §Q-D가 (c)를 정식화하지 않고 Defer했다(§3 근거). (c)는
문서화된 hazard로만 존재하며, 그 계약화·배치·HQ State 설계 구속 여부는
v1 `ADR-0007` 결정 11(State Model)이 다뤄질 때 후속 절차가 결합 판정한다.
이 절은 (c)에 어떤 규범 효력도 부여하지 않는다.
```

> 위 블록의 마지막 문단은 (c)를 **부속 명세로 정식화하지 않는다**는
> 경계 서술이다 — (c)의 규약 자체를 Baseline 문언으로 도입하지 않고,
> hazard의 존재만 적으며 규범 효력을 명시적으로 부인한다. `ADC-0020`
> §8-4("(c)는 후속 ADR에 반영하지 않는다")에 부합한다. 이 경계 서술을
> §16.6 본문에 두는 이유는 §Decision 3에 기록한다.

#### 2.4 "**이 Accept가 결정하지 않는 것**" 문단 교체

기존:

```markdown
**이 Accept가 결정하지 않는 것**: 구현체 선택(LangGraph 채택 여부 포함),
이 책임의 명칭(Workflow Adapter / Workflow Engine 등), Public Port 정의,
구현 전략은 모두 별도 절차(RFC → ADC → ADR)로 남는다 — Execution
Host가 존재(`ADC-0013`) → 명명(`ADC-0014`) → 구현 전략(`ADC-0015`)
3단계로 분리한 선례를 그대로 따른다. ...
```

교체 후(첫 문장에서 명칭 항목 제거, 확정 서술 한 문장 추가 — 나머지
문장은 문자 그대로 유지, `ADR-0004`가 §16.3의 동일 문단을 다듬은
방식과 동일):

```markdown
**이 Accept가 결정하지 않는 것**: 구현체 선택(LangGraph 채택 여부 포함),
Public Port 정의, 구현 전략은 모두 별도 절차(RFC → ADC → ADR)로 남는다 —
Execution Host가 존재(`ADC-0013`) → 명명(`ADC-0014`) → 구현
전략(`ADC-0015`) 3단계로 분리한 선례를 그대로 따른다. 이 책임의 **명칭**은
그 선례대로 별도 명명 절차(`ADC-0020` §Q-B)로 **Workflow Adapter**로
확정됐다(위 "명칭" 문단). `docs/decisions/adc/ADC.md` ADC-02(Runtime
존폐, Open·NOW)와 `docs/architecture/core/ADC-0008`(넓은 "유지 대 대체",
Not Accepted)은 이 Accept로 갱신·전복되지 않는다 — 이 책임은 §6
"Runtime" 정의 중 "조건부·반복 조율" 조각 하나일 뿐이다(`ADC-0019` §Q8).
```

### 3. (c)의 처리 — Baseline 미반영

`ADC-0020` §Q-D는 후보 절 (c)(병렬 State disjoint key / reducer 규약)를
**Defer**했고, §8-4는 "(c)는 후속 ADR에 반영하지 않는다"고 명시한다.
이 ADR은 그에 따른다:

- Adapter Contract 부속 명세로 정식화되는 집합은 **(a)(b)(d)에 한정**된다.
- §16.6 본문에는 (c) 규약이 규범 문언으로 들어가지 않는다. §2.3 마지막
  문단은 (c)를 **정식화하지 않는다는 경계 서술**일 뿐이며, hazard의
  존재만 기록하고 규범 효력을 명시적으로 부인한다.
- **이 경계 서술을 §16.6 본문에 두는 이유(확정)**: (a)(b)(d)만 나열하고
  (c)를 침묵으로 빼면, §16.6 독자는 (c)가 검토되어 Defer된 것인지
  애초에 논외였는지 그 자리에서 알 수 없다. 한 문단의 명시적 배제
  서술이 `ADC-0020` §Q-D Defer의 가시성을 높이고, 규범 효력 부인이
  명문이라 §8-4("반영하지 않는다")와도 충돌하지 않는다. (c)를 본문에서
  아예 언급하지 않는 축약안은 채택하지 않는다.
- (c)의 (i) 계약화 여부, (ii) 배치(§16.6 A-IN 부속 vs 별도 계층),
  (iii) HQ State 설계 구속 여부는 후속 Implementation Strategy ADC 또는
  별도 Governance 단계가 v1 `ADR-0007` 결정 11과 결합해 판정한다
  (`ADC-0020` §12 #1).

### 4. `BASELINE.md` §6 Concept Model 표 갱신 여부

**추가·수정하지 않는다.** `ADR-0004` §3이 Execution Host에 대해 내린
판단("§6 Concept Model은 Jarvis OS 전체 수준의 넓은 어휘 기준선이고,
§16.1~§16.2도 Accept된 Kernel Module이지만 §6 표에 별도 행으로
추가되지 않았다")이 Workflow Adapter에도 그대로 적용된다.

- Workflow Adapter는 §16 Kernel Module 내부의 좁은 책임 명칭이다 —
  §6에 추가하면 이 선례와 어긋나고, "Runtime"(넓은 정의)·"Adapter"(§6
  Concept Model의 Engine 구현체 의미)와의 관계를 §6 스스로 설명해야 하는
  부담이 생긴다. 그 관계는 §16.6 본문 **명칭** 문단에 이미 명시한다.
- §6의 "Adapter" 행("특정 Engine에 대한 구체 구현체")은 Engine Port
  계열의 어휘이며 Workflow Adapter와 별개다 — 이 ADR은 그 행을 손대지
  않는다. Workflow Adapter의 "Adapter" 접미사가 §6 "Adapter"와 다른
  층위임은 §16.6 본문이 구분한다(Execution Host가 §6 "Runtime"과
  공존한 것과 동일한 방식).

### 5. `docs/00_governance/GLOSSARY.md` 갱신 내용

"Kernel Modules — Execution Host (Reference)" 절과 "핵심 원칙 (Reference)"
절 사이에 새 절을 삽입한다("Concept Model 용어" 절은 §6 미러링이므로
무변경).

```markdown
## Kernel Modules — Workflow Adapter (Reference)

상세 정의는 `docs/architecture/baseline/BASELINE.md` §16.6 참조.

| 용어 | 정의 |
|---|---|
| Workflow Adapter | HQ가 정의한 고정 Workflow 그래프의 실행 진행(State 보유·Node 진행·조건부 분기·Loop·값 기반 Checkpoint/Resume — §16.6 A-IN 5항목)을 담당하는 책임의 공식 명칭. §16.2 **Engine Adapter**(Model/LLM Provider 호출)와는 별개의 책임이며 그것을 재명명·흡수한 것이 아니다(`docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` §Q-B). v1 `archive/v1` `ADR-0007`의 `IWorkflowEngine` Port("Engine" 계보)를 계승하지 않는다 — "Engine" 프레이밍이 함의하던 Core 소유 Lifecycle 소비를 v2가 폐기했기 때문이다(`ADC-0019` G2) |
| Adapter Contract | Workflow Adapter 구현체가 지켜야 할 **내부 의무**를 §16.6 A-IN의 부속 명세로 정련한 것 — (a) caller-owned Checkpoint 값 소유, (b) 실행 결과의 값 표현 = 어댑터 책임, (d) Reversibility 재확인. Public Surface가 아니고 §14 Kernel Public Contract가 아니며 그 선행물도 아니다 — §14 자동 승격 경로 없음(`ADC-0020` §Q-C). 병렬 State 동시 쓰기 규약("(c)")은 이 명세에서 Defer됨(`ADC-0020` §Q-D) |

> Workflow Adapter는 §6 Concept Model 표에 등재되지 않는다 — Execution
> Host(§16.3)와 같은 Kernel Module(§16) 수준의 좁은 책임이다
> (`docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md`
> §Decision 4). Reversibility는 이 책임의 필수 Architecture 불변조건이며,
> 어떤 구현체(LangGraph 포함)를 제거·교체해도 Kernel·HQ 코드는 수정되지
> 않는다. 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 2/5/9/11이 미해결인 동안 §14 승격·Production 구현
> 착수는 불가하다. `hqs/development/IMPLEMENTATION_RULES.md`의 Workflow/
> Scheduler/Runtime/Event Bus 구현 금지는 그대로 유효하다.
```

### 6. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADC-0020` §6 조건 4는 "이 ADC는 `ADC-0015`류 부분
해제를 하지 않는다"고 명시한다. `ADR-0004`(Execution Host 명칭 반영)가
"명칭 결정만으로는 `IMPLEMENTATION_RULES.md`를 해제하지 않는다"고 판단한
선례와 동일하다 — 이 ADR은 명칭과 기존 §16.6 의무의 재기술만 반영하며,
구현 착수를 허용하지 않는다.

- `ADC-0019` §Decision 조건 5가 여전히 Production 구현 착수를 금지한다 —
  v1 `ADR-0007` 결정 2/5/9/11의 v2 공백 해소 + Reversibility v2 통합
  테스트 재현 검증 전까지. 지금 Scoped 해제할 대상이 없다.
- `IMPLEMENTATION_RULES.md` line 9/13/14/19(Workflow Parser / Scheduler·
  우선순위·Workflow orchestration·Dynamic Routing·§6 넓은 Runtime /
  Stage 재진입·조건부 Stage / Event Bus 구현 금지)는 `ADC-0019` A-IN의
  실제 구현을 직접 덮으며 전면 **유지**된다. 명칭·부속 명세 반영과
  구현 금지는 공존한다(`ADR-0008` §4·`ADR-0003` §16.3 선례).

### 7. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.12 | **v1.13** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 `RFC-0020` → `ADC-0020` → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0008`의 선례와 동일하다.

**Minor 증가(v1.13)를 택한 이유**: 신설 최상위·하위 절이 없다. 기존
§16.6 절 내부에 **명칭** 문단과 **Adapter Contract 부속 명세** 문단을
추가하고, 같은 절의 "이 Accept가 결정하지 않는 것" 문단 한 곳을
다듬을 뿐이다(§16.1~§16.5·§16.7·§6·§14 무변경, `IMPLEMENTATION_RULES.md`
무변경). 선행 `ADR-0004`(명칭 반영, v1.8)·`ADR-0005`(구현 전략 문단
신설, v1.9)와 같은 granularity로 Minor 단위로 기록한다. `ADC-0020`
§8-6이 예상한 폭(v1.13, Minor)과 일치한다.

### 8. Migration Strategy

> 아래 1~4는 Review PASS 이후 **실행되었다**(Status: Accepted). 5(커밋)는
> 별도로 진행한다 — 이 시점까지 Commit/PR/Merge는 없다.

1. `docs/architecture/baseline/BASELINE.md`:
   - §16.6 절 제목을 §2.1대로 교체한다.
   - §16.6 본문에 §2.2 **명칭** 문단과 §2.3 **Adapter Contract 부속
     명세** 문단을, "Workflow Module Defer(§16.7)와의 구분" 문단과
     "이 Accept가 결정하지 않는 것" 문단 사이에 그 순서대로 삽입한다.
   - "이 Accept가 결정하지 않는 것" 문단을 §2.4대로 교체한다.
   - §16.1~§16.5·§16.7·§6·§14·§15.2는 문자 그대로 유지한다.
   - §17 Version 표의 `Version` 값을 v1.12 → v1.13으로 바꾸고, 변경
     이력 맨 위에 다음 한 줄을 추가한다:

     > `| v1.13 | §16.6 책임에 명칭 **Workflow Adapter** 반영(재명명 아님 — §16.2 Engine Adapter와 별개, v1 `IWorkflowEngine` "Engine" 계보 비계승) + Adapter Contract 부속 명세 (a)(b)(d)를 §16.6 A-IN 부속으로 추가((a) caller-owned Checkpoint 값 소유, (b) 실행 결과의 값 표현 = 어댑터 책임, (d) Reversibility 재확인). 부속 명세는 구현체 내부 의무이며 Public Surface·§14 Kernel Public Contract가 아니고 그 선행물도 아님(자동 승격 경로 없음) — §14 무변경, "Port/Public/Guarantee/Interface" 어휘 불사용. (c) 병렬 State 동시 쓰기(disjoint key/reducer) 규약은 Defer — 반영하지 않음(v1 ADR-0007 결정 11과 결합해 후속 판정). Checkpoint 입도(C1)·phase 경계 선언 주체·"Sequential=Reference"·구현체 선택(LangGraph)·구현 전략·Conformance Test·IMPLEMENTATION_RULES Scoped 해제는 반영 대상 아님(후속 Implementation Strategy). v1 ADR-0007 결정 2/5/9/11 미해결 유지, Rule B 미충족(재검토 조건 (c)) 유지. §16.1~§16.5·§16.7·§6 Concept Model 표·§14는 변경하지 않음. `GLOSSARY.md`에 "Kernel Modules — Workflow Adapter (Reference)" 절 신설. `IMPLEMENTATION_RULES.md` 무변경. 근거: `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md` |`

2. `docs/00_governance/GLOSSARY.md` — §5의 새 절을 "Kernel Modules —
   Execution Host (Reference)" 절 뒤에 삽입한다. "Concept Model 용어"
   절("Runtime"·"Adapter" 행 포함)은 무변경.

3. `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
   `docs/architecture/core/ADC-0008` — 변경하지 않는다.

4. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 유지되는지 확인(신설
     최상위 절 없음, §16 내부 재배치 없음 — §16.6은 같은 번호 유지).
   - §6 Concept Model 표·각주, §14, §15.2, §16.1~§16.5·§16.7이 문자
     그대로인지 확인(`git diff`가 §16.6과 §17에만 국한).
   - §16.6에 추가된 두 문단이 §16.3~16.5·§14의 어떤 문장도 인용
     이상으로 변형하지 않는지 확인. "Port/Public/Guarantee/Interface"
     어휘가 Adapter Contract 문단에 없는지 확인. §14에 추가된 항목이
     없는지 확인.
   - (c) 규약이 §16.6에 규범 문언으로 들어가지 않았는지 확인(§2.3
     마지막 문단은 경계 서술로 한정).
   - `GLOSSARY.md`의 "Concept Model 용어" 절이 문자 그대로인지 확인.
   - `IMPLEMENTATION_RULES.md`가 `git diff` 0줄인지 확인.
   - `git status`로 `core/`·`hqs/`·`dashboard/`·`docs/decisions/`가
     무변경인지 확인.

5. 커밋 — 이 ADR과 위 `BASELINE.md`·`GLOSSARY.md` 변경을 함께 커밋한다
   (승인 이후).

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.12 → v1.13이 되고, §16.6
  책임이 이제 **Workflow Adapter**라는 공식 명칭을 갖는다. 재명명이
  아니다 — §16.2 Engine Adapter와 별개이며, v1 `IWorkflowEngine`의
  "Engine" 계보를 계승하지 않는다.
- §16.6에 **Adapter Contract 부속 명세**가 (a)(b)(d) 세 항목으로
  기록된다 — 전부 §16.6 A-IN이 이미 짊어진 의무의 계약 언어 재기술이다.
  Public Surface·Interface·Port가 아니며, §14로의 자동 승격 경로가 없음이
  명문화된다.
- 후보 절 **(c)**(병렬 State disjoint key / reducer)는 Baseline에
  반영되지 않는다 — `ADC-0020` §Q-D Defer. 문서화된 hazard로만 남으며,
  계약화·배치·HQ 구속 여부는 v1 `ADR-0007` 결정 11과 함께 후속 절차가
  판정한다.
- `docs/00_governance/GLOSSARY.md`에 Workflow Adapter·Adapter Contract
  항목이 추가되어, 향후 문서 작성의 표준 어휘가 생긴다. §6 미러링 절은
  무변경.
- `BASELINE.md` §6 Concept Model의 "Runtime"·"Adapter" 항목,
  `docs/decisions/adc/ADC.md` ADC-02, `docs/architecture/core/ADC-0008`은
  이 ADR로 전혀 변경되지 않는다.
- `hqs/development/IMPLEMENTATION_RULES.md`는 **무변경**이다 — `ADC-0020`이
  구현 착수를 허용하지 않으므로 Scoped 해제할 대상이 없다(§6). Workflow
  Parser / Scheduler / Workflow orchestration / 조건부 목적지 선택 /
  Stage 재진입·조건부 Stage / Event Bus 구현 금지는 전면 유지된다.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface를 정의하지
  않았다. §14.1의 "Task 전달 책임" 미결 상태도 그대로다.
- v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계, 구현체 선택(LangGraph 포함),
  구현 전략, Checkpoint 입도 C1의 문언화, phase 경계 선언 주체,
  "Sequential = Reference", Conformance Test는 모두 이 ADR 이후에도
  별도 절차(후속 Implementation Strategy ADC 등)를 거쳐야 한다.
- Rule B는 여전히 미충족이다(`ADC-0019` §Q2, 재검토 조건 (c)). 이 반영은
  §14 승격·Implementation Strategy·`IMPLEMENTATION_RULES.md` Scoped
  해제·(c) 계약화의 hard gate를 약화하지 않는다.
- 이 ADR은 **Accepted** 상태이며, §Decision·§Migration Strategy의
  `BASELINE.md`(§16.6 두 문단 추가 + "결정하지 않는 것" 문단 정정 + §17
  v1.13)·`GLOSSARY.md`("Workflow Adapter (Reference)" 절 신설) 변경이
  Review PASS 이후 반영되었다. 커밋은 별도로 진행한다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(명칭 반영 + 기존 불변조건의 계약 언어
  재기술)** — §16.6이 가리키는 책임의 범위(A-IN/A-OUT)는 전혀 바뀌지
  않는다. 이름이 확정되고, §16.6이 이미 담은 의무 (a)(b)(d)가 "Adapter
  Contract"라는 부속 명세로 정련된다. Component 설계(§10 Out of Scope)에는
  영향이 없다 — Interface·구현 전략·Checkpoint 입도는 여전히 미정이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다. Kernel
  Public Contract(§14)는 무변경. Adapter Contract는 구현체 내부 의무의
  부속 명세이지 Public Contract가 아니며, §14.1 "Task 전달 책임" 미결
  상태가 이 책임의 §14 승격을 계속 막는다(조건 이월).
- **Kernel Impact**: **있음(제한적, 조건부)** — Kernel Concept 목록의
  이름 없던 책임 하나가 "Workflow Adapter"로 명명되고 내부 의무 3건이
  명문화되나, 이것이 Public Contract·Component로 구체화되려면 v1 결정
  2/5/9/11 공백 해소 + Reversibility v2 재현 검증 + Implementation
  Strategy 단계가 필요하다.

## Governance Chain 검증

`RFC-0020`(Proposed — 명칭·Adapter Contract 후보·Checkpoint 입도·Open
Questions만 제기, 판단은 `ADC-0020`에 위임) → `ADC-0020`(Decided — Q-A
번들링 허용, Q-B 명칭 Accept, Q-C 3계층 Accept·Modify, Q-D (a)(b)(d)
Accept·(c) Defer, Q-E-1 C1·Q-E-2 Defer, Q-F 진행 가부만) → 이
ADR(Accepted — `ADC-0020` §8 지침 중 명칭 + (a)(b)(d)를 `BASELINE.md`
§16.6·§17과 `GLOSSARY.md`에 반영, 새 결정 없음).

- `RFC-0020`은 Open Questions만 열고 `ADC-0020`에 위임했다 — 위반 없음.
- `ADC-0020`은 `RFC-0020` §5 권고를 자동 채택하지 않고 Evidence(P5·P6
  등) 기반으로 독립 판정했으며, (c)를 Defer하고 "Sequential = Reference"·
  Implementation Strategy·§14 승격·`IMPLEMENTATION_RULES.md` 해제를 범위
  밖으로 명시했다(`ADC-0020` §5·§7) — 위반 없음.
- 이 ADR은 `ADC-0020` §Q-B·§Q-C·§Q-D (a)(b)(d)와 §8 지침만 Baseline
  문서 변경으로 옮겼을 뿐, `ADC-0020`이 Defer/범위 밖으로 둔 것((c),
  Checkpoint 입도 C1의 문언화, phase 경계 선언 주체, "Sequential =
  Reference", LangGraph 채택, 구현 전략, Conformance Test, §14 승격,
  `IMPLEMENTATION_RULES.md` 해제, v1 결정 재설계)을 새로 결정하지
  않았다(§Out of Scope, §3, §6) — 위반 없음.
- `ADC-0019` §Decision 조건 1~6, Rule B 미충족, v1 `ADR-0007` 결정
  2/5/9/11 미해결이 §Out of Scope·§Consequences에 그대로 재확인됨을
  확인했다 — `ADC-0020` §6과 일치.
- §16.6에 추가되는 두 문단이 §16.3~16.5·§14의 문장을 인용은 하되
  수정·재정의하지 않음을 §2가 명시하고 §8 검증 절차가 확인하도록 함 —
  충돌 없음.

## Self Review

- `ADC-0020`이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of Scope에
  명시한 항목((c), Checkpoint 입도 C1의 문언화, phase 경계 선언 주체,
  "Sequential = Reference", LangGraph 채택, 구현 전략, Conformance Test,
  §14 승격, `IMPLEMENTATION_RULES.md` 해제, v1 결정 재설계)은 손대지
  않았다.
- 명칭 "Workflow Adapter"만 반영했는가(재명명 아님) — **예**(§2.2) —
  §16.2 Engine Adapter와 별개, v1 `IWorkflowEngine` "Engine" 계보 비계승을
  명시했다.
- Adapter Contract 정식화 집합을 (a)(b)(d)로 한정했는가 — **예**(§2.3,
  §3).
- (c)를 Baseline에 규범 문언으로 반영했는가 — **아니오**(§2.3 마지막
  문단은 명시적 배제 서술, §3) — 규범 효력을 명문으로 부인하며
  `ADC-0020` §8-4("반영하지 않는다")에 부합.
- Adapter Contract 문단이 §14 / Public Port를 신설·우회하는가 —
  **아니오**(§2.3) — "Port/Public/Guarantee/Interface" 어휘 불사용,
  "§14 아님·선행물 아님·자동 승격 경로 없음" 명문화, §14에 항목 추가
  없음.
- Checkpoint 입도 C1을 Baseline 문언으로 박았는가 — **아니오**(§Out of
  Scope) — (a) 문단이 "재개 입도는 이 절이 정하지 않는다"로 명시.
- §16.1~§16.5·§16.7·§6 Concept Model 표·§14·§15.2를 수정했는가 —
  **아니오**(§2·§4·§8 검증 절차).
- `hqs/development/IMPLEMENTATION_RULES.md`를 변경했는가 — **아니오**(§6)
  — `ADC-0015`류 부분 해제 없음, 금지 조항 전면 유지.
- v1 `ADR-0007` 결정 2/5/9/11을 해소했는가 — **아니오**(§Out of Scope,
  §Consequences).
- Rule B 충족을 선언했는가 — **아니오**(§Consequences) — 미충족·재검토
  조건 (c) 유지.
- Reversibility 필수 Architecture 불변조건을 유지했는가 — **예**((d)
  문단이 재기술, 검증 실행은 이연).
- 새 최상위·하위 절을 신설했는가 — **아니오**(§7) — §16.6 내부 문단
  추가만, §16.6 번호 유지.
- `BASELINE.md` / `GLOSSARY.md`를 실제로 수정했는가 — **예(승인 반영)** —
  Review PASS 이후 §Migration Strategy 1~4를 실행했다(§16.6 두 문단 추가 +
  "결정하지 않는 것" 문단 정정, §17 v1.13, `GLOSSARY.md` 절 신설).
  §16.1~§16.5·§16.7·§6·§14·§15.2·`IMPLEMENTATION_RULES.md`·`ADC.md`·
  `ADC-0008`은 무변경. 커밋은 별도.
- Production Code를 변경했는가 — **아니오**.
- 반영 과정에서 `ADC-0020`이 이미 인지한 것 이상의 새 Architecture 결정
  지점이 나타났는가 — **아니오**. (c) 경계 서술을 §16.6 본문에 두는
  것으로 확정했다(§3).
