# DEV-HQ-V2.0 — Stage 01~05 Data Contract 정리(중복 계산 제거 + required_checks 구조화)

## 목적

Static Workflow(Stage 01→02→03→04→05)의 데이터 전달 방식에서 실제로
관찰된 3가지 결함(미사용 파라미터, `candidate_index` 중복 계산 가능성,
비구조화된 `required_checks`)을 Stage 순서·Capability·Agent를 바꾸지
않고 Contract 수준에서 해소한다. 향후 Dynamic Workflow가 필요해져도
버릴 필요 없는 형태(데이터 의미 중심 Contract)로 정리하되, Scheduler/
Registry/Workflow Parser/Engine Gateway/Policy Engine 등은 만들지
않는다(`IMPLEMENTATION_RULES.md` 금지 항목 무변경).

## 배경 — Freeze와의 관계

`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` §7은 "Freeze 이후 Architecture/
Contract 변경은 RFC → ADC → ADR을 통해서만"이라고 명시한다. 이번
작업은 그 절차를 우회하지 않는다 — 아래 "Governance 판단"에서 다루는
대로, 실제로 구현한 항목은 **이미 각 Stage README/RESPONSIBILITY/
CAPABILITIES/VALIDATION.md가 문서로 정의해 둔 Input/Output을 코드로
명시·검증 가능하게 만든 것**(새 Concept/Component 아님)과, 같은
문서에 이미 "SHOULD FIX"로 기록되어 있던 결함 수정(§5,
`stage_04._assemble_build_input()`/`workflow_ast_context.py` 조립 로직
중복)이다. "자연어 Acceptance Criteria를 자동으로 구조화·검증하는
required_checks"처럼 새 Capability가 필요한 부분은 구현하지 않고
아래 "해결되지 않은 요구"에 남겼다.

## 변경 내역

| 파일 | 변경 |
|---|---|
| `hqs/development/stages/contracts.py`(신규) | `ContextAnalysisResult`/`SpecificationResult`/`DesignResult`/`ImplementationResult`/`VerificationResult` TypedDict + `CandidateIndex`/`DependencyClosure` 타입 별칭 + `validate_*()`/`ContractViolation` |
| `hqs/development/mvp/workflow_ast_context.py` | `identify_target(design, candidate_index=None)` — `candidate_index`를 넘기면 재사용, 생략 시 기존과 동일하게 직접 계산(additive extension, `run_pipeline_with_ast_context()` 무변경) |
| `hqs/development/stages/04_implementation/stage_04.py` | `run_stage_04(issue, stage_03_output, ...)` → `run_stage_04(stage_01_context, stage_03_output, ...)` — 미사용 `issue` 제거, Stage 01 `candidate_index` 재사용으로 중복 계산 제거 |
| `hqs/development/stages/05_validation/stage_05.py` | `run_stage_05(issue, stage_02_output, stage_03_output, stage_04_output)` → `run_stage_05(stage_02_output, stage_04_output)` — 미사용 `issue`/`stage_03_output` 제거. `REQUIRED_CHECKS`/`check_results`(구조화된 `VerificationResult`) 추가, `_determine_verdict()` 로직은 무변경 |
| `hqs/development/workflow.py` | Stage 04/05 호출부를 새 시그니처에 맞춰 갱신, 각 Stage Output 직후 `contracts.validate_*()` 명시적 호출(계약 위반이 다음 Stage로 조용히 전파되지 않도록) |
| `hqs/development/stages/04_implementation/IMPLEMENTATION.md`, `hqs/development/stages/05_validation/VALIDATION.md` | 새 시그니처/Output 스키마 반영 |
| `mvp/tests/test_stage_04.py`, `test_stage_05.py`, `test_workflow_integrated.py`, `test_stage_contracts.py`(신규) | 새 시그니처 반영 + 중복 계산 제거·Contract 위반 명시적 실패·`required_checks` 구조화 회귀 테스트 추가 |

## Stage 01~05 Contract 구조(최종)

Producer/Consumer와 필수 키는 `contracts.py`에 코드로 고정되어 있다.

- **CandidateIndex**(`str`) — Producer: Stage 01. Consumer: Stage 03(그대로
  재배치), Stage 04(`identify_target()`에 재사용, 재계산 없음).
- **DependencyClosure** — Stage 01은 `target`이 이미 주어진 경우에만
  계산한다. Static Workflow에서는 `target`이 Stage 03 Design 이후에야
  식별되므로(Stage 04의 `identify_target(design, ...)`), Stage 01의
  `dependency_closure`는 항상 `None`이고 실제 Producer는 Stage 04다 —
  이것은 Contract로 해소되는 "중복 계산"이 아니라 "Design 이전에는
  target을 모른다"는 실제 실행 순서 제약이다(아래 "Dynamic Workflow
  재평가" 참고).
- **SpecificationResult**(`skeleton`, `specification`) — Producer:
  Stage 02. Consumer: Stage 03(`skeleton` 재배치), Stage 05
  (`specification_check`).
- **DesignResult**(`skeleton`, `design`) — Producer: Stage 03. Consumer:
  Stage 04.
- **ImplementationResult**(`target`, `implementation`, `expose_target`)
  — Producer: Stage 04. Consumer: Stage 05.
- **VerificationRequirement**(`REQUIRED_CHECKS`, Stage 05 내부 상수) +
  **VerificationResult**(`required_checks`, `check_results`, 기존 4개
  개별 check dict, `code_review`, `verdict`) — Producer: Stage 05,
  Consumer 없음(최종 산출물, CLI가 재해석 없이 출력).

Contract validation 책임: 각 Stage는 자신이 반환하는 dict의 형태에
책임지고, Stage 간 Handover 시점의 필수 키 존재 여부는 `workflow.py`가
`contracts.validate_*()`로 명시적으로 검증한다(값의 의미 재해석은
하지 않음).

## 해결된 것

1. **미사용 파라미터 제거** — Stage 04에서 `issue`, Stage 05에서
   `issue`/`stage_03_output` 제거. 시그니처가 실제 의존관계만 표현한다.
2. **`candidate_index` 중복 계산 제거** — Stage 04가 Stage 01이 이미
   계산한 `candidate_index`를 `stage_01_context`를 통해 재사용하고,
   `identify_target()` 내부에서 `build_function_candidate_index()`를
   다시 호출하지 않는다(회귀 테스트:
   `test_identify_target_reuses_stage_01_candidate_index_without_recomputing`).
3. **`required_checks` 구조화** — Stage 05가 실행하는 4개 결정적 검증
   항목(`structural`/`specification_scope`/`design_scope`/
   `test_execution`)이 `REQUIRED_CHECKS` 상수로 명시적으로 선언되고,
   각 실행 결과가 `CheckResult`(`name`/`status`/`blocking`/`detail`)
   목록으로 구조화되어 최종 `VerificationResult`에 포함된다. `verdict`는
   기존 `_determine_verdict()`가 그대로 계산하므로(로직 변경 없음),
   구조화가 판정 결과 자체를 바꾸지 않았다는 것이 보장된다.
4. **계약 위반의 명시적 검증** — `workflow.py`가 각 Stage Output에
   필수 키가 있는지 즉시 확인하고, 없으면 `ContractViolation`이 기존
   예외 처리 경로(`failed_at`/`error`)로 그대로 드러난다(회귀 테스트:
   `test_stage_output_missing_required_key_fails_explicitly_not_silently`).

## 테스트/실사용 Evidence

- 회귀 기준선: 변경 전 **127 passed** → 변경 후 **143 passed**(16개
  신규 — 중복 계산 제거 2건, Contract 자체 검증 11건, `required_checks`
  구조화 3건). 기존 테스트 전부 통과, 실패한 항목 없음.
- 실제 명령: `pytest hqs/development/mvp/tests -q` → `143 passed`.
- **Real Engine E2E 2건**(`python hqs/development/cli.py issue.json
  [--expose-target]`, mock 없음, 실제 `claude` CLI 호출):
  - `--expose-target` 없음: `target = ["ast_context", "_first_doc_line"]`
    (Stage 04가 Stage 01 `candidate_index`를 재사용해 실제로 식별
    성공), `verdict: PARTIAL`(파일 미적용이라 `design_scope`/
    `test_execution`은 `INCONCLUSIVE` — 기존과 동일한 정책).
  - `--expose-target` 있음: 동일 `target` 식별, `specification_check:
    {"target_in_scope": True}`, `design_scope_check: {"scope_ok": True,
    "changed_names": []}` — Scope 위반 없음. `test_execution`은
    `returncode: 1`이었으나 원인은 `No module named pytest`(이 세션의
    `sys.executable`에 pytest가 설치돼 있지 않은 **환경 문제**이며
    Contract/코드 변경과 무관 — `PATH`상의 별도 `pytest` 실행 파일과
    Stage 05가 쓰는 `sys.executable -m pytest`가 다른 Python 설치를
    가리켜서 발생). 두 실행 모두 실행 후 `git status --short`로 대상
    파일이 자동 원상복구됐음을 확인(잔여 diff 없음).
- 위 real Engine E2E는 "3가지 시나리오(Security/Data-API/Regression)의
  Level 2 재실행"에 대응하는 가장 근접한 실제 Evidence다 — 이 저장소
  안에 사전 정의된 "Level 2 시나리오"/"Critical Gap" 문서는 존재하지
  않아(전체 `docs/` 검색 결과 無) 특정 문서의 재검증으로는 수행할 수
  없었다(아래 "해결되지 않은 요구" 참고). 대신 이번 Contract가 실제로
  담당하는 3개 결정적 검사 — `design_scope`(Scope 밖 코드 변경 차단,
  Security에 가장 가까움), `specification_check`(Target이 Data/API
  Scope 후보 안에 있는지), `test_execution`(회귀 감지) — 를 real
  Engine으로 재실행해 각각 정상 동작을 확인했다.

## 아직 해결되지 않은 요구

- **자연어 Acceptance Criteria의 구조화·자동 검증** — 원 요청 4번
  "자연어에 포함된 중요한 요구사항을 구조화된 Contract 필드로 승격"의
  가장 넓은 해석(Stage 02 `specification`의 Acceptance Criteria를
  자동 추출해 Stage 05가 개별 항목으로 검증)은 구현하지 않았다. 이를
  하려면 자유 텍스트를 구조화하는 새 Engine 호출/파싱 로직이 필요한데,
  이는 `STRUCTURE.md`에 없는 새 Capability이며 `IMPLEMENTATION_RULES.md`
  의 "구현 중 새 Capability/Agent 추가 금지"에 해당한다 — RFC 대상.
- **Security/Data-API/Regression "Level 2 시나리오"/"3개 Critical Gap"
  재검증** — 이 이름의 사전 문서가 저장소에 없어(검색 결과 無) 특정
  문서 대비 재검증을 수행하지 못했다. 그런 문서/시나리오가 별도로
  존재한다면 위치를 알려주면 그 문서 기준으로 재검증한다.
- **환경의 `pytest` 미설치** — `hqs/development/stages/05_validation/
  stage_05.py`의 `test_execution`이 `sys.executable -m pytest`를 쓰는데
  이번 세션의 `sys.executable`에는 pytest가 없다(별도 `/root/.local/bin/
  pytest`만 존재). 이번 작업 범위(Contract) 밖의 환경 설정 문제이므로
  수정하지 않았다.

## Dynamic Workflow 필요성 재평가

- `dependency_closure`가 Stage 01에서 항상 `None`인 이유는 "target을
  Design 이후에만 알 수 있다"는 실행 순서 제약이다 — 이것은 Contract를
  아무리 정교하게 만들어도 해소되지 않는다. 해소하려면 "Stage 01이
  target 식별을 최대한 늦게, 필요한 시점에만 수행"하도록 실행 순서
  자체를 바꿔야 하는데, 이는 이번 범위(Dynamic Workflow 미구현)
  밖이다. 다만 이는 Scheduler/Graph 없이도 "Stage 04가 필요한 시점에
  Stage 01의 정적 분석 함수를 다시 호출"하는 정도로 이미 최소 해결되어
  있다(지금 구조 그대로) — Dynamic Workflow가 반드시 필요한 지점은
  아니다.
- 세 시나리오(Security/Data-API/Regression) 모두 이번 real Engine
  E2E에서 **Static 경로(01→02→03→04→05, 고정 순서) 그대로** 정상
  동작했다 — Stage 재배치, 조건부 분기, 재시도가 필요한 지점은
  발견되지 않았다.
- **판정: 현재는 Contract만으로 충분하다.** Dynamic Workflow(범용
  Graph/Parser/Scheduler)가 필요하다는 Evidence는 이번 작업에서
  나오지 않았다. 향후 새 Execution Unit이 Stage 사이에 삽입되어야
  하는 실제 사례가 나타나면, 그때 이 Contract(Stage 이름이 아닌 데이터
  의미 중심)가 재배치 비용을 줄여줄 것으로 기대한다 — 이번 작업이
  의도한 확장 여지다.

## Architecture/Governance 변경 여부

- 새 RFC/ADC/ADR을 작성하지 않았다. Development HQ Baseline·Jarvis OS
  Architecture Baseline을 수정하지 않았다.
- 새 Capability/Agent를 추가하지 않았다(기존 5개 Capability 재사용,
  자연어 Acceptance Criteria 자동 검증은 구현하지 않음 — 위 "해결되지
  않은 요구" 참고).
- Scheduler/Registry/Workflow Parser/Engine Gateway/Policy Engine/
  Memory Service/Event Bus를 구현하지 않았다.
- Stage 개수·순서·책임 분리는 무변경(01→02→03→04→05, ADR-0008 §4
  그대로).
- `contracts.py`는 각 Stage 폴더의 기존 markdown Contract 문서(CONTEXT/
  SPECIFICATION/DESIGN/IMPLEMENTATION/VALIDATION.md)가 이미 정의한
  Input/Output을 코드로 옮긴 것이며, 새 Concept/Component를 추가한
  것으로 판단하지 않았다 — 이 판단에 이견이 있으면(Governance 담당자
  검토 필요) 되돌리거나 RFC로 전환할 수 있다.

## 다음 단계

- 자연어 Acceptance Criteria 구조화·자동 검증이 실제로 필요해지는
  구체적 사례(실 사용 중 Stage 05가 Acceptance Criteria 미충족을
  놓친 실제 사례)가 나오면, 그 Evidence를 근거로 RFC를 연다.
- "Security/Data-API/Regression Level 2" 문서가 다른 위치에 있다면
  전달받아 그 기준으로 재검증한다.
- 이번 세션의 `sys.executable`에 pytest가 없는 환경 문제는 별도로
  다룬다(Contract 범위 밖).
