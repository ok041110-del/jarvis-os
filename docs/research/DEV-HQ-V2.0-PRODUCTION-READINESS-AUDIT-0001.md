# Development HQ v2.0 Production Readiness Audit

**문서 성격**: READ-ONLY Audit. 이 문서는 Architecture를 변경하거나, 새
Component/Interface/Contract를 설계하거나, Production 코드를 수정하지
않는다. 이 Audit이 발견한 모든 개선 필요 사항은 Gap 또는 Recommendation으로만
기록하며, 이 문서 자체가 그것을 구현하거나 확정하지 않는다.

## 1. Purpose

Development HQ v1.0의 6-Stage Workflow가 실제 Repository에서 어느 수준까지
구현되어 있는지 조사하고, 각 Stage의 **Frozen Contract → Current
Implementation → Gap → Evidence**를 정확히 Mapping한다. 새로운
Architecture/기능 설계, Contract 확정, 코드 수정은 이번 작업의 범위가
아니다.

## 2. Audit Scope

- `hqs/development/` 전 문서(BASELINE/BOUNDARY/CONSTITUTION/HANDOVER/
  IMPLEMENTATION_RULES/MISSION/MVP/RESPONSIBILITY/STRUCTURE/stages/*)
- `hqs/development/mvp/` 실제 코드(`agents.py`, `engine.py`, `cli.py`,
  `project_intelligence.py`, `workflow*.py` 7종) 및 `tests/`(pytest 파일
  7종)
- `docs/01_mvp/`의 MVP Observation/Plan 문서(MVP-0002~0052, 53개 파일)
- `docs/decisions/{rfc,adc,adr}/`와 `docs/governance/{adc,observations,
  rt}/`, `docs/architecture/core/`의 Development HQ 관련 Governance 문서
- 저장소 전체에서 CI 설정, 실행 코드, Symbol/Dependency 분석 도구 존재
  여부를 Glob/Grep으로 확인

## 3. Frozen Workflow Baseline

6-Stage는 `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` →
`docs/governance/adc/ADC-0003.md` 판단 1(Accept) →
`docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md`
경로로 채택되었다. 이 경로가 실제로 확정한 것은 다음 세 가지뿐이다.

1. Stage는 Division/Team과 동위의 **선택적 내부 조직 구조**다
   (`hqs/development/STRUCTURE.md`).
2. 6개 Stage 각각의 **목적(1문장) + Responsibility(항목 나열) +
   Reference**만 문서로 존재한다(`hqs/development/stages/*/README.md`).
3. **Capability 배정과 실행 코드 배치는 이 ADR이 규정하지 않는다**
   (ADR-0001 §2: "Capability 배정이나 실행 코드 배치는 규정하지 않는다").
   신규 Capability Catalog 확장 자체도 ADC-0003 판단 2에서 **Defer**
   됐다.

즉 이 감사가 다루는 "Frozen Contract"에는 **Input/Output 스키마, Interface,
Stage 간 전달 형식이 원래부터 정의되어 있지 않다.** 이는 감사 대상 문서의
누락이 아니라 ADR-0001이 명시적으로 위임하지 않은 범위다. 아래 Stage별
Section에서 "Input/Output/경계가 명확한가"를 물을 때, Contract 자체가
이를 정의하지 않은 경우 NOT IMPLEMENTED가 아니라 **NOT DEFINED IN
CONTRACT**로 별도 표기한다.

6개 Stage(RFC-0003 §8, ADR-0001 §4 그대로 인용):

| # | Stage | 목적(원문) |
|---|---|---|
| 01 | Repository Intelligence | 프로젝트를 이해한다 |
| 02 | Planning & Specification | 사람의 Intent를 실행 가능한 명세로 변환한다 |
| 03 | Architecture & Design | 구현 전에 구조를 설계한다 |
| 04 | Implementation | 명세를 코드로 구현한다 |
| 05 | Validation | 구현 결과를 검증한다 |
| 06 | DevOps & Release | 배포와 운영 자동화 |

## 4. Repository Baseline

Audit 시작 시점 확인:

```
$ git branch --show-current
claude/dev-hq-v2-readiness-audit-qyzj8e
$ git log -1 --oneline
64bf17d Merge pull request #101 from ok041110-del/claude/investment-hq-dogfooding-d4g247
$ git status
nothing to commit, working tree clean
```

병렬로 존재하는 두 Governance 문서 계열을 확인했다(둘 다 실재하며 서로
다른 트랙을 다룬다 — 혼동 방지를 위해 기록):

- `docs/decisions/{rfc,adc,adr}/` — CLAUDE.md/HANDOVER.md가 직접 참조하는
  경로. RFC-0001~0006(Kernel Boundary, Task Dispatcher Boundary,
  **Development HQ SDLC Pivot**, Task Dispatcher Runtime Boundary,
  Development HQ Execution Boundary, Structure v1 Taxonomy).
- `docs/governance/{adc,observations,rt}/` + `docs/architecture/core/` —
  Kernel 연구 트랙과 Governance Review/Freeze 문서(`ADC-0001~0004`,
  `GOVERNANCE-REVIEW-0001~0007`, `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`
  등)가 위치. Stage 채택을 최종 결정한 `ADC-0003`은 **이 트리 쪽**에
  있다(`docs/governance/adc/ADC-0003.md`), `docs/decisions/adc/`가
  아니다.

두 트리가 서로 다른 문서 종류(RFC/ADC/ADR)를 같은 번호로 독립적으로
채번하고 있어(예: `docs/decisions/rfc/RFC-0003`은 SDLC Pivot,
`docs/architecture/core/RFC-0003-kernel-context-model.md`은 Kernel Context
Model — 완전히 다른 문서), 참조 시 경로를 반드시 함께 명시해야 한다. 이
자체는 §15 Gap Matrix에 기록한다.

## 5. Stage 01 — Repository Intelligence

### Frozen Contract
`hqs/development/stages/01_repository_intelligence/README.md`(전문):
목적 "프로젝트를 이해한다." Responsibility: Repository 분석 / 관련 파일
탐색 / Symbol 검색 / Dependency 분석 / Context 최적화. Reference: Aider
Repository Map. 상태 절 원문: "이 Stage는 문서 정의만 존재한다. Capability
배정과 실행 코드는 아직 없다."

### Current Implementation
`hqs/development/mvp/project_intelligence.py`(171줄, MVP-0005)가 가장
근접한 실제 코드이나, 파일 자신의 docstring이 "Development HQ 내부
전용이며 Jarvis OS 공통 계층으로 일반화하지 않는다"고 명시한다.
구현된 것: 키워드 매칭 기반 관련 파일 스코어링(`_keywords`, `_score`,
`_relevant_files`), 디렉토리 구조 나열(`_directory_structure`),
`collect_relevant_context()`, `build_context_bundle()`. `workflow_
project_intelligence.py`, `workflow_0008.py`, `workflow_0009.py`,
`workflow_artifact_flow.py` 4개 Workflow에 실제로 배선되어 있다(고립된
스크립트 아님).

Symbol 검색, Dependency 분석은 코드 어디에도 없다(저장소 전체 grep으로
확인, "symbol"/"dependency"를 실제로 구현하는 함수 없음).

### Gap
- Responsibility 5개 중 "Repository 분석"/"관련 파일 탐색"/"Context
  최적화"만 키워드 매칭 수준으로 부분 대응. "Symbol 검색", "Dependency
  분석"은 코드가 전혀 없다.
- `project_intelligence.py`의 `CATEGORY_PATHS` 중 2개 항목이 `docs/
  02_rfc`, `docs/04_adr`를 참조하는데 이 경로는 현재 존재하지 않는다
  (실제로는 `docs/decisions/rfc/`, `docs/decisions/adr/` 또는
  `docs/architecture/core/`) — 항상 빈 리스트를 반환하는 죽은 코드다.
  Structure v1 Migration(커밋 `71d4fa7`) 이후 경로가 바뀌었는데
  `project_intelligence.py`는 갱신되지 않은 것으로 보인다.
- Stage 문서(§상태)는 "문서 정의만 존재한다"고 선언하지만, 실제로는
  `project_intelligence.py`가 존재하고 4개 Workflow에 배선되어 실행된다
  — **문서가 코드 현실을 반영하지 못하는 상태(Stale)**다.

### Evidence
- `hqs/development/mvp/tests/test_workflow_project_intelligence.py`
  (147줄, 8개 테스트) — `collect_relevant_context`를 호출하는
  `run_issue_to_planning`/`run_issue_to_design`을 검증하나, Engine 호출은
  Mock 처리(Characterization Test).
- `docs/01_mvp/MVP-0005-observation.md`, `MVP-0006-observation.md`,
  `MVP-0009-observation.md` — Dogfooding 기록 존재(문서 근거).
- 전체 테스트 스위트 실행 결과: `python3 -m pytest hqs/development/mvp/
  tests/` → **36 passed** (본 Audit 세션에서 실행 확인, 약 71초, 그 중
  2건은 실제 `claude` CLI subprocess 호출 포함).

Grade: **B (Validated Documentation)** — `collect_relevant_context`/
`build_context_bundle` 자체는 실행·테스트되나, Stage Contract가 요구하는
Symbol 검색/Dependency 분석은 D(No Evidence). CATEGORY_PATHS 죽은 코드는
Gap.

### Status
**PARTIAL** (Repository 분석/Context 최적화 일부만; Symbol 검색·
Dependency 분석은 NOT IMPLEMENTED)

## 6. Stage 02 — Planning & Specification

### Frozen Contract
`hqs/development/stages/02_planning_specification/README.md`(전문):
목적 "사람의 Intent를 실행 가능한 명세로 변환한다." Responsibility:
Requirement 분석 / User Story / Functional Spec / Non Functional Spec /
Task 분해. 상태: "문서 정의만 존재한다... 기존 Capability 중
`requirement_analysis`가 이 Stage의 일부 Responsibility와 이미 대응된다."

### Current Implementation
`hqs/development/mvp/agents.py::requirements_agent_requirement_analysis
(issue: dict) -> str`(66~74행) — "goal, scope, risks"를 산문으로
서술하도록 지시하는 단일 Engine 호출 함수. `workflow_hello_sdlc.py`,
`workflow_project_intelligence.py`, `workflow_0008.py`,
`workflow_0009.py`, `workflow_artifact_flow.py` 5개 Workflow에 배선됨.

### Gap
- Responsibility 5개 중 "Requirement 분석" 1개만 코드로 존재.
- **Task 분해**는 이 Stage Contract에 명시적으로 나열되어 있음에도
  코드가 전혀 없다 — `IMPLEMENTATION_RULES.md`가 Workflow Parser/
  Scheduler(Task 분해를 일반화하는 형태)를 명시적으로 금지하므로, 이
  Gap은 우연한 누락이 아니라 의도된 결과다.
- User Story, Functional Spec, Non-Functional Spec은 구분되지 않는다 —
  `requirement_analysis` 하나가 세 가지를 뭉뚱그린 산문 하나만 반환한다.

### Evidence
`test_workflow_hello_sdlc.py`, `test_workflow_project_intelligence.py`,
`test_workflow_0008.py`, `test_workflow_0009.py` — 전부 Engine 호출을
Mock한 Characterization Test(36 passed에 포함).

Grade: **B** (`requirement_analysis` 좁은 범위) / **D** (User Story,
Functional/Non-Functional Spec, Task 분해).

### Status
**PARTIAL**

## 7. Stage 03 — Architecture & Design

### Frozen Contract
`hqs/development/stages/03_architecture_design/README.md`(전문): 목적
"구현 전에 구조를 설계한다." Responsibility: Architecture / Module 설계
/ Interface / Workflow / Prototype. 상태: "문서 정의만 존재한다... 기존
Capability 중 `design`이 이 Stage의 일부 Responsibility와 이미
대응된다."

### Current Implementation
`agents.py::design_agent_design(issue, requirement) -> str`(77~85행) —
"approach, responsibilities, risks"를 산문으로 서술. 동일하게 5개
Workflow에 배선.

### Gap
Module 설계/Interface/Prototype은 별도 산출물로 존재하지 않는다 — 산문
하나에 뭉뚱그려져 있다. Workflow 설계는 이 Stage의 코드가 아니라
`hqs/development/mvp/workflow*.py` 자체(하드코딩된 함수 호출 순서)가
그 실체이며, `design_agent_design`이 이를 산출하지 않는다.

### Evidence
Stage 02와 동일 테스트 파일(Mock, 36 passed에 포함).

Grade: **B**(`design` 좁은 범위) / **D**(Module/Interface/Prototype).

### Status
**PARTIAL**

## 8. Stage 04 — Implementation

### Frozen Contract
`hqs/development/stages/04_implementation/README.md`(전문): 목적
"명세를 코드로 구현한다." Responsibility: Coding / Refactoring / Git /
Documentation. "참고 구현 예시(기존 코드, 이동하지 않음)" 절이
`agents.py::backend_agent_code_review()`, `engine.py::call_engine()`,
`workflow.py`/`workflow_0002.py`를 인용하나, 이 인용 자체가 문서 작성
시점(ADR-0001, MVP-0004 이전)의 예시일 뿐 실제 Capability 매핑이
아니라고 명시한다. 상태: Capability 배정 미결정(Defer).

### Current Implementation
`agents.py::backend_agent_code_generation(design: str) -> str`(97~110행,
MVP-0004에서 추가) — 실제 코드 생성 지시("Return only the code, with no
surrounding commentary") + `_strip_code_fence()`(88~94행, Engine이 마크
다운 펜스로 감싸는 것을 실측 확인 후 벗기는 후처리). `workflow_
hello_sdlc.py`, `workflow_0008.py`, `workflow_artifact_flow.py`에 배선.

### Gap
- Refactoring, Git 작업, Documentation — 코드 없음(저장소 전체 확인).
- Stage 문서가 예시로 든 `code_review`는 실제로는 Stage 05(Validation)에
  더 가깝다(Review는 Stage 05 Responsibility로 명시됨) — 문서 자체가
  인정하듯 이 인용은 ADR-0001 작성 시점(MVP-0001만 존재하던 시점)의
  임시 예시이며, MVP-0004 이후 실제 `code_generation` 함수가 생겼음에도
  Stage 문서는 갱신되지 않았다(Stage 01과 동일한 Stale 패턴).

### Evidence
`test_workflow_hello_sdlc.py`, `test_workflow_0008.py`, `test_workflow_
artifact_flow.py`(Mock, 36 passed에 포함).

Grade: **B**(`code_generation`) / **D**(Refactoring/Git/Documentation).

### Status
**PARTIAL**

## 9. Stage 05 — Validation

### Frozen Contract
`hqs/development/stages/05_validation/README.md`(전문): 목적 "구현
결과를 검증한다." Responsibility: Unit Test / Integration Test / Review
/ Lint / Security / Performance. 참고 구현 예시: `agents.py::qa_agent_
test_execution()`, `workflow.py`/`workflow_0002.py`,
`tests/test_mvp_0001.py`. 상태: Lint/Security/Performance 세분화
미결정(Defer).

### Current Implementation
- `agents.py::backend_agent_code_review(code) -> str`(30~51행) —
  "Review" Responsibility 대응.
- `agents.py::qa_agent_test_execution(code, review) -> str`(54~63행) —
  이름과 달리 **테스트를 실행하지 않는다.** 지시문은 "propose a list of
  test cases to add"이며, 실제 반환값은 산문으로 서술된 테스트 케이스
  제안 목록이다. Unit Test Responsibility에 대응하려면 "실행"이 아니라
  "케이스 아이디어 제안"으로 좁혀 읽어야 한다.
- Lint, Security, Performance, Integration Test — 코드 없음.

### Gap
- "Unit Test" Responsibility와 실제 `test_execution` 함수 이름 사이에
  실질적 의미 차이가 있다(실행 vs. 제안). Contract 자체가 이 차이를
  구분하지 않으므로 이는 Contract 결함이 아니라 **이름-행동 불일치**로
  기록한다.
- Lint/Security/Performance/Integration Test는 Contract가 명시했지만
  전혀 구현되지 않았다 — Stage 문서 자신도 "미결정"이라고 인정한다.

### Evidence
- `hqs/development/mvp/tests/test_mvp_0001.py`(58줄) — **실제 `claude`
  CLI subprocess를 호출하는 진성 E2E 테스트**(Mock 없음).
  `test_returns_review_then_test_cases_without_manual_intervention`,
  `test_review_content_reaches_test_execution_as_context`,
  `test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope`
  3건 전부 본 Audit 세션에서 재실행하여 통과 확인.
- `docs/architecture/core/GOVERNANCE-REVIEW-0004-engine-mvp-closure-
  and-production-entry.md` — success/failure path, `results` 단일/다중,
  CLI 진입점을 real Engine으로 검증 완료했다고 기록(재인용, 원문 재조사
  안 함).
- `test_workflow_0002.py`(136줄) — 분기 로직 검증하나 Engine은 Mock.

Grade: **A (Production Evidence)** — `code_review` + `test_execution`의
MVP-0001 좁은 범위(real Engine, 반복 통과)에 한해. **B** — `workflow_
0002.py`의 분기 로직(Mock). **D** — Lint/Security/Performance/
Integration Test.

### Status
**PARTIAL** (Review/제안형 Unit Test만 A/B 등급; Lint/Security/
Performance/Integration Test는 NOT IMPLEMENTED)

## 10. Stage 06 — DevOps & Release

### Frozen Contract
`hqs/development/stages/06_devops_release/README.md`(전문): 목적
"배포와 운영 자동화." Responsibility: CI / CD / Release / Monitoring.
상태: "문서 정의만 존재한다... 기존 Capability 중 `deployment`,
`incident_response`가 이 Stage의 일부 Responsibility와 이미 인접한다"
(대응이 아니라 "인접"이라고만 표현 — Capability 매핑 자체가 없음을
문서가 스스로 인정).

### Current Implementation
**없음.** `.github/workflows/` 디렉토리 자체가 저장소에 존재하지 않음
(직접 확인). Lint 설정, 배포 스크립트, Release 자동화, Monitoring 코드
어디에도 없음(전체 저장소 Glob/Grep으로 확인).

### Gap
Responsibility 4개(CI/CD/Release/Monitoring) 전부 100% 미구현. Contract
자체가 "실행 코드는 아직 없다"고 선언하므로, 이는 예상치 못한 발견이
아니라 Contract와 일치하는 상태다.

### Evidence
**D (No Evidence)** — 코드, 테스트, CI 설정, Dogfooding 기록 전부 없음.
`docs/01_mvp/*.md` 53개 파일 중 "DevOps"/"Release"/"CI/CD"/"Monitoring"을
언급하는 파일은 `MVP-0004-plan.md` 1건뿐이며, 그 문서조차 "실제 Git/CI
연동... 구현하지 않는다"고 명시한다(Non-goals 절).

### Status
**NOT IMPLEMENTED**

## 11. Cross-Stage Workflow Analysis

- **실제 전달 확인**: `workflow.py::run_mvp_0001()`에서 `review =
  backend_agent_code_review(code)` → `test_cases = qa_agent_test_
  execution(code, review)`로 Task 1 출력이 Task 2 입력에 실제로 전달됨
  (코드로 직접 확인). 더 넓은 체인은 `workflow_0008.py::run_pipeline()`
  (Project Intelligence→Planning→Design→Implementation→Validation, 5개
  키 반환) — 저장소에서 가장 많은 Stage를 연결한 실제 코드다.
- 모든 연결은 하드코딩된 Python 함수 호출 순서이며, Parser/Scheduler/
  Queue는 전혀 없다 — `IMPLEMENTATION_RULES.md`의 명시적 금지에 따른
  의도된 설계다.
- **Contract 계층에서의 Stage 간 전달 정의는 없다.** ADR-0001은 Stage
  문서에 Capability 배정/실행 코드 배치를 규정하지 않았으므로, 실제 코드의
  전달 순서(01→02→03→04→05)는 Contract가 강제한 것이 아니라 각 MVP
  Plan 문서(MVP-0004~0009)가 개별적으로 설계한 것이다. 즉 "Cross-Stage
  Contract가 있고 코드가 이를 구현했다"가 아니라, **"코드가 먼저
  생겼고, Stage Contract는 그 뒤를 규정하지 않는다"**가 실제 순서다.

## 12. State / Handover Analysis

- 모든 Workflow 함수는 순수 In-Memory 지역 변수(`review`, `context`,
  `enriched_issue`)로만 데이터를 주고받는다. 직렬화, DB, 파일 기반 상태
  저장은 어디에도 없다.
- 이는 사고가 아니라 `IMPLEMENTATION_RULES.md`의 명시적 금지("Memory
  Service(영속화 계층) 구현 금지 — Context는 in-memory 변수로만
  다룬다")에 따른 의도된 결과다.
- **Status: NOT IMPLEMENTED (의도된 설계).** "필요하지 않다"가 아니라
  "지금까지 관찰(Evidence)로 필요성이 확인되지 않아 의도적으로 유보됨"
  — NEED UNDETERMINED로 별도 표기한다(HANDOVER.md "Kernel Extraction
  Rule" 참조).

## 13. Checkpoint / Recovery Analysis

- 모든 `run_*` Workflow 함수는 전체를 단일 `try/except Exception`으로
  감싸고, 실패 시 하위 키 전부를 `f"Engine call failed: {exc}"` 형태의
  고정 문자열로 채운다(`workflow.py::_engine_failure_message`, 5개
  Workflow 파일이 재사용).
- **예외**: `workflow_hello_sdlc.py`만 다른 실패 반환 형태(`None` 값 +
  `status`/`error` 키)를 쓴다. 이 불일치는 `test_workflow_hello_sdlc.py`
  docstring이 "이 비대칭 자체가 실제 현재 behavior임을 증명하기 위함"
  이라고 명시적으로 기록한 **의도적으로 고정된(characterized) 상태**다
  — 아직 통일 리팩토링(P1-1로 지칭)은 이뤄지지 않았다.
- 재시도(Retry) 로직은 어디에도 없다 — 단일 실패가 전체 파이프라인을
  즉시 종료시킨다.
- Recovery/Resume: **NOT IMPLEMENTED.** 중간 Stage에서 재개하는 기능은
  코드/문서 어디에도 없다.

## 14. Evidence Matrix

| Stage | Responsibility 항목 | Grade | 근거 |
|---|---|---|---|
| 01 | Repository 분석 / Context 최적화 | B | `project_intelligence.py` + Mock 테스트 8건 |
| 01 | Symbol 검색 / Dependency 분석 | D | 코드 없음 |
| 02 | Requirement 분석 | B | `requirements_agent_requirement_analysis` + Mock 테스트 |
| 02 | User Story / Functional·NFR Spec / Task 분해 | D | 코드 없음 |
| 03 | Architecture/Design(단일 산문) | B | `design_agent_design` + Mock 테스트 |
| 03 | Module 설계 / Interface / Prototype | D | 코드 없음 |
| 04 | Coding(code_generation) | B | `backend_agent_code_generation` + Mock 테스트 |
| 04 | Refactoring / Git / Documentation | D | 코드 없음 |
| 05 | Review, Unit Test(제안형) | **A** | `test_mvp_0001.py` real-Engine E2E, 반복 통과 + `GOVERNANCE-REVIEW-0004` |
| 05 | 분기 로직(no-issue 경로 등) | B | `test_workflow_0002.py`(Mock) |
| 05 | Lint / Security / Performance / Integration Test | D | 코드 없음 |
| 06 | CI / CD / Release / Monitoring | D | 코드·설정 전무 |

CI 자체: **D** — 저장소에 `.github/workflows/`가 존재하지 않아, 위 36개
테스트 통과도 전부 로컬 수동 실행 결과이며 자동화된 검증 경로가 아니다.

## 15. Gap Matrix

| Gap | 성격 | 근거 |
|---|---|---|
| Stage 01/04 문서의 "문서 정의만 존재" 서술이 실제 코드(`project_intelligence.py`, `code_generation`)와 불일치(Stale) | 문서-코드 동기화 지연 | Stage README vs. MVP-0004~0009 코드 존재 |
| `project_intelligence.py::CATEGORY_PATHS`의 `docs/02_rfc`, `docs/04_adr` 참조가 죽은 경로 | 코드 결함(경로 오류) | Structure v1 Migration(`71d4fa7`) 이후 미갱신 추정 |
| `qa_agent_test_execution`이 이름과 달리 테스트를 실행하지 않고 제안만 함 | 이름-행동 불일치 | `agents.py` 54~63행 실측 |
| Stage 06(CI/CD/Release/Monitoring) 전면 미구현 | Contract와 일치(의도됨) | Stage 문서 자체 인정 |
| Task 분해(Stage 02), Lint/Security/Performance(Stage 05) 미구현 | Contract와 일치(의도됨, IMPLEMENTATION_RULES.md 금지) | ADC-0003 판단 2 Defer |
| 두 Governance 문서 트리(`docs/decisions/` vs `docs/governance/`+`docs/architecture/core/`)의 번호 중복 | 참조 혼동 위험 | §4 실측 |
| ~~RFC-0005/engine.py 표면적 불일치~~ | **RESOLVED(A. Historical Mismatch)** — `DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001.md`(본 문서) 작성 후속 조사로 규명 완료. RFC-0005는 MVP-0005~13 시점에는 사실이었고, 그 이후 ENGINE-CONNECT-0001(MVP-0013과 MVP-0014 사이)에서 `call_engine()`이 실제 Engine 호출로 교체되며 구현이 변경됐다. RFC-0005는 Evidence 범위를 스스로 MVP-0005~13으로 명시하고 있어 Stale 문서가 아니며, 수정하지 않는다. | `docs/01_mvp/MVP-0014-observation.md`, `MVP-0038-observation.md`, `MVP-0043-observation.md`, `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`, `hqs/development/mvp/engine.py` docstring(MVP-0043 삭제 기록) |
| Recovery/Resume, 재시도, 영속 상태 없음 | Contract와 일치(의도됨) | `IMPLEMENTATION_RULES.md` 명시 금지 |
| CI 부재로 36개 테스트가 전부 수동 실행에만 의존 | 실제 Gap(의도되지 않음, Stage 06 자체가 미구현이므로 당연한 결과) | `.github/workflows/` 부재 실측 |

## 16. Architecture / Governance Impact

- 이번 Audit은 Architecture를 변경하지 않았다. 위 Gap 중 "의도된 설계"로
  표기된 항목(Recovery/State/Task Dispatcher 등)은 `IMPLEMENTATION_
  RULES.md`·`CONSTITUTION.md`가 이미 근거를 제공하는 Freeze 대상이며, 이
  Audit이 재론하지 않는다.
- "실제 Gap"으로 표기된 항목(CATEGORY_PATHS 죽은 경로, 문서-코드 Stale,
  이름-행동 불일치, Governance 트리 중복, RFC-0005/engine.py 표면적
  불일치)은 Architecture 변경 사안이 아니라 **문서 정정/코드 결함
  수정** 수준이며, RFC → ADC → ADR 없이도 다룰 수 있는 성격으로
  보이나, 이 판단 자체도 이 Audit이 확정하지 않는다 — 다음 세션의
  Governance 판단에 맡긴다.

## 17. Recommendations

(구현 아님 — 기록만)

1. Stage 01/04 README.md의 "문서 정의만 존재한다" 서술을 실제 코드
   존재 여부에 맞춰 갱신할지 검토.
2. `project_intelligence.py::CATEGORY_PATHS`의 죽은 경로 2건을 실제
   경로로 정정할지, 혹은 의도적으로 비활성화된 것인지 확인.
3. `qa_agent_test_execution`이 "실행"이 아니라 "제안"만 한다는 사실을
   Stage 05 Contract 또는 함수 docstring에 명시할지 검토.
4. ~~RFC-0005의 "LLM/ML 호출 없음" 서술과 현재 `engine.py` 실제 동작 사이의
   시점 차이를 규명할 별도 조사~~ — 완료(§15 참조, A. Historical Mismatch,
   문서 수정 불필요로 판정).
5. `docs/decisions/`와 `docs/governance/`+`docs/architecture/core/`
   두 Governance 트리의 관계(병존/통합/역할 분리)를 명확히 문서화할지
   검토.

## 18. v2.0 Implementation Readiness

Evidence 기준으로만 판단한다(추정 배제):

- Stage 05(Validation)의 Review+제안형 Unit Test 좁은 범위만 Grade A
  (real Engine, 반복 검증)다.
- Stage 01~04는 각각 Contract의 일부 Responsibility만 Grade B로
  존재하며, 나머지는 D(No Evidence)다.
- Stage 06은 전면 D다.
- Cross-Stage 연결은 실제로 동작하나, 이는 Stage Contract가 강제한
  것이 아니라 개별 MVP(0004~0009)가 설계한 것이다.
- State/Recovery/CI는 의도적으로 미구현 상태이며, 이 상태를 바꿀
  Evidence 기반 필요성이 아직 관찰되지 않았다(`HANDOVER.md` "Kernel
  Extraction Rule").

## 19. Open Issues

1. ~~RFC-0005의 "LLM/ML 호출 없음" 서술과 현재 `engine.py`의 실제 subprocess
   호출 사이의 표면적 불일치(§15)~~ — **해결됨.** A. Historical Mismatch로
   판정, 문서 수정 불필요(§15 참조).
2. 두 Governance 문서 트리의 관계 — 통합 여부는 이 Audit이 결정하지 않음.
3. Stage 06 재개 조건 — Contract에 재개 조건 자체가 정의되어 있지 않다
   (Stage 01/04와 달리 06은 RFC-0003 §11에 후속 MVP 후보조차 없음).

## 20. Next Implementation Task

이 Audit은 구현 Task를 생성하지 않는다. 아래는 **Next Implementation
Candidate**이며, 그 이유만 Evidence에 근거해 설명한다.

**Next Implementation Candidate: Stage 05(Validation)의 Lint/Security/
Performance/Integration Test 세분화 여부 재관찰, 또는 Stage 06(DevOps &
Release) 첫 MVP 후보 설계 이전에 §15 "실제 Gap"(문서 Stale, 죽은 경로,
이름-행동 불일치) 정리.**

이유: Stage 05는 이미 Grade A Evidence(real Engine 반복 검증)를 가진
유일한 Stage이므로 그 위에 세분화를 얹는 것이 새 Stage(06)를 처음부터
여는 것보다 위험이 낮다. 반면 Stage 06은 Contract에 후속 MVP 후보조차
없어(§19-3) 무엇을 먼저 관찰해야 할지 근거가 없다 — 여기서 시작하면
Observation 없이 설계부터 하게 될 위험이 있다. §15의 "실제 Gap" 3건
(CATEGORY_PATHS 죽은 경로, 문서 Stale, 이름-행동 불일치)은 코드 규모가
작고 이미 Evidence로 확인되어 있어, 다음 세션이 가장 먼저 판단하기
쉬운 항목이다.

---

## 최종 판정

### B. PARTIALLY READY

Stage 05의 Review/제안형 Unit Test 좁은 범위만 Grade A Evidence로
뒷받침되며, Stage 01~04는 Responsibility의 일부만 Grade B로 존재하고
나머지는 D다. Stage 06은 Contract와 일치하게 전면 미구현이다.
Cross-Stage 연결 자체는 실제로 동작하지만 Contract가 아니라 개별 MVP
설계의 산물이다. v2.0 Productionization을 곧바로 시작하기에는 Stage
06 전체와 Stage 01~04의 상당 부분에 Evidence가 없으나, 핵심 파이프라인
(01→05)이 실제 코드로 연결되어 있고 반복 검증된 부분(Stage 05 좁은
범위)이 존재하므로 "C. NOT READY"로 판정하지 않는다.

---

## Git 변경 확인

```
$ git diff --stat
$ git diff --check
$ git status
```

(아래 "Git 변경 확인 결과" 절에서 실행 결과를 기록한다 — 이 문서
자체 신규 생성 외 변경 없음을 확인한다.)

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NONE
