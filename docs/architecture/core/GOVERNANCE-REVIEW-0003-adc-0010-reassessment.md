# GOVERNANCE-REVIEW-0003: ADC-0010 재평가 (ENGINE-CONNECT-0005 Evidence 반영)

**문서 성격**: Governance Review. **Decision 문서가 아니다.**
**대상**: `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`
(Engine Caller의 위치와 책임, 6개 후보 C1~C6 전부 Not Accepted)
**촉발 Evidence**: `docs/research/ENGINE-CONNECT-0005-full-pipeline-real-engine-wiring.md`
(Development HQ의 실제 Implementation Specification → Execution
Layer의 `run_execution_layer_pipeline()` 전체 → 실제 Engine 1회 호출
→ ExecutionResult, verbatim 보존 확인)
**목적**: 새 Evidence(ENGINE-CONNECT-0005)가 ADC-0010이 스스로 남긴
"§부족한 Evidence" 6개 항목 중 하나라도 실제로 충족시켰는지 판정한다.

이 문서는 새 RFC를 작성하지 않는다. 새 Architecture/Concept을 설계하지
않는다. C1~C6 중 어느 것도 지금 Accept하지 않는다. ADC-01·ADC-02
(재조사하지 않음), Execution Result Consumer, `ADC-0011`(별도 실행
위치)의 Not Accepted 상태를 재론하지 않는다. **이번 검토에서 코드는
한 줄도 작성하지 않았다.**

이 문서가 판단하는 것은 오직 하나다: **ENGINE-CONNECT-0005 하나만으로,
6개 후보 중 Production caller 위치를 지금 결정할 수 있게 된 후보가
있는가?**

---

## 0. ENGINE-CONNECT-0005가 실제로 무엇을 새로 관찰했는가

`ADC-0010` 작성 시점(및 `ADC-0011`/`ENGINE-CONNECT-0002~0004` 작성
시점)까지 관찰된 것은 다음과 같다.

| 관찰 | 출처 |
|---|---|
| caller → `call_engine()` → 실제 Engine → `results` → `ExecutionResultBuilder` 1개 | `ENGINE-CONNECT-0002` |
| 그 caller를 Production으로 승격하려는 시도(조사만, 실행 아님) | `ENGINE-CONNECT-0003`(Blocked로 종결) |
| `ADC-0010` C6("별도 스크립트/함수")의 실체를 구체화하려는 조사 | `ENGINE-CONNECT-0004` |

`ENGINE-CONNECT-0005`가 이번에 새로 추가한 것은 다음 세 가지뿐이다.

1. `ExecutionResultBuilder` 하나가 아니라 **6개 Builder를 하나로 묶은
   `run_execution_layer_pipeline()` 함수 전체**를 실제 Engine과 함께
   1회 실행했다 — 이전에는 이 Pipeline 함수 자체가 실제 Engine과
   함께 관찰된 적이 없었다.
2. caller가 만든 Implementation Specification이 **Development HQ의
   고정 fixture 파일(`toy_issue.*`)이 아니라, `_analyze_requirement`/
   `_design_from_requirement`/`_generate_code`를 그 자리에서 직접
   순서대로 호출해 만든 실제 산출물**이었다.
3. 실제 Engine에 넘긴 prompt가 Implementation Specification 원문이
   아니라, Execution Layer 자신의 `build_prompt_specification()`이
   렌더링한 **Prompt Specification**이었고, 그 결과 Engine이 반환한
   코드가 명세의 함수/클래스 이름을 정확히 반영했다.

**이 셋 모두 "caller 수준 연결이 동작하는가"(`ADC-0005` Q0가 이미
Accept한 질문)에 대한 관찰의 폭을 넓힌 것이지, "그 caller가 어디
있어야 하는가"(`ADC-0010`이 판단하는 질문)에 대한 새로운 답은
아니다.** 이 구분이 아래 §1의 판정을 결정한다.

---

## 1. C1~C6 후보별 재평가

`ADC-0010` §부족한 Evidence가 후보별로 명시한 조건을 그대로 인용하고,
`ENGINE-CONNECT-0005`가 그 조건을 충족시켰는지만 확인한다.

### C1. Kernel Engine Port/Adapter

**필요 조건(ADC-0010)**: Kernel Component Architecture 설계 착수
(현재 `BASELINE.md` §10 Out of Scope) — Kernel Module Defer 3건,
ADC-01·02, Engine 수 ≥2 등 여러 선행 조건에 걸려 있음.

**ENGINE-CONNECT-0005가 건드렸는가**: 아니다. 실험은 Kernel
Component를 설계하거나 호출하지 않았다 — Development HQ 함수와
Execution Layer 함수를 scratchpad 스크립트가 직접 호출했을 뿐이다.
Engine 수도 여전히 1개(Claude Code)다.

**판정**: **미충족. Not Accepted 유지.**

### C2. Runtime

**필요 조건(ADC-0010)**: `ADC-02`(`ADC-0008-runtime-existence-boundary.md`)의
재검토 조건이 먼저 충족되어야 함.

**ENGINE-CONNECT-0005가 건드렸는가**: 아니다. 실험은 상태를 보관하지
않는 단발 함수 호출 나열이었다 — Runtime의 존재 여부와 무관하다.

**판정**: **미충족. Not Accepted 유지.**

### C3. Session

**필요 조건(ADC-0010)**: Session을 Kernel Concept Model에 등재하는
새 RFC가 필요함.

**ENGINE-CONNECT-0005가 건드렸는가**: 아니다. 실험은 Session이라는
이름의 어떤 개념도 참조하지 않았다.

**판정**: **미충족. Not Accepted 유지.**

### C4. Development HQ

**필요 조건(ADC-0010)**: `RFC-0005-development-hq-execution-boundary.md`의
Freeze 목록(Engine Adapter, Model Routing) 자체를 재론해야 함 — Phase
1 종료 후 불변 원칙과 충돌.

**ENGINE-CONNECT-0005가 건드렸는가**: 아니다 — 오히려 반대 방향의
사실을 보탰다. 실험의 caller는 `development-hq/mvp/` 패키지 **밖**
(scratchpad)에서 그 패키지의 공개 함수를 **import해서** 호출했다.
Development HQ 코드 자체는 caller 역할을 맡지 않았다 — Freeze 목록을
건드릴 근거가 생기지 않았다.

**판정**: **미충족. Not Accepted 유지.**

### C5. Dogfooding 스크립트(6개)

**필요 조건(ADC-0010)**: 검증 스크립트를 production 위치로 승격하려는
시도가 실제로 관찰되거나 명시적으로 제안되어야 함.

**ENGINE-CONNECT-0005가 건드렸는가**: 아니다. 실험의 caller는 기존
6개 Dogfooding 스크립트(`core/execution_layer/mvp_0001~0006/dogfooding/`)
중 어느 것도 아니다 — 새 scratchpad 스크립트였고, 문서 자신이
"tracked 브랜치에는 반영되지 않았다"고 명시했다. 승격 시도 자체가
없었다.

**판정**: **미충족. Not Accepted 유지.**

### C6. 별도 스크립트/함수(Dev HQ↔Execution Layer를 잇는, 이름 없음)

**필요 조건(ADC-0010)**: 이 후보 자체를 구체화하는 새 RFC — 이름·
형태·소속 네임스페이스(Dev HQ? Execution Layer? 독립?) 무엇도 없음.

**ENGINE-CONNECT-0005가 건드렸는가**: 부분적으로, 그러나 요구된
방향이 아니다. 실험의 caller는 정확히 "Dev HQ↔Execution Layer를 잇는
별도 스크립트"의 **형태**를 하나 더 실행해 보였다 — 그러나 그
스크립트에 이름을 붙이거나, 소속 네임스페이스를 정하거나, tracked
코드베이스의 한 위치로 승격하는 어떤 결정도 의도적으로 하지 않았다
(`ENGINE-CONNECT-0005` §"이 문서가 하지 않는 것": *"caller의
production 위치를 결정하지 않았다... 어떤 tracked 위치로도 승격하지
않는다"*). `ADC-0010`이 C6에 요구한 것은 "이름·형태·소속을 구체화하는
RFC"이지 "한 번 더 동작을 관찰하는 것"이 아니다 — `C5`(Dogfooding
6회 실행)에 대해 이미 내려진 것과 같은 이유("Contract가 동작한다는
증거일 뿐, production 위치여야 한다는 근거는 아니다")가 여기에도
그대로 적용된다. ENGINE-CONNECT 계열 실험은 이제 2건(`0002`, `0005`)
이 됐지만, 둘 다 같은 이유로 같은 결론에 도달한다.

**판정**: **미충족. Not Accepted 유지.**

---

## 2. 새롭게 강화된 것은 무엇인가 (판단 근거이지 결정 변경이 아님)

C1~C6 어느 것도 Accept 가능해지지 않았지만, 다음은 이번 검토로 실제로
강화됐다 — 정직하게 구분해 기록한다.

- `ADC-0005` Q0("caller 수준 연결은 허용된다")의 신뢰도가 커졌다:
  단일 Builder가 아니라 **Pipeline 함수 전체**가, **고정 fixture가
  아니라 그 자리에서 만든 실제 Implementation Specification**으로,
  **Raw Implementation Specification이 아니라 실제 Prompt
  Specification**을 프롬프트로 써서 관찰됐다 — 이전보다 Production에
  더 가까운 형태의 배선이 실제로 예외 없이 동작함을 확인했다.
- `results: list[str]`이 단일 항목(`[raw_output]`)으로 충분하다는
  관찰이 2회 연속(`ENGINE-CONNECT-0002`, `ENGINE-CONNECT-0005`)
  재현됐다.
- 이 강화는 **"caller가 어디 있어야 하는가"라는 `ADC-0010`의 질문에는
  답하지 않는다** — Q0(연결 가능 여부)와 caller 위치(어디)는 `ADC-0010`
  자신이 이미 구분한 서로 다른 질문이며, 이번 관찰도 전자만 강화했다.

---

## 3. Governance Assessment

| 절차 | 필요 여부 | 근거 |
|---|---|---|
| **RFC** | **불필요** | §1의 6개 판정 모두 "미충족"이다 — 새 Boundary Question이 열리지 않았다. `ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준(지금 결정하지 않으면 상위 Architecture 진행 불가 / 되돌리는 비용이 커짐) 중 어느 것도 이번 검토로 새로 충족되지 않았다 |
| **ADC** | **불필요** | 이 검토 자체가 이미 기존 `ADC-0010`의 재검토 조건 틀 안에서 이뤄졌다 — 6개 조건 중 어느 것도 충족되지 않았으므로 새 ADC를 낼 근거가 없다 |
| **ADR** | **불필요** | 선행 결정 변경이 없으므로 Baseline에 옮길 것이 없다 |

## 4. Final State

> ## **Hold — ADC-0010 Decision 불변**

| 항목 | 상태 |
|---|---|
| C1~C6 | **전부 Not Accepted 유지.** 억지로 하나를 고르지 않는다 |
| `ADC-0010` 문서 | 수정하지 않는다 — 이 재평가는 별도 문서(`GOVERNANCE-REVIEW-0003`)로 남긴다 |
| `ADC-0005` Q0 | 그대로 유지(재론하지 않음), 다만 신뢰도가 실측으로 더 강화됐다는 사실만 §2에 기록 |
| `ADC-0011`(별도 실행 위치) | 재론하지 않는다 |
| 다음 Implementation | 이 재평가로 새로 해소된 Architecture Blocking이 없다 — caller 위치가 필요한 작업(Production 승격)은 여전히 진행할 수 없다. caller 위치가 필요 없는 작업(개별 Contract 실험·Evidence 축적)은 계속 가능하다 |

### 4.1 이 판정이 뜻하지 않는 것

- *"ENGINE-CONNECT-0005가 무의미했다"* — 아니다. §2가 기록한 것처럼
  Q0의 신뢰도를 실측으로 넓혔다. 다만 그것은 `ADC-0010`이 판단하는
  질문(위치)이 아니다.
- *"caller 위치는 영원히 결정 불가능하다"* — 아니다. `ADC-0010`
  §부족한 Evidence 1~6이 각 후보에 대해 이미 구체적으로 적어 둔
  조건(예: C1의 Kernel Component Architecture 설계 착수, C6의 이름·
  형태·소속을 구체화하는 새 RFC) 중 하나가 실제로 충족되면 재검토
  대상이 된다 — 이번 검토는 그중 어느 것도 이번 Evidence로 충족되지
  않았다는 사실만 확인했다.

## 5. Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0010`, `ENGINE-CONNECT-0002~0005`
  만 인용했다. 새 실험은 하지 않았다.
- caller 위치를 임의로 선택했는가 — **아니오**. 6개 후보 전부 Not
  Accepted로 유지했다.
- C6을 억지로 Accept했는가 — **아니오**. C6에 대해서만 "부분적으로
  건드렸으나 요구된 방향이 아니다"라고 명시적으로 구분해 이유를
  남겼다.
- 새 RFC를 만들었는가 — **아니오**.
- 새 Architecture/Concept(Session 등)을 설계했는가 — **아니오**.
- ADC-01·ADC-02·`ADC-0011`을 재조사했는가 — **아니오**. 상태만
  인용했다.
- `ADC-0010` 문서를 직접 수정했는가 — **아니오**. 이 검토는 별도
  문서로 존재한다.
- 억지로 결론을 내렸는가 — **아니오**. 6개 후보 전부 Not Accepted로
  남겼고, 강화된 부분과 강화되지 않은 부분을 구분해 기록했다.
- 코드를 작성했는가 — **아니오**.
