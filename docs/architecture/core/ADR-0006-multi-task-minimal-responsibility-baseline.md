# ADR-0006: Multi-Task 최소 책임(ADC-0016)의 Baseline·Rules 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0006` |
| 제목 | `ADC-0016`의 Accept 결정(독립 Task 동시 실행·결과 수집 책임의 존재, Scoped, Data/Artifact Isolation Conditional)을 Architecture Baseline·Development HQ Rules에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md` — **Decision: A. Accept (Scoped, Conditional on Data/Artifact Isolation)**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md` §8(Boundary Question) |
| 관련 ADC | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md` |
| 선행 ADR | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`(§16.3 신설), `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`(명칭), `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md`(구현 전략 — 같은 절차로 §16 Kernel Modules·`IMPLEMENTATION_RULES.md`를 갱신한 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`/`ADR-0003`(Execution Host 존재), `docs/architecture/core/ADC-0014-execution-responsibility-naming.md`/`ADR-0004`(명칭), `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`/`ADR-0005`(구현 전략), `docs/architecture/core/ADC-0008-runtime-existence-boundary.md`(넓은 범위, Not Accepted), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW, 이 ADR이 변경하지 않음) |

이 ADR은 `ADC-0016`이 이미 내린 Accept(Scoped, Conditional) 결정을
다시 논의하지 않는다. 새로운 철학이나 Architecture를 제안하지
않는다. 그 Accept 결정을 실제 Baseline·Rules 문서 변경으로 옮기기
위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0016`이 Accept 범위에서 명시하지 않은 것은 **하나도 반영하지
않는다.**

| 항목 | 근거 |
|---|---|
| Multi-Task 명칭 확정(그대로 쓸지, 다른 이름으로 바꿀지) | `ADC-0016` §Implementation Boundary "제외" — 후속 RFC 대상 |
| 구현 전략(`ThreadPoolExecutor`/`asyncio`/기타) | `ADC-0016` §Implementation Boundary "제외" — 후속 RFC/ADC 대상 |
| Data/Artifact Isolation 위험(파일 덮어쓰기, Artifact/Result 충돌, 공유 상태, Git 충돌, Retry 충돌)의 구체적 해소 방법 | `ADC-0016` §Q4·§Implementation Boundary "제외" — 최소 안전조건으로만 요구, 해소책은 설계하지 않는다 |
| Task→Agent 동적 할당 | `ADC-0016` §Q5 — 기존 Agent 재사용이 전제, 이 ADR도 그대로 유지 |
| Scheduler, 우선순위, Workflow orchestration | `ADC-0016` §Q7 — 계속 Out of Scope |
| `BASELINE.md` §6 Concept Model의 "Runtime" 넓은 정의(Workflow 참조, Agent 배분) 전체 채택·수정 | `ADC-0016` §Q6 — 이 ADR도 §6 표·정의를 건드리지 않는다 |
| Execution Host(§16.3)의 범위 확장 | `ADC-0016` §Q3·§Decision 조건 2 — Execution Host는 전혀 넓어지지 않는다 |
| `docs/decisions/adc/ADC.md`의 ADC-02 항목 수정 | `ADC-0016` §Next Step 3, `ADR-0003` §5·`ADR-0005` §Out of Scope와 동일한 판단 — 별도 트랙, 별도 절차 |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16에 새 절(16.4)을 신설해 Multi-Task 최소 책임을 Accept(Scoped, Conditional)로 기록한다. 기존 §16.4("미결 항목")는 §16.5로 밀린다. §17 Version을 v1.10으로 갱신한다 |
| `hqs/development/IMPLEMENTATION_RULES.md` | "Scheduler/Multi-Task/Workflow 및 §6 넓은 Runtime 구현 금지" 행의 범위를 좁혀 이 Accept를 반영하고, Execution Host 선례와 같은 형식으로 "Multi-Task 구현 허용 범위(Scoped, Conditional)" 절을 신설한다 |

그 외 어떤 파일도 변경하지 않는다(§Out of Scope). `docs/decisions/adc/ADC.md`,
Kernel Public Contract(§14), Production Code는 이번에도 건드리지
않는다.

### 2. `BASELINE.md` §16 갱신 내용

`ADC-0016`과 `RFC-0016`이 이미 정리한 것만 옮긴다. 새 문장을 만들지
않는다. 기존 §16.1(Governance)·§16.2(Execution Layer)·§16.3(Execution
Host)은 변경하지 않는다 — §16.3 본문 문자열도 그대로 유지한다(Execution
Host 범위는 이 ADR로 전혀 넓어지지 않는다, `ADC-0016` §Q3).

새로 삽입할 §16.4(기존 §16.4 "미결 항목" 앞에 삽입, 기존 절은 §16.5로
재배치):

```markdown
### 16.4 Multi-Task — 독립 Task 동시 실행·결과 수집 (Accept, Scoped, Conditional)

**책임**: 서로 입력 독립·출력 비의존인, 이미 코드/설계에 고정된
소수의 실행 단위를 동시에 시작하고, 모두 끝났음을 판단해 결과를
수집·결합하는 책임. 우선순위 판단, 조건부 분기, Workflow 그래프
해석, Agent 동적 선택은 포함하지 않는다.

**근거**: `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md`
§8이 연 좁은 Boundary Question("서로 독립적인 복수 Task를 동시에
실행하고 결과를 수집하는 책임을, Execution Host(§16.3)와 별개의
Kernel Concept으로 Accept하는가")을,
`docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`가
실제 Production Code 1건(`hqs/development/mvp/workflow_0009.py`의
`run_comparison`, 이미 `main`에 병합)을 근거로 Accept(Scoped,
Conditional)했다.

**Kernel Module로서 다루는 것**: 서로 독립적인 소수 실행 단위의
동시 시작·대기(join)·결과 수집이라는 조율(Coordination) 그 자체
(`ADC-0016` §Implementation Boundary "포함"). 한 실행 단위의
실패가 다른 실행 단위의 진행·결과에 영향을 주지 않는다는 실패
격리도 이 책임에 포함된다.

**Execution Host와의 경계**: Multi-Task는 Execution Host(§16.3)의
확장이 아니라 별개 Concept이다(`ADC-0016` §Q3). Execution Host는
이미 dispatch가 결정된 **단일** 실행 단위의 Execution
Isolation(실행 상태 오염 방지)을 다루고, Multi-Task는 **복수**
독립 실행 단위의 Coordination(시작·대기·수집)을 다룬다. 두 책임은
서로 배타적이지 않다 — 향후 동일 Target을 동시에 여러 번 실행해야
하는 조합이 생기면 Multi-Task가 각 실행을 Execution Host에 위임하는
구성도 가능하나, 그 구성 자체는 이 Accept가 설계하지 않는다.
Execution Host의 범위(§16.3)는 이 Accept로 전혀 넓어지지 않는다.

**Data/Artifact Isolation — 최소 안전조건**: 이 책임을 실제로
적용하는 모든 Task 조합은, 동시 실행되는 각 Task가 서로 다른
파일/Artifact 이름공간에 쓰거나 아무것도 쓰지 않는다는 것이
**사전에 확인된 경우에만** 이 Accept의 범위 안에 있다(`ADC-0016`
§Q4). 이 조건이 확인되지 않는 조합(예: 여러 Task가 같은 파일을
쓸 수 있는 경우)은 이 Accept가 다루지 않은 것으로 취급한다. 이
조건의 구체적 해소 방법(파일 잠금, Artifact 이름공간 분리 규칙 등)
은 설계하지 않는다.

**Task→Agent 할당**: 기존 Agent 재사용을 이 책임의 전제로 삼는다.
새 Agent·Capability 도입, 동적 Task→Agent 할당 로직은 이 Accept에
포함하지 않는다(`ADC-0016` §Q5) — `hqs/development/IMPLEMENTATION_RULES.md`의
"새 Capability/Agent 추가 금지", "Registry 일반화 금지"와 일치한다.

**이 Accept가 결정하지 않는 것**: 이 책임의 명칭(Multi-Task를
그대로 쓸지), 구현 전략(`ThreadPoolExecutor`/`asyncio`/기타),
Data/Artifact Isolation 위험의 구체적 해소 방법, Task→Agent 동적
할당, Scheduler·우선순위·Workflow orchestration, `BASELINE.md` §6의
원래 넓은 정의(Workflow 참조 전체)로의 확장 여부는 모두 별도
절차(RFC → ADC → ADR)로 남는다(`ADC-0016` §Implementation Boundary
"제외"). `docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐)는 이
Accept로 전혀 갱신되지 않는다 — 이 책임은 그 넓은 질문 중 아주 좁은
부분 집합 하나일 뿐이다.

**Production 구현과의 관계**: 이 Accept는 Multi-Task 범위(서로
독립·출력 비의존인 소수 실행 단위의 동시 시작·대기·수집, 기존 Agent
재사용, Data/Artifact Isolation이 사전 확인된 조합)에 한해 구현
착수를 허용한다(`hqs/development/IMPLEMENTATION_RULES.md`,
`ADC-0016` §Next Step 4). 착수 전, 대상 Task 조합에서 Data/Artifact
Isolation 조건이 실제로 충족되는지 재확인해야 한다. Scheduler/
우선순위/Workflow orchestration, `BASELINE.md` §6의 넓은 "Runtime"
구현은 여전히 금지 상태다 — ADC-02가 Open으로 남아 있는 한 그대로
유효하다.
```

기존 §16.4("미결 항목")는 내용 변경 없이 §16.5로 재배치한다(Workflow/
Memory/Event Bus Defer 상태 기록 — `ADC-0016`은 이 상태를 재판단하지
않는다).

### 3. `BASELINE.md` §6 Concept Model 표 갱신 여부

**변경하지 않는다.** `ADR-0004` §3이 이미 "§6에 Execution Host를
추가하지 않기로" 결정했고, 그 근거(이름 귀속을 암묵적으로 확정하는
효과를 피한다)는 Multi-Task에도 그대로 적용된다 — Multi-Task 역시
§6의 "Runtime" 항목을 재명명·구체화한 것이 아니라 그와 별개의, 더
좁은 범위의 Concept이다(`ADC-0016` §Q6). §6은 이번에도 무변경.

### 4. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 내용

기존 "금지 사항" 표의 다음 행을 교체한다.

```markdown
| Scheduler/Multi-Task/Workflow 및 §6 넓은 Runtime 구현 금지 | Multi-Task orchestration과 Workflow 참조·배분은 `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 존폐)가 여전히 Open이다. Execution Host(§16.3)의 Scoped 허용 범위는 "Execution Host 구현 허용 범위" 절 참조 |
```

교체 후:

```markdown
| Scheduler/우선순위/Workflow orchestration 및 §6 넓은 Runtime(Workflow 참조 전체, Agent 동적 배분) 구현 금지 | 이들은 `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 존폐)가 여전히 Open이다. Execution Host(§16.3)와 Multi-Task(§16.4)의 Scoped 허용 범위는 각각 아래 절 참조 — 두 절 모두 이 표의 나머지 금지(Scheduler/우선순위/Workflow orchestration/§6 넓은 Runtime)를 해제하지 않는다 |
```

"Execution Host 구현 허용 범위(Scoped, ADC-0015)" 절 바로 다음에 새
절을 신설한다.

```markdown
## Multi-Task 구현 허용 범위 (Scoped, Conditional, ADC-0016)

`docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`
가 Accept(Scoped, Conditional)한 범위에 한해, 아래 조건을 모두
지키는 경우 Multi-Task 구현을 허용한다.

- 적용 대상: 서로 입력 독립·출력 비의존인, 이미 코드/설계에 고정된
  소수의 실행 단위를 동시에 시작하고 결과를 수집하는 최소 구현만
  허용한다. 우선순위 판단, 조건부 분기, Workflow 그래프 해석, Agent
  동적 선택은 포함하지 않는다.
- Data/Artifact Isolation 사전 확인 필수: 적용 대상 Task 조합에서
  동시 실행되는 각 Task가 서로 다른 파일/Artifact 이름공간에 쓰거나
  아무것도 쓰지 않는다는 것이 **구현 착수 전에** 확인되어야 한다
  (`ADC-0016` §Q4·§Decision 조건 3). 이 조건이 확인되지 않으면 이
  허용 범위 밖이다 — 확인 방법(정적 분석, 코드 리뷰 체크리스트 등)의
  구체화는 이 절이 정하지 않는다.
- Task→Agent 할당: 기존 Agent 재사용만 허용한다. 새 Agent·Capability
  도입, 동적 Task→Agent 할당 로직은 이 허용에 포함되지 않는다(위
  "구현 중 새 Capability/Agent 추가 금지" 절과 함께 적용).
- 이 허용은 Scheduler, 우선순위, Workflow orchestration,
  `BASELINE.md` §6의 넓은 "Runtime"(Workflow 참조, Agent 동적 배분)
  구현을 포함하지 않는다 — 이들은 여전히 금지 상태다(위 표).
- 이 허용은 Execution Host(§16.3)의 범위를 넓히지 않는다 — 별개
  책임이다(`ADC-0016` §Q3).
- 새 Public Interface/Contract를 정의하지 않는다 — Kernel Public
  Contract(§14)는 이 허용과 무관하게 무변경이다.
```

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.9 | **v1.10** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0016 → ADC-0016 → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0005`의 선례와 동일하다.

**Minor 증가(v1.10)를 택한 이유**: §16에 새 절(16.4)을 신설하되,
그 책임의 범위를 의도적으로 좁게 한정했고(§Out of Scope), 다른 어떤
절의 기존 문언도 수정하지 않았다(§16.1~§16.3 무변경, §6 무변경).
선행 `ADR-0003`(신설, v1.7)과 같은 granularity로 Minor 단위로
기록한다.

### 6. Migration Strategy

1. `BASELINE.md` — §16에 16.4 신설(§2), 기존 16.4를 16.5로 재배치,
   변경 이력 한 줄 추가, v1.10 갱신.
2. `hqs/development/IMPLEMENTATION_RULES.md` — "Scheduler/Multi-Task/
   Workflow 및 §6 넓은 Runtime 구현 금지" 행 교체(§4), "Multi-Task
   구현 허용 범위" 절 신설(§4).
3. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(신설 최상위 절 없음, §16 내부만 재배치).
   - §6 Concept Model 표·각주, §14(Kernel Public Contract), §16.1~
     §16.3이 문자 그대로 변경되지 않았는지 확인.
   - `IMPLEMENTATION_RULES.md`의 나머지 금지 항목(Workflow Parser,
     Registry, Engine Gateway/Routing, Policy, Memory Service, Event
     Bus, Multi-HQ/Multi Engine, Baseline 수정 금지)과 "Execution
     Host 구현 허용 범위" 절이 문자 그대로 유지되는지 확인.
   - `git status`로 `core/`·`dashboard/`(Production 소스),
     `hqs/development/mvp/`(Production 구현), `docs/decisions/adc/ADC.md`
     이하에 변경이 없는지 확인.
   - `git diff -- hqs/ core/ dashboard/`가 `IMPLEMENTATION_RULES.md`
     외에는 0줄인지 확인.
4. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.9 → v1.10이 되고,
  §16.4가 Multi-Task 최소 책임(독립 Task 동시 실행·결과 수집,
  Execution Host와 분리, Data/Artifact Isolation Conditional)을
  Accept(Scoped)로 등재한다.
- `hqs/development/IMPLEMENTATION_RULES.md`가 이 좁은 범위(Data/
  Artifact Isolation이 사전 확인된, 기존 Agent 재사용 전제의 독립
  Task 동시 실행·결과 수집)에 한해 구현을 허용하고, Scheduler/
  우선순위/Workflow orchestration 및 §6 넓은 Runtime 구현은 계속
  금지한다.
- §6 Concept Model의 "Runtime" 항목, `docs/decisions/adc/ADC.md`의
  ADC-02(Open·NOW)는 이 ADR로 전혀 변경되지 않는다.
- Execution Host(§16.3)의 범위·명칭·구현 전략은 이 ADR로 전혀
  바뀌지 않는다.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface를
  정의하지 않았다.
- 실제 구현 착수는 이 ADR 이후 가능해지지만, 착수 전 대상 Task
  조합에서 Data/Artifact Isolation 조건이 실제로 충족되는지
  재확인해야 한다 — 이 ADR 자체가 구현을 수행하지는 않는다.
  Production Code(`core/`, `hqs/`, `dashboard/`)는 전혀 수정하지
  않는다.
- 이 Accept는 영구 고정이 아니다 — `ADC-0016` §Risks·재검토 조건이
  이 ADR 이후에도 그대로 유효하다.
- 이 ADR은 **승인되었으며**, §Decision에 정의된 실제 문서 변경이 이
  승인에 따라 실행된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(Scoped)** — `BASELINE.md` §16에
  Multi-Task라는 새 책임이 좁은 범위로 처음 등재된다. Component
  설계(§10 Out of Scope)에는 영향을 주지 않는다 — 책임의 존재와
  경계만 기록했을 뿐, 명칭·구현 전략은 여전히 미정이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경.
- **Kernel Impact**: **있음(제한적)** — Kernel Concept 목록에 이름
  없는 책임 하나가 추가됐으나(Execution Host와 별개), 이것이
  Component·Interface로 구체화되려면 별도 ADR(명칭·구현 전략 확정
  이후)이 필요하다.

## Governance Chain 검증

`RFC-0016`(Boundary Question만 개설, 판단은 후속 절차로 위임 —
개설 당시 Proposed, 이후 `ADC-0016` → 이 ADR로 Resolved) →
`ADC-0016`(Accept, Scoped·Conditional — 그 질문에 답함, 명칭·전략·
위험 해소 방법·동적 할당·§6 넓은 정의는 명시적으로 제외) → 이
ADR(Accepted — Baseline·Rules에 반영, 새로운 결정 추가 없음). 세
문서가 각각 인용하는 근거가 상위 문서의 범위를 벗어나지 않는지
확인했다.

- RFC-0016은 답을 제시하지 않고 질문만 열었다(§8) — 위반 없음.
- ADC-0016은 RFC-0016이 연 질문에만 답했고, RFC-0016이 제외한
  항목(명칭·전략·위험 해소 방법·동적 할당·Scheduler·Workflow
  orchestration·§6 넓은 정의)을 판단하지 않았다(§Implementation
  Boundary "제외") — 위반 없음.
- 이 ADR은 ADC-0016의 Decision을 그대로 옮겼을 뿐, ADC-0016이
  판단하지 않은 것(명칭, 구현 전략, 위험 해소 방법, 동적 할당,
  Scheduler/Workflow orchestration, §6 넓은 정의, ADC.md, Contract
  신설)을 새로 결정하지 않았다(§Out of Scope, §Decision 2·4) — 위반
  없음. `diff` 검증 결과도 §6 Concept Model 표·§14 Kernel Public
  Contract·§16.1~§16.3·`ADC.md`·Production Code 어디에도 변경이
  없음을 확인했다(§6 Migration Strategy).

## Self Review

- ADC-0016이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(명칭, 구현 전략, 위험 해소 방법, 동적 할당,
  Scheduler/Workflow orchestration, §6 넓은 정의, Execution Host
  확장, ADC.md, Contract 신설, Production Code)은 손대지 않았다.
- Multi-Task의 Scoped Conditional Accept만 Baseline에 반영했는가 —
  **Pass**(§2 "Multi-Task — 독립 Task 동시 실행·결과 수집" 절, §4
  Rules 절) — 새로운 판단 기준을 추가하지 않고 ADC-0016의 문구를
  그대로 옮겼다.
- 책임을 복수 독립 Task의 동시 시작·대기·결과 수집으로 한정했는가 —
  **Pass**(§2 "책임"·"Kernel Module로서 다루는 것" 문단).
- Execution Host의 단일 실행 격리 책임을 변경했는가 — **아니오**
  (§2 "변경하지 않는다" 명시, §3, §Governance Chain 검증) — §16.3
  본문은 문자 그대로 유지했다.
- Data/Artifact Isolation 조건을 명시했는가 — **Pass**(§2
  "Data/Artifact Isolation — 최소 안전조건" 문단, §4 Rules 절의
  "사전 확인 필수" 항목).
- Scheduler/우선순위/Workflow orchestration/넓은 Runtime을 계속
  Out of Scope로 두었는가 — **Pass**(§2 "이 Accept가 결정하지 않는
  것" 문단, §4 표 교체 후 행, §Consequences).
- Task→Agent 동적 할당을 결정했는가 — **아니오**(§2 "Task→Agent
  할당" 문단, §4 Rules 절 — 기존 Agent 재사용만 허용).
- `BASELINE.md`와 `IMPLEMENTATION_RULES.md`만 필요한 범위에서
  갱신했는가 — **Pass**(§1) — `docs/decisions/adc/ADC.md`, Kernel
  Public Contract(§14)는 건드리지 않았다.
- 새로운 Public Contract/Kernel Interface를 정의했는가 —
  **아니오**(§14 무변경, §Architecture/Contract/Kernel 영향).
- Production Code를 변경했는가 — **아니오**.
- §6 "Runtime" 항목을 재명명·수정했는가 — **아니오**(§3) — `ADR-0004`
  §3의 판단을 그대로 유지했다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- 새 최상위 절 또는 §16 내부 재배치 외의 변경을 했는가 — **아니오**.
  기존 §16.4를 §16.5로 재배치했을 뿐, 다른 절은 재배치하지 않았다
  (§2).
- RFC-0016 → ADC-0016 → 이 ADR chain과 diff를 검증했는가 —
  **Pass**(§Governance Chain 검증, §6 Migration Strategy 검증
  절차).
