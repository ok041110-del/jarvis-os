# OpenRouter Production Engine Migration — Implementation

## Summary

- `RFC-0041`/`ADC-0044`/`ADR-0027`이 승인한 Free Model Selection
  Architecture를 실제 Stage 01~05 Production 코드에 Migration했다.
- 새 Engine Adapter(`hqs/development/mvp/openrouter_engine.py`)를
  구현하고, Stage 01/02(Reasoning), Stage 01(PRD Synthesis의
  Requirements Agent), Stage 03(Design), Stage 04(Implementation),
  Stage 05(Review)의 실제 LLM 호출 지점 5곳(파일 5개, import 5줄)을
  이 Adapter로 연결했다.
- **ADR-0027 §10 명시적 Deviation(사용자 승인)**: `ADR-0027` §10은
  "Validation Gate를 전부 통과하기 전에는 Stage 01~05 Production
  코드를 실제로 변경하지 않는다"고 명시했다. 이 작업은 그 문구와
  직접 충돌하는 선택 — 사용자가 명시적으로 "오늘 Stage import까지
  전부 전환"을 선택했다(AskUserQuestion 응답, 이 세션 기록). 이
  Migration은 **코드 배선까지만** 완료된 상태이며, Gate가 요구하는
  실측 검증(quota 정상 상태 실행/latency/model quality/Stage 05
  Review 품질/retry 회복/E2E)은 **내일 별도로 수행**하고, 그 결과가
  나오기 전까지 이 경로의 Production 신뢰성은 검증된 것으로
  간주하지 않는다.
- Stage Contract/Output Schema/Stage 순서/deterministic validation
  semantics는 전부 보존했다(git diff가 import 라인 5개 + docstring
  주석만 변경했음을 증명).
- 기존 Production 테스트 스위트: **352 passed, 6 skipped**(기존 324
  + 신규 28개, 회귀 없음). 신규 테스트 28개(Adapter 24개 + Engine
  Boundary 확장 4개) 추가.
- Central Router/Gateway 미생성, 특정 모델 하드코딩 없음, Stage별
  모델 매핑 없음, scoring/judge/latency-routing 없음 — 전부 정적
  검사로 확인(§7).
- 오늘 실제 OpenRouter 호출을 시도한 검증은 **수행하지 않았다** —
  이는 내일 Validation Gate의 몫이다(§9).

---

## 1. 사전 조사(main/현재 branch 대조)

- `git status --short` — 작업 착수 전 clean.
- `git branch --show-current` — `claude/jarvis-openrouter-validation-bin9aj`.
- Governance 최신 상태 확인: 현재 branch `RFC-0041`/`ADC-0044`/`ADR-0027`
  (이번 세션 직전 커밋으로 이미 존재), main은 그보다 이전 상태
  (`RFC-0037`/`ADC-0040`/`ADR-0024`) — 번호 충돌 없음, 새 문서를
  만들지 않고 기존 3건을 그대로 구현 근거로 삼았다(이번 작업은
  Governance 문서를 수정하지 않는다, §8).
- `RFC-0040`/`ADC-0043`/`ADR-0026`(Architecture Boundary 원 결정),
  `RFC-0041`/`ADC-0044`/`ADR-0027`(Production Adoption 결정), `ADR-0024`
  (2-Engine 구조), `IMPLEMENTATION_RULES.md`(Multi-Engine 허용 범위)를
  코드 작업 착수 전 재확인했다.
- 기존 Stage 01~05 실제 LLM 호출 지점은 `OPENROUTER-STAGE-PRODUCTION-
  MIGRATION-EVIDENCE-0001.md`가 이미 조사해둔 것을 재사용하되, 이번
  조사에서 그 문서가 놓친 지점을 하나 추가로 발견했다(§2).

## 2. Migration 대상 — 실제 호출 지점(최종)

| # | 파일 | 이전 Engine | 이후 Engine | 비고 |
|---|---|---|---|---|
| 1 | `hqs/development/stages/01_context_analysis/reasoning.py` | ChatGPT | OpenRouter | Stage 01 Multi-Agent Reasoning(intent/goal/requirement/ambiguity) |
| 2 | `hqs/development/mvp/agents/requirements.py` | ChatGPT | OpenRouter | **이번 조사에서 새로 발견** — `stages/01_context_analysis/prd_synthesis.py::synthesize_prd()`가 호출, `stage_01_multi_agent.py::run_stage_01_multi_agent()`(실제 Stage 01 진입점, `teams/context/team.py`가 호출)의 일부 |
| 3 | `hqs/development/stages/02_planning_specification/task_dependency_agent.py` | ChatGPT | OpenRouter | Stage 02 Task & Dependency Agent |
| 4 | `hqs/development/mvp/agents/design.py` | ChatGPT | OpenRouter | Stage 03(`stage_03.py::design_agent_design` 호출) |
| 5 | `hqs/development/mvp/agents/backend.py`(2곳) | ChatGPT(review) / Claude Code(generation) | OpenRouter(둘 다) | Stage 04(`code_generation`)/Stage 05(`code_review`) |

**의도적으로 Migration 범위 밖에 남긴 것**:

- `hqs/development/mvp/agents/qa.py`(`qa_agent_test_execution`, Claude
  Code Engine) — Production Stage 05는 이 Capability를 호출하지
  않는다(결정적 `pytest` subprocess 실행을 쓴다, `OPENROUTER-STAGE-
  PRODUCTION-MIGRATION-EVIDENCE-0001.md` §1 Stage 05 항목이 이미
  확인) — Migration 대상 자체가 아니므로 손대지 않았다.
- `hqs/development/mvp/workflow_ast_context.py` — 실제 Stage 01~05
  파이프라인 진입점이 아니라 AST Context 유틸리티의 과거 예제
  모듈(T18 Evidence 스냅샷, `HANDOVER.md` "Development HQ Team
  Architecture Migration v1" 항목이 실제 진입점을 `workflow.py` →
  `teams/` → `stages/0N_*/stage_0N.py`로 명시) — 이 파일 자신의
  직접 ChatGPT 호출은 건드리지 않았다(`RFC-0041` §Migration Scope
  범위 밖).
- `mvp/workflow.py::run_mvp_0001` — 이것도 MVP-0001 구버전 단일 흐름
  (Dev HQ v2.0 Stage 01~05와 다른 레거시 경로)이며, 이 흐름이 호출
  하는 `backend_agent_code_review`는 §2의 5번 변경으로 이미 함께
  전환됐다(공유 Agent 함수이므로 자동 반영, 별도 작업 불필요).

## 3. OpenRouter Production Engine Adapter 구현

파일: `hqs/development/mvp/openrouter_engine.py`(신규, 251줄).

- 외부 계약: `call_engine_via_openrouter(prompt: str) -> str`, 실패
  시 단일 `RuntimeError` — `chatgpt_engine.py::call_engine_via_chatgpt`/
  `engine.py::call_engine`과 완전히 동일한 형태(사용자 지시 §11).
- 내부 8단계 중 Jarvis 책임 구간(Free Pool → Deterministic Filter →
  Candidate Selection ≤3 → `models[]` 요청)을 그대로 구현:
  - `_fetch_free_model_pool()` — `/api/v1/models` 조회, `:free` 접미사만.
  - `_estimate_min_context_tokens()` — 프롬프트 길이 기반 추정(추정치
    임을 docstring에 명시, 과장하지 않음).
  - `_deterministic_filter()` — free 여부(Pool이 이미 보장)/알려진
    비기능 모델 제외/context 길이/modality(text)만으로 판정. 판정
    불가능한 항목(예: `context_length` 없음)은 제외하지 않는다
    (`ADR-0026` §6 원칙 그대로, `test_missing_context_length_metadata_
    is_not_excluded`로 회귀 방지).
  - `_select_candidates()` — 3개 초과 시 Pool 응답 순서 그대로 앞에서
    부터 자름(재정렬 없음).
  - `_single_chat_call()` — `models[]` 필드로 OpenRouter Chat
    Completions 호출.
  - `_classify_failure()` — `429_quota`/`5xx`/`malformed_response`/
    `connection_error`/`empty_response` 5개로 분리, **quota를 모델
    품질 실패와 절대 혼동하지 않음**(`test_classify_failure_never_
    conflates_quota_with_malformed`로 회귀 방지).
  - `call_engine_via_openrouter()` — 위 전부를 orchestrate, bounded
    retry(최대 1회, 실패 후보를 재시도 Pool에서 제외).
- 모든 Stage 공통 상수(`_DEFAULT_OUTPUT_TOKEN_BUDGET = 2048`)만 사용
  — Stage별 값을 두지 않는다(Stage-model 매핑의 다른 형태 재도입
  방지, `test_stage_requirements_have_no_model_name_field`류 원칙과
  동일 정신).
- API Key: `OPENROUTER_API_KEY` 환경변수가 있을 때만 Authorization
  헤더를 실어 보낸다 — 없으면 헤더 자체를 생략(Egress Proxy류 자동
  인증 환경 지원). 코드/로그/예외 메시지 어디에도 Key 값을 남기지
  않는다(`test_api_key_read_only_from_env_not_hardcoded`,
  `test_no_authorization_header_when_api_key_absent`로 확인).
- Central Router/Gateway 패턴 미포함을 정적으로 확인
  (`test_no_central_router_or_gateway_abstraction_in_module`).

## 4. Stage 01~05 연결

§2 표의 5개 파일에서 import 한 줄씩만 변경했다(각 파일 diff 3~7줄,
전부 import 대상 변경 + docstring 주석 갱신). Stage/Agent 코드의
함수 본문, 프롬프트 구성 로직, 반환값 처리 로직은 **한 글자도**
바꾸지 않았다 — `call_engine`/`call_engine_review`/`call_engine_
generation`이라는 목적 기반 이름(Provider-specific 이름 아님)을
그대로 유지한 채 그 이름이 가리키는 실제 함수만 바뀌었다.

## 5. Contract/Schema Regression

- Stage 01 Contract(`parse_structured_output` + 필수 키), Stage 02
  Contract(동일 파서 + `tasks`/`dependencies`), Stage 03 Contract(6개
  섹션 prose), Stage 04 Contract(AST 기반 Target 함수 확인), Stage 05
  Contract(`contracts.py` 결정적 검사) — **전부 무변경**. 이 Contract
  들을 검사하는 함수 자체를 수정하지 않았으므로 회귀 가능성이
  구조적으로 없다.
- `mvp/tests/test_stage_01*.py`, `test_stage_02.py`, `test_stage_03.py`,
  `test_stage_04.py`, `test_stage_05.py` 전부 기존 그대로 통과
  (§6 전체 스위트 결과에 포함).

## 6. Deterministic Validation / 기존 Regression 수행 결과

```
$ pytest mvp/tests/ -q
352 passed, 6 skipped
```

- 기존 324 passed(baseline) + 신규 28개(Adapter 24개 + Engine Boundary
  확장 4개) = 352. 6 skipped는 기존과 동일(무관 항목).
- 최초 실행에서 **3개 실패**가 있었다(정직하게 기록) — 전부 "Engine
  Boundary가 ChatGPT여야 한다"고 구시대 사실을 assert하던 기존
  회귀 테스트였다:
  - `test_ast_context.py::test_closure_follows_relative_imports_across_modules`
    — 의존성 폐쇄가 `chatgpt_engine`을 포함해야 한다고 assert —
    `openrouter_engine`으로 수정.
  - `test_engine_boundary.py::test_chatgpt_routed_files_import_chatgpt_engine_only`
    — `requirements.py`가 ChatGPT를 import해야 한다고 assert —
    Migration된 파일 목록(`OPENROUTER_ROUTED_FILES`)으로 재분류.
  - `test_engine_boundary.py::test_backend_py_splits_engine_boundary_by_capability`
    — `backend.py`가 ChatGPT+Claude Code 두 Engine을 각각 써야
    한다고 assert — 두 Capability 모두 OpenRouter를 쓰도록 검증
    로직을 갱신(`test_backend_py_uses_openrouter_engine_for_both_
    capabilities`로 이름도 변경, 사실을 반영).
  - 이 3개는 "Migration이 실패했다"는 신호가 아니라 "Engine Boundary
    가 실제로 바뀌었으니 그 사실을 검증하는 테스트도 바뀌어야
    한다"는, Migration 자체가 의도한 변화의 정상적 결과다. 이
    3개를 수정한 뒤 Adapter/Rollback/API Key 관련 대칭 테스트
    (`test_openrouter_engine_does_not_import_other_engine_modules`,
    `test_openrouter_engine_importable_standalone`,
    `test_openrouter_engine_defines_exactly_one_public_function`)를
    함께 추가해 3-Engine 체계 전체의 일관성을 다시 확인했다.

## 7. Production Diff Review

```
$ git status --short
 M hqs/development/mvp/agents/backend.py
 M hqs/development/mvp/agents/design.py
 M hqs/development/mvp/agents/requirements.py
 M hqs/development/mvp/tests/test_ast_context.py
 M hqs/development/mvp/tests/test_engine_boundary.py
 M hqs/development/stages/01_context_analysis/reasoning.py
 M hqs/development/stages/02_planning_specification/task_dependency_agent.py
?? hqs/development/mvp/openrouter_engine.py
?? hqs/development/mvp/tests/fake_openrouter_server.py
?? hqs/development/mvp/tests/test_openrouter_engine.py
```

- 10개 파일 — 5개 import 전환, 2개 회귀 테스트 갱신, 3개 신규
  파일(Adapter + fake server + Adapter 테스트). 의도한 Migration
  범위(§9 Migration Boundary — "LLM Engine adapter/Model selection
  path"만)를 벗어난 변경이 없다.
- **하드코딩 모델 검색**: `grep -rniE "gpt-4o|claude-[0-9]|nemotron|
  nex-agi|inclusionai" hqs/development/stages/ hqs/development/mvp/
  agents/ hqs/development/mvp/openrouter_engine.py` — **0건**.
- **기존 OpenRouter call path 검색**: 이번 작업 이전에는 `hqs/
  development/` 전체에 OpenRouter 참조가 0건이었다(`OPENROUTER-
  STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` §1이 이미 확인) —
  이번에 추가한 `openrouter_engine.py`가 유일한 참조 지점이다.
- **Central Router/Gateway 미생성**: `mvp/*.py`에 `*router*.py`/
  `*gateway*.py` 이름의 신규 파일 없음(`openrouter_engine.py` 자체는
  파일명에 "router" 문자열이 포함된 것이지 Router 모듈이 아니다 —
  `test_no_central_router_or_gateway_module_created`가 이미 이
  구분을 반영한 이름 목록으로 검사).
- **Rollback 경로 확인**: `git diff --stat -- hqs/development/mvp/
  chatgpt_engine.py hqs/development/mvp/engine.py hqs/development/
  mvp/omniroute_engine.py` — 빈 결과(3개 기존 Engine 모듈 전부
  무변경). `test_claude_code_engine_importable_standalone`/
  `test_chatgpt_engine_importable_standalone`가 여전히 통과 —
  두 모듈 다 독립적으로 여전히 import 가능함을 확인. Rollback은
  §2 표의 5개 파일에서 import 한 줄씩만 되돌리면 된다(`RFC-0041`
  §Rollback Strategy가 설계한 대로).

## 8. Governance 준수 확인

- `RFC-0040`/`ADC-0043`/`ADR-0026`/`RFC-0041`/`ADC-0044`/`ADR-0027`
  전부 무수정(`git diff --stat -- docs/architecture/core/` 빈 결과).
- **`ADR-0027` §10과의 관계(재확인)**: 이 Migration은 §10이 명시한
  "Gate 통과 전 Stage 01~05 Production 코드 변경 금지"와 문자
  그대로는 충돌한다 — 이 문서 §Summary가 이미 그 충돌을 명시했고,
  사용자가 이 구현을 진행하도록 명시적으로 선택했다(오늘 대화의
  AskUserQuestion 응답). 이 Deviation은 숨기지 않고 이 Evidence
  문서 전체에 걸쳐 반복적으로 표시한다 — "Migration 코드가
  구현됨"과 "Gate가 통과했음"은 서로 다른 사실이며, 후자는 **전혀
  주장하지 않는다**.
- Central Router/Gateway 미생성(§3, §7), 특정 모델 하드코딩 없음(§7),
  Stage별 모델 매핑 없음(§3 — 모든 Stage가 동일한 상수/로직 공유),
  Stage Contract/Output Schema/Stage 순서 무변경(§5).

## 9. 내일 별도 수행 — Validation Gate(`ADR-0027` §10, 12개 항목)

이 구현이 **하지 않은 것**을 명확히 남긴다:

1. quota 정상 상태에서의 실제 OpenRouter 호출 — 미수행.
2. Stage 01~05 각각의 실제 Contract 재확인(실제 LLM 응답 기준) —
   미수행(오늘은 offline/fake-server 테스트만).
3. Free Pool availability 실시간 재확인 — 미수행.
4. Candidate ≤3/`models[]` 정확성의 실제 API 응답 기준 재확인 —
   미수행(offline 테스트로 로직만 확인, §6).
5. Retry 실제 회복 효과(다른 candidate로의 실제 fallback) — 미수행.
6. Failure classification의 실제 API 응답 기준 재확인 — 미수행
   (offline 분류 로직만 확인).
7. Stage 05가 실제 Stage 04 Implementation으로 Review를 수행하는지
   (실제 LLM 응답 기준) — 미수행.
8. Stage 01→05 전체 E2E 실제 실행 — 미수행.

**이 8개 항목 중 어느 것도 오늘 "성공"으로 기록하지 않는다** — 이
Evidence 문서는 코드가 구현되고 offline/fake-server 테스트를
통과했다는 사실만 기록한다.

## Governance / Production 영향(요약)

- RFC/ADC/ADR 무수정.
- Production `hqs/` 코드 변경: §7 표(10개 파일, 의도한 Migration
  범위로 제한 확인).
- Stage Contract/Output Schema/Stage 순서/Agent/Capability 경계 —
  전부 보존.
- API Key/Credential 값 미출력.

## Related

- `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md`
- `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md`
- `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md`
  (§10 Validation Gate — 내일 수행 대상)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
- `docs/research/OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md`
  (이 Migration 이전의 STOP 기록, Migration 대상 조사의 선행 작업)
- `hqs/development/mvp/openrouter_engine.py`(신규 Adapter)
- `hqs/development/mvp/tests/test_openrouter_engine.py`,
  `hqs/development/mvp/tests/fake_openrouter_server.py`(신규 테스트)
