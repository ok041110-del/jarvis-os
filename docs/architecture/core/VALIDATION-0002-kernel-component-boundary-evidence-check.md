# VALIDATION-0002: Kernel Component Boundary — 실제 코드·테스트·Evidence 대조 검증

**문서 성격**: Review 문서. **Governance 문서가 아니다.** ADC 상태를
변경하지 않는다. 새 Architecture·Component·Layer·Concept을 설계하지
않는다. 문제를 발견해도 코드나 문서를 수정하지 않는다 — Problem →
Evidence → Boundary → Recommendation만 기록한다.

**검토 대상**: `docs/01_architecture/BASELINE.md` v1.6 §7·§10·§11~§16이
정의한 Component 경계가, 실제 코드(`core/execution_layer/`,
`development-hq/mvp/`, `projects/`)와 누적 Evidence(MVP-0001~0048,
Investment Dogfooding 10건)에서 실제로 지켜지는지.

**선행 문서**: `VALIDATION-0001-kernel-reference-architecture.md`(문서
자체의 내부 정합성 검증, §15 문언 대상)와 이 문서는 대상이 다르다 —
이 문서는 **문서가 아니라 코드·테스트·Evidence**를 대상으로 한다.

**입력 자료**: `docs/04_adr/ADR-0002~0005`, `docs/01_architecture/BASELINE.md`
§7·§10~§16, `development-hq/{BOUNDARY,IMPLEMENTATION_RULES,HANDOVER}.md`,
`core/execution_layer/**`(코드+테스트), `development-hq/mvp/**`(코드+테스트),
`docs/architecture/core/ADC-0009~0011`, `docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`,
`docs/research/INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md`,
`development-hq/HANDOVER.md`(2026-08-14 시점).

---

## 0. 실행한 검증

```
python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q
```

**결과**: `58 passed in 64.73s`. 실패 없음. 이 실행이 이번 검증의 유일한
코드 실행 Evidence다(그 외는 문서 대조).

---

## 1. Component별 경계 판정

| Component | 책임 | 비책임 | 구현 위치 | Evidence | 경계 위반 |
|---|---|---|---|---|---|
| Kernel Core (Responsibility) | Kernel Context 조립·검증·정렬·렌더 **책임의 정의** | 구현, Component 설계 | `BASELINE.md` §11~§15 (문서만, 코드 없음) | ADR-0002~0005 | 없음 |
| Execution Layer | Implementation Specification → Execution Result 6단계 결정론적 변환 | AI 판단, 코드 실행, Model 선택 | `core/execution_layer/mvp_0001~0006/`, `pipeline.py` | 42+ builder 테스트 + `test_pipeline.py`, 58건 전체 통과 | 없음 |
| Engine Adapter | (설계된 적 없음 — 후보만 존재) | — | 없음 | ADC-0010(6개 caller 후보 전부 Not Accepted) | **N/A — 존재하지 않아 위반 불가** |
| Implementation Engine (`call_engine`) | 단일 함수로 실제 Engine(`claude -p`) 호출, 결과를 그대로 반환 | Routing, Retry, 여러 Engine 선택 | `development-hq/mvp/engine.py` | MVP-0043(rule-based 790줄 삭제), ENGINE-CONNECT-0001 | 없음 — 단일 함수 유지 확인 |
| Agent | 배분된 Task 실행, Capability에 대응하는 프롬프트 구성 | Task 배분 메커니즘, Registry | `development-hq/mvp/agents.py` | `AGENT_CAPABILITY_MAP`(리터럴 딕셔너리, MVP-0001부터 미확장), MVP-0025/27/28/47 관찰 | 없음 |
| Capability | 도메인 업무 내용(무엇을 검토·생성하는가) | 실행 메커니즘 | `agents.py` 각 함수의 `instruction` 문자열 | 동일 | 없음 |
| Workflow / Task | Task 순서를 **하드코딩된 함수 호출**로 표현 | Parser, Scheduler, 조건부 분기 일반화 | `development-hq/mvp/workflow*.py` | `run_mvp_0001()`: `review = ...; test_cases = ...` 순차 호출 | 없음 — Stop Trigger 미발동 |
| Memory | 미구현 (Kernel Module Defer) | 영속화, Context 복원 | 없음 — `review` 지역 변수(in-memory)만 존재 | `BASELINE.md` §14.6 N-4(Defer), `HANDOVER.md`: "Memory Service 구현 금지" | 없음 — 구현하지 않은 것이 곧 준수 |
| Registry / Lifecycle | 미구현 (§7 Jarvis OS 책임으로 귀속되었으나 착수 안 됨) | HQ가 스스로 등록·전이하는 것 | 없음 | `INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md` §2-3 | 없음 — Development HQ·Investment HQ 둘 다 동일하게 비-live |
| External Data / Connector | (Kernel Concept으로 미정의 — MCP Connector는 Meta Architecture §5에만 명칭 존재) | Kernel/Execution의 책임으로 전제된 적 없음 | `projects/*/agents.py`(project-local `runner.py`가 raw_data.md 작성) | `AGG-DATA-BOUNDARY-REPRODUCTION-0001.md` | **경계 모호 사례 1건 — 아래 §3 참조** |

---

## 2. 핵심 질문에 대한 답

### Q1. Execution Layer가 Artifact의 Deterministic / Immutable / Lossless 특성을 보장하는가?

**Yes — 코드와 테스트 양쪽에서 확인됨.**

- **Deterministic**: 6개 Builder(`mvp_0001`~`mvp_0006`) 전부
  `test_transformation_is_deterministic`/`test_rendering_is_deterministic`
  테스트를 가지며, 이번 실행에서 통과했다. `pipeline.py`의
  `_derive_id()`도 SHA-256 해시 기반 결정론적 유도이며 무작위 발급이
  아니다.
- **Immutable**: 각 Builder는 입력 문자열을 새 문자열로 변환할 뿐
  in-place 수정이 없다(Python 문자열 자체가 불변이라는 언어 특성에
  더해, 각 모듈 docstring이 "이전 Artifact를 수정하지 않는다"를
  명시). `pipeline.py`도 caller가 넘긴 `results`/`state` 등을 그대로
  전달할 뿐 변형하지 않는다.
- **Lossless**: MVP-0003 docstring: "Model Request는 Prompt Specification의
  정보를 손실 없이 보존한다." MVP-0001/0002도 "입력 텍스트를 한 글자도
  바꾸지 않는다"를 코드 수준에서 보장(머리말만 추가, 고정
  `RENDERING_MAP`으로 절 재배치만 수행).
- 시계·난수 미사용도 확인됨 — 6개 모듈 docstring 전부가 "시스템 시계
  접근 없음"을 명시하고, `created_at`/`submitted_at`/`state`/`changed_at`/
  `produced_at`은 전부 caller-supplied.

**한계**: 이 보장은 **Builder 코드 수준**에서 확인된 것이며,
`BASELINE.md` §14의 Kernel Public Contract(G-1~G-7)가 요구하는
**Kernel** 수준 보장과는 다르다 — Execution Layer는 아직 Kernel
Context Model(§13)을 사용하지 않는다(§15.3 각주: "Execution Layer
기존 Builder는 Kernel Renderer가 아니다"). 즉 이 보장은 **Execution
Layer 자체 설계 원칙으로서 지켜지고 있다**는 것이지, "Kernel
Contract를 만족한다"는 것을 의미하지 않는다 — 그 연결 자체가 아직
결정되지 않았다(R-3 미해결, ADR-0005 §Consequences).

### Q2. Engine Adapter와 Implementation Engine의 책임이 Reference Architecture와 실제 코드에서 일치하는가?

**"일치 여부를 판단할 대상 자체가 없다" — 더 정확히는, 일치하지
않을 여지가 원천적으로 차단되어 있다.**

- **Engine Adapter(Kernel Engine Port/Adapter)는 설계된 적이 없다.**
  `ADC-0010`이 caller 위치 후보 6개(C1 Kernel Engine Port/Adapter
  포함)를 전수 검토했고 **전부 Not Accepted**로 남겼다. `BASELINE.md`
  §10은 Engine Gateway를 Component Design으로 분류해 Out of Scope에
  그대로 둔다.
- **Implementation Engine(`call_engine`)은 실제로 존재하며, 단일
  함수 하나로 유지된다.** `engine.py` 자체가 "Engine Gateway(추상화)
  구현 금지 — 단일 함수로 Engine을 호출하는 것으로 충분"이라는
  `IMPLEMENTATION_RULES.md` 규칙을 코드 docstring에서 재확인한다.
  MVP-0043에서 이전에 존재했던 rule-based 대체 로직(약 790줄)을
  삭제해 "선택지가 여러 개인 상태"를 스스로 제거한 이력이 있다.
- 따라서 두 개념은 **한쪽(Engine Adapter)이 존재하지 않으므로 서로
  다른 층위에서 충돌할 수 없다.** `call_engine()`이 Engine Adapter의
  자리를 대신 차지하고 있는가? 아니다 — `call_engine()`은 Kernel
  경계 밖(Development HQ 소속 `development-hq/mvp/engine.py`)에
  있으며, Kernel 책임을 흡수한 적이 없다. Kernel Engine
  Port/Adapter가 아직 없다는 사실 자체가 §10 Out of Scope를 그대로
  지키고 있다는 증거다.

### Q3. Agent / Capability와 Kernel Component 사이에 책임 중복 또는 잘못된 결합이 있는가?

**중복·결합 없음 — 각 경계가 코드 수준에서 물리적으로 분리되어 있다.**

- `AGENT_CAPABILITY_MAP`은 MVP-0001부터 지금까지 리터럴 딕셔너리
  2개 항목(`code_review`→Backend Agent, `test_execution`→QA Agent)
  그대로다 — 조회 함수·클래스로 감싸이지 않았다. `HELLO_SDLC_CAPABILITY_MAP`이
  MVP-0004에서 별도로 추가됐으나, **기존 맵을 확장하지 않고 분리된
  새 딕셔너리**로 존재한다(코드 주석이 이 분리 자체가 "Registry
  중복 관리로 이어지는지는 관찰만 하고 판단하지 않는다"고 스스로
  명시).
- Capability의 내용(`instruction` 문자열)은 전부 `agents.py`에
  있으며, `engine.py`(Implementation Engine)는 그 내용을 전혀 모른다
  — `call_engine(prompt: str) -> str` 단일 시그니처만 갖는다. 이
  분리가 §7 "Capability의 내부 구현 방식은 HQ 책임"과 "Engine 호출은
  Kernel 책임"을 코드로 물리화한다.
- Stop Trigger(두 조건: Registry 일반화, Workflow Parser/Scheduler화)가
  MVP-0001부터 지금까지 **한 번도 발동한 적이 없다**(`HANDOVER.md`:
  "지금까지 발동 사례 없음"). 이는 관찰(observation)이며 이 문서가
  새로 발견한 것이 아니다.

### Q4. Registry / Lifecycle은 현재 Kernel 책임인가, 아니면 아직 미래 Runtime 단계의 책임인가?

**책임의 귀속은 확정(Kernel/Jarvis OS), 실행 주체는 미착수 — 둘을
구분해야 한다.**

- `BASELINE.md` §7: "HQ/Agent의 등록과 발견(Registry)", "HQ의
  생명주기 관리"는 **Jarvis OS의 책임**으로 이미 Frozen 상태다(v1.0
  부터).
- 그러나 이 책임을 수행할 **Component(Registry)는 §10 Component
  Design으로 Out of Scope**이며, 실제로 어떤 코드도 구현하지 않았다.
- `INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md` §2-3이 이를 직접
  확인했다: Development HQ와 Investment HQ **둘 다** Registry에
  등록되지 않은 "비-live" 상태로 동일하게 존재한다.
- **답**: Registry/Lifecycle은 **Kernel(Jarvis OS)의 책임으로 이미
  결정되어 있다** — "미래 Runtime 단계의 책임"이 아니다. 다만 그
  책임을 수행할 **구현(Component)은 아직 미착수**이며, 이는 §10이
  의도적으로 그렇게 둔 상태다("설계 안 함"이 아니라 "책임은 정의됨,
  구현은 의도적으로 미착수" — `HANDOVER.md` 그대로 인용). ADC-01
  (Model↔Component 대응)과 ADC-02(Runtime 존폐)가 Open인 이상 그
  구현에 착수할 근거(Model 축 정의, Runtime 존재 여부)도 아직 없다.

### Q5. External Data / Connector 문제를 Kernel/Execution 문제와 명확히 분리할 수 있는가?

**분리 가능함이 실제 재현으로 확인됐다 — 단, 그 분리 기준(Acquisition
경계)은 Architecture 문서 어디에도 아직 정의되어 있지 않다.**

- `AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`가 실제 사례(AGG ETF 분석에서
  SCHD 수치가 "범위 밖"으로 보였던 관찰)를 2회+2회(KO/PG) 재현했다.
  결론: 문제는 Execution(Engine 호출) 단계가 아니라 **Acquisition
  (project-local `runner.py`가 `raw_data.md`를 작성하는 단계)**에서
  비교 대상 자산의 수치가 섹션 경계를 넘어 섞여 들어간 것이었다.
  Engine은 재현 4회 전부 "입력에 실제로 주어진 것만" 사용했다.
- 이 재현은 Execution Layer(§Q1이 확인한 Deterministic/Lossless
  보장)가 실제로 지켜지고 있다는 **간접 증거**이기도 하다 — Engine이
  입력 범위를 벗어나지 않았다.
- **그러나** "Acquisition"이라는 경계 자체는 `BASELINE.md` §6·§7
  어디에도 Concept으로 등재되어 있지 않다. External Data/Connector는
  Meta Architecture(§5)에 `Connector (MCP)`라는 이름만 있을 뿐,
  §6 Concept Model의 10개 분류(Entity/Definition/Process/Event/
  Service/Interface/Metadata/Policy/State/Resource) 중 무엇에
  속하는지 정의된 적이 없다. `ADC-03`(Connector의 Architecture 상
  위치)이 여전히 Open인 것과 일치한다.
- **답**: 개별 사례 수준에서는 분리 가능함이 실증됐다(Execution
  결함이 아님을 확인). 그러나 그 분리를 뒷받침하는 **Concept 자체는
  아직 미정의**이므로, "명확히 분리할 수 있다"는 것은 지금까지의
  Evidence(1개 사례군)에 한정된 결론이며 일반화된 Architecture
  경계로 승격된 것은 아니다.

---

## 3. 발견된 문제 (Problem → Evidence → Boundary → Recommendation)

### P-1. Acquisition이 Concept Model에 없는 채로 실제 경계 역할을 하고 있다

**Problem**: `runner.py`(project-local, `projects/*/runner.py`)가
외부 자산 데이터를 `raw_data.md`로 수집·정리하는 단계가 실제로는
Data Boundary 사고(AGG 사례)의 **실제 책임 경계**로 작동했다. 그러나
이 단계는 Jarvis OS Concept Model에 이름도, 정의도 없다.

**Evidence**: `AGG-DATA-BOUNDARY-REPRODUCTION-0001.md` §Boundary(원문:
"Acquisition(raw_data.md 작성) — 실제 책임 경계"); `BASELINE.md` §6
Concept Model 10개 분류에 "Acquisition"이라는 항목 없음.

**Boundary**: 이 문제는 Kernel/Execution Layer 경계 위반이 아니다 —
Execution Layer(§Q1)와 Kernel(§Q2·§Q4)은 실제로 관찰된 범위 안에서
자기 경계를 지켰다. 위반이 있다면 그것은 **"External Data/Connector가
Kernel Concept으로 정의되지 않았다"는 공백**이며, 이는 이미
ADC-03(Open, NEXT)이 다루는 질문과 겹친다.

**Recommendation**: 새 RFC를 지금 열 근거로 삼지 않는다 — 재현
표본이 1개 project 계열(ETF/Dividend Stock 4건)에 그친다.
`ADC-03`이 NEXT로 이미 등재되어 있으므로, 그 우선순위가 올라갈 때
이 재현 Evidence를 참고 자료로 인용할 것을 권고한다(새 ADC를
만들지 않는다).

### P-2. Kernel Context Model(§13~§15)과 Execution Layer 코드가 아직 연결되지 않았다

**Problem**: Execution Layer의 결정론적 보장(§Q1)은 Kernel Public
Contract(G-1~G-7)와 **표면적으로 동일한 성질**(Deterministic,
Immutable, No Silent Failure에 준하는 상태값 검증)을 갖지만, 코드
수준에서는 서로 다른 두 체계다. `prompt_specification_builder.py`는
Kernel Context를 입력으로 받지 않는다.

**Evidence**: `BASELINE.md` §15.3 각주("RR-4는 Execution Layer의
기존 Builder를 판정하지 않는다 — `prompt_specification_builder.py`는
Kernel Context를 입력으로 받지 않으므로 Kernel Renderer가 아니다");
R-3 미해결 상태(§13.4 각주).

**Boundary**: 위반이 아니다 — ADR-0005가 이미 이 비연결을
"의도적"이라고 명시했고(§Consequences 4번), Execution Layer는
Kernel Module로 Accept되었을 뿐 Kernel Context Model 사용을
요구받은 적이 없다.

**Recommendation**: 지금 통합을 시도하지 않는다. ADR-0005가 정한
재검토 조건("Execution Layer가 훗날 Kernel Context를 사용하도록
정렬되면")이 실제로 발생하기 전까지는 두 체계가 병존하는 현재
상태가 Architecture와 일치한다.

### P-3 (참고, 위반 아님). HELLO_SDLC_CAPABILITY_MAP 분리가 Registry 중복 관리 초기 신호일 수 있다는 자기 관찰

**Problem**: `AGENT_CAPABILITY_MAP`(MVP-0001, 2개 항목)과
`HELLO_SDLC_CAPABILITY_MAP`(MVP-0004, 3개 항목)이 별도 딕셔너리로
존재한다. 두 맵을 합치는 조회 로직이 생기면 Registry 일반화로 갈
잠재 경로가 된다.

**Evidence**: `agents.py` 코드 주석 자체가 이 가능성을 이미 기록.
`MVP-0004-observation.md`(선행 문서, 이 검증에서 재조사하지 않음).

**Boundary**: 위반 아님 — 현재 두 딕셔너리는 병합되지 않은 채
독립적으로 남아 있고, Stop Trigger는 발동하지 않았다.

**Recommendation**: 새 조치 불필요. 두 맵을 합치려는 시도가 실제
코드에서 관찰되면 그 시점에 Stop Trigger로 처리한다(기존 절차
그대로 유효).

---

## 4. 최종 보고

### 확정된 Boundary

- Execution Layer의 6개 Builder + `pipeline.py`는 Deterministic /
  Immutable-input / Lossless를 코드와 테스트(58건 통과) 양쪽에서
  실제로 만족한다(§Q1).
- Engine Adapter는 설계된 적이 없으며(ADC-0010 전부 Not Accepted),
  `call_engine()`(Implementation Engine)은 그 자리를 대신 차지하지
  않고 Development HQ 소속 단일 함수로 남아 있다(§Q2).
- Agent/Capability와 Kernel 사이에는 물리적 코드 분리가 유지되고
  있으며 Stop Trigger 미발동(§Q3).
- Registry/Lifecycle의 **책임 귀속은 Kernel**로 이미 결정되어 있고,
  **구현은 의도적으로 미착수** — Development HQ·Investment HQ 둘 다
  동일하게 비-live(§Q4).
- Memory는 미구현이며, 이것이 곧 Architecture 준수다(in-memory
  변수 하나로만 Context 전달, `HANDOVER.md` 규칙과 일치).

### 불확실한 Boundary

- External Data/Connector(Acquisition)가 실제로 어느 Concept
  분류에 속하는지 — ADC-03이 아직 Open이며, 이번 검증도 이를
  해소하지 않는다(§Q5, P-1).
- Kernel Context Model과 Execution Layer의 향후 연결 여부(R-3,
  ADR-0005 미해결 항목 4번) — 재검토 조건 자체가 아직 발생하지
  않았다(P-2).

### 발견된 Boundary Violation

**없음.** 관찰된 3건(P-1~P-3) 중 어느 것도 실제 코드 수준의 경계
위반이 아니다 — P-1은 미정의 Concept의 공백, P-2는 의도된
비연결, P-3은 잠재 신호(미발동)다.

### Architecture 변경 필요 여부

**없음.** 이 검증은 새 RFC를 열 근거(ADC 채택 기준의 두 조건 —
"지금 결정하지 않으면 진행 불가" 또는 "지연 비용이 매우 크다")를
발견하지 못했다.

### ADC 영향

**없음.** ADC-01·02·03·09·10·11 모두 기존 상태(Open) 그대로
유지한다. 이 문서는 ADC-09/ADC-10/ADC-11의 기존 Not Accepted
결론을 재확인만 했을 뿐 재조사하지 않았다. `docs/03_adc/ADC.md`는
수정하지 않는다.

### 다음 Validation

- External Data/Connector 재현 표본이 늘어나면(예: Investment HQ
  4번째 Dogfooding, 또는 다른 project 계열) P-1의 일반화 가능성을
  재검토한다.
- Kernel Context Model 사용 사례가 실제로 발생하면(예: 두 번째
  Renderer 또는 두 번째 Ordering Policy 요구) P-2를 재검토한다.
- Registry/Lifecycle 구현 착수 조건(ADC-01·ADC-02 해소)이
  충족되면, 이번 §Q4 판정을 다시 확인한다.

### Tests

```
python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q
58 passed in 64.73s (0:01:04)
```

### Files

주요 대조 파일(전체 목록은 §입력 자료):
`docs/01_architecture/BASELINE.md`, `docs/04_adr/ADR-0002~0005`,
`docs/architecture/core/ADC-0009~0011`, `development-hq/BOUNDARY.md`,
`development-hq/IMPLEMENTATION_RULES.md`, `development-hq/HANDOVER.md`,
`core/execution_layer/{pipeline.py,mvp_0001~0006/*.py,mvp_0001~0006/tests/*.py}`,
`development-hq/mvp/{agents.py,engine.py,workflow.py}`,
`docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`,
`docs/research/INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md`

### Commit / Branch

이 문서 자체를 커밋 대상으로 한다(branch:
`claude/jarvis-os-documentation-drift-9lymtn`). 코드·다른 문서는
변경하지 않는다.

---

## Architecture/Contract 변경 여부

**없음.** `BASELINE.md`, `docs/03_adc/ADC.md`, `core/`, `development-hq/`
(이 문서 자체 제외) 어느 것도 수정하지 않았다. 새 Agent, Capability,
Kernel Component, Runtime, Concept을 만들지 않았다. ADC-01/02/09/10을
Evidence 없이 상태 변경하지 않았다(그대로 Open 유지). Stop Trigger
미발동.
