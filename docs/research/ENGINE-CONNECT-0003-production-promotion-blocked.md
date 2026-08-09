# ENGINE-CONNECT-0003: `ENGINE-CONNECT-0002` Production 승격 조사 — Blocked

이 문서는 구현 문서가 아니다. `ENGINE-CONNECT-0002-execution-layer-results-wiring.md`
가 worktree 실험으로 확인한 흐름(외부 caller → `call_engine()` → 실제
Engine → `results:list[str]` → `ExecutionResult`)을 Production
Implementation으로 승격할 수 있는지 조사한 기록이다. **결론: 조사
결과 Blocked — Production 코드 변경을 하지 않았다.** 새 RFC/ADC/ADR을
작성하지 않는다. ADC-01·ADC-02를 재조사하지 않는다. Execution Result
Consumer·Kernel Component Architecture를 설계하지 않는다. 새
Architecture/Contract를 임의로 만들지 않는다.

## 조사 질문과 답

### Q1. 검증된 흐름을 Production에 최소 변경으로 연결할 수 있는가?

**기술적으로는 가능하지만, 배치할 수 있는 위치가 없어 실제로는
불가능하다.** `ENGINE-CONNECT-0002`가 이미 구조를 실행·관찰로
증명했다 — `call_engine()`(`development-hq/mvp/engine.py`)과
`build_execution_result()`(`core/execution_layer/mvp_0006/`)는
둘 다 이미 존재하는 공개 함수이며, 그 사이를 잇는 코드는 새 로직이
필요 없다(`results=[call_engine(prompt)]`로 충분함을 1회 관찰). 그러나
"어디에 두는가"는 Q3에서 확인하듯 현재 Architecture Governance가
답을 주지 않는다 — 코드를 어디든 추가하면 그 자체가 새 Architecture
결정(caller 위치 확정)이 된다.

### Q2. 기존 Development HQ / Execution Layer Contract를 변경하지 않고 구현 가능한가?

**Contract 자체는 변경 불필요.** `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md`
Q0가 이미 caller-supplied `results: list[str]`를 Accept했고,
`ADC-0002`·`ADC-0003`(형태=목록, 항목 타입=`str`)도 그대로 유지된다.
6개 Builder + Pipeline의 소스 코드도 수정할 필요가 없다(caller가
Builder 밖에서 `call_engine()`을 호출하므로 "AI 호출 없음" 불변식
— Builder 자신의 소스 코드 검사 — 을 건드리지 않는다, `ADC-0005` Q0
Evidence와 동일). 이 질문에 대해서는 Blocker가 없다.

### Q3. Production caller를 어느 기존 코드 위치에 둘 수 있는가?

**없음 — 이것이 이번 조사의 Blocking 지점이다.**

`docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`
가 이미 정확히 이 질문을 전수 조사했다(6개 후보, RFC-0010 후속).
이번 조사는 그 6개 후보를 재조사하지 않고, 그 Decision을 그대로
적용한다:

| 후보 | ADC-0010 판단 | 이번 조사에 적용한 결과 |
|---|---|---|
| C1. Kernel Engine Port/Adapter | Not Accepted — 책임은 Baseline에 있으나 설계 자체가 §10 Out of Scope | 이번 조사 규칙("Kernel Component Architecture 설계 금지")과도 정확히 일치 — 선택 불가 |
| C2. Runtime | Not Accepted — 존재 자체가 ADC-02 Open(재조사 금지) | 선택 불가 |
| C3. Session | Not Accepted — Kernel Concept Model에 등재된 적 없는 개념 | 새 Concept 도입 금지 규칙과 충돌 — 선택 불가 |
| C4. Development HQ | Not Accepted — 명시적으로 배제 | `development-hq/CONSTITUTION.md` "Architecture Freeze" 목록에 **Engine Adapter**, **Model Routing**이 그대로 남아 있음을 이번 조사에서 재확인(§Evidence). Execution Layer의 `results`를 채우기 위해 `call_engine()`과 `build_execution_result()`를 잇는 코드는 두 서로 다른 서브시스템(Development HQ의 Engine 호출 지점 ↔ Execution Layer의 Artifact Builder)을 연결하는 것 — Freeze 목록의 "Engine Adapter"가 금지하는 것과 정확히 같은 모양이다. `development-hq/mvp/`에는 애초에 Execution Layer(`core/execution_layer`)를 import하는 코드가 하나도 없다(`grep -rl "execution_layer" development-hq/` 결과 0건, §Evidence) — 이는 두 트랙이 지금까지 실제로 분리되어 있었다는 사실이며, 이번 조사가 처음 만든 경계가 아니다. |
| C5. Dogfooding 스크립트(6개) | Not Accepted — 검증 목적으로만 문서화, production 근거 없음 | 상태 변화 없음 — 이번 조사는 이 스크립트들을 production으로 승격할 새 Evidence를 만들지 않았다(§Non-goals) |
| C6. 별도 스크립트/함수(이름 없음) | Not Accepted — 예시 수준, 형태·소속 미정 | `ENGINE-CONNECT-0002`의 worktree caller가 실제로 이 모양(별도 스크립트)이었으나, 그 스크립트는 실험 종료와 함께 폐기되었고 tracked 브랜치에 반영된 적이 없다 — C6을 구체화하는 새 근거가 아니다 |

**핵심 관찰**: `ENGINE-CONNECT-0002`는 caller가 **기술적으로 작동한다**는
사실만 새로 추가했다. `ADC-0010`이 판단한 대상은 "caller가 어디에
**있어야 하는가**(production 위치)"였고, 이 질문은 caller가
작동하는지와 독립적이다 — `ADC-0010` Risks 절이 이미 명시한 그대로다:
*"`ADC-0005-engine-connection-boundary.md` Q0가 Accept한 'caller 수준
연결 자체는 허용된다'는 결론은 이 ADC로 바뀌지 않는다 — 다만 그
caller가 실제로 어디 있어야 하는지는 여전히 공백으로 남는다."*
`ENGINE-CONNECT-0002`는 그 공백을 메우는 새 Evidence가 아니다 —
"작동함"을 보였을 뿐 "어디"에는 답하지 않았다.

### Q4. 실제 Engine 호출을 Production workflow에 연결할 때 새 Architecture/Contract 결정이 필요한가?

**필요하다.** 정확히는 새 Contract가 아니라 **새 위치 결정**(Q3의
공백)이 필요하다 — `ADC-0010`이 이미 "6개 후보 전부 Not Accepted,
재검토 조건은 §부족한 Evidence 1~6"이라고 명시했고, 그 재검토 조건
중 이번 조사가 실제로 충족한 항목은 없다(§부족한 Evidence 대조,
아래). 이 결정은 이번 작업의 권한 밖이다(작업 규칙: "새로운
Architecture/Contract 임의 설계 금지") — RFC → ADC → ADR 절차가
선행되어야 한다(`CLAUDE.md`, `HANDOVER.md` 동일 원칙).

`ADC-0010` §부족한 Evidence 대조:

| 후보 | 재검토에 필요한 것 | 이번 조사가 제공했는가 |
|---|---|---|
| C1 | Kernel Component Architecture 설계 착수 | 아니오 — 이번 작업 규칙이 명시적으로 금지 |
| C2 | ADC-02 재검토 조건 충족 | 아니오 — 이번 작업 규칙이 명시적으로 재조사 금지 |
| C3 | Session을 Kernel Concept Model에 등재하는 새 RFC | 아니오 |
| C4 | Freeze 목록 재론 | 아니오 — 오히려 Freeze 목록이 그대로 유지됨을 재확인만 했다 |
| C5 | 검증 스크립트를 production 위치로 승격하려는 시도가 실제로 관찰·제안됨 | 아니오 — 이번 조사는 그 승격을 제안하지 않는다(Blocked로 결론) |
| C6 | 후보를 구체화하는 새 RFC | 아니오 |

### Q5. 필요한 변경이 있다면 정확히 어떤 최소 코드 단위인가?

**해당 없음 — Q3·Q4에서 Blocked됐으므로 코드 단위를 정의하지
않는다.** 코드 단위(예: 새 파일 하나, 함수 하나)를 지금 정의하는
것 자체가 "그 파일이 어디 있는가"라는 위치 결정을 전제하므로, Q3의
공백을 우회해서 답할 수 없다.

## Evidence

| 항목 | 확인 방법 | 결과 |
|---|---|---|
| Development HQ Architecture Freeze 목록에 Engine Adapter/Model Routing 존재 | `development-hq/CONSTITUTION.md` "Architecture Freeze" 절 직접 확인(이번 조사에서 재확인, 새로 만들지 않음) | `Engine Adapter`, `Model Routing` 항목이 그대로 존재 |
| Development HQ가 Execution Layer를 import하는 코드 존재 여부 | `grep -rl "execution_layer" development-hq/` (이번 조사에서 실행) | 0건 — 두 트랙은 현재 코드에서 서로 연결되어 있지 않다 |
| ADC-0010의 6개 후보 판단 | `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md` 원문 인용 | 6개 전부 Not Accepted (based on current evidence), 이번 조사가 재조사하지 않음 |
| ADC-0005 Q0/Q1 판단 | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` 원문 인용 | Q0 Accept(caller 수준 연결 허용) 유지, Q1 Not Accepted(Builder 내부 호출) 유지 — 이번 조사가 재조사하지 않음 |
| `ENGINE-CONNECT-0002`가 caller 위치에 대해 새로 증명한 것 | `docs/research/ENGINE-CONNECT-0002-execution-layer-results-wiring.md` 원문 재확인 | "작동함"만 증명 — "어디"는 다루지 않음(문서 자신의 §이 문서가 하지 않는 것: *"caller의 production 위치를 결정하지 않았다"*) |

## Stop Trigger / Blocking 대조

| 확인 항목 | 결과 |
|---|---|
| Production 코드 변경 발생 | **없음** — 이 문서 작성 외 어떤 파일도 수정하지 않았다 |
| 새 Architecture/Component/Concept 도입 | **없음** |
| ADC-01·ADC-02 재조사 | **없음** |
| Kernel Component Architecture 설계 | **없음** |
| Execution Result Consumer 설계 | **없음** |
| ADC-0010 재조사(6개 후보 재판단) | **없음** — 기존 판단을 그대로 적용만 했다 |
| 새 caller 위치를 임의로 선택 | **없음** — Q3에서 명시적으로 선택하지 않았다 |

## Conclusion

`ENGINE-CONNECT-0002`가 검증한 흐름은 기술적으로 작동한다(구조·
Contract 문제 없음, Q1·Q2). 그러나 그 caller를 Production 코드
어디에 둘 것인가(Q3)는 `ADC-0010`이 이미 6개 후보 전부 Not Accepted로
판단해 둔 공백이며, 이번 조사는 그 공백을 메울 새 Evidence를 만들지
않았다 — Development HQ의 Architecture Freeze(Engine Adapter/Model
Routing)가 재확인됐을 뿐이다(C4). 이 공백이 메워지지 않는 한 Q4(새
위치 결정 필요)가 그대로 성립하고, Q5(코드 단위)는 정의할 수 없다.

**판단: Blocked.** Production 코드 변경 없이 조사를 종료한다. 다음
단계는 이 작업의 범위가 아니다 — caller 위치를 다루는 새 RFC(예:
C6을 구체화하거나, Dogfooding 스크립트 승격을 명시적으로 제안하는
RFC)가 먼저 필요하며, 이는 `RFC → ADC → ADR` 절차를 통해 별도로
판단되어야 한다.
