# ADR-0007: Multi-Task Result Store 저장 전 검증 게이트(ADC-0017)의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0007` |
| 제목 | `ADC-0017`의 Accept 결정(Result Store 저장 전 검증 게이트 책임의 존재, Scoped, Narrow)을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` — **Decision: A. Accept (Scoped, Narrow — 저장 전 검증 게이트로 한정)**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md` §5(Boundary Question) |
| 관련 ADC | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` |
| 선행 ADR | `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md`(§16.4 Multi-Task 신설 — 같은 절차로 §16 Kernel Modules를 갱신한 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`/`ADR-0006`(Multi-Task 존재, Accept Scoped·Conditional), `docs/architecture/core/ADC-0013`~`ADC-0015`/`ADR-0003`~`ADR-0005`(Execution Host 존재·명칭·구현 전략), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW, 이 ADR이 변경하지 않음) |

이 ADR은 `ADC-0017`이 이미 내린 Accept(Scoped, Narrow) 결정을 다시
논의하지 않는다. 새로운 철학이나 Architecture를 제안하지 않는다. 그
Accept 결정을 실제 Baseline 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0017`이 Accept 범위에서 명시하지 않은 것은 **하나도 반영하지
않는다.**

| 항목 | 근거 |
|---|---|
| Resume 시점 재검증 | `ADC-0017` §Q5·§Decision 조건 1 — Not Accepted, 후속 판단 대상 |
| 저장 전 검증의 구체적 판정 기준·구현 알고리즘 | `ADC-0017` §Q7·§Decision 조건 5 — 존재만 Accept, 형태는 미확정 |
| 실패 감지 이후의 자동 Retry/Alert/Recovery 정책 | `ADC-0017` §Q6·§Decision 조건 4 — Result Store 책임은 저장 게이트까지 |
| `call_engine()`(`hqs/development/mvp/engine.py`) 자체의 수정 | `ADC-0017` §Q3 — 근본 원인이나, 별도 Dev HQ 개선 트랙(`efa-2026-08/EVIDENCE.md` §DEV_HQ_FEEDBACK)이 다룬다. 이 ADR·ADC 체인이 대체하지 않는다 |
| 새 Component/Interface/Public Contract 신설 | `ADC-0017` §Q7·§Decision 조건 5 |
| Execution Host(§16.3)·Multi-Task(§16.4)의 범위 확장 | `ADC-0017` §Q4·§Decision 조건 2 — 두 책임 모두 전혀 넓어지지 않는다 |
| `BASELINE.md` §6 Concept Model("Runtime")의 넓은 정의 채택·수정 | 이 ADR도 §6 표·정의를 건드리지 않는다(선행 `ADR-0004` §3·`ADR-0006` §3과 동일 판단) |
| Development HQ에 Result Store(Checkpointer류) 컴포넌트를 새로 요구 | `ADC-0017` §Decision 조건 6 — 이 Accept는 원칙 차원, 각 HQ의 설계 선택으로 남긴다 |
| `docs/decisions/adc/ADC.md`의 ADC-02 항목 수정 | `ADR-0003` §5·`ADR-0006` §Out of Scope와 동일한 판단 — 별도 트랙, 별도 절차 |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16에 새 절(16.5)을 신설해 Multi-Task Result Store 저장 전 검증 게이트를 Accept(Scoped, Narrow)로 기록한다. 기존 §16.5("미결 항목")는 §16.6으로 밀린다. §17 Version을 v1.11로 갱신한다 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
Kernel Public Contract(§14), Production Code는 이번에도 건드리지
않는다(§4 "IMPLEMENTATION_RULES.md 변경 필요성 검토" 참조 — 검토
결과 변경 불필요로 판단했다).

### 2. `BASELINE.md` §16 갱신 내용

`ADC-0017`과 `RFC-0017`이 이미 정리한 것만 옮긴다. 새 문장을 만들지
않는다. 기존 §16.1(Governance)·§16.2(Execution Layer)·§16.3(Execution
Host)·§16.4(Multi-Task)는 변경하지 않는다 — 본문 문자열도 그대로
유지한다(Execution Host·Multi-Task 범위는 이 ADR로 전혀 넓어지지
않는다, `ADC-0017` §Q4).

새로 삽입할 §16.5(기존 §16.5 "미결 항목" 앞에 삽입, 기존 절은 §16.6으로
재배치):

```markdown
### 16.5 Multi-Task Result Store — 저장 전 검증 게이트 (Accept, Scoped, Narrow)

**책임**: Multi-Task(§16.4)가 공유하는 Result Store가 결과를 저장하기
전에 그 결과의 유효성을 판정하고, 무효로 판정되면 저장을 막는 게이트
책임. Resume 시점의 재검증, 실패 감지 이후의 자동 Retry/Alert/
Recovery 정책은 포함하지 않는다.

**근거**: `docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md`
§5가 연 좁은 Boundary Question("Multi-Task가 공유하는 Result
Store(Checkpointer)에 저장 결과의 유효성·무결성을 보장하는 책임을
Execution Host(§16.3)·Multi-Task(§16.4)와 별개의 Kernel Concept
또는 그 두 책임에 속한 하위 의무로 Accept하는가")을,
`docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md`
가 `hqs/investment/dogfooding/pg-hq-verify/EVIDENCE.md`의 콘텐츠
레벨 실패 4회 재현(Investment HQ MVP 경로 2건 포함)을 근거로
Accept(Scoped, Narrow)했다.

**Investment HQ Checkpointer/`run_step`에 한정된 책임**: 이 Accept의
실증 사례는 `hqs/investment/checkpoint.py`의 `Checkpointer`/
`run_step`/`ContentFailureError` 패턴 하나뿐이다 — 이 컴포넌트는
`hqs/development/mvp/`에 존재한 적이 없다(`ADC-0017` §Q3 인용,
`docs/research/PHASE4-HQ-CROSS-VALIDATION-0001.md` 확인). 이 Accept는
"Result Store가 존재하는 곳에서는 이런 게이트 책임이 필요하다"는
원칙을 Kernel 수준에서 Accept하는 것이며, Development HQ를 포함한
다른 HQ에 동일한 컴포넌트를 새로 만들 것을 요구하지 않는다
(`ADC-0017` §Decision 조건 6).

**Multi-Task와의 경계**: 이 책임은 Multi-Task(§16.4) 전용이 아니다
(`ADC-0017` §Q4) — 근거로 삼은 4회 재현 중 2건은 Multi-Task 도입
이전(project-local Dogfooding)에 발생했고, Investment HQ 안의 2건도
모두 `ThreadPoolExecutor`가 관여하지 않는 순차 구간(Wave3, Synthesis)
에서 발생했다. 따라서 이 책임은 동시 실행 여부와 무관하게 Result
Store가 존재하는 모든 호출 경로에 적용되는 더 일반적인 책임이며,
Multi-Task(§16.4)의 Coordination·실패 격리 책임과 Execution
Host(§16.3)의 Execution Isolation 책임은 이 Accept로 전혀 변경되지
않는다.

**근본 원인과의 분리**: 이 Accept는 콘텐츠 레벨 실패가 발생하는
근본 원인을 해결하지 않는다. 근본 원인은 Engine 호출 계층
(`hqs/development/mvp/engine.py`의 `call_engine()`이 `subprocess.run()`
의 `returncode`/`stderr`를 확인하지 않고 `stdout`을 무조건 반환하는
것)에 있다고 `ADC-0017` §Q3이 독립적으로 확인했다 — 이는 이미 별도
Dev HQ 개선 후보 트랙으로 격상돼 있다(`hqs/investment/dogfooding/
efa-2026-08/EVIDENCE.md` §DEV_HQ_FEEDBACK). 이 Accept는 그 근본
원인이 해결되기 전까지, 손상된 결과가 Result Store에 영속화돼
Resume을 통해 하위 Task로 전파되는 것을 막는 봉쇄(containment)
책임만 다룬다 — `call_engine()` 자체의 수정은 이 Accept·이 ADR의
범위가 아니며, 별도 Dev HQ 개선 트랙이 독립적으로 진행한다.

**이 Accept가 결정하지 않는 것**: Resume 시점 재검증 여부
(`ADC-0017` §Q5 — 저장 전 검증이 우선순위가 높다고 판단해 이번엔
Not Accepted), 저장 전 검증의 구체적 판정 기준·구현 알고리즘
(`ADC-0017` §Q7), 실패 감지 이후의 자동 Retry/Alert/Recovery 정책
(`ADC-0017` §Q6 — Result Store의 책임은 저장 게이트까지로 한정),
`call_engine()` 자체의 수정(위 문단), 새 Component/Interface 신설
(`ADC-0017` §Q7)은 모두 별도 절차(RFC → ADC → ADR, 또는 독립된
Dev HQ 개선 트랙)로 남는다.

**Production 구현과의 관계**: 이 Accept가 실증 근거로 삼은
`hqs/investment/checkpoint.py`의 `Checkpointer`/`run_step`/
`ContentFailureError`는 이미 `main`에 존재하는 Production Code다 —
이 Accept는 그 기존 패턴의 책임을 Kernel 수준에서 인정한 것이며,
새로운 구현 착수를 이번에 승인하지 않는다. 저장 전 검증 판정 기준을
확장하는 등의 실제 변경은 별도 판단(가능하면 Engine 호출 계층 개선
Dev HQ 트랙과 조율)을 거쳐야 한다.
```

기존 §16.5("미결 항목")는 내용 변경 없이 §16.6으로 재배치한다
(Workflow/Memory/Event Bus Defer 상태 기록 — `ADC-0017`은 이 상태를
재판단하지 않는다).

### 3. `BASELINE.md` §6 Concept Model 표 갱신 여부

**변경하지 않는다.** `ADR-0004` §3·`ADR-0006` §3이 이미 "§6에
Execution Host/Multi-Task를 추가하지 않기로" 결정했고, 그 근거(이름
귀속을 암묵적으로 확정하는 효과를 피한다)는 이 Result Store 게이트
책임에도 그대로 적용된다 — 이 책임은 §6의 "Runtime" 항목을
재명명·구체화한 것이 아니라 그와 별개의, 더 좁은 범위의 책임이다
(`ADC-0017` §Q4). §6은 이번에도 무변경.

### 4. `hqs/development/IMPLEMENTATION_RULES.md` 변경 필요성 검토

`ADC-0015`/`ADR-0005`(Execution Host)와 `ADC-0016`/`ADR-0006`
(Multi-Task)는 각각 `IMPLEMENTATION_RULES.md`의 금지 표를 Scoped
해제하고 "구현 허용 범위" 절을 신설했다 — 두 경우 모두 **Development
HQ MVP-0001 안에서 아직 구현되지 않은 것을, 그 문서의 금지 표가
막고 있던 상황**이었다. 이 ADR은 그 선례를 그대로 따르지 않는다 —
검토 결과는 다음과 같다.

- `hqs/development/IMPLEMENTATION_RULES.md`는 첫 줄부터 "Claude
  Code가 이 저장소에서 Development HQ MVP-0001을 구현할 때 반드시
  지켜야 하는 규칙"으로 스스로 범위를 한정한다. 이 문서의 금지 표
  (Workflow Parser, Scheduler, Registry, Policy, Memory Service,
  Event Bus 등)의 어느 항목도 "Result Store" 또는 "저장 전 검증"을
  명시적으로 금지하지 않는다 — Development HQ MVP-0001에는 애초에
  `Checkpointer`류 컴포넌트가 존재한 적이 없다(`ADC-0017` §Q3,
  `PHASE4-HQ-CROSS-VALIDATION-0001.md`).
- 이 Accept의 실증 근거인 `hqs/investment/checkpoint.py`는 이미
  Production Code로 **존재하며 동작 중**이다 — `ADC-0015`/`ADC-0016`
  처럼 "아직 금지돼 있어 새로 허용해야 구현 착수가 가능한" 상황이
  아니다. 저장 전 검증 게이트(`ContentFailureError` → `cp.save()`
  건너뜀)는 이미 Investment HQ Production Code에 구현·동작 중이며,
  이 ADC/ADR은 그 기존 동작의 책임을 Kernel 수준에서 사후 인정할
  뿐이다.
- `hqs/investment/STRUCTURE.md` §"금지 사항"(`IMPLEMENTATION_RULES.md`
  와 동일 원칙을 Investment HQ에 맞게 옮긴 자체 문서)도 확인했다 —
  이 표 역시 Workflow Parser/Scheduler/Registry/Runtime/Engine
  Gateway·Routing/Policy·Memory Service·Event Bus만 금지할 뿐,
  Result Store 저장 게이트를 금지하는 항목이 없다.

**결론(검토 결과)**: `IMPLEMENTATION_RULES.md`와 `hqs/investment/
STRUCTURE.md` 어느 쪽도 이 책임을 막고 있지 않으므로, "구현 허용
범위" 절을 신설해 금지를 해제할 대상 자체가 없다 — **이 ADR은
`IMPLEMENTATION_RULES.md`를 변경하지 않는다.** 이는 임의로 새 허용
범위를 만들지 않기 위한 것이며(작업 지시 §10), `ADC-0015`/`ADC-0016`
선례를 기계적으로 반복하지 않고 실제 필요를 확인한 결과다. 향후
Development HQ MVP-0001에도 Result Store류 컴포넌트가 새로 도입되는
시점이 오면, 그때 이 문서에 이 책임을 반영할 필요가 있는지 별도로
재검토해야 한다.

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.10 | **v1.11** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0017 → ADC-0017 → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0006`의 선례와 동일하다.

**Minor 증가(v1.11)를 택한 이유**: §16에 새 절(16.5)을 신설하되, 그
책임의 범위를 의도적으로 좁게 한정했고(§Out of Scope), 다른 어떤
절의 기존 문언도 수정하지 않았다(§16.1~§16.4 무변경, §6 무변경).
`IMPLEMENTATION_RULES.md`도 변경하지 않았다(§4). 선행 `ADR-0006`
(신설, v1.10)과 같은 granularity로 Minor 단위로 기록한다.

### 6. Migration Strategy

1. `BASELINE.md` — §16에 16.5 신설(§2), 기존 16.5를 16.6으로 재배치,
   변경 이력 한 줄 추가, v1.11 갱신.
2. `hqs/development/IMPLEMENTATION_RULES.md` — 변경하지 않는다(§4).
3. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(신설 최상위 절 없음, §16 내부만 재배치).
   - §6 Concept Model 표·각주, §14(Kernel Public Contract), §16.1~
     §16.4가 문자 그대로 변경되지 않았는지 확인.
   - `IMPLEMENTATION_RULES.md`가 문자 그대로 무변경인지 확인
     (`git diff` 0줄).
   - `git status`로 `core/`·`dashboard/`(Production 소스),
     `hqs/development/mvp/`·`hqs/investment/`(Production 구현),
     `docs/decisions/adc/ADC.md` 이하에 변경이 없는지 확인.
   - `git diff -- hqs/ core/ dashboard/`가 완전히 0줄인지 확인(이번
     ADR은 `IMPLEMENTATION_RULES.md`조차 변경하지 않으므로, 선행
     ADR과 달리 `hqs/` 전체가 무변경이어야 한다).
4. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.10 → v1.11이 되고,
  §16.5가 Multi-Task Result Store 저장 전 검증 게이트(Investment HQ
  Checkpointer/`run_step`에 한정, Multi-Task 전용 아님, 근본 원인은
  별도 Dev HQ 트랙)를 Accept(Scoped, Narrow)로 등재한다.
- `hqs/development/IMPLEMENTATION_RULES.md`는 무변경이다 — 검토
  결과 이 책임을 막고 있는 금지 항목이 없어 Scoped 해제할 대상
  자체가 없었다(§4).
- §6 Concept Model의 "Runtime" 항목, `docs/decisions/adc/ADC.md`의
  ADC-02(Open·NOW)는 이 ADR로 전혀 변경되지 않는다.
- Execution Host(§16.3)·Multi-Task(§16.4)의 범위·명칭·구현 전략·
  Accept 조건은 이 ADR로 전혀 바뀌지 않는다.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface를
  정의하지 않았다.
- Resume 재검증, 저장 전 검증의 구체적 판정 기준, Retry/Alert/
  Recovery 정책, `call_engine()` 수정은 모두 이 ADR 이후에도 별도
  절차(후속 RFC/ADC, 또는 독립된 Dev HQ 개선 트랙)를 거쳐야 한다 —
  이 ADR 자체가 그 구현을 수행하지는 않는다. Production
  Code(`core/`, `hqs/`, `dashboard/`)는 전혀 수정하지 않는다.
- 이 Accept는 영구 고정이 아니다 — `ADC-0017` §Risks·재검토 조건이
  이 ADR 이후에도 그대로 유효하다.
- 이 ADR은 **승인되었으며**, §Decision에 정의된 실제 문서 변경이 이
  승인에 따라 실행된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(Scoped, Narrow)** — `BASELINE.md`
  §16에 Result Store 저장 게이트라는 새 책임이 매우 좁은 범위로
  처음 등재된다. Component 설계(§10 Out of Scope)에는 영향을 주지
  않는다 — 책임의 존재와 경계만 기록했을 뿐, 판정 기준·구현
  알고리즘은 여전히 미정이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경.
- **Kernel Impact**: **있음(제한적)** — Kernel Concept 목록에 이름
  없는 책임 하나가 추가됐으나(Execution Host·Multi-Task와 별개,
  Investment HQ 실증 사례 하나에 한정), 이것이 Component·Interface로
  구체화되려면 별도 ADR(판정 기준 확정 이후)이 필요하다.

## Governance Chain 검증

`RFC-0017`(Boundary Question만 개설, 판단은 후속 절차로 위임 —
개설 당시 Proposed, 이후 `ADC-0017` → 이 ADR로 Resolved) →
`ADC-0017`(Accept, Scoped·Narrow — 그 질문에 답함, Resume 재검증·
판정 기준·Retry 정책·`call_engine()` 수정·새 Component는 명시적으로
제외) → 이 ADR(Accepted — Baseline에 반영, 새로운 결정 추가 없음).
세 문서가 각각 인용하는 근거가 상위 문서의 범위를 벗어나지 않는지
확인했다.

- RFC-0017은 답을 제시하지 않고 질문만 열었다(§5) — 위반 없음.
- ADC-0017은 RFC-0017이 연 질문에만 답했고, RFC-0017이 제외한
  항목(구현 방법, Retry/Resume 책임 경계 확정, `call_engine()` 근본
  해결, Execution Host/Multi-Task 재론, Scheduler/Workflow
  orchestration, §6 넓은 정의, 새 Component)을 새로 확정하지 않았다
  (§Implementation Boundary "제외") — 위반 없음.
- 이 ADR은 ADC-0017의 Decision을 그대로 옮겼을 뿐, ADC-0017이
  판단하지 않은 것(Resume 재검증, 판정 기준 형태, Retry/Alert/
  Recovery 정책, `call_engine()` 수정, Execution Host/Multi-Task
  확장, §6 넓은 정의, ADC.md, Contract 신설)을 새로 결정하지 않았다
  (§Out of Scope) — 위반 없음. `diff` 검증 결과도 §6 Concept Model
  표·§14 Kernel Public Contract·§16.1~§16.4·`ADC.md`·Production
  Code·`IMPLEMENTATION_RULES.md` 어디에도 변경이 없음을 확인했다
  (§6 Migration Strategy).

## Self Review

- ADC-0017이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(Resume 재검증, 판정 기준·구현 알고리즘,
  Retry/Alert/Recovery 정책, `call_engine()` 수정, 새 Component/
  Interface/Contract, Execution Host/Multi-Task 확장, §6 넓은 정의,
  Development HQ에 컴포넌트 신설 요구, ADC.md, Production Code)는
  손대지 않았다.
- Multi-Task Result Store 저장 전 검증 게이트의 Scoped·Narrow
  Accept만 Baseline에 반영했는가 — **Pass**(§2 "Multi-Task Result
  Store — 저장 전 검증 게이트" 절) — 새로운 판단 기준을 추가하지
  않고 ADC-0017의 문구를 그대로 옮겼다.
- "저장 전 결과 유효성·무결성 검증 후 유효한 결과만 Checkpoint
  저장" 책임을 좁게 등재했는가 — **Pass**(§2 "책임" 문단).
- Investment HQ Checkpointer/`run_step`에 한정된 책임임을
  명시했는가 — **Pass**(§2 "Investment HQ Checkpointer/`run_step`에
  한정된 책임" 문단).
- Resume 시점 재검증을 결정했는가 — **아니오**(§2 "이 Accept가
  결정하지 않는 것" 문단, §Out of Scope).
- 자동 Retry/Alert/Recovery 정책을 결정했는가 — **아니오**(§2 동일
  문단, §Out of Scope).
- 구체적인 검증 기준이나 구현 알고리즘을 결정했는가 — **아니오**
  (§2 동일 문단, §Out of Scope).
- `call_engine()` 수정을 별도 Dev HQ 개선 트랙으로 유지했는가 —
  **Pass**(§2 "근본 원인과의 분리" 문단, §Out of Scope, §Consequences).
- 새로운 Component/Interface/Public Contract를 정의했는가 —
  **아니오**(§14 무변경, §Architecture/Contract/Kernel 영향).
- Execution Host/Multi-Task 범위와 §6 Runtime에 영향을 주었는가 —
  **아니오**(§2 "Multi-Task와의 경계" 문단, §3, §Governance Chain
  검증) — §16.3·§16.4 본문은 문자 그대로 유지했다.
- `IMPLEMENTATION_RULES.md` 변경 필요성을 ADC-0017 범위에서
  검토했는가 — **Pass**(§4) — 검토 결과 변경 대상이 없어 무변경으로
  결론냈고, 새로운 허용 범위를 임의로 확장하지 않았다.
- 문서 변경만 수행하고 Production Code는 수정하지 않았는가 —
  **Pass**(§1, §6 Migration Strategy 검증 절차) — `hqs/` 전체가
  무변경이다(선행 ADR들과 달리 `IMPLEMENTATION_RULES.md`조차 건드리지
  않았다).
- §6 "Runtime" 항목을 재명명·수정했는가 — **아니오**(§3) — `ADR-0004`
  §3·`ADR-0006` §3의 판단을 그대로 유지했다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- 새 최상위 절 또는 §16 내부 재배치 외의 변경을 했는가 — **아니오**.
  기존 §16.5를 §16.6으로 재배치했을 뿐, 다른 절은 재배치하지 않았다
  (§2).
- RFC-0017 → ADC-0017 → 이 ADR chain과 diff를 검증했는가 —
  **Pass**(§Governance Chain 검증, §6 Migration Strategy 검증
  절차).
