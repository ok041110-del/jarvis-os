# RFC-0008: Agent 함수 물리적 배치(단일 파일 ↔ 패키지)와 AST Context Module Resolution 경계

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Agent Package Refactoring 작업 중 구현 중단 지점에서 요청)
**대상**: `hqs/development/mvp/agents.py`를 `hqs/development/mvp/agents/`
패키지로 물리적으로 재배치할 수 있는가 — 재배치 방식의 경계만 다룬다.
**Evidence 범위**: `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`(Agent
Definition 확정), 실제 코드(`hqs/development/mvp/ast_context.py`,
`hqs/development/mvp/tests/test_ast_context.py`,
`hqs/development/mvp/tests/test_stage_01.py`). 새로운 실험은 하지
않았다 — Agent Package Refactoring 작업을 실제로 시작하기 직전, 코드
변경 전에 발견한 구조적 충돌만 기록한다.

> 본 RFC는 Agent Class/Runtime/Registry/Manager 도입, 신규
> Capability/Agent 추가, Engine/Prompt/Workflow/Stage 로직 변경을
> 다루지 않는다. 이미 확정된 Agent 4개·Capability 5개
> (`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`)를 물리적으로 어떤 파일
> 구조로 배치할 수 있는지, 그 배치가 이미 검증된 AST 기반 컴포넌트의
> 전제와 충돌하는지만 다룬다.

## 0. 이 RFC가 열린 이유

`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`로 확정된 4개 Agent
(Requirements/Design/Backend/QA)의 책임을 `mvp/agents.py` 한 파일이
아니라 `mvp/agents/{requirements,design,backend,qa}.py` 패키지로
분리하는 리팩토링을 요청받았다. 구현 착수 전 실제 코드를 확인한 결과,
이 재배치가 이미 Freeze·Evidence로 검증된 `ast_context.py`(ADC-0005
§1/§2)의 전제와 충돌함을 발견했다. 코드를 바꿔 우회하지 않고
(`IMPLEMENTATION_RULES.md` "Architecture 문제 발견 시 절차"), 사실만
기록한다.

## 1. 관찰된 사실

- `ast_context.py`의 모듈 탐색은 평면 구조만 인식한다:
  - `_mvp_source_files()`는 `_MVP_DIR.glob("*.py")`만 사용한다 — 하위
    디렉터리를 재귀 탐색하지 않는다(`ast_context.py:13-14`).
  - `module_source_path(module)`은 `module`을
    `hqs/development/mvp/{module}.py` **단일 파일 경로**로만
    변환한다(`ast_context.py:17-20`) — dotted path(`agents.backend`
    같은 패키지 하위 모듈 표기)를 지원하지 않는다.
  - `build_dependency_closure(module, function)`의 `resolve()`도
    동일하게 `_MVP_DIR / f"{module_name}.py"` 단일 파일만
    본다(`ast_context.py:77`).
- 이 세 함수는 Stage 01(AST Function Candidate Index, Dependency
  Closure)과 Stage 04(Target File Exposure)가 그대로 재사용하는,
  ADC-0005 §1/§2/§7/§8로 이미 real Engine E2E까지 검증된 Frozen
  컴포넌트다(`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` §1).
- 현재 테스트는 "agents"라는 모듈 이름이 `mvp/agents.py` 평면 파일로
  실제 존재함을 전제로 **mock 없이** 검증한다:
  - `test_ast_context.py::test_closure_single_module_contains_target_only_dependencies`
    — `build_dependency_closure("agents", "_strip_code_fence")`
  - `test_ast_context.py::test_closure_follows_relative_imports_across_modules`
    — 폐쇄 결과에 `# module: agents`가 포함되어야 함을 검증
  - `test_ast_context.py::test_closure_is_smaller_than_full_source_for_multi_module_case`
    — `agents.py` 파일을 직접 읽어 길이를 비교
  - `test_stage_01.py::test_target_given_computes_dependency_closure`
    — `stage_01.run_stage_01(SAMPLE_ISSUE, target=("agents", "_strip_code_fence"))`
- `agents.py`를 `agents/` 패키지로 바꾸면 위 4개 테스트가 실제로(mock이
  아닌 실제 파일시스템 기준으로) 실패한다 — `module_source_path("agents")`가
  더 이상 존재하지 않는 `mvp/agents.py`를 가리키게 되고,
  `build_dependency_closure()`는 `if not order: raise ValueError`로
  종료한다.
- 같은 이유로, Stage 01의 `build_function_candidate_index()`가
  산출하는 AST Function Candidate Index에서 Agent 함수 전체가
  사라진다(패키지 하위 파일은 glob 대상이 아니므로) — Stage 04가
  Agent 함수를 Target File Exposure 대상으로 식별할 수 있는 경로도
  함께 사라진다. 이는 테스트로 직접 고정되어 있지는 않지만, Stage
  01/04의 실제 산출물이 달라지는 기능적 회귀다.
- Python 자체의 제약: 같은 디렉터리에 `agents.py`와 `agents/`를 동시에
  둘 수 없다(이름 충돌) — "패키지로 완전히 전환하되 평면 파일도
  겸용으로 유지"하는 절충은 불가능하다.

## 2. 이 RFC가 결정하지 않는 것

- `agents.py`의 내부를 책임별로 재정리할 수 있는지 여부(패키지화 없이
  단일 파일 내부 재구성) — 이는 Architecture 충돌이 없으므로 RFC
  대상이 아니다.
- `ast_context.py`를 확장해 dotted module path(`agents.backend`)를
  지원하도록 바꿀지 여부 — 이는 Freeze된 ADC-0005 컴포넌트의 실제
  변경이며, 이 RFC는 그 변경이 필요한지 제기할 뿐 결정하지 않는다.
- 기존 4개 테스트의 리터럴(`"agents"`)을 변경할지 여부 — 이는
  "기존 테스트 Contract 유지" 원칙과 직접 충돌하므로 Governance
  판단이 선행되어야 한다.

## Out of Scope

- Agent Class/Runtime/Registry/Manager 도입.
- 신규 Capability 추가.
- Engine 호출 방식, Prompt, Workflow/Stage 로직 변경.
- Agent Definition(4개 Agent, 5개 Capability) 자체의 재검토 —
  `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`가 이미 확정했다.

## Non-goals

- 이 RFC는 Development HQ Baseline이나 Jarvis OS Architecture
  Baseline을 변경하지 않는다.
- 이 RFC는 `ast_context.py`를 직접 수정하지 않는다.
- 이 RFC는 Agent Package Refactoring을 대신 완료하지 않는다 — 실제
  리팩토링(코드 이동)은 후속 ADC 판단 이후에만 진행한다.

## 다음 절차

이 RFC 자체는 아무것도 결정하지 않는다. 후속 ADC가 필요하다면 다음만
판단 대상이 된다.

1. `mvp/agents.py`를 `mvp/agents/` 패키지로 물리적으로 재배치하는
   것을 허용할지, 아니면 단일 파일 내부 재정리(패키지화 없이 책임별
   섹션/함수 분리)로 대체할지.
2. (1)에서 패키지화를 허용한다면, `ast_context.py`의 모듈 탐색 로직을
   확장해 dotted path를 지원하는 변경을 별도 작업으로 승인할지, 그
   경우 `test_ast_context.py`/`test_stage_01.py`의 리터럴
   (`"agents"` → `"agents.backend"` 등) 갱신을 "기존 테스트 Contract
   유지" 원칙의 예외로 허용할지.
3. (1)에서 패키지화를 허용하지 않는다면, Agent Package Refactoring
   요청은 "단일 파일 내부 책임 분리"로 범위를 좁혀 재상정한다.
