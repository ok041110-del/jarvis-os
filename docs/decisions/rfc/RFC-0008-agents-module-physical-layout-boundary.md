# RFC-0008: AST Context Module Discovery — Dotted Package Path 지원 확장 여부

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Agent Package Refactoring 작업 중 구현 착수
직전 발견한 구조적 충돌에 대해 사용자 지시로 작성)
**대상**: `hqs/development/mvp/ast_context.py`의 module discovery를
평면 module path(`mvp/{module}.py`)뿐 아니라 dotted package module
path(`mvp/{package}/{module}.py`)까지 지원하도록 확장하는 것을 허용할
것인가 — 이 하나의 질문만 다룬다.
**Evidence 범위**: `hqs/development/mvp/ast_context.py`,
`hqs/development/mvp/agents.py`,
`hqs/development/mvp/tests/test_ast_context.py`,
`hqs/development/mvp/tests/test_stage_01.py`,
`docs/governance/adc/ADC-0005.md`(RFC-0007 후속, T06~T19 Evidence),
`docs/research/DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`. 새로운 실험은
하지 않았다.

> 이번 Task는 코드를 변경하지 않는다. `ast_context.py`를 실제로
> 수정하지 않고, `agents.py`를 이동하지 않고, 기존 테스트를 바꾸지
> 않는다. ADR도 작성하지 않는다. 이 문서는 RFC이며 결정을 내리지
> 않는다 — 후속 ADC가 판단할 Decision Candidate만 제시한다.

## 핵심 질문

**Agent Package Refactoring(`mvp/agents.py` → `mvp/agents/{requirements,
design,backend,qa}.py`)을 위해, AST Context의 module discovery를
평면 module path뿐 아니라 dotted package module path까지 지원하도록
확장하는 것을 허용할 것인가?**

## 1. 현재 `agents.py` 기반 AST Context 동작

`ast_context.py`(ADC-0005 §1/§2)는 세 함수 모두 "module 이름 =
`hqs/development/mvp/` 바로 아래의 평면 `.py` 파일 하나"라는 동일한
전제를 공유한다.

| 함수 | 동작 | 근거 |
|---|---|---|
| `_mvp_source_files()` | `_MVP_DIR.glob("*.py")` — 하위 디렉터리 비재귀 | `ast_context.py:13-14` |
| `module_source_path(module)` | `module`을 `mvp/{module}.py` 단일 경로로 변환 | `ast_context.py:17-20` |
| `build_dependency_closure(module, function)`의 `resolve()` | `_MVP_DIR / f"{module_name}.py"` 단일 파일만 열어 AST 파싱 | `ast_context.py:77` |

현재 `agents.py`는 이 전제를 만족하는 평면 파일이며, 이 상태에서
다음이 실제로 성립한다(전부 real, mock 아님):

- `build_function_candidate_index()`가 산출하는 AST Function
  Candidate Index에 `agents.py`의 함수(`backend_agent_code_review`,
  `requirements_agent_requirement_analysis` 등)가 시그니처+docstring
  형태로 포함된다.
- `build_dependency_closure("agents", "_strip_code_fence")`가
  `mvp/agents.py`를 열어 해당 함수와 그 의존성만 폐쇄로 추출한다.
- `build_dependency_closure("workflow_project_intelligence",
  "run_issue_to_design")`가 상대 import(`from .agents import ...`)를
  재귀로 따라가 `agents` 모듈을 폐쇄에 포함시킨다.

## 2. `agents/` package 전환 시 발생하는 Contract 영향

`agents.py`를 `agents/` 패키지로 바꾸면(코드 변경 없이 가정만 함):

- `module_source_path("agents")`가 존재하지 않는 `mvp/agents.py`를
  가리키게 된다 — Stage 04 Target File Exposure가 module="agents"를
  대상으로 지정된 경우 파일을 찾지 못한다.
- `build_dependency_closure("agents", ...)`가 `path.exists()`
  체크에서 즉시 반환되어 `order`가 비고, `if not order: raise
  ValueError`로 종료한다.
- `build_function_candidate_index()`의 glob이 `agents/` 하위 파일을
  전혀 보지 못하므로, Stage 01의 AST Function Candidate Index에서
  Agent 함수 전체가 조용히 사라진다 — 이는 어떤 예외도 던지지 않고
  발생하는 **무음(silent) 산출물 변화**다.
- Python 자체의 제약으로 `agents.py`와 `agents/`를 같은 디렉터리에
  동시에 둘 수 없다 — "패키지 전환 + 평면 파일 겸용 유지"라는 절충은
  존재하지 않는다.

## 3. ADC-0005 Evidence와의 관계

ADC-0005(RFC-0007 후속)는 이 세 함수(판단 1: Candidate Index, 판단
2: Dependency Closure)를 **모두 Accept**했으나, 그 Evidence는 다음
전제 위에서만 수집됐다:

- 판단 1의 Risk란: "3건 모두 이 저장소(`hqs/development/mvp/`) 규모에서
  검증됐다 — 함수 수가 수십~수백 개로 늘어난 저장소에서 인덱스
  크기·식별 정확도가 유지되는지는 검증되지 않았다."
- 판단 2의 Evidence(T09~T19)는 전부 `hqs/development/mvp/` **평면
  구조** 위에서 수행됐다 — `agents`, `engine`,
  `project_intelligence`, `workflow`, `workflow_project_intelligence`
  모두 최상위 평면 파일이다. 하위 패키지 구조에서의 재현은 T06~T19
  어디에도 없다.
- 즉 ADC-0005의 Accept 4건은 **"평면 모듈 구조"라는 조건 위에서
  성립한 Decision**이지, "모든 물리적 파일 배치에서 성립한다"는
  일반 결론이 아니다. Dotted package path 지원 확장은 ADC-0005가
  검증한 범위를 벗어난 새 조건에서 같은 함수를 재사용하겠다는
  요청이므로, 기존 Accept가 자동으로 커버하지 않는다.

## 4. `ast_context.py` 변경 필요성

Dotted package path를 지원하려면 최소한 다음 변경이 필요하다(구현은
하지 않음, 필요성만 서술):

- `_mvp_source_files()` — `glob("*.py")` → 재귀 탐색(`rglob` 등)으로
  변경, 각 파일의 dotted 이름(`agents.backend`)을 함께 계산해야 함.
- `module_source_path(module)` — `module`에 `.`이 포함된 경우
  `mvp/{a}/{b}.py`로 분해하는 로직 추가.
- `build_dependency_closure()`의 `resolve()` — 동일하게 dotted
  이름을 경로로 변환하는 로직 추가. 상대 import 추적(`node.module`)도
  dotted 대상을 만들어낼 수 있어야 함(현재는 `imports[alias] =
  (node.module, alias.name)`가 단일 레벨만 가정).

이는 ADC-0005가 Accept한 로직 자체(순수 정적 분석, Engine 미호출,
90줄 내외 함수)의 **동작 조건을 확장하는 것**이며, 파일 이동이나
포맷팅 수준의 변경이 아니다.

## 5. 기존 테스트 Contract에 미치는 영향

`test_ast_context.py`/`test_stage_01.py`의 4개 테스트가 `"agents"`를
리터럴 모듈 이름으로 mock 없이 사용한다(§1 표와 동일 근거). Dotted
path 지원을 추가하는 것 자체는 기존 평면 모듈 이름(`"agents"`,
`"engine"`, `"project_intelligence"` 등)의 동작을 바꾸지 않으므로,
**`ast_context.py` 확장만으로는 이 4개 테스트가 깨지지 않는다** —
단, `agents.py`가 실제로 `agents/` 패키지로 이동하는 후속 작업이
실행되는 시점에는, 저 4개 테스트의 대상 함수(`_strip_code_fence`
등)가 어느 서브모듈로 이동했는지에 맞춰 리터럴(`"agents"` →
`"agents.backend"` 등)을 갱신해야 한다. 즉 **Contract 영향은
`ast_context.py` 확장 자체가 아니라, 그 확장을 전제로 한 후속
`agents.py` 이동 작업에서 발생**한다 — 이 RFC는 그 이동을 수행하지
않으므로 이번 Task에서 테스트 변경은 필요하지 않다.

## 6. 대안 비교

| 대안 | 설명 | Frozen 컴포넌트 영향 | 테스트 Contract 영향 | 목표 구조(패키지) 달성 |
|---|---|---|---|---|
| A. `agents.py` 유지 | 패키지화를 포기하고 단일 파일 내부를 책임별 섹션/함수로만 재정리 | 없음 | 없음 | 미달성(파일 분리 없음) |
| B. `ast_context.py` package 지원 확장 | 본 RFC의 핵심 질문대로 dotted path 지원을 추가한 뒤 `agents/` 패키지로 이동 | 있음 — ADC-0005 Accept 4건의 검증 조건(평면 구조) 밖으로 로직을 확장 | 있음 — 패키지 이동 시점에 4개 테스트 리터럴 갱신 필요 | 달성 |
| C. 다른 호환성 방식(예: `agents/` 패키지 + `mvp/agents.py` 위치에 재-export만 하는 최상위 shim 모듈을 별도 이름으로 유지) | Python 제약상 `agents.py`와 `agents/`는 동일 이름 공존 불가하므로, 실제로는 "다른 이름의 평면 shim 파일 1개"를 추가로 유지하는 방식만 가능(예: 실제 함수는 패키지에, `ast_context.py`가 참조할 대표 함수 1~2개만 담은 별도 평면 파일 유지) | 없음(ast_context.py 무변경) | 부분 있음 — 패키지 내 이동된 함수 대부분은 여전히 AST Candidate Index/Closure 밖에 있음 | 부분 달성(shim의 성격에 따라 절충 필요) |

## 7. Architecture Impact

**NONE으로 잠정 판단** — 대안 B(`ast_context.py` 확장)를 택하더라도
Runtime/Registry/Event Bus/Engine Gateway 등 `IMPLEMENTATION_RULES.md`
금지 목록에 해당하는 개념은 추가되지 않는다. 확장 대상은 이미 Kernel
범위 밖(MVP Implementation, `BASELINE.md` Not Included)으로 확정된
순수 정적 분석 함수 내부 로직뿐이다. 다만 이 판단은 ADC-0005가
판단 4에서 사용한 것과 같은 근거 구조를 재사용한 것이며, 실제
Architecture Drift 여부는 후속 ADC가 다시 명시적으로 재확인해야
한다.

## 8. Contract Impact

- `agents.py`의 함수 시그니처(`requirements_agent_requirement_
  analysis` 등), `AGENT_CAPABILITY_MAP`/`HELLO_SDLC_CAPABILITY_MAP`
  값, Engine 호출 방식, Prompt 문자열 — 이 RFC가 다루는 어떤 대안도
  이들을 변경하지 않는다.
- `ast_context.py`의 공개 함수 시그니처(`module_source_path(module:
  str) -> Path`, `build_dependency_closure(module: str, function:
  str) -> str`, `build_function_candidate_index() -> str`) 자체는
  대안 B에서도 변경되지 않는다 — 확장은 내부 구현(모듈 이름 → 경로
  변환 로직)에 한정되며, 호출부(Stage 01/04)의 호출 방식은 그대로다.
- 대안 B를 택할 경우 **테스트 Contract**는 §5에서 서술한 대로,
  `ast_context.py` 확장 시점이 아니라 `agents.py` 이동 시점에
  변경이 필요해진다 — 이 Contract 영향의 승인 여부는 이 RFC가 아니라
  후속 ADC(및 필요시 그 이후 별도 Task)에서 다뤄야 한다.

## 9. 권장 Decision (Candidate, 확정 아님)

이 RFC는 결정하지 않는다. 후속 ADC가 판단할 Decision Candidate로
다음을 제시한다.

- **Decision Candidate**: 대안 B(`ast_context.py`의 module discovery를
  dotted package path까지 지원하도록 확장) — **조건부 Accept 권고**.
  - 근거: 대안 A는 사용자가 요청한 목표 구조(패키지 분리)를 달성하지
    못하고, 대안 C는 Python의 이름 충돌 제약상 실질적으로 "shim
    파일 유지"에 불과해 패키지 전환의 이점(책임별 파일 분리)을
    온전히 얻지 못한다. 대안 B가 목표 구조를 그대로 달성하면서
    Architecture Impact가 NONE으로 유지되는 유일한 대안이다.
  - 조건: (a) `ast_context.py` 확장은 기존 평면 모듈 동작을 전혀
    바꾸지 않는 **추가(additive)** 변경으로 한정한다. (b) 확장 자체와
    `agents.py`의 실제 이동은 별도 Task로 분리해, 확장이 먼저
    검증(회귀 테스트 109 유지 확인)된 뒤에만 이동을 진행한다. (c)
    `agents.py` 이동 시점에 갱신이 필요한 4개 테스트 리터럴 변경은
    "기존 테스트 Contract 유지" 원칙의 예외로 이 시점에 함께
    명시적으로 승인한다.
  - Evidence Gap: 저장소 규모가 커졌을 때의 Candidate Index 정확도
    (ADC-0005 판단 1의 기존 Risk)와 마찬가지로, dotted path 확장
    이후의 동작은 아직 재현/검증되지 않았다 — 후속 ADC가 Accept할
    경우, 실제 구현 후 최소 1건의 real Engine E2E 재검증을 함께
    요구할 것을 권고한다.

## Out of Scope

- Agent Class/Runtime/Registry/Manager 도입.
- 신규 Capability 추가.
- Engine 호출 방식, Prompt, Workflow/Stage 로직 변경.
- Agent Definition(4개 Agent, 5개 Capability) 자체의 재검토 —
  `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`가 이미 확정했다.
- 실제 `ast_context.py` 코드 변경, `agents.py` 이동, 테스트 파일 수정
  — 전부 이 RFC 이후 별도 Task.

## Non-goals

- 이 RFC는 Development HQ Baseline이나 Jarvis OS Architecture
  Baseline을 변경하지 않는다.
- 이 RFC는 ADC나 ADR을 작성하지 않는다 — Decision Candidate만
  제시한다.
- 이 RFC는 Agent Package Refactoring을 대신 완료하지 않는다.

## 다음 절차

1. 이 RFC의 핵심 질문(§핵심 질문)에 대해 `docs/decisions/adc/`에
   Decision Candidate로 등록한다.
2. ADC가 §9의 조건부 Accept를 채택하면, `ast_context.py` 확장을
   별도 Task로 진행하고 회귀 테스트(109 기준선) 유지를 확인한다.
3. 확장이 검증된 이후에만 `agents.py` → `agents/` 이동을 재개하고,
   그 시점에 4개 테스트 리터럴 갱신을 함께 진행한다.
4. ADC가 대안 A 또는 C를 채택하면, Agent Package Refactoring 요청은
   그에 맞춰 범위를 재조정한다(이 RFC는 그 재조정 내용을 미리
   규정하지 않는다).
