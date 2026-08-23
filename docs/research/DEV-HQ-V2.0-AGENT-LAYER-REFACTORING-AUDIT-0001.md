# DEV-HQ-V2.0 — Agent Layer Readiness & Refactoring Audit

**문서 성격**: Audit(READ 중심 + 최소 문서 정정 2건). 새 RFC/ADC/ADR을
작성하지 않는다. Architecture/Contract/검증된 Stage 로직을 변경하지
않는다.

## 1. Agent Layer 상태

**결론: 현재 상태 그대로 v2.0에 포함 가능(추가 구현 불필요).**

- `STRUCTURE.md`의 공식 모델은 `Workflow → Task → Capability → Agent`
  이며, "Task는 Agent를 직접 호출하지 않는다 — Runtime이 Task를
  Agent에 배분한다"고 명시한다. 이 Runtime 배분 계층은 Kernel 범위이고
  `BASELINE.md` Not Included/`IMPLEMENTATION_RULES.md`가 Runtime/Registry
  구현 자체를 금지한다.
- 실제 구현(`agents.py`)은 Runtime 없이 "Agent 이름을 접두어로 가진
  Capability 함수"(`backend_agent_code_review`,
  `requirements_agent_requirement_analysis` 등)로 Agent를 나타낸다 —
  이는 MVP-0001부터 이미 승인된 단순화이며(`MVP.md`, `HANDOVER.md`
  "What Claude Code Can Do": "Agent-Capability 매핑을 리터럴 딕셔너리로
  작성"), Stage 01~05는 이 패턴을 그대로 재사용했을 뿐 새로 도입하지
  않았다.
- Stage 코드(`stage_02.py`~`stage_05.py`)는 Capability 함수를 직접
  import해 호출한다 — 공식 모델의 "Capability 경유 + Runtime 배분"을
  건너뛴 것처럼 보이지만, 이는 MVP-0001의 `workflow.py`가 이미 같은
  방식으로 `agents.py`를 직접 호출해온 것과 동일한, 이미 승인된 경로다.
- Agent를 실제 객체/클래스/상태로 승격시키는 것은 Runtime/Registry를
  Kernel Extraction 없이 먼저 만드는 것과 같으므로 지금 시도하면
  Implementation Stop Trigger에 해당한다(`IMPLEMENTATION_RULES.md`).
  **Agent Layer는 "아직 구현 안 됨"이 아니라 "Kernel이 준비되기 전까지
  의도적으로 이 수준에 머문다"가 정확한 상태 진단이다.**
- 중복/불필요한 Agent 계층 없음 — `AGENT_CAPABILITY_MAP`/
  `HELLO_SDLC_CAPABILITY_MAP` 2개 리터럴 딕셔너리만 존재하고, 그 이상의
  래퍼/클래스는 없다.

## 2. Refactoring Audit 결과

전체 구조(`agents.py`/`engine.py`/`workflow.py`/`cli.py`/`stages/01~05`/
`tests/`/Governance 문서)를 점검했다. 항목별 발견사항:

| 항목 | 발견 | 분류 |
|---|---|---|
| Stage 간 중복 로직 — Stage 02/03의 "골격 추출 + 텍스트 직렬화 + 기존 Capability 호출" 패턴이 구조적으로 유사(필드는 다름) | 각 Stage 독립 실행 요구사항(`stages/*/README.md`, 매 세션 반복 지시)과 상충하는 공유 모듈 도입 없이는 제거 불가 | DEFER |
| Agent/Engine 호출 중복 — `stage_04._assemble_build_input()`이 `workflow_ast_context.run_pipeline_with_ast_context()`의 조립 로직(Closure/Exposure 삽입 순서)을 그대로 재현 | 실제 코드 중복(있음). 검증된 `workflow_ast_context.py`(ADC-0005 §8, Scope 준수 3/3)를 건드리지 않기 위한 의도적 선택이었음이 `stage_04.py` docstring에 이미 기록됨 | SHOULD FIX(향후 공유 helper로 추출 — 이번엔 보류) |
| Workflow/CLI 책임 중복 | 없음 — `workflow.py`는 orchestration만, `cli.py`는 입출력만. Stage 내부 로직 복제 없음(코드 확인 완료) | NO ISSUE |
| import 구조 — 각 `stage_0N.py`/`workflow.py`가 모듈 최상단에서 `sys.path.insert()`를 반복 실행(패키지화되지 않은 폴더 구조의 결과) | 중복 경로 삽입이 누적되나 기능적 부작용 없음(idempotent). Stage 독립 실행 요구사항의 직접적 귀결 | DEFER |
| 테스트 중복 — `SAMPLE_ISSUE` 등 fixture성 리터럴이 `test_stage_0N.py`마다 반복 정의됨 | 사소함, `conftest.py` 공유 fixture 도입은 이번 범위의 "불필요한 추상화 금지" 원칙과 충돌할 만큼의 이득 없음 | NO ISSUE |
| 명명/파일 구조 불일치 — `hqs/development/workflow.py`(신규, Stage orchestration)와 `hqs/development/mvp/workflow.py`(MVP-0001)가 동일 basename | 두 파일 모두 docstring에서 서로를 명시적으로 구분·교차 참조함(혼동 완화 조치 기 반영). 사용자가 직접 지정한 구조 원칙(다이어그램)을 그대로 따른 결과 | NO ISSUE |
| 문서와 실제 코드 불일치 — `hqs/development/mvp/README.md`가 MVP-0001 4개 파일만 나열하고, 이후 추가된 10개 파일(project_intelligence/ast_context/workflow_ast_context/workflow_0002~hello_sdlc 등)과 Stage/workflow.py/cli.py 트랙을 전혀 언급하지 않음 | 실제 존재 | **MUST FIX(수정 완료 — 아래 4번 참고)** |
| 문서와 실제 코드 불일치 — `HANDOVER.md` Current Status 표가 이번 세션 전체(RFC-0007 재평가부터 CLI Integration까지)를 전혀 반영하지 않음 | 실제 존재 — HANDOVER.md는 CLAUDE.md가 "현재 작업 상태" 1차 참조 문서로 지정한 문서 | **MUST FIX(수정 완료 — 아래 4번 참고)** |
| Legacy/MVP 코드와 v2.0 코드의 경계 | `mvp/` 디렉터리 안에 v1.0 Freeze 대상(MVP-0001~0052)과 v2.0 신규 추가(ast_context.py 등)가 물리적으로 섞여 있으나, 각 파일 자체의 docstring과 Governance 문서(ADC-0005 등)로 소속이 식별 가능함. 전용 경계 문서는 없음 | DEFER(향후 v2.0 Freeze 문서에서 명시적으로 정리 권장 — `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`와 대응하는 v2.0판) |
| Architecture Drift 가능성 | 없음 — 모든 Stage/Workflow/CLI가 기존 Capability/Agent/Engine 함수만 재사용, 새 Interface/Contract 미도입 확인(각 RESPONSIBILITY.md에 이미 명시) | NO ISSUE |
| 유지보수성/확장성/불필요한 복잡성 | Stage 06(DevOps & Release) 폴더가 README.md 1개만 있고 코드 없음(README에 이미 "미구현" 명시) — 의도된 상태, 문제 아님 | NO ISSUE |
| Policy 판정 도입 여부 | Stage 05가 PASS/FAIL/PARTIAL을 Engine 판정이 아닌 결정적 규칙으로만 산출함을 재확인(코드 직접 확인) — Policy 구현 금지 원칙 준수 | NO ISSUE |
| Governance 문서 정합성 | `docs/decisions/adr/README.md`/`docs/governance/adc/README.md`의 개수 표기가 최신 상태와 일치함(Stage 01~05 자체는 신규 ADC/ADR을 만들지 않았으므로 갱신 대상 아님) | NO ISSUE |
| `__pycache__` 등 산출물 커밋 여부 | 없음(`git ls-files` 확인, `.gitignore`에 `__pycache__/` 존재) | NO ISSUE |

## 3. MUST FIX

1. **`hqs/development/mvp/README.md`가 자기 디렉터리의 실제 파일 10여 개와
   Stage/Workflow/CLI 트랙을 설명하지 않음** — "이 문서의 범위" 절을
   추가해 MVP-0001 4개 파일만 다룬다는 것과 나머지 산출물의 참조 위치를
   명시(수정 완료, Contract/동작 변경 없음).
2. **`HANDOVER.md` Current Status가 이번 세션 전체(v2.0)를 반영하지
   않음** — Current Status 표에 "Development HQ v2.0" 행 1개를
   추가해 존재와 Evidence 위치를 기록(수정 완료, v1.0 Freeze 선언·
   Next Step 구조는 변경하지 않음 — Freeze 선언은 이 Audit의 권한 밖).

두 항목 모두 문서 전용 변경이며, 코드/Contract/이미 검증된 동작은
건드리지 않았다.

## 4. SHOULD FIX

- `stage_04._assemble_build_input()`과 `workflow_ast_context.run_
  pipeline_with_ast_context()`의 조립 로직 중복. 향후 별도 세션에서
  `workflow_ast_context.py`에 공유 helper(`assemble_build_input()`)를
  추출하고, 두 호출부가 이를 재사용하도록 정리하는 것을 권장한다 — 단,
  이는 ADC-0005 §8에서 이미 real Engine E2E로 검증된 코드를 건드리는
  작업이므로 그 자체의 재검증(E2E 재실행)을 동반해야 한다. 이번 Audit
  에서는 수행하지 않는다(Freeze를 막지 않음).

## 5. DEFER

- Stage 02/03의 골격 추출 패턴 유사성 — Stage 독립 실행 요구사항이
  유지되는 한 공유 추상화를 도입하지 않는다.
- `sys.path.insert()` 반복 — Stage 폴더가 패키지화되지 않은 구조의
  자연스러운 결과이며 기능적 문제 없음.
- Legacy(v1.0)/v2.0 경계를 명시하는 전용 Freeze 문서 부재 — 다음
  단계(Dev HQ v2.0 Freeze Review)에서 `DEVELOPMENT-HQ-V1.0-FREEZE-
  0001.md`에 대응하는 문서를 작성할 때 함께 정리 권장.
- `docs/architecture/core/DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`가 실제
  경로(`hqs/development/mvp/`)와 다른 경로(`development-hq/mvp/`)를
  인용하는 것으로 보이는 표기 — 이번 Audit 대상(v2.0 Stage/Workflow/
  CLI) 이전부터 존재한 무관 문서이므로 이번 범위에서 다루지 않는다.

## 6. 최종 Freeze 가능 여부

**가능** — Agent Layer는 현재 상태(Runtime 없는 명명 규칙 수준)로
v2.0에 포함해도 Architecture 위반이 없고, Refactoring Audit에서 발견된
문제 중 Freeze를 막을 만한 것(MUST FIX)은 문서 정합성 2건뿐이었으며
둘 다 이번 Audit에서 문서 전용으로 즉시 해결했다. SHOULD FIX 1건과
DEFER 항목들은 Freeze를 막지 않는 개선/후속 과제다. 실제 Freeze 선언
자체(v1.0의 `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`에 대응하는 v2.0
Freeze 문서 작성)는 이 Audit의 권한 밖이며 별도 세션에서 수행한다.

## 7. 실제 변경 내용과 검증 결과

- `hqs/development/mvp/README.md` — "이 문서의 범위" 절 추가(문서 전용)
- `hqs/development/HANDOVER.md` — Current Status 표에 v2.0 행 1개 추가(문서 전용)
- 코드/Contract/Stage 로직/Workflow/CLI/Agent/Engine 변경 없음
- 회귀: `pytest hqs/development/mvp/tests/ -q` → **109 passed**(변경
  전과 동일 — 문서만 수정했으므로 예상대로 회귀 없음)
- Real Engine E2E: 이번 Audit은 코드를 변경하지 않았으므로 별도
  E2E를 새로 실행하지 않았다 — 직전 CLI Integration E2E
  (`DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001.md`, verdict PASS)가 계속
  유효하다
