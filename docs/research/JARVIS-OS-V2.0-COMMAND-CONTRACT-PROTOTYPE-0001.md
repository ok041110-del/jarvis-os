# JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001: Command Contract Experimental Prototype — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, `BASELINE.md`를 수정하지
않는다.

**핵심 질문**: "Global Jarvis Chat이 HQ에 작업을 전달하기 위해
Command → Task → Context라는 별도 계층을 실제로 필요로 하는가?"

**핵심 결론**: 이번 Prototype 범위(단발 동기 read-only 명령, 2개
HQ)에서는 **Task와 Context 둘 다 관찰 가능한 이점을 제공하지
않았다.** Command → HQ Target → Snapshot(Case A)만으로 충분했고,
Command → Task → HQ(Case B)는 사용되지 않는 `task_id`/`status`
필드만 추가했다. Command 자체는 "raw_input → intent/target_hq
파싱" 구조가 필요했다 — 단순 문자열/함수 호출보다 유리한 지점(에러
사유 구분, HQ Isolation 테스트 가능성)이 실측됐다.

---

## 1. Objective

`JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001.md`가 Q6로 남긴
"Command/Task/Context 계층이 실제로 필요한가"를 검증한다.
Production Command Architecture를 확정하지 않는다.

---

## 2. Existing Evidence

Repository 조사 결과, Command/Task/Context/Conversation에 해당하는
기존 코드나 Contract는 **없다**(확인, `grep -rln "class Command\|
CommandContract\|class Task\b\|ConversationID"` 저장소 전체 0건).
`hqs/development/mvp/cli.py`, `hqs/investment/run.py`는 각각 실제
Engine을 호출하는 실행 진입점이며, Command Resolution 계층을 거치지
않는다 — 이번 Prototype이 처음으로 이 계층을 시험한다. 중복 생성
위험 없음을 확인.

`docs/architecture/core/STRUCTURE.md`는 저장소에 존재하지 않는다
(`STRUCTURE-V1.0-FROZEN.md`가 실제 Source of Truth) — 작업 지시가
언급한 경로와 실제 파일명이 다름을 확인하고 올바른 문서를 읽었다.

---

## 3. Prototype Boundary

- 위치: `projects/command-contract/`(격리).
- `hqs/`, `core/`, Production `dashboard/`, 기존 Runtime: **무수정**.
- 신규 dependency: **0개**(stdlib만 사용).
- 의존: `projects/unified-dashboard/`의 읽기 전용 Snapshot Builder
  (Prototype 간 연결, Production External Interface Contract
  아님 — 작업 지시 §12). 이 Prototype은 `claude/unified-dashboard-
  prototype` 브랜치 위에서 작업했다(해당 브랜치가 아직 main에
  merge되지 않았으므로, 이 Prototype도 그 의존을 명시적으로
  브랜치 계보로 반영했다).
- 실제 Production Workflow(Engine 호출)를 실행하지 않는다 — 전부
  read-only intent(`show_status`)만 다룬다.

---

## 4. Command Model

**최종 필드**: `Command(raw_input, intent, target_hq)`,
`CommandResult(status, reason, hq_identity, detail)`.

**Evidence 없이 넣지 않은 필드**(작업 지시 §5):

| 필드 | 판정 | 근거 |
|---|---|---|
| `command_id` | **NOT REQUIRED**(이 Prototype 범위) | §9 Q1/§테스트 8 — 단일 동기 요청-응답 흐름에서 ID를 조회·상관시키는 코드가 어디에도 필요하지 않았다(`test_command_has_no_id_field_and_resolution_still_works`) |
| Agent ID | **NOT REQUIRED** | Command Layer가 Agent를 직접 호출하지 않으므로(Boundary) Agent 식별자를 가질 이유가 없다 |
| Context ID | **FUTURE** | §7에서 판정 — 이번 범위에서 상태 보존 요구가 관찰되지 않음 |
| Task ID | **EXPERIMENTAL로만 존재**(Case B 비교용) | §6에서 판정 — Case A에는 없음 |
| Permission | **NOT REQUIRED** | 이번 Prototype은 read-only 단일 사용자 가정, Permission 분기가 필요한 시나리오가 없었다 |
| Priority | **NOT REQUIRED** | 동시 다중 Command 큐잉 시나리오를 다루지 않음(Multi-HQ Execution 자체가 금지 목록, §13) |
| Dependency | **NOT REQUIRED** | 단발 명령 간 순서 의존성이 관찰되지 않음(§9 Multi-HQ 순차 테스트에서 독립성 확인) |

`target_hq`는 사용자가 직접 채우는 필드가 아니라 Resolver가
`raw_input`에서 파싱한 결과다(Q2 검증을 위해 "입력"과 "파싱 결과"를
의도적으로 분리).

---

## 5. Command → HQ Resolution

**흐름(Case A)**: `raw_input → parse_command() → Command(intent,
target_hq) → resolve() → HQ Snapshot Builder → CommandResult`.

**실측(`demo.py` 실행 결과)**:

```
> Development HQ 상태를 보여줘
  status=ok hq=Development HQ (Phase/Workflow/Agent Roles/Latest Validation/Current Task 5개 항목)

> Investment HQ 최신 상태를 보여줘
  status=ok hq=Investment HQ (Stock/Dividend Stock/ETF 3개 Team 상태)

> Trading HQ 상태를 보여줘
  status=invalid reason=unknown_hq

> Development HQ에서 주문을 실행해줘
  status=invalid reason=unsupported_intent
```

**Q1 판정**: 독립 Command Model이 문자열/함수 호출 직접 처리보다
유리한 지점이 실측됐다 — `unknown_hq`(HQ 인식 실패)와
`unsupported_intent`(HQ는 인식했지만 지원 안 하는 요청)를 **구분된
사유**로 반환할 수 있었다. 단순 `if/elif` 문자열 매칭이었다면 이
구분 자체는 가능했겠지만, `Command`/`CommandResult` 구조가 이
구분을 테스트로 강제할 수 있게 했다(`test_unknown_hq_returns_invalid`
vs `test_unknown_command_returns_invalid`가 서로 다른 `reason`을
독립적으로 검증). **판정: EXPERIMENTAL**(이 Prototype 범위에서
유용성 실증, Production Contract로 Freeze할 근거는 아직 부족 —
표본이 read-only 단일 intent 하나뿐).

**Q2 판정**: `target_hq`를 별도 필드로 분리한 것이 HQ Isolation
테스트(§8)를 가능하게 했다 — Command가 파싱한 target이 명시적
값이므로 "Dev Command가 Investment 데이터에 접근하지 않는다"를
직접 assert할 수 있었다. **판정: EXPERIMENTAL**(분리가 유용했음을
실증, 그러나 2개 HQ·1개 intent 표본으로 Production Contract 확정은
이르다).

---

## 6. Command → Task Evaluation

Case A와 Case B를 동일 입력("Investment HQ 최신 상태를 보여줘")으로
비교했다(`test_task_wrapping_adds_no_observable_value_for_single_readonly_command`).

| 비교 항목 | Case A(Command→HQ) | Case B(Command→Task→HQ) |
|---|---|---|
| 결과 값 | `CommandResult` | 동일한 `CommandResult`(`task.result`) |
| 추가된 것 | 없음 | `task_id`(UUID, 이후 어디서도 조회되지 않음), `status`(pending→completed/failed, 이후 어디서도 재조회되지 않음) |
| 실행 시간/동작 차이 | 없음 | 없음(완전 동기, 즉시 완료) |

작업 지시 §9가 예시한 Task의 잠재적 이점(상태 추적/실행 단위
식별/결과 연결/재실행/진행 상태/실패 상태)을 하나씩 대조:

- **상태 추적**: read-only 단발 명령은 실행 시간이 사실상 0이라
  "진행 중" 상태를 관찰할 대상 자체가 없었다.
- **실행 단위 식별**: `task_id`가 생성되지만 이를 나중에 조회하는
  코드/시나리오가 이 Prototype에 없었다 — 식별할 필요가 아직
  발생하지 않았다.
- **결과 연결**: `CommandResult`가 이미 동기 반환값으로 직접
  연결되므로 별도 연결 메커니즘이 불필요했다.
- **재실행**: 이번 Prototype은 매 호출이 stateless(§7)이므로
  "재실행"과 "새 호출"이 구분되지 않았다.
- **진행 상태/실패 상태**: `status`는 `completed`/`failed` 둘 중
  하나로 즉시 확정되며, `resolve()`의 반환값(`CommandResult.status`)
  과 정보가 100% 중복됐다.

**Q3 판정**: **NOT REQUIRED**(이 Prototype 범위) — Task가 실제
독립 책임을 가진다는 Evidence를 찾지 못했다. Command → HQ 구조를
유지한다(작업 지시 §9 원칙 그대로 적용). 단, 이 판정은 "read-only
단발 동기 명령"이라는 범위에 한정된다 — 실제 Workflow 실행(비동기,
장시간, 재시도 가능)이 Command 대상이 되는 순간 이 결론은 재검증
대상이다(§14).

---

## 7. Context Evaluation

`test_multi_hq_sequential_commands_do_not_require_shared_state`로
검증: Dev Command → Investment Command → 동일 Dev Command를 순차
실행했을 때, 세 번째 호출(첫 번째와 동일 입력)의 결과가 첫 번째와
**완전히 동일**했다 — 중간에 실행된 다른 HQ Command가 결과에 어떤
영향도 주지 않았다. 각 Command는 파일 시스템의 현재 상태만 읽는
순수 함수처럼 동작했다.

**Q4 판정**: **NOT REQUIRED**(이 Prototype 범위) — "같은 Command가
실행될 때 보존해야 할 이전 상태/정보"가 관찰되지 않았다. Context는
Command → HQ → Snapshot만으로 충분했다. Command → Task → Context →
HQ 구조로 승격할 근거가 없다 — Architecture Candidate로도 기록하지
않는다(작업 지시 §10 원칙: "실제로 필요해지는 경우에만 Candidate로
기록").

---

## 8. HQ Isolation

`test_hq_isolation_dev_and_investment_do_not_cross_reference`로
검증: Dev HQ 결과 텍스트에 "Investment"/"Trader" 문자열이 없고,
Investment HQ 결과 텍스트에 "Stage"/"Agent Roles" 문자열이 없음을
확인 — 두 HQ의 `detail`이 서로 침범하지 않는다.

추가로 `test_resolver_does_not_import_hq_or_kernel_code_directly`
(AST 기반)가 `resolver.py`가 `hqs`/`core`/`mvp`를 import하지 않음을
자동 검증한다 — Command Layer가 HQ Business Logic을 소유하지 않는다
(작업 지시 §11 금지 사항 준수, 테스트로 강제).

---

## 9. Validation

### Functional (8건 최소 요구 중 실제 작성 11건)
1. Development Command → Development HQ — PASS
2. Investment Command → Investment HQ — PASS
3. Unknown HQ("Trading HQ") — PASS(`reason=unknown_hq`)
4. Unknown Command(인식 안 되는 intent + 인식되지만 미지원 intent) — PASS(`reason=unknown_command` / `unsupported_intent` 구분)
5. Command → Snapshot 연결(동일 데이터 재사용 확인) — PASS
6. Command → Task 필요성 비교(Case A vs Case B) — PASS(§6)
7. HQ Isolation(내용 격리 + import 격리) — PASS(§8)
8. Command ID 필요성(없어도 동작) — PASS

### Boundary
- Engine 직접 호출 없음 — PASS(`grep call_engine` 소스 0건, 테스트 문자열 제외).
- Agent 직접 호출 없음 — PASS.
- Kernel 의존성 없음 — PASS(`core/` import 0건).
- `hqs/*` 직접 의존 없음 — PASS(AST 테스트).

### Regression
`projects/`에 완전히 격리(§3), `hqs/`·`core/`·Production `dashboard/`
무수정 확인 후 전체 회귀 1회 실행: **298 passed**(unified-dashboard
Prototype 포함 기존 287 + 신규 11, 0 failed) — 회귀 없음.

---

## 10. Evidence Generated

| 요소 | 판정 |
|---|---|
| Command(독립 Model) | **EXPERIMENTAL** — 유용성 실증(§5 Q1), Production Contract Freeze는 이름/에러 사유 등 표본 부족으로 아직 이름 |
| Task | **NOT REQUIRED**(이 Prototype 범위) — §6 |
| Context | **NOT REQUIRED**(이 Prototype 범위) — §7 |
| HQ Target(공통 모델) | **EXPERIMENTAL** — `target_hq: str` 하나로 2개 HQ 모두 충분, Contract화는 이름/스키마 확정 필요 |
| Multi-HQ(하나의 Command가 여러 HQ 동시 대상) | **NOT REQUIRED** — 순차 실행만으로 충분했고 동시 실행 필요성이 관찰되지 않음(작업 지시 §13 그대로 준수, 구현하지 않음) |
| Dashboard 연결(Command 결과를 Dashboard가 소비) | **EXISTING(Prototype 간)** — `unified-dashboard`의 Snapshot Builder를 그대로 재사용해 성립, 추가 Adapter 불필요 |

---

## 11. Architecture Findings

- **Command Resolution이 실제로 독립된 책임임을 확인**했다 — "raw
  input에서 HQ/intent를 분리해 파싱하고, 실패 사유를 구분해
  반환한다"는 것은 단순 `if raw.startswith(...)` 스타일 처리보다
  테스트 가능성과 에러 명확성에서 우위가 있었다(§5).
- **Task와 Context는 이번 범위에서 순수 오버헤드였다** — 추가된
  필드(`task_id`, `status`)가 어디서도 소비되지 않았다(§6). 이는
  "Task/Context가 영원히 불필요하다"는 뜻이 아니라, **read-only
  단발 동기 명령이라는 범위 안에서** 불필요하다는 뜻이다 — 실제
  Workflow 실행(비동기·장시간·재시도)이 Command 대상이 되면 이
  결론은 자동으로 무효화되며 재검증이 필요하다(§14).
- Dashboard Prototype과의 연결이 **Adapter 없이** 성립한 것은
  두 Prototype이 이미 같은 원칙(읽기 전용, HQ Business Logic
  미소유)으로 설계됐기 때문이다 — 이는 우연이 아니라
  `ARCHITECTURE_GOVERNANCE.md`의 Experimental Implementation 절
  조건(기존 Contract 보호, HQ production path 무단 연결 금지)이
  두 Prototype 모두에 일관되게 적용된 결과다.

---

## 12. Kernel Impact

**없음.** `core/` 어디에도 의존하지 않았다(§9 Boundary). Task
Scheduler/Dependency Resolver/Worker Manager/Event Bus/Runtime/
Memory Engine 중 어느 것도 만들지 않았다(작업 지시 §17 금지 목록
준수). Cross-HQ 공통 Responsibility가 실제로 확인된 바 없으므로
**KERNEL CANDIDATE는 임의로 생성하지 않는다**(작업 지시 §16 원칙).
Phase 7은 이 Prototype으로 재개되지 않는다.

---

## 13. Governance Impact

- RFC/ADC/ADR: **불필요** — Experimental Implementation 절의 허용
  범위(격리 Prototype, HQ production path 무단 연결 금지, 성공/실패
  기준 기록) 안에서 진행됐다.
- 이번 Prototype의 Evidence(§10)는 그 존재만으로 Formal Architecture
  Decision이나 Kernel 승격을 발생시키지 않는다
  (`ARCHITECTURE_GOVERNANCE.md` L43 재적용).
- `BASELINE.md`, Structure v1.0, Dev HQ/Investment HQ Freeze 문서:
  **무수정**.

---

## 14. Next Step

**Production Command API로 승격하지 않는다**(작업 지시 §22). 이
Prototype이 답하지 못한 것:

- **비동기/장시간 Command**: 이번엔 전부 즉시 완료되는 read-only
  조회였다 — 실제 Workflow 실행(Dev HQ Stage 트리거, Investment HQ
  Team 실행처럼 수십 초~수 분 걸리는 작업)을 Command 대상으로 삼는
  순간 Task의 필요성(§6 결론)이 달라질 가능성이 높다. **이것이
  다음으로 검증해야 할 가장 중요한 Gap이다.**
- **Multi-HQ 동시 실행**: 순차 실행만 검증했다(작업 지시가 명시적
  금지). 동시 실행 Need가 실제로 관찰되면 별도 Prototype 대상.
- **HQ가 3개 이상(Trading HQ 포함)일 때** `target_hq` 문자열 매칭
  방식이 계속 충분한지 미검증.

**후보(우선순위 미확정)**:
1. 비동기/장시간 Command Prototype(Dev HQ 실제 Stage 트리거를
   read-only가 아닌 방식으로 다룰 때 Task 필요성 재검증) — 단, 이는
   실제 Engine 호출을 포함하므로 별도의 더 엄격한 Experimental
   Boundary 검토가 선행되어야 한다.
2. Trading HQ 등장 시 `HQSnapshot`/`target_hq` 3-HQ 재검증(Dashboard
   Prototype의 Next Step과 동일 트리거).

---

## Self Review

- Production Command API/Task Engine/Context Engine을 구현했는가 —
  **아니오**.
- Global Orchestrator/Scheduler/Dependency Resolver/Worker Manager/
  Event Bus/Runtime/Memory Engine/Agent Manager/Kernel Component를
  만들었는가 — **아니오**.
- 실제 Trade Execution/Investment Order/Dev HQ Workflow를
  실행했는가 — **아니오**(전부 read-only 조회).
- Production Dashboard를 변경했는가 — **아니오**.
- Evidence 없이 Agent ID/Context ID/Permission/Priority/Dependency
  필드를 추가했는가 — **아니오**(§4에서 전부 NOT REQUIRED로 명시
  배제).
- Multi-HQ Execution을 구현했는가 — **아니오**(순차 실행만).
- Task/Context를 "필요할 것 같다"는 이유로 만들었는가 — **아니오**
  (§6·§7에서 NOT REQUIRED 판정, 실제 비교 실험으로 근거 확보).
- Kernel Candidate를 임의로 만들었는가 — **아니오**(§12).
- 전체 회귀 테스트를 실제로 실행했는가 — **예**(298 passed, §9).

---

## 최종 보고

1. **무엇을 구현했는가**: `projects/command-contract/` 격리
   Prototype — Command → HQ Target → Snapshot(Case A)과 Command →
   Task → HQ(Case B)를 나란히 구현해 비교.
2. **실제 어떤 Command를 사용했는가**: read-only intent
   `show_status` 하나 — "Development/Investment HQ 상태를 보여줘"
   (실제 실행 성공), "Trading HQ..."(unknown_hq), "...주문을
   실행해줘"(unsupported_intent).
3. **Command Model이 필요했는가**: 예 — `Command`/`CommandResult`
   구조가 에러 사유 구분·HQ Isolation 테스트를 가능하게 했다
   (EXPERIMENTAL 판정).
4. **Task가 필요했는가**: **아니오** — 이 Prototype 범위에서
   `task_id`/`status`가 소비되지 않았다(NOT REQUIRED).
5. **Context가 필요했는가**: **아니오** — 순차 명령 간 상태 보존
   Need가 관찰되지 않았다(NOT REQUIRED).
6. **HQ Isolation이 검증됐는가**: 예 — 내용 격리(텍스트 교차 없음)
   + 구조 격리(`hqs/*` import 없음) 둘 다 테스트로 확인.
7. **Dashboard와 연결이 필요한가**: 예, 그리고 Adapter 없이 이미
   성립했다 — `unified-dashboard`의 Snapshot Builder를 그대로
   재사용.
8. **생성된 Evidence**: §10 표 전체(Command/Task/Context/HQ
   Target/Multi-HQ/Dashboard 6개 요소 판정).
9. **Architecture Candidate 발생 여부**: 약한 후보 없음 — Command
   자체는 EXPERIMENTAL(승격 근거 부족), 나머지는 NOT REQUIRED.
10. **Kernel Impact**: 없음.
11. **Governance Impact**: 없음(Experimental Implementation 범위,
    신규 RFC/ADC/ADR 불필요).
12. **Production 승격 가능 여부**: **아니오** — 비동기/장시간
    Command라는 핵심 Gap이 미검증(§14).
13. **다음 Implementation**: 비동기/장시간 Command Prototype(Task
    필요성 재검증) 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위
    미확정.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음(`projects/command-contract/`만 신규 추가, `hqs/`·`core/`·`dashboard/` 무수정)
Tests: `projects/command-contract/tests/` 11 passed(신규), 전체 저장소 298 passed(기존 287 + 신규 11, 0 failed, 회귀 없음)
E2E: 해당 없음(read-only 파일 기반 Prototype, Engine 호출 없음)
RFC: 없음(Experimental Implementation 범위 — 불필요)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 작업 커밋 예정)
Branch: `claude/command-contract-prototype`(`claude/unified-dashboard-prototype` 위에서 작업 — 아직 main에 merge되지 않은 두 Prototype 브랜치가 계보로 연결됨, §16 참조)
Next Implementation Candidate: 비동기/장시간 Command Prototype(Task 필요성 재검증) 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정
