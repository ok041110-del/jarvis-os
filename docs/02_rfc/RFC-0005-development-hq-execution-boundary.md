# RFC-0005: Development HQ ↔ Execution Layer Boundary

**Status**: Proposed (검토 대상, 결정 아님) — 저장소 내 13개 RFC 중 유일하게 후속 ADC가 아직 작성되지 않은 채 Open으로 남아 있다(STABILITY-0001 §1.3: Kernel/Development HQ 어느 영역도 막고 있지 않음).
**Author**: Claude Code (Development HQ Phase 1 종료 시점 요청에 대한 RFC)
**대상**: Development HQ의 종료 지점과 Execution Layer의 시작 지점 (경계 정의만)
**Evidence 범위**: `docs/01_mvp/MVP-0005-observation.md` ~
`docs/01_mvp/MVP-0013-observation.md` (9개 Observation). 새로운 실험은
하지 않았다.

> 본 RFC는 Runtime, Multi-Agent, Model Routing, Engine Adapter 구현,
> Claude Code Prompt 설계, Prompt Builder 구현, Git/PR/Deployment를
> 다루지 않는다. 본 RFC는 이미 관찰된 사실로부터 Development HQ와
> Execution Layer 사이의 경계만 정리한다.

## 0. 이 RFC가 열린 이유

Development HQ Phase 1(Capability Foundation)은 `Development HQ
Constitution v1.0`이 정의한 Capability Loop(Real Issue → Project
Intelligence → Planning → Design → Validation → Dogfooding →
Observation → Evidence Review → Capability Logic Improvement)를 5개
Capability에 반복 적용해 종료된 것으로 간주한다: Project Intelligence
(MVP-0009), Planning(MVP-0010), Design(MVP-0011), Validation
(MVP-0012), Implementation Specification(MVP-0013). 이 Phase 동안 새
Capability는 추가되지 않았다 — 기존 Capability 5개의 내부 로직만
반복적으로 성숙시켰다.

RFC-0003 §4.2·§14와 ADC-0003 판단 4는 이미 "Model(Claude
Code/GPT/Codex/Qwen) 교체 가능"이라는 요구를 Development HQ가 단독으로
결정할 수 없는 Jarvis OS 수준 사안으로 분리해 두었고, "Execution
Layer의 Multi-Model 지원 여부는 별도 MVP/RFC로 다룬다"고 기록했다.
MVP-0013까지 Implementation Capability가 실제로 무엇을 산출하는지가
Observation으로 축적된 지금, 그 분리된 경계를 Implementation
Specification이라는 구체적 산출물 기준으로 정의할 수 있는 최소한의
근거가 마련되었다. 이 RFC는 그 근거만으로 경계를 정리한다.

## 1. Development HQ의 종료 지점

**근거로 사용한 사실만 기록한다.**

- MVP-0013 Observation: Implementation Capability
  (`backend_agent_code_generation`)는 코드를 생성하지 않는다. Design
  Draft와 그 안에 포함된 Requirement에서 실제 문장만 추출해
  Implementation Specification(Target File / Public Interface /
  Functions / Classes / Dependencies / Algorithm Outline / Edge Cases
  / Validation Notes 8개 항목)을 텍스트로 생성하고 끝난다. 이 함수의
  반환값은 여전히 `str`이며, 실행 가능한 코드나 파일 쓰기, 프로세스
  실행을 만들지 않는다.
- MVP-0005~0013 전 구간에 걸쳐 Development HQ의 모든 Capability(Project
  Intelligence/Planning/Design/Validation/Implementation Specification)는
  `development-hq/mvp/engine.py`의 문자열 마커 매칭(정규식, 부분 문자열
  포함 검사, 섹션 헤더 파싱)만으로 구현되어 있다. LLM/ML 호출은 한
  번도 추가되지 않았다(`IMPLEMENTATION_RULES.md`의 금지 사항이자,
  MVP-0005~0013 각 Observation이 "ML/LLM 호출 없음"을 명시).
- MVP-0012 Observation: Validation Capability는 입력 Artifact를
  Requirement/Design(Architecture Draft)/Code 3가지로만 구분하고,
  각 Stage에 대해 "필수 섹션이 존재하는가"만 확인한다. 코드가 실제로
  동작하는지, 테스트가 실제로 통과하는지는 어떤 Capability도 확인하지
  않는다 — `_review_python_code`조차 정적 문자열 규칙(bare except,
  line length, docstring, mutable default)만 검사할 뿐 코드를 실행하지
  않는다.
- MVP-0013 Observation(Regression 절): Implementation Specification을
  Validation에 통과시키면, Validation은 그것을 "design"으로
  오분류한다(Reference Design 절에 중첩된 `## Interfaces`/`## Reference
  Requirement` 마커 때문). 이는 Validation Logic의 결함이 아니라,
  Development HQ의 Validation Capability가 애초에 "Implementation
  Specification 자체가 올바른가"까지만 다룰 수 있고, 그 Specification을
  바탕으로 실제로 생성된 코드가 올바른지는 다룰 수 있는 설계가 아니라는
  사실을 보여준다.

**결론(사실 기반)**: Development HQ는 Implementation Specification을
생성하고, 그 Specification 자체의 구조적 완전성(필수 섹션 존재 여부)을
Validation하는 지점에서 끝난다. Development HQ는 Specification으로부터
실제 코드를 생성하지 않으며, 생성된 코드를 실행·테스트하지 않으며,
어떤 모델(Claude Code, Codex, GPT, Qwen 등)도 호출하지 않는다.

## 2. Execution Layer의 시작 지점

**근거로 사용한 사실만 기록한다.**

- `development-hq/BOUNDARY.md`: "Development HQ가 절대 책임지지 않는
  것"에 이미 "Engine 호출 — Kernel Engine Port/Adapter의 책임"이
  명시되어 있다. Development HQ의 유일한 Engine 호출 지점은
  `engine.py`의 `call_engine()` 하나이며(`IMPLEMENTATION_RULES.md`:
  "Engine Gateway 구현 금지 — 단일 함수로 Engine을 호출하는 것으로
  충분하다"), MVP-0005~0013 전 구간에서 이 함수는 항상 규칙 기반
  응답(`_rule_based_response`)만 반환했다 — 실제 LLM Engine으로
  교체된 적이 없다.
- RFC-0003 §4.2: "Model(Claude Code/GPT/Codex/Qwen)은 Execution
  Layer에서 교체 가능해야 한다는 부분은 Development HQ의 권한 밖이다.
  Engine 호출과 그 표준 인터페이스(Port/Adapter)는 Jarvis OS Kernel의
  책임이다."
- ADC-0003 판단 4: Execution Layer의 Multi-Model 지원을 "Out of
  Authority (Escalate)"로 판단해 Development HQ ADC 권한 밖으로 이미
  분리해 두었다.
- MVP-0013 Observation: Implementation Specification의 Functions
  절은 Design의 Interfaces 절(MVP-0011)에서 온 `{slug}_check_N() ->
  bool` 같은 함수 시그니처 "제안"만 담고 있으며, 이 시그니처에 대응하는
  실제 함수 바디는 어디에도 존재하지 않는다. 즉 Development HQ가 만든
  산출물은 "무엇을 구현해야 하는가"에 대한 명세이지, "어떻게 구현이
  실행되는가"에 대한 것이 아니다.

**결론(사실 기반)**: Execution Layer는 Implementation Specification을
입력으로 받아, 그 안에 나열된 Public Interface/Functions를 실제로
구현하는 코드를 만들어내는 지점(Code Generation)부터 시작한다.
Execution Layer는 그 코드를 실제로 실행·테스트하는 것, 그리고 그
실행을 담당할 Model/Agent(Claude Code, Codex, GPT, Qwen, 또는 다른
규칙 기반 실행기)를 선택·호출하는 것까지 포함한다. 이는 이미
`BOUNDARY.md`가 Kernel Engine Port/Adapter의 책임으로 명시한 "Engine
호출"과 동일한 경계다 — 이 RFC는 그 경계를 새로 만드는 것이 아니라,
Implementation Specification이라는 구체적 산출물 위에서 다시 확인한다.

## 3. Implementation Specification이 Execution Layer에 제공해야 하는 최소 정보

MVP-0013 Observation에서 실제로 관찰된, `_generate_code()`가 생성하는
8개 항목을 그대로 최소 정보로 채택한다. 이 RFC는 이 형식을 새로
설계하지 않는다 — 이미 구현되어 Dogfooding으로 검증된 형식을 그대로
Interface 정의에 채택할 뿐이다.

| 항목 | MVP-0013에서 관찰된 내용 | Execution Layer가 사용하는 방식(사실 관찰, 제안 아님) |
|---|---|---|
| Target File | slug 기반 파일 경로 제안(`development-hq/mvp/generated/{slug}.py`) | 실제 코드를 어느 파일에 쓸지의 후보 |
| Public Interface | Component의 함수 시그니처 1개 | 외부에서 호출할 진입점 |
| Functions | Public Interface + Design Interfaces 절의 검증 함수 시그니처 N개 | 구현해야 할 함수 목록(바디 없음) |
| Classes | Design이 단일 함수형 Component만 제안하는 한 항상 "필요 없음" | 클래스 분해가 필요한 Design이 나타나면 그때 채워질 자리(MVP-0013까지는 관찰되지 않음) |
| Dependencies | Project Intelligence(Reference Context)의 source_code/existing_workflow 파일 목록 | 참고해야 할 기존 코드 |
| Algorithm Outline | Design Responsibility 절을 순서 있는 단계로 나열 | 구현 순서의 출발점(문장 단위, 의사코드 아님) |
| Edge Cases | Design Constraints 절(Out of Scope + Risk 회피) | 처리해야 할 경계 조건 |
| Validation Notes | Design Open Questions 절(실제 Open Question + 고정 확인 문구) | 구현 완료 후 별도로 확인해야 할 항목 |

이 8개 항목 중 어느 것도 실행 가능한 코드나 실제 함수 바디를 포함하지
않는다(§1의 근거와 동일). Execution Layer가 이 항목들로부터 실제 코드를
만드는 방법(Prompt 구성, Model 선택, 코드 생성 전략)은 이 RFC의 범위
밖이다(Out of Scope 참고).

## 4. Development HQ가 Claude Code/Codex/GPT/Qwen을 직접 다루지 않는 이유

**근거로 사용한 사실만 기록한다.**

1. **권한 경계가 이미 확정되어 있다.** `BOUNDARY.md`는 "Engine 호출"을
   Development HQ가 "절대 책임지지 않는 것"으로 이미 명시했다. 이는
   이번 Phase에서 새로 만든 결정이 아니라, MVP-0001부터 유지된 결정을
   재확인한 것이다.
2. **Development HQ의 모든 Capability는 규칙 기반으로만 성숙해 왔고,
   그 접근이 실제로 동작했다.** MVP-0009(Context Bundle)부터
   MVP-0013(Implementation Specification)까지, 문자열 마커 매칭만으로
   Planning/Design/Validation/Implementation Specification 품질이
   실제로 개선되는 것을 Before/After 비교로 반복 확인했다(각 Observation
   문서). 이는 "Development HQ 내부에서 해결 가능한 문제"와 "Model
   호출이 필요한 문제"가 다른 종류의 문제라는 것을 보여준다 — 지금까지
   Development HQ가 만난 문제는 전자였다.
3. **Development HQ가 Model을 직접 다루면 이미 Frozen인 항목을
   침범한다.** `Development HQ Constitution v1.0`의 Architecture
   Freeze 목록에 Engine Adapter, Model Routing이 이미 포함되어 있다.
   Development HQ가 Claude Code/Codex/GPT/Qwen 중 무엇을 호출할지
   결정하는 로직을 만드는 것은 곧 Engine Adapter/Model Routing을
   구현하는 것과 같다 — 이는 "충분한 Evidence가 나올 때까지 동결"
   대상이며, 이번 Phase는 그 Evidence를 만드는 절차(Capability Loop)를
   실행했을 뿐 Model Routing이 필요하다는 Evidence를 만들지 않았다.
4. **지금까지 Model 호출 없이도 Capability Loop가 반복 가능했다.**
   MVP-0009~0013 5개 MVP 모두 "Baseline 저장 → Logic Improvement →
   Dogfooding → Before/After 비교 → Regression 확인 → Observation"
   절차를 Model 호출 없이 완결했다. Model을 직접 다뤄야 할 필요성
   자체가 아직 Observation으로 나타나지 않았다 — RT-0001의 재평가
   Trigger 방식과 동일하게, "필요가 실측될 때 재평가"하는 것이 지금까지
   Development HQ가 따라온 방식이다.

## Out of Scope

이번 RFC는 다음을 다루지 않는다.

- Runtime, Multi-Agent, Model Routing, Engine Adapter의 실제 구현.
- Claude Code Prompt 설계, Prompt Builder 구현.
- Git, PR, Deployment.
- Execution Layer의 내부 구조(어떤 Model을 언제 호출할지, 실패 시
  재시도 정책 등) 설계.
- Implementation Specification 형식 자체의 변경 — MVP-0013이 이미
  구현한 8개 항목을 그대로 인용했을 뿐이다.

## Non-goals

- 이 RFC는 Development HQ Baseline이나 Jarvis OS Architecture
  Baseline을 변경하지 않는다.
- 이 RFC는 Execution Layer를 설계하거나 구현하지 않는다.
- 이 RFC는 새 Capability, Runtime, Pipeline을 만들지 않는다.
- 이 RFC는 MVP-0005~0013 이후 새로운 실험이나 Dogfooding을 수행하지
  않는다 — 기존 Observation만 근거로 사용했다.
- 이 RFC는 ADC-0003 판단 4(Execution Layer Multi-Model, Out of
  Authority)를 대신 결정하지 않는다. 그 판단은 여전히 Jarvis OS 수준
  결정이 선행되어야 한다.

## 다음 절차

이 RFC 자체는 아무것도 결정하지 않는다. 후속 ADC가 필요하다면 다음만
판단 대상이 된다.

1. §1·§2에서 정리한 Development HQ 종료 지점 / Execution Layer 시작
   지점을 Development HQ Baseline에 반영할지.
2. §3의 8개 항목(Implementation Specification 최소 정보)을 Development
   HQ와 Execution Layer 사이의 고정 Interface로 채택할지, 아니면 계속
   Development HQ 내부 구현 세부사항으로만 둘지.
3. Execution Layer 자체의 설계·구현은 별도 Jarvis OS 수준 RFC로 언제
   상정할지 — 이 RFC는 그 시점을 결정하지 않는다.
