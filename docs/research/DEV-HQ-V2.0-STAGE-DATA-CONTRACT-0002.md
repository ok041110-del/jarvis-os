# DEV-HQ-V2.0 — Stage 05 required_checks 인과관계 연결(decorative mirror 해소)

## 목적

`DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0001.md`(1차 구현) 이후 실사용 검증에서
`required_checks`/`check_results`가 `REQUIRED_CHECKS` 상수·
`_build_check_results()`·`_determine_verdict()` 사이에 실제 인과관계
없이 서로 독립적으로만 계산되는 **decorative mirror**임이 실증됐다
(`REQUIRED_CHECKS`를 빈 튜플로 바꿔도 실행되는 검사와 Verdict가 전혀
변하지 않음). 이번 작업은 기존 4개 결정적 검사(`structural`/
`specification_scope`/`design_scope`/`test_execution`) 범위 안에서만
`required_checks → 실제 실행 → VerificationResult → Verdict`의 실제
데이터 흐름을 구축한다. Security/Data-API 전용 검증(대응 Capability
자체가 없음)은 이번 작업에 추가하지 않았다.

## 무엇을 수정했는가

| 파일 | 변경 |
|---|---|
| `hqs/development/stages/contracts.py` | `KNOWN_CHECK_NAMES`(Single Source of Truth) 추가. `validate_verification_requirement()`(빈 값/알 수 없는 이름 즉시 거부) 추가. `validate_verification_result()`를 강화해 `required_checks`에 선언된 항목이 `check_results`에서 `SKIPPED`로 남아 있으면(=선언만 되고 실행되지 않음) Contract 위반으로 차단 |
| `hqs/development/stages/05_validation/stage_05.py` | `_CHECK_EVALUATORS`(name → `(blocking_fail, incomplete)` 평가 함수) 표를 도입해 `_determine_verdict()`와 `_build_check_results()`가 판정 규칙을 **공유**하도록 통합(이전엔 두 함수가 같은 규칙을 각자 다시 적어 우연히 일치했을 뿐). `run_stage_05(stage_02_output, stage_04_output, required_checks=None)` — `required_checks`에 없는 검사는 해당 함수 자체를 호출하지 않고(SKIPPED) Verdict 계산에서도 제외. 진입 시점에 `contracts.validate_verification_requirement()`로 즉시 검증 |
| `hqs/development/mvp/tests/test_stage_05.py`, `test_stage_contracts.py`, `test_workflow_integrated.py` | 새 시그니처/의미에 맞춰 fixture 갱신 + 인과관계 회귀 테스트 5건, Contract 위반 회귀 테스트 4건 추가 |
| `hqs/development/stages/05_validation/VALIDATION.md` | `required_checks`의 인과관계·SKIPPED 의미 반영 |

`hqs/development/workflow.py`, Stage 01~04는 무변경 — Static Workflow
01→02→03→04→05 구조, Capability, Agent는 그대로다.

## required_checks의 실제 실행 경로

```
run_stage_05(stage_02_output, stage_04_output, required_checks=None)
  └─ required_checks 없으면 REQUIRED_CHECKS(=contracts.KNOWN_CHECK_NAMES, 4개 전부)
  └─ contracts.validate_verification_requirement(required_checks)   # 빈 값/미지 이름 즉시 거부
  └─ "structural" in required_checks   → _check_structural() 호출, 아니면 None(미실행)
  └─ "specification_scope" in ...      → _check_specification_scope() 호출, 아니면 None
  └─ "design_scope" in ...             → _check_design_scope() 호출, 아니면 None
  └─ "test_execution" in ...           → _run_pytest_with_applied_implementation() 호출, 아니면 None
  └─ _determine_verdict(..., required_checks)   # required_checks에 없는 항목은 raw_checks.get(name) is None → 판정에서 제외
  └─ _build_check_results(..., required_checks) # 없는 항목은 "SKIPPED" 상태로 기록
  └─ 반환: {..., "required_checks": tuple(required_checks), "check_results": [...], "verdict": ...}
```

`_determine_verdict()`와 `_build_check_results()`는 이제 `_CHECK_EVALUATORS`
표 하나만 참조한다 — 판정 규칙이 두 곳에 따로 적혀 있다가 갈라질 수 있는
구조 자체를 제거했다.

## VerificationResult/Verdict 연결

- **실행 집합 변경**: `required_checks`에서 제외된 검사는 함수 호출 자체가
  일어나지 않는다(단위 테스트: `test_excluding_test_execution_from_required_checks_skips_its_actual_execution`
  — spy로 호출 0회 확인).
- **결과 반영**: 제외된 항목은 `check_results`에 `"SKIPPED"`로 정직하게
  기록된다(status는 `PASS`/`FAIL`/`INCONCLUSIVE`/`SKIPPED` 4가지).
- **Verdict 반영**: 동일한 Stage 04 Output(테스트가 실패하는 상태)에서
  `required_checks`에 `test_execution`을 포함하면 Verdict가 `FAIL`,
  빼면 `PASS`로 실제로 달라진다(단위 테스트:
  `test_required_checks_value_changes_verdict_for_same_underlying_state`,
  real Engine E2E 아래).
- **조용한 PASS 차단**: `required_checks=()` 또는 알 수 없는 이름을
  넣으면 `run_stage_05()` 진입 즉시 `ContractViolation`이 발생한다
  (workflow.py를 통하면 `failed_at="stage_05"`로 명시적으로 드러남).
  `validate_verification_result()`는 한 걸음 더 나아가 "required로
  선언됐지만 실제로는 SKIPPED로 남은" 상태까지 차단한다.

## 기존 4개 검사의 blocking/non-blocking semantics 불변 확인

`required_checks`를 생략(=기본값, 4개 전부)했을 때 기존 143개 테스트가
그대로 통과한다는 것으로 확인했다 — 특히 기존 `_determine_verdict` 단위
테스트 7건(FAIL 3종/PARTIAL 3종/PASS 1종)이 시그니처 변경 없이(새
`required_checks` 인자는 기본값 `None`으로 하위 호환) 전부 그대로
통과했다. `specification_scope`는 여전히 non-blocking(미충족 시
PARTIAL만 유발)이고, `structural`/`design_scope`/`test_execution`은
여전히 blocking이다.

## 테스트 결과

- **152 passed**(1차 구현 143 → 이번 152, 신규 9건: Contract 위반 방어
  4건 + 인과관계 실증 5건). 회귀 없음.
- Mock/검증 우회 없음 — 모든 새 테스트가 실제 `run_stage_05()`/
  `_determine_verdict()`/`_build_check_results()`/`contracts.validate_*()`
  실제 코드 경로를 실행한다(`monkeypatch`는 결정성 확보를 위해 4개 하위
  검사 함수의 반환값만 고정했을 뿐, 검증 대상인 required_checks
  causal-wiring 자체는 실제 코드로 실행됨).
- 실행 명령: `pytest hqs/development/mvp/tests -q` → `152 passed`.

## Real Engine Evidence

`hqs/development/stages/01_context_analysis/stage_01.py` ~
`04_implementation/stage_04.py`를 실제 `claude` CLI 호출로 끝까지
실행해(mock 없음) 얻은 실제 `target = ("ast_context", "_first_doc_line")`,
`implementation`으로 Stage 05를 두 가지 `required_checks`로 실행:

| required_checks | test_execution 실행? | test_execution 상태 | verdict |
|---|---|---|---|
| 4개 전부(기본값) | O(실제 pytest subprocess 실행) | `FAIL`(returncode 1 — 이 세션 `sys.executable`에 pytest 미설치, 환경 문제이지 코드 결함 아님, 0001 문서에서 이미 확인) | **FAIL** |
| `test_execution` 제외 | X(호출 자체가 일어나지 않음) | `SKIPPED` | **PASS** |

동일한 실제 `target`/`implementation`(같은 근본 상태)에서 `required_checks`
값만 바꿨을 때 Verdict가 `FAIL → PASS`로 실제로 달라졌다 — 이것이
이번 작업이 닫으려는 인과관계의 직접 증거다. `required_checks=()`를
넘기면 `ContractViolation`이 즉시 발생함도 확인했다(조용한 PASS 없음).
실행 후 대상 파일은 Stage 05의 `finally`로 원상복구됐다(`git status`
production 변경 없음, 아래 참고).

## Security/Data-API/Regression 상태 재평가

| 시나리오 | Contract에 표현? | 실제 실행? | 실패 시 FAIL/차단? | 판정 |
|---|---|---|---|---|
| Regression | `test_execution` | O(real pytest) | O(blocking, 이번에 `required_checks`로 선택적 활성화까지 가능해짐) | **개선됨** — 실행 여부/Verdict 반영이 이제 `required_checks`로 실제 제어된다 |
| Security | 대응 검사 없음 | X | X | **미해결** — 이번 작업이 만든 것은 "기존 4개 중 무엇을 요구할지" 선택 메커니즘이지 새 검사 종류가 아니다. Security 검사 자체가 없으므로 `required_checks`에 넣을 대상이 없다 |
| Data-API | `specification_scope`가 가장 가까우나 "대상 파일이 후보 목록에 있는가"일 뿐 API 계약 검증 아님 | 실행되나 목적이 다름, 여전히 non-blocking(`_BLOCKING_CHECKS`에 없음, 정책 불변) | **미해결** | Security와 동일한 이유로 미해결 |

## Dynamic Workflow 필요성 변화

변화 없음. 이번 작업은 Stage 05 **내부**에서 "어떤 검사를 실행할지"를
데이터(`required_checks`)로 표현했을 뿐이며, Stage 개수·순서·
Capability·Agent·Stage 간 Control Flow는 전혀 바뀌지 않았다. Security/
Data-API 검사가 실제로 필요해지는 시점에도, 그 검사 자체가 결정적
정적 분석(예: 기존 `design_scope`처럼 AST/파일 비교)으로 구현 가능하면
`_CHECK_EVALUATORS`에 항목을 추가하는 것으로 충분하며 — 다만 이는 새
Capability이므로 Governance 절차가 우선이다(아래). Dynamic Workflow
(범용 Graph/Scheduler)가 필요하다는 근거는 여전히 없다.

## Governance 영향

- 새 RFC/ADC/ADR 없음. `contracts.py`/`stage_05.py`만 수정했고 Stage
  개수·순서·Capability·Agent·`workflow.py`는 무변경.
- **Security/Data-API 검사 자체의 신설은 이번 작업 범위 밖으로 명시적으로
  남겨뒀다** — `IMPLEMENTATION_RULES.md`의 "구현 중 새 Capability/Agent
  추가 금지"에 해당하므로, 실제로 그런 검사가 필요해지면 RFC → ADC → ADR
  절차를 거쳐야 한다. 이번 작업은 그 검사들을 만들지 않았고 우회하지도
  않았다 — "미해결"로 명확히 표시했을 뿐이다.
- Static Stage 01→02→03→04→05 구조, Workflow Parser/Engine/Scheduler/
  Runtime/Dynamic Routing/Event Bus/Memory, Retry/Re-entry 모두 구현하지
  않았다.

## 상태

- `git status`: `contracts.py`, `stage_05.py`, `VALIDATION.md`, 테스트
  3개 파일, 신규 문서 2개(본 문서 포함) 외 변경 없음(production 변경은
  Stage 05/contracts.py로 한정, Stage 01~04/`workflow.py`/RFC/ADC/ADR/
  BASELINE 무변경).
- 회귀 기준선: 152 passed.
