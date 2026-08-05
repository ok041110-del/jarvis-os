# ADR-0006: Connector Execution Model

- 날짜: 2026-08-03
- 상태: **Accepted**

---

## 배경 (Context)

Phase 4(Connector Adapter — MCP)에 착수하기 전, 현재 코드를 조사했다.

1. `packages/core/src/jarvis_core/ports/i_connector.py`는 `IConnector.call_tool(tool_name,
   arguments) -> Any`라는 최소 시그니처만 가지고 있다. 요청/응답에 대한 Domain Model이
   없고, 반환 타입이 `Any`다.
2. `adapters/connector-mock/.../connector.py`(현재 실사용)는 고정 응답을 반환할 뿐
   Timeout/Retry/Cancellation/Idempotency/Failure 중 어떤 것도 다루지 않는다 — "Agent
   → MCP 호출 경로 자체가 실제로 발생하는가"만 검증하는 Walking Skeleton이다.
3. `adapters/connector-mcp/.../mcp_connector.py`는 docstring만 있고 구현이 비어 있다
   — Phase 4가 채워야 할 대상.
4. `apps/poc-runner/main.py`의 `run_organization_layer`(Stage 8)가 Connector를
   호출하는 유일한 지점이다: `connectors[tool].call_tool(tool, {"query": ...})`.
   이 호출은 Team이 아니라 사실상 `main.py`가 Agent 대신 대행하고 있다 — 실제로는
   "Agent가 Connector를 호출한다"는 개념이 아직 코드로 구체화되지 않았다.
5. `docs/architecture/v1.0/04-policy-engine.md`는 "Agent→MCP" 지점을 미래의 PEP
   (Policy Enforcement Point) 후보로 이미 언급했으나(ADR-0005 결정 2에서도 재확인),
   아직 코드로 존재하지 않는다. 이번 ADR과 Phase 4는 그 PEP를 새로 만들지 않는다 —
   범위 밖이다.

이 ADR은 Connector라는 Domain 개념 자체(책임, 요청/응답 모델, 실행 정책)를 확정한다.
MCP는 그 Domain을 만족시키는 구현체 중 하나일 뿐이며, MCP SDK의 세부 사항(전송 방식,
JSON-RPC 메시지 형태 등)은 이 ADR에 포함하지 않는다 — 그건 `adapters/connector-mcp`
내부의 구현 디테일이다.

## 결정 (Decision)

### 결정 1 — Connector의 책임: 단일 도구 호출의 실행, 그 이상도 이하도 아니다

Connector는:

- **무엇을 할지 결정하지 않는다.** 어떤 도구를, 어떤 인자로 호출할지는 Agent(호출자)의
  결정이다. Connector는 전달받은 `ToolRequest`를 그대로 실행할 뿐이다.
- **결과를 해석하지 않는다.** 도구 호출 결과가 "시장 리서치가 끝났다"는 의미인지
  "코드 리뷰가 통과했다"는 의미인지 Connector는 모른다. `ToolResponse`를 Agent에게
  돌려주면 그걸로 끝이다.
- **허용 여부를 판단하지 않는다.** "이 Agent가 이 도구를 호출해도 되는가"는 Policy
  Engine(PDP)의 몫이다(ADR-0005). Connector는 Policy 판단이 이미 끝난 뒤에만 호출된다는
  전제로 동작하며, 자체적으로 권한을 검사하지 않는다.
- **한 번의 시도만 책임진다** (결정 4에서 상술).

### 결정 2 — MCP Adapter의 책임

`adapters/connector-mcp`는 `IConnector`를 MCP(Model Context Protocol) SDK로 구현하는
Adapter다. 이 Adapter만의 책임:

- `ToolRequest`(Domain Model)를 MCP 프로토콜이 요구하는 메시지 형태로 변환
- MCP 서버(공식 레퍼런스 filesystem/fetch)와의 실제 통신 수행
- MCP 응답(또는 MCP 프로토콜 자체의 오류·타임아웃·연결 실패)을 `ToolResponse`(Domain
  Model)로 변환 — 예외를 던지지 않고 항상 `ToolResponse`를 반환한다(결정 7, ADR-0005
  결정 4의 Fail-Closed 패턴을 Connector에 동일 적용)
- MCP 세션/연결 관리(연결 수립, 재사용, 종료)

Core와 Agent는 이 목록의 어떤 것도 알지 못한다.

### 결정 3 — Tool Request 모델 (Domain Model, Core 소속)

```python
@dataclass
class ToolRequest:
    tool_name: str
    arguments: dict[str, Any]
    timeout_ms: int = DEFAULT_TIMEOUT_MS   # 결정 5
    idempotency_key: str | None = None      # 결정 8
```

`DEFAULT_TIMEOUT_MS`는 Core 상수다(어떤 Adapter를 쓰든 기본 타임아웃은 Domain이
정한다 — ADR-0005 결정 3에서 "Tier는 Adapter가 아니라 Core가 정의한다"고 한 것과
동일한 원리). `arguments`는 Connector 입장에서 불투명한(opaque) 값이다 — Connector는
그 내용을 해석하지 않고 그대로 전달한다.

### 결정 4 — Tool Response 모델 (Domain Model, Core 소속)

```python
class ToolCallStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"     # 도구가 실행됐지만 실패를 응답함 (예: 파일 없음)
    TIMEOUT = "timeout"     # 결정 5의 시간 내에 응답을 받지 못함
    CANCELLED = "cancelled" # 호출자가 결과를 기다리지 않기로 결정함 (결정 6)


@dataclass
class ToolResponse:
    status: ToolCallStatus
    result: Any | None = None
    error: str | None = None   # SUCCESS가 아닐 때 반드시 채워짐 (No Silent Failure)
```

`SUCCESS`와 `FAILURE`를 구분하는 이유: "도구 호출 자체가 실행되지 않음"(연결 실패,
타임아웃)과 "도구는 정상 실행됐으나 그 결과가 실패"(예: 존재하지 않는 파일 조회)는
Agent 입장에서 다른 대응이 필요하다 — 전자는 재시도 가치가 있을 수 있지만 후자는
재시도해도 결과가 바뀌지 않는다. 이 구분을 Domain Model에 명시적으로 남긴다.

### 결정 5 — Timeout 정책

- 모든 `ToolRequest`는 반드시 `timeout_ms`를 가진다(기본값 = Core 상수). "타임아웃
  없음"은 허용하지 않는다 — 무한 대기는 Kernel 전체를 블로킹할 수 있으므로 Architecture
  차원에서 금지한다.
- Adapter는 이 시간 내에 응답하지 못하면 `ToolResponse(status=TIMEOUT, ...)`을
  반환해야 한다. 시간을 넘겨서까지 내부적으로 계속 기다리는 것은 계약 위반이다.
- 구체적인 타임아웃 구현 메커니즘(스레드 인터럽트, asyncio 타임아웃, MCP SDK 자체
  타임아웃 옵션 등)은 Adapter의 선택이다 — Architecture는 "언젠가 반드시 값을
  반환한다"만 요구한다.

### 결정 6 — Cancellation 정책

Cancellation은 **호출자(Agent/Team)가 결과를 더 이상 기다리지 않기로 결정하는 것**으로
정의한다. 이는 Domain 개념이다.

- Domain이 요구하는 것: 호출자가 취소를 요청하면, Connector는 최대한 빠르게
  `ToolResponse(status=CANCELLED, ...)`를 반환해야 한다.
- Domain이 요구하지 않는 것: 외부 도구(MCP 서버) 쪽에서 실제로 실행 중이던 작업이
  물리적으로 중단되는 것까지는 보장하지 않는다. 이건 각 Adapter/외부 도구의 능력에
  달려 있다 — "취소를 요청했는데 MCP 서버가 이미 파일을 다 읽어버렸다"는 상황은
  Architecture 위반이 아니다.
- **PoC(Phase 4) 범위**: 현재 `apps/poc-runner`는 완전히 동기(synchronous) 실행
  구조이므로, 실제 Cancellation(호출 도중 중단)은 이번 Phase에서 구현하지 않는다.
  `ToolRequest`/`ToolResponse`에 Cancellation을 위한 Domain 개념(상태값)만 정의해
  두고, 실제 중단 메커니즘은 Phase 5(LangGraph — 비동기 실행 가능)에서 재검토한다.
  이는 은폐가 아니라 명시적 범위 축소다(아래 기각된 대안 및 영향 범위 참고).

### 결정 7 — Idempotency 정책

- `ToolRequest.idempotency_key`는 선택 필드다. 호출자가 "이 호출은 여러 번 실행돼도
  안전하다(같은 key로는 부작용이 중복되지 않는다)"고 판단할 때만 채운다.
- Connector는 idempotency를 스스로 만들어내지 않는다 — 외부 도구가 idempotency key를
  실제로 지원하는지, 어떻게 지원하는지는 Adapter/외부 도구의 능력이다. Connector는
  key를 있는 그대로 전달할 뿐, 이를 강제하거나 검증하지 않는다.
- `idempotency_key`가 없는 호출은 **비멱등(non-idempotent)으로 간주**하며, 이런
  호출은 향후 Retry Policy(v1.1, ADR-0005가 이미 Tier 3로 예약해 둔 개념)가 자동
  재시도 대상에서 제외해야 한다는 원칙만 이번 ADR로 남긴다 — 실제 자동 재시도 로직
  구현은 여전히 범위 밖이다(결정 8).

### 결정 8 — Retry 정책: Connector는 재시도하지 않는다

Connector(및 MCP Adapter)는 **정확히 한 번만 시도**한다. 실패·타임아웃이 발생해도
Connector 내부에서 스스로 재시도하지 않고, 그 결과를 `ToolResponse`로 즉시 반환한다.

- **이유**: "몇 번, 어떤 간격으로 재시도할 것인가"는 ADR-0005/04-policy-engine.md가
  이미 Retry Policy(Tier 3)로 정의해 둔 정책 결정이다. 이걸 Connector 내부에 숨기면
  ADR-0005 결정 1(Policy Engine 책임)이 깨진다 — 재시도 여부와 횟수가 코드에 다시
  하드코딩되는 것을 막기 위해서다.
- 재시도가 필요하면 **호출자(Team/Agent 계층)가 `call_tool()`을 다시 호출**하는
  형태로 구성해야 한다. Retry Policy 자체(횟수, 간격, 멱등 여부에 따른 재시도 허용
  여부)는 이번 Phase에서 구현하지 않는다 — ADR-0005가 이미 Tier 2/3를 PoC 범위
  밖으로 명시했으므로 이 원칙을 그대로 따른다.

### 결정 9 — Tool Failure 처리 (No Silent Failure)

- `IConnector.call_tool()`은 예외를 던지지 않는다. 어떤 실패든(연결 실패, 프로토콜
  오류, 도구 자체의 실패 응답, 타임아웃) `ToolResponse`로 변환되어 반환된다 —
  ADR-0005 결정 4(Fail-Closed 계약)와 동일한 패턴을 Connector에 적용한 것이다.
- `status != SUCCESS`인 모든 `ToolResponse`는 `error` 필드가 반드시 채워진다. 호출자
  (Agent/Team)는 이 실패를 삼키지 않고 사용자에게 투명하게 전달해야 한다(Request
  Processing Kernel v1의 No Silent Failure 원칙, ADR-0004/ADR-0005에서도 반복 적용된
  원칙을 여기서도 그대로 따른다).
- 실패 시 무엇을 할지(재시도? 대체 도구? 사람에게 에스컬레이션?)는 Connector가
  결정하지 않는다 — 이는 04-policy-engine.md의 Escalation Policy 영역이며, 여전히
  범위 밖이다.

### 결정 10 — Connector와 Agent의 책임 경계

| | Agent | Connector |
|---|---|---|
| 어떤 도구를 호출할지 | 결정한다 (Domain/Task 지식 보유) | 모른다 |
| 어떤 인자로 호출할지 | 결정한다 | 그대로 전달만 함(불투명 값) |
| 호출해도 되는지(권한) | Policy Engine에 위임(향후 PEP, 이번 범위 밖) | 판단하지 않음 |
| 호출 실행 자체 | Connector에 위임 | 실행 담당 |
| 결과 해석("성공적으로 리서치했다" 등) | 담당 | 하지 않음(SUCCESS/FAILURE 구분까지만) |
| 실패 시 대응(재시도/포기/에스컬레이션) | 담당(향후, 이번 범위 밖) | 하지 않음 |

Agent는 `IConnector` Port만 안다 — 그 뒤에 MCP가 있는지, Mock이 있는지, 향후 HTTP
REST 기반 Connector가 있는지 알지 못한다. 이는 ADR-0003 결정 4(Core는 Adapter를
추론하거나 분기하지 않는다)를 Agent-Connector 관계에도 동일하게 적용한 것이다.

### 결정 11 — MCP의 위치: Connector 구현체이지 Architecture가 아니다

- MCP는 `IConnector`의 구현체 중 하나다. `ToolRequest`/`ToolResponse`/`ToolCallStatus`
  (Domain Model)와 Timeout/Cancellation/Idempotency/Retry에 대한 위 결정들이
  Architecture이고, MCP는 그 Architecture를 만족시키는 PoC 단계의 선택(ADR-0001의
  ADR-0004, "공식 레퍼런스 서버 채택")일 뿐이다.
- Adapter Reversibility 조건(ADR-0003 결정 5, ADR-0005 결정 6과 동일한 패턴): MCP
  Adapter를 제거하고 `adapters/connector-mock`(또는 향후 HTTP/gRPC 기반 Connector)로
  교체해도 `packages/core`와 Agent를 구현하는 Organization 코드는 단 한 줄도 수정하지
  않는다. 교체는 Composition Root(`apps/poc-runner`)의 import 한 줄과 `pyproject.toml`
  의존성 한 줄로 끝나야 한다.
- MCP 프로토콜의 JSON-RPC 메시지 형식, MCP SDK의 세션/클라이언트 API는 Adapter
  내부에서만 사용하는 언어다. `ToolRequest`/`ToolResponse`로 변환하는 지점(Adapter의
  `call_tool()` 메서드)이 MCP 문법과 Domain Language의 유일한 경계다.

### 결정 12 — Connector Capability 선언과 Discovery (Agent는 Connector 이름을 모른다)

Capability Registry가 HQ에 대해 하는 역할(ADR-0004)을 Connector에도 동일하게
적용한다. Connector는 Jarvis OS의 Plugin이며, **자신이 이름이 아니라 Capability로
발견된다.**

- 모든 Connector 구현체는 자신이 제공하는 Capability 목록을 선언한다. 예:

  ```
  MCP Connector      capabilities: [filesystem, github, notion]
  Browser Connector   capabilities: [browser, playwright]
  HTTP Connector       capabilities: [http, webhook]
  ```

  이 선언의 정확한 스키마/파일 형식(YAML, entry point 등)은 Architecture 결정이
  아니라 구현 세부사항이다 — ADR-0004가 `capabilities.yaml` 스키마를 Architecture와
  분리했던 것과 동일한 원칙을 적용한다. 이 ADR은 "Connector는 Capability를 선언해야
  한다"는 요구만 확정한다.
- **Agent는 Connector의 이름(MCP인지, Browser인지, HTTP인지)을 알지 못한다.** Agent가
  아는 것은 자신에게 필요한 Capability뿐이다(`Agent.required_tools`가 이미
  Capability 수준의 이름을 담고 있다는 전제와 일치한다 — `packages/core/.../
  organization/entities.py`).
- Connector 선택(어떤 Connector 구현체가 이 Capability를 처리할지 결정하는 것)은
  **Registry(향후 Connector Registry)의 책임**이다. Agent도 Connector 자신도 이
  결정을 하지 않는다.
- 확정 구조:

  ```
  Agent
    ↓ Required Capability
  Connector Discovery (Registry)
    ↓ Connector 선택
  Tool 실행 (선택된 Connector의 call_tool)
  ```

- 이 결정은 Connector가 "MCP 하나만 존재하는 특수한 대상"이 아니라 Capability
  Registry(ADR-0004)와 동일한 패턴을 따르는 **일반화된 Plugin 카테고리**임을
  명시한다. 이번 Phase(Phase 4)는 실제 Connector Registry 구현까지는 포함하지
  않는다(결정 13 이후 참고) — Domain 요구사항(Capability 선언, Agent는 이름을
  모름, 선택은 Registry 소관)만 이 ADR로 먼저 확정하고, 실제 자동 Discovery
  구현은 Phase 4 Implementation Plan에서 범위를 정한다.

### 결정 13 — Connector Lifecycle (Domain State)

HQ가 8-state Lifecycle(`docs/architecture/v1.0`, ADR-0003/Phase 1)을 가지듯,
Connector도 최소 Lifecycle을 Domain 개념으로 정의한다. 지금 구현하지 않더라도
State 자체는 이 ADR에서 먼저 확정해 둔다.

```
Registered → Available → Busy → Unavailable → Removed
```

- **Registered**: Connector Registry에 선언(Capability 포함)은 됐지만 아직
  사용 가능 여부가 확인되지 않은 상태.
- **Available**: Tool 호출을 받을 수 있는 상태. Discovery(결정 12)가 선택
  대상으로 고려하는 상태는 이 상태뿐이다.
- **Busy**: 현재 호출을 처리 중이라 추가 호출을 받을 수 없는 상태(동시성 제약이
  있는 Connector에 한함 — 모든 Connector가 이 상태를 거쳐야 하는 것은 아니다).
- **Unavailable**: Health Check 실패, 연결 끊김 등으로 일시적으로 호출을 받을
  수 없는 상태. `Registered`와의 차이는 "한 번은 Available이었다가 실패했다"는
  이력이 있다는 점이다.
- **Removed**: Registry에서 완전히 제거된 상태. 이후 Discovery 대상에서
  제외된다.

이 State는 HQ Lifecycle(ADR-0003)과 마찬가지로 **Core의 Domain 개념**이며 특정
Adapter(MCP)의 내부 상태가 아니다 — Connector 구현체가 무엇이든 이 State 전이
규칙은 동일하게 적용된다.

**Phase 4 범위**: 이 State들을 Domain Enum으로 정의하는 것까지만 이번 Phase의
대상이다(아래 영향 범위 참고). 실제 State 전이를 일으키는 메커니즘(Health
Check, 장애 감지, Failover, Auto Recovery)은 이번 Phase에서 구현하지 않는다 —
결정 6(Cancellation)이 "Domain 개념만 정의하고 실제 구현은 Phase 5로 미룬다"고
한 것과 동일한 논리다. 이 State 정의는 향후 Health Check/Failover/Auto
Recovery가 추가될 때 재작업 없이 바로 사용할 수 있는 기반을 미리 마련해 두기
위한 것이다.

## 근거 (Rationale)

ADR-0003(Domain Port / Adapter Reversibility)과 ADR-0005(Policy Decision Model,
특히 결정 1의 "책임 범위를 좁게 유지"와 결정 4의 "Fail-Closed 계약")의 원칙을
Connector에 동일하게 적용했다. Connector가 재시도를 스스로 하지 않는다는 결정(결정
8)은 ADR-0005가 확립한 "정책은 코드가 아니라 데이터/Policy Engine의 소관"이라는
원칙의 직접적 연장이다 — 재시도 횟수를 Connector에 하드코딩하면 Request Processing
Kernel v1이 이미 한 번 지적했던 실수("N회 재시도"를 Kernel 로직에 박아넣는 것)를
Connector 계층에서 반복하는 것이 된다.

Connector Capability 선언/Discovery(결정 12)는 ADR-0004(Capability Registration
Model)가 HQ에 대해 확립한 패턴 — "Agent/Kernel은 구체적인 이름이 아니라 Capability로
대상을 찾는다"는 원칙 — 을 Connector에도 동일하게 적용한 것이다. HQ가 이름이 아니라
Capability로 Discovery되듯, Connector도 이름(MCP/Browser/HTTP)이 아니라 Capability로
Discovery되어야 ADR-0003 결정 4("Core는 Adapter를 추론하거나 분기하지 않는다")가
Agent-Connector 관계에서도 일관되게 유지된다. Connector Lifecycle(결정 13)은 HQ
Lifecycle(ADR-0003, Phase 1)과 동일한 이유로 존재한다 — Domain State를 먼저
정의해 두면 이후 Health Check/Failover 같은 운영 기능이 추가될 때 Core의 State
모델을 다시 설계하지 않아도 된다.

## 기각된 대안 (Rejected Alternatives)

- **대안 A**: Connector가 자체적으로 Retry Policy(횟수, 백오프)를 구현한다. 기각 —
  ADR-0005가 이미 Retry를 Tier 3 Policy 소관으로 확정했다. Connector에 재시도 로직을
  두면 정책이 두 곳(Policy Engine 설계 문서와 Connector 코드)에 분산되어 Drift 위험이
  생긴다(ADR-0003 결정 3이 Guard Rule에 대해 지적한 것과 같은 문제).
- **대안 B**: PoC 범위에서 실제 Cancellation(도중 중단)까지 구현한다. 기각 — 현재
  Composition Root가 완전히 동기 구조라 의미 있는 Cancellation 구현이 불가능하다.
  Domain 개념만 정의하고 실제 구현은 비동기 실행이 가능한 Phase 5(LangGraph)로
  미루는 것이 범위에 맞다(ADR-0004가 Division/Agent 확장을 후속 Phase로 미룬 것과
  같은 논리).
- **대안 C**: `ToolRequest`/`ToolResponse`를 만들지 않고 기존 `call_tool(tool_name,
  arguments) -> Any`를 그대로 유지한다. 기각 — Timeout/Idempotency 같은 실행 정책을
  표현할 자리가 없고, 실패와 성공을 구분할 표준화된 방법이 없어 Adapter마다 실패
  표현 방식이 달라질 위험이 있다(예: 어떤 Adapter는 `None`을 반환하고 어떤 Adapter는
  예외를 던지는 식). Fail-Closed 계약(결정 9)을 강제하려면 반환 타입 자체가
  Domain Model이어야 한다.
- **대안 D**: Agent→MCP 지점에 Policy Engine PEP를 이번 Phase에서 함께 구현한다.
  기각 — 04-policy-engine.md와 ADR-0005가 이미 언급한 확장 지점이지만, 이번 Phase의
  목표(Connector Adapter Reversibility 증명)와 직접 관련이 없다. 범위를 넓히면
  검증이 지연된다(ADR-0005 대안 A와 동일한 논리).
- **대안 E**: Agent(또는 Organization 코드)가 Connector를 이름으로 직접 지정한다
  (예: `connectors["mcp"].call_tool(...)`, 현재 `main.py`가 하고 있는 방식).
  기각 — 이는 ADR-0004가 HQ에 대해 이미 기각한 패턴("이름을 하드코딩하는 것")을
  Connector에서 반복하는 것이다. Agent가 이름을 알면 Connector Reversibility가
  깨진다 — 새 Connector 구현체로 교체할 때 Agent 코드까지 함께 수정해야 하기
  때문이다. Capability 기반 Discovery(결정 12)만이 이번 Phase의 최종 Architecture
  Validation 목표("새 Connector를 코드 수정 없이 추가하여 자동 Discovery 및 선택이
  가능하다")를 만족시킨다.

## 영향 범위 (Impact)

- 신규(Core): `packages/core/.../connector/models.py`에 `ToolRequest`, `ToolResponse`,
  `ToolCallStatus`, `DEFAULT_TIMEOUT_MS` 정의 (신규 Domain Model — ADR-0003 결정 1과
  같은 원리로 "예정된 확장"으로 취급, Architecture 변경이 아님)
- 신규(Core): Connector Lifecycle State(결정 13)를 표현하는 Domain Enum
  (`Registered/Available/Busy/Unavailable/Removed`) — 실제 전이 로직(Health Check
  등)은 포함하지 않고 State 정의만 포함
- 신규(Core 또는 Port): Connector Discovery 계약(결정 12) — Agent가 Capability로
  Connector를 찾을 수 있는 최소 인터페이스. ADR-0004의 `ICapabilityProvider`와
  같은 층위. 구체적 형태(신규 Port인지 기존 Capability Registry 확장인지)는
  Implementation Plan에서 결정한다.
- 수정(Core): `packages/core/.../ports/i_connector.py`의 `call_tool()` 시그니처를
  `ToolRequest -> ToolResponse`로 변경 (현재 `Any` 기반의 최소 시그니처를 이번 ADR이
  확정한 Domain Model로 교체 — Port의 계약을 명확히 하는 것이므로 ADR-0003 결정 1의
  선례를 따름)
- 무수정: `packages/core/.../kernel/`, `packages/core/.../policy/`,
  `packages/core/.../lifecycle/`(HQ Lifecycle 자체), `packages/core/.../
  capability_registry/`의 기존 HQ 로직
- 구현 예정(Phase 4): `adapters/connector-mcp`(신규 구현, Capability 선언 포함),
  `adapters/connector-mock`(신규 시그니처 + Capability 선언에 맞춰 갱신 — 여전히
  Adapter Reversibility 증명용으로 보존)
- 수정 예정(Phase 4): `apps/poc-runner/main.py` (Composition Root 배선을 이름
  하드코딩에서 Capability 기반 Discovery로 교체 + Stage 8을 "Agent가 Connector를
  호출한다"는 형태로 재정리할지는 Implementation Plan에서 별도 검토)

## Definition of Done

ADR-0003 공통 DoD에 더해 다음을 모두 만족해야 한다(Phase 4 승인 시).

- MCP Adapter가 기존 Mock Connector 시나리오(Agent→MCP 호출 경로, Must #9)를 동일하게
  통과한다.
- MCP Adapter를 제거하고 Mock Connector로 되돌렸을 때 Core/Agent 무수정으로 즉시
  복구 가능함을 통합 테스트로 증명한다(Adapter Reversibility).
- Timeout을 강제로 유발했을 때 `call_tool()`이 예외 없이 `ToolResponse(status=TIMEOUT,
  ...)`을 반환함을 계약 테스트로 증명한다(Fail-Closed 계약의 Connector 버전).
- 실패 응답(status=FAILURE)에는 항상 `error`가 채워져 있음을 계약 테스트로 증명한다.
- 새 Connector 구현체(코드 수정 없이 Capability 선언만 추가)가 Discovery 대상에
  자동으로 포함되고, Agent 코드나 Core를 수정하지 않고 실제로 선택·호출됨을 통합
  테스트로 증명한다(결정 12, Capability 기반 Discovery).

## 향후 적용

본 ADR은 Jarvis OS의 Connector Execution Model(요청/응답 모델, Timeout/Retry/
Cancellation/Idempotency/Failure 정책, Connector-Agent 경계)의 기준 문서다. 향후
HTTP REST/gRPC 기반 Connector, 그리고 Agent→MCP PEP가 실제로 추가될 때 모두 본 ADR을
상위 원칙으로 인용한다. Cancellation의 실제 구현(결정 6에서 범위를 좁혀 둔 부분)은
Phase 5(LangGraph, 비동기 실행) 착수 시 재검토 대상이다.
