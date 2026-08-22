# PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001: Parallel Execution의 Kernel Component 배치 판단

**문서 성격**: Architecture 설계 판단 기록이다. **이 문서는 코드를 작성·수정하지 않는다.** Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze / `core/` / `hqs/` 어느 것도 수정하지 않는다. Registry/Scheduler/Runtime/Engine Gateway를 만들지 않는다. Phase 6 PASS(도메인 독립성 실증)를 Migration 승인으로 간주하지 않는다.

## 목적

Phase 6에서 확정한 Kernel Candidate("Parallel Execution 원시 기법")을 (1) 기존 `core/execution/` 내부 책임으로 편입할지, (2) 별도 Kernel Component로 둘지, (3) 기존 `core/execution/` 자체를 재검토해야 하는지 판단한다. 근거는 Structure v1.0, `BASELINE.md` §16.2, `PHASE4-HQ-CROSS-VALIDATION-0001.md`, `PHASE5-KERNEL-CANDIDATE-0001.md`, Phase 6 Prototype Evidence로 한정한다.

## 1. Current Execution(`core/execution/pipeline.py`) 책임 분석

`run_execution_layer_pipeline()`은 `ExecutionRequest → PromptSpecification → ModelRequest → ExecutionHandle → ExecutionState → ExecutionResult` 6개 Builder(MVP-0001~0006)를 순서대로 호출하는 순수 함수다. `request_id`/`handle_id`는 SHA-256 해시로 결정론적으로 유도하며, 시스템 시계·난수·실제 I/O를 쓰지 않는다.

결정적 근거: `core/execution/tests/test_pipeline.py`의 `test_no_ai_or_runtime_symbols_present_in_module()`이 `inspect.getsource(pipeline)`에서 `call_engine`/`subprocess`/`requests.`/`openai`/`anthropic`/`urllib`/`http.client`/`datetime.now`/`uuid.uuid4`/`time.time`이 **소스에 존재하지 않음을 테스트로 강제**한다. 즉 이 모듈은 실제 Model/Engine 호출을 자신의 계약(테스트)으로 명시적으로 배제하고 있다 — "아직 안 만듦"이 아니라 "만들지 않기로 계약된" 상태다.

`PHASE4-HQ-CROSS-VALIDATION-0001.md`가 이미 확인한 대로 Dev HQ/Investment HQ 어느 실제 코드에서도 이 모듈을 import하지 않는다(0건). → **책임: Specification/Artifact 구성. 실제 호출은 범위 밖으로 자체 배제.**

## 2. Parallel Execution Prototype 책임 분석

`ThreadPoolExecutor.submit()`+`.result()`로 독립 Task 각각을 실제 `subprocess.run(["claude", ...])`으로 동시 호출하는 기법이다(Phase 6 `engine_caller.py`/`run_prototype.py`). Artifact 변환·Specification 구성은 하지 않는다 — 완성된 Prompt를 입력으로 받아 실제 프로세스를 실행하고 결과 텍스트를 반환한다. 상태를 보관하지 않지만 실제 부작용(프로세스 실행)이 있다.

→ **책임: 실제 Execution(Engine 호출) 자체의 동시성 Dispatch. Artifact 구성은 범위 밖.**

## 3. Component Boundary 비교표

| 항목 | `core/execution/pipeline.py` | Parallel Execution 원시 기법 |
|---|---|---|
| 책임 범위 | Specification → Result Artifact 변환(6 Builder) | 독립 Task를 동시에 실제 Engine 호출 |
| 실제 Engine 호출 | 없음 — 테스트로 명시적 금지(`call_engine`/`subprocess` forbidden) | 있음 — `subprocess.run` 직접 호출 |
| 상태/부작용 | 없음(순수 함수, 결정론적 ID) | 있음(실제 프로세스 실행, I/O, 타임아웃) |
| 동시성 | 없음 | `ThreadPoolExecutor` 기반 동시 호출 |
| HQ 실사용 | 0건(Dev/Investment 어디서도 import 안 됨) | 2개 HQ 프로덕션 + Prototype 3번째 독립 맥락에서 반복 확인 |
| Structure v1.0 디렉터리 대응 | `core/execution/`(줄 55: "Capability를 실제로 실행하는 Execution Layer")과 이름·경로 일치 | 이름 매핑 없음 — 원시 기법, 소속 디렉터리 미정 |
| §16.2 Accept 범위 내 위치 | 경계 내부(Specification 변환 부분만) | 경계 내부이나 "내부 구조"(Multi-Model Routing·재시도 정책과 동일 성격)로 Open 처리된 영역 |

두 책임은 이름("Execution")은 같지만 실제 코드 수준에서 겹치지 않는다 — 하나는 Artifact를 만들고, 하나는 그 결과물(또는 그에 준하는 Prompt)을 실제로 실행한다. `pipeline.py`는 스스로의 계약 테스트로 실제 호출을 금지하고 있으므로, 두 책임을 무비판적으로 합치면 기존 테스트 계약을 깨뜨린다.

## 4. Execution Specification/Artifact 구성 vs 실제 Execution/Parallel Dispatch 구분

- **Specification/Artifact 구성**: `core/execution/pipeline.py`의 전체 범위. 입력을 받아 다음 Artifact를 결정론적으로 만들어내는 것으로 끝난다.
- **실제 Execution/Parallel Dispatch**: Phase 6 Prototype의 전체 범위. 완성된 Prompt를 실제로 Engine에 넘기고(단일 또는 동시), 결과를 회수한다.

`BASELINE.md` §16.2가 선언한 Execution Layer Kernel Module의 책임("Development HQ가 만든 Implementation Specification을 입력으로 받아, 코드 생성·실행·테스트, Model/Engine 선택·호출까지의 경계")은 **이 두 구분을 모두 포함**한다 — "선택·호출까지"라는 문구가 실제 Dispatch까지 Kernel Module 경계 안에 있음을 명시한다. 다만 "내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model Routing)"는 여전히 Open이라고 못박았다 — 동시성 Dispatch 전략은 이 "내부 구조" 목록과 동일한 성격(호출을 "어떻게" 할지의 정책)이므로, 명시적으로 나열되지 않았을 뿐 같은 Open 범주로 판단한다.

## 5. Kernel Component 경계와 책임 정의(제안)

- **Specification/Artifact Component**(기존 `core/execution/pipeline.py`): Specification → Result Artifact 변환 전담. 실제 호출 금지 계약 유지.
- **Dispatch Component**(신규, 명칭 미정): 완성된 Prompt(들)를 실제로 Engine에 호출·회수하는 전담. 단일 호출과 동시 호출(Parallel Execution 원시 기법)을 모두 포함할 수 있는 자리.

두 Component는 순서 관계(Specification 완료 → Dispatch 수행)이지 대체 관계가 아니다.

## 6. 최종 Architecture 선택안: **B. ARCHITECTURE DESIGN REQUIRED**

판단 근거:
1. 기존 `core/execution/`과 신규 Candidate의 관계가 코드·계약 수준에서 확정되지 않았다(§3·§4) — 사용자가 제시한 steering rule("관계가 확정되지 않았다면 B를 우선")에 해당.
2. §16.2 Accept는 이미 "선택·호출까지"를 Kernel Module 경계 안으로 선언했으므로 **완전히 새로운 영역(A도 아니고 C도 아님)** — Migration을 지금 바로 실행할 만큼 Interface가 정의되어 있지 않다(A 아님). 동시에 Kernel 소속 자체는 §16.2·Structure v1.0 Core Domain Model(`...→Execution→Provider/Tool/MCP`)이 이미 시사하므로 "관련 없음/판단 불가"(C)도 아니다.
3. `pipeline.py`의 자체 계약 테스트(`call_engine`/`subprocess` 금지)를 깨지 않고 Dispatch 책임을 어디에 어떻게 붙일지는 코드 작성이 아니라 **설계 결정**이 먼저 필요하다.

## 7. Interface/Dependency 방향(제안, 미구현)

- 방향: `ExecutionResult`(또는 Dispatch가 필요로 하는 최소 형태의 Prompt/Specification) → Dispatch Component가 이를 입력으로 받아 실제 호출을 수행하는 단방향 의존을 제안한다. 역방향(Dispatch가 Builder를 직접 호출)은 책임 역전이므로 배제 제안.
- Dispatch Component는 `pipeline.py`의 내부 Builder 구현을 몰라도 되도록, 좁고 안정된 텍스트 Interface(문자열 입력 → 문자열 출력)만 의존하는 것을 제안한다. 구체 시그니처 채택은 RFC에서 다룬다.
- HQ의 `call_engine()`(Kernel Engine Port/Adapter 책임으로 §16.2 근거 문서에 이미 언급됨, `PHASE9-CLOSURE-0001`이 실제 추출은 Defer)과의 관계도 이 RFC 범위 안에서 함께 정리가 필요하다는 점만 기록한다 — `PHASE9-CLOSURE-0001`의 기존 판정을 재론하지 않는다.

## 8. 기존 `core/execution/` 처리 방향

**그대로 유지한다. 재작성·흡수·수정하지 않는다.** 이 모듈은 자기 계약(테스트)으로 실제 호출을 명시적으로 배제하고 있으므로, 이번 판단만으로 이 모듈을 확장해 호출 로직을 넣는 것은 승인되지 않는다. "이 모듈이 최종적으로 Dispatch 앞단(Specification 전용)으로 남을지, 계약을 넓혀 Dispatch까지 포함할지"는 향후 RFC에서 별도로 결정해야 한다.

## 9. Migration 범위(제안, 이번 단계에서 구현하지 않음)

RFC 승인을 전제로 한 최소 범위 제안:
- 신규 하위 구조(가칭 `core/execution/dispatch/` 또는 별도 Kernel 하위 Component)를 신설해 Parallel Execution 원시 기법을 이관한다. `pipeline.py`는 수정하지 않는다.
- Dev HQ/Investment HQ의 기존 `call_engine()`/`ThreadPoolExecutor` 코드를 즉시 치환하지 않는다 — Migration은 Interface가 RFC에서 확정된 이후 별도 단계로 다룬다.
- Checkpointing은 이번 Migration 범위에서 명시적으로 제외한다(`PHASE5-KERNEL-CANDIDATE-0001.md` 판정 유지, Investment-specific).

## 10. Governance 필요 여부: **필요 — RFC → ADC → ADR**

`BASELINE.md` §16.2 Execution Layer는 이미 `ADR-0002-execution-layer-module-baseline.md`로 Accept된 Kernel Module이다. 그 "내부 구조"(Open 영역)를 구체화하는 것 — 즉 동시성 Dispatch 전략을 Kernel Module 안에 채워 넣는 것 — 은 Frozen Architecture의 미결 영역을 확정하는 일이므로, CLAUDE.md의 Frozen Architecture 규칙에 따라 RFC 없이 직접 반영할 수 없다. Phase 6 PASS는 "기법이 도메인에 종속되지 않고 유효하다"를 실증했을 뿐, "어디에 배치할지"는 Architecture 결정이며 이 문서가 대신 확정하지 않는다.

## Phase 7 판정: **PASS**

Phase 7이 요구한 조사·비교·판단(현재 Execution 책임 분석, Candidate 책임 분석, Boundary 비교, 최종 선택안, Interface 방향 제안, 기존 모듈 처리 방향, Migration 범위 제안, Governance 필요 여부)을 모두 근거와 함께 완료했다. 결론은 **B. ARCHITECTURE DESIGN REQUIRED**이며, 코드/Migration은 후속 RFC 승인 전까지 보류한다.

## 다음 작업(1개, 이번 세션에서 착수하지 않음)

RFC 초안 작성 — "Parallel Execution 원시 기법의 `core/execution/` 내부(또는 인접) 배치와 Dispatch Component Interface"를 다루는 RFC를 `docs/decisions/rfc/`에 제안한다. 사용자의 명시적 지시 없이는 착수하지 않는다.

---

## Architecture/Governance 영향

**없음.** Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze / `core/` / `hqs/` 어느 것도 수정하지 않았다. Registry/Scheduler/Runtime/Engine Gateway를 만들지 않았다. Migration을 수행하지 않았다. 새 RFC/ADC/ADR을 작성하지 않았다(다음 작업으로만 제안). `PHASE9-CLOSURE-0001`의 기존 판정을 재론하지 않았다.
