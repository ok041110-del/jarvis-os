# Python Refactor Wave 2 — Repository-wide Audit

**Governance 근거**: `docs/architecture/core/RFC-0042` → `ADC-0045` →
`ADR-0028`(Lifecycle 확정). Wave 0(Inventory)·Wave 1(Docstring 456건 +
`#` Comment 103건, `docs/research/PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001.md`)에
이은 세 번째 단계다. 이번 Wave는 **Audit-only**다 — `*.py` 변경 0건,
후보 확정과 우선순위만 산출한다.

## 1. Scope

- 대상: Repository 전체 git-tracked `*.py` **453개**(Wave 0/1과 동일
  전체 집합, `archive/v1` 82개 포함해 재검사).
- 실제 Refactoring 후보 풀: `archive/v1`(Historical, `ADR-0006`이 Migration
  제외 명시)을 제외한 **Active 371개**만 대상(Wave 0 §1.1과 동일 경계).
- `*.md`는 대상 아님. 일반 String Literal 변경 없음. Wave 1의 Comment/
  Docstring 결과는 되돌리지 않음(§10에서 확인).
- 이번 문서는 **분석·분류만** 수행한다 — 실제 코드 변경은 이 문서가
  WAVE 2 IMPLEMENT로 확정한 항목에 한해 **별도 커밋/PR**에서 진행한다.

## 2. Repository Baseline

재현 방법: `git ls-files '*.py'` + `ast.parse()`(AST 재순회, 외부 도구
미사용) — Wave 0와 동일 방법론.

| 항목 | 값 |
|---|---|
| 전체 `*.py` | 453개 |
| Active tree(`archive/` 제외) | 371개, 36,562 LOC |
| `archive/v1/` | 82개, 3,039 LOC |
| Active 중 Test 파일(`test_*.py`/`tests/`) | 105개 |
| Active 중 Non-test 파일 | 266개 |
| `ast.parse()` 실패 | **0건**(453/453 성공) |
| `python3 -m py_compile`(453개 전체) | **오류 0건** |
| `hqs/` pytest baseline | **380 passed, 6 skipped** |

Active LOC 36,562는 Wave 1 완료 시점(comment cleanup 이후) 수치와 정확히
일치한다 — 이 Audit 시작 시점까지 `*.py` 변경이 없었음을 재확인한다.

## 3. Audit Method

Wave 0의 Tier 방법론을 그대로 승계했다 — 371개 전체를 한 줄씩 수동
검토하는 것은 이번에도 시간/신뢰성 제약상 불가능하므로, 범위를 명시적으로
공개한다.

- **Tier 1(전수, 기계적)**: 371개 전체를 AST 기반 스크립트로 재순회해
  다음 지표를 수집했다 — 파일 LOC, 함수별 LOC/로컬 nesting depth/분기
  수(`If`/`For`/`While`/`Try`/`BoolOp` 합)/인자 수/return 수, 클래스별
  메서드 수, bare `except`, `global`/`nonlocal` 사용, 그리고 함수 본문
  AST를 정규화(`ast.unparse`)해 SHA1 해시로 비교한 **정확 일치 중복**.
  100% 커버(371/371).
- **Tier 2(표적 심층 검토)**: Tier 1이 상위 신호(최대 LOC/최대 nesting/
  최대 분기/최다 인자/cross-file 중복)로 표시한 파일 중 **actual
  production 코드에 속하는 것**(테스트 fixture/실험 스크립트 제외)을
  직접 열어 Ponytail 기준(§4)으로 판단했다 — 약 20개 파일.
- **Tier 3(기본값)**: Tier 2에 걸리지 않은 나머지는 Wave 0 §3의 원칙과
  동일하게 "적극적 개선 신호를 발견하지 못함" 의미의 `KEEP` 기본값으로
  분류한다(§16).
- Wave 0/1의 기존 판단(특히 `investment/teams`, `auto_selection_client.py`)은
  **재사용하지 않고 현재 코드를 다시 읽어 재판단**했다(§10).

## 4. Semantic Visibility Findings

- 대부분의 non-test 파일(예: `candidate_selection.py`, `stage_05.py`의
  개별 `_evaluate_*` 함수들, `reasoning.py`)은 함수명이 역할을 그대로
  드러내고, 최상위 흐름이 "입력 검증 → 계산 → 구조화된 반환" 순서를
  코드만으로 보여준다 — 별도 Semantic Visibility 개선이 필요한 사례를
  다수 찾지 못했다.
- 예외: `hqs/investment/teams/{stock,etf,dividend_stock}_team.py`의
  `run()`은 함수 하나 안에 "Wave 1(병렬 분석) → Wave 2(병렬 bull/bear)
  → Wave 3(trader) → Wave 4(report) → 파일 저장 → call_log 기록"까지
  6단계가 이어져 있어, 상위 의도(4-Wave 파이프라인)는 보이지만 각
  Wave의 반복되는 "checkpoint 확인 → 병렬 실행 → 결과 수집" 패턴이
  두 번(Wave 1/Wave 2) 그대로 반복돼 있다(§10.1).

## 5. Cognitive Load Findings

- `auto_selection_client.py::call_with_auto_selection`(133 LOC)은
  실패 유형(전송 실패/빈 응답/Contract 실패/성공) 4갈래 분기마다
  거의 동일한 필드 10개짜리 `AutoSelectionAttempt(...)` 생성 코드가
  반복돼, 실제 분기 로직(재시도 여부 판단)을 읽기 위해 매번 같은
  10줄짜리 생성자 호출을 건너뛰어야 한다(§10.2).
- `hqs/development/mvp/ast_context.py::build_dependency_closure`(60 LOC,
  nesting 4, 분기 22)는 재귀 AST 의존성 폐쇄 계산이라는 알고리즘
  자체의 본질적 복잡도이며, 각 분기가 "정의인가/import인가/이미
  방문했는가"처럼 명확한 이름의 조건으로 나뉘어 있어 Cognitive Load가
  구조적으로 낮다 — Wave 0 §3.1의 KEEP 판단을 재확인한다(§10.3).
- `hqs/development/stages/01_context_analysis/reasoning.py::aggregate_reasoning`(72 LOC,
  분기 16)은 분기 수는 높지만 각 분기가 서로 독립적인 단일 조건
  검사(agent별 null 체크, confidence 평균, status 판정)이며 nesting은
  낮다(1) — "코드를 왕복해야 이해되는" 유형이 아니라 "선형으로 읽으면
  끝나는" 유형이라 Cognitive Load 개선 대상에서 제외한다.

## 6. Duplication Findings

- 정확히 동일한 함수 본문을 가진 그룹 **146개**(Wave 0의 140개와
  유사 규모, 정규화 방식 약간 차이로 재현값 상이 — 둘 다 같은 결론:
  대부분 프로젝트 템플릿/테스트 fixture 중복), 그중 cross-file
  **144개**.
- 유형 분류는 Wave 0 §2.4를 재확인한다(파일 이동/삭제가 없었으므로
  구조 변화 없음):
  1. **투자 분석 프로젝트 템플릿 복제**(`stock-analysis-*`/
     `dividend-stock-analysis-*`/`etf-analysis-*`의 `runner.py`/
     `agents.py`) — 각 프로젝트가 독립 Dogfooding Historical
     Evidence(`docs/research/*-DOGFOODING-REVIEW-*.md`)라 Ponytail
     권한 밖(§11, `GOVERNANCE REQUIRED`).
  2. **`core/execution/mvp_000N/` MVP Evidence 간 중복** — 각 MVP
     번호가 독립 Evidence, 동일 사유로 `GOVERNANCE REQUIRED`.
  3. **테스트 fixture 중복**(`fake_design`/`fake_requirement`/`_load`
     등) — 순수 테스트 헬퍼, 낮은 우선순위(§13 P3).
  4. **`hqs/investment/teams/{stock,etf,dividend_stock}_team.py` 3개
     파일 간 `run()` 구조 중복** — **유일하게 Active Production 코드
     간의 진짜 중복**이며 Ponytail 권한 내(§10.1에서 재확정).
  5. **신규 확인**: `report_writer_final_report` 계열 함수(10~15개
     프로젝트에 걸쳐 인자 개수만 다른 거의 동일 구조)는 §2.4에는
     없던 신규 관찰이나, 유형 1과 동일한 Historical Evidence
     디렉터리에 속해 같은 사유로 `GOVERNANCE REQUIRED`로 묶는다.

## 7. Abstraction Findings

- 371개 전체에서 "호출부 1곳뿐인 wrapper"나 "실제 의미 없는 helper"
  패턴은 Tier 2 범위에서 추가로 발견되지 않았다 — Wave 0 §4의
  "Unnecessary abstraction/indirection 0건" 결론이 유지된다.
- 유일한 경계 사례는 `auto_selection_client.py`의 `_single_call`/
  `classify_failure`/`call_with_auto_selection` 3단 분리인데, 이는
  "지나치게 쪼개짐"이 아니라 오히려 "한 함수 안에 HTTP 호출/실패
  분류/재시도 정책이라는 세 semantic responsibility가 섞여 있고
  responsibility 경계가 함수 경계와 일치하지 않는" 반대 방향
  문제다(§10.2, `REFACTOR` 대상은 함수 추가 분리가 아니라 반복되는
  결과 기록 코드의 통합).

## 8. Control Flow Findings

- Bare `except:` **0건**(371개 전체).
- `global`/`nonlocal` 사용 **1건**(`projects/workflow-adapter-gate-c-real-engine-v1/domain/engine_cache.py`,
  2회) — 실험적 프로젝트의 캐시 초기화용, 파일 범위가 좁고(단일
  모듈 캐시) 대체 시 API 변경이 필요해 이번 Wave IMPLEMENT 대상에서
  제외, `KEEP`(비용 대비 이득 낮음).
- Early-return으로 명확해질 수 있는 깊은 if/else 체인은 Tier 2
  범위에서 발견되지 않았다 — 이 저장소는 이미 대체로 guard-clause
  스타일(`if not X: return`)을 쓰고 있다(예: `candidate_selection.py`,
  `deterministic_filter.py`).
- `call_with_auto_selection`의 4단 `if failure_class ...: attempts.append(...); if ...: break; continue` 패턴은
  control flow 자체는 명확하나(재시도 루프, `continue`/`break` 의미
  뚜렷) §5/§10.2에서 지적한 반복 코드 때문에 그 명확한 흐름이
  가려진다 — Control Flow 문제가 아니라 Duplication 문제로 분류한다.

## 9. Naming Findings

- 함수/변수명이 의미를 전달하지 못하는 사례를 광범위하게 찾지
  못했다 — 이 저장소의 명명 관례(`fundamental_analyst_fundamental_analysis`,
  `_evaluate_structural`, `identify_target` 등)는 장황할지언정 항상
  구체적이다.
- 유일한 개선 여지: `report_writer_final_report`류 함수의 위치 인자
  9~11개(예: `hqs/investment/teams/dividend_stock_team.py`)는 이름은
  명확하나 호출부에서 인자 순서를 실수하기 쉬운 구조다 — 그러나 이는
  Naming이 아니라 함수 시그니처(Abstraction) 문제이며, 개선하려면
  호출부(`run()`)의 `results` dict를 그대로 전달하는 구조 변경이
  필요해 Contract(파일별 출력 dict 키)에 영향을 줄 가능성이 있다 —
  `GOVERNANCE REQUIRED`로 분리한다(§11).

## 10. Existing Wave 0 Candidate Reassessment

### 10.1 `hqs/investment/teams/{stock,etf,dividend_stock}_team.py` — 재확정

현재 코드를 다시 읽은 결과(§4~6), Wave 0의 `SIMPLIFY` 판단을 **재확인**한다.

- **실제 중복인가**: 그렇다. `run()` 내부의 "pending 계산 → checkpoint
  로드 → `ThreadPoolExecutor`로 병렬 실행 → 결과 수집" 블록이 Wave 1과
  Wave 2에서 토씨 하나 다르지 않게 반복되고(3개 파일 × 2블록 = 6곳),
  세 파일 사이에서도 이 블록 자체는 완전히 동일하다(분석 함수
  dict/개수만 다름).
- **공통화 가치가 있는가**: 있다. "checkpoint-aware 병렬 실행"이라는
  하나의 semantic 단위를 `_run_checkpointed_wave(cp, jobs: dict) -> dict`
  형태로 뽑아내면, 3개 파일 각각에서 6곳 반복이 사라지고 `run()`의
  나머지 부분(Wave별 입력 조립·출력 조합)만 팀별 차이로 남는다.
- **Contract 영향**: `run()`의 반환 dict 형태(`results`/`wave_summary`
  키, `results` 내부 `*.md` 파일명)와 각 팀의 분석 함수 시그니처는
  **무변경 가능** — 추출 대상은 순수 제어 흐름(pending 계산 + 병렬
  실행 + 결과 dict 구성)이며 어떤 분석 함수가 호출되는지는 여전히
  각 팀 파일이 결정한다.
- **결론**: `SIMPLIFY`+`DUPLICATION`, P1, **WAVE 2 IMPLEMENT 후보**
  (§14) — `hqs/investment/tests/test_*_team_integration.py`가 즉시
  회귀 확인 가능.

### 10.2 `auto_selection_client.py::call_with_auto_selection`(133 LOC) — 재확정

- **실제 semantic responsibility 분리 필요성**: 함수 자체가 여러
  책임을 섞은 것이 문제가 아니라(재시도 루프 하나의 책임), 4개
  실패/성공 분기마다 `AutoSelectionAttempt(...)` 10개 필드 생성이
  반복되는 것이 문제다 — Wave 0가 제안했던 "재시도/실패분류 분리"보다
  **정확한 원인은 결과 기록 코드 중복**임을 이번 재검토에서 새로
  확인했다.
- **함수 분리가 readability를 개선하는가**: 재시도 루프 자체를
  쪼개면(예: 재시도 여부 판단만 별도 함수로) 오히려 상태(`current_pool`,
  `attempts`, `overall_start`)를 여러 함수에 걸쳐 전달해야 해서
  Cognitive Load가 늘어난다 — 대신 `_record_attempt(...)` 헬퍼로
  `AutoSelectionAttempt` 생성만 통합하면 함수 분리 없이(제어 흐름은
  그대로) 반복 코드 4곳이 사라지고 각 분기가 "무엇이 실패했는지 +
  기록"만 남아 명확해진다.
- **Contract 영향**: `AutoSelectionAttempt`/`AutoSelectionResult`
  필드는 무변경 — 순수 내부 리팩터링.
- **결론**: `DUPLICATION`(Wave 0의 `REFACTOR` 판단을 "함수 분리"에서
  "결과 기록 통합"으로 정정), P1, **WAVE 2 IMPLEMENT 후보**(§14) —
  `projects/openrouter-auto-selection-v1/tests/`(15 passed)로 즉시
  회귀 확인 가능.

### 10.3 `ast_context.py` 재확인

Wave 0 §3.1의 `KEEP` 판단을 그대로 재확인한다(§5) — 재귀 AST 순회의
본질적 복잡도이며 이름이 역할을 명확히 설명한다.

## 11. Architecture/Contract Risks

이번 Wave에서 **임의 변경하지 않는** 영역(Stage/Team responsibility,
Public Contract, Output schema, Engine boundary, OpenRouter architecture,
Stage ordering, validation semantics, Governance rules)에 개선 여지가
있는 것으로 관찰된 항목은 실행하지 않고 아래로 격리한다.

| 항목 | 관찰 | 격리 사유 |
|---|---|---|
| `report_writer_final_report` 계열 위치 인자 9~11개 | 함수 시그니처를 dict/dataclass로 바꾸면 호출 안전성 향상 | 호출부(`run()`)와 각 팀의 `results` 조립 로직을 함께 바꿔야 하고, Historical Evidence 프로젝트(15개+)까지 건드리게 되면 Wave 0 §6의 Historical Evidence 보존 판단과 충돌 — `GOVERNANCE REQUIRED` |
| `stock-analysis-*`/`dividend-stock-analysis-*`/`etf-analysis-*`의 `runner.py`/`agents.py` 반복 구조 | 대량 통합 가능(§6 유형 1/5) | Wave 0 §6/§7이 이미 "Historical Evidence 통합 여부는 별도 RFC 판단 필요"로 확정 — 이번 Wave가 재론하지 않음, `GOVERNANCE REQUIRED` 유지 |
| `core/execution/mvp_000N/` 간 중복 | 통합 가능해 보임 | 각 MVP 번호가 독립 Evidence(ADR/ADC 인용 대상) — `GOVERNANCE REQUIRED` |

이 세 항목 모두 **Ponytail 권한 밖**이며, 통합을 원할 경우 RFC → ADC
→ ADR 절차(Frozen Architecture)를 먼저 거쳐야 한다.

## 12. Candidate Matrix

| # | file | symbol | 문제 | 현재 구조 | 제안 구조 | 기대 효과 | Regression Risk | Architecture Risk |
|---|---|---|---|---|---|---|---|---|
| C1 | `hqs/investment/teams/stock_team.py`, `etf_team.py`, `dividend_stock_team.py` | `run()` | Wave1/Wave2 "checkpoint-aware 병렬 실행" 블록이 파일당 2회, 3파일에 걸쳐 완전 동일 반복 | 각 `run()`에 동일한 pending 계산+`ThreadPoolExecutor` 블록이 인라인 반복 | 공통 `_run_checkpointed_wave(cp, jobs)` 헬퍼를 3개 파일이 공유하는 신규 내부 모듈(또는 팀 공통 유틸)로 추출 | 3파일 각 6곳 → 0곳, 팀별 분석 로직만 남아 파일 간 차이가 즉시 드러남 | 낮음(`test_*_team_integration.py`로 즉시 확인) | 낮음(반환 dict/함수 시그니처 무변경) |
| C2 | `projects/openrouter-auto-selection-v1/domain/auto_selection_client.py` | `call_with_auto_selection` | 4개 실패/성공 분기마다 `AutoSelectionAttempt` 10필드 생성 반복 | 분기마다 인라인 dataclass 생성 | `_record_attempt(...)` 헬퍼로 생성 통합 | 133 LOC 중 반복 코드 약 40줄 제거, 분기별 차이만 드러남 | 낮음(전용 테스트 15개) | 낮음(dataclass 필드 무변경) |
| C3 | `hqs/investment/teams/dividend_stock_team.py` 등 `report_writer_final_report` 계열 | 위치 인자 9~11개 | 호출 시 인자 순서 실수 위험 | 위치 인자 나열 | dict/dataclass 인자로 전환 | 호출 안전성 향상 | 중간(Historical Evidence 프로젝트까지 연쇄) | 있음 — `GOVERNANCE REQUIRED`(§11) |
| C4 | `stock-analysis-*`/`dividend-stock-analysis-*`/`etf-analysis-*` (15개+) | `runner.py`/`agents.py` | 대규모 cross-file 중복(유형 1) | 프로젝트별 독립 파일 | 공유 템플릿 모듈화 | 대량 중복 제거 | 높음(Historical Evidence 문언 변경 위험) | 있음 — `GOVERNANCE REQUIRED`(Wave 0 §6/§7 기존 결론 유지) |
| C5 | `core/execution/mvp_000N/*/dogfooding/run_dogfooding.py` | `main`/`_derive_id` 등 | cross-file 중복(유형 2) | MVP별 독립 스냅샷 | 통합 가능해 보이나 Evidence 성격 | — | 높음 | 있음 — `GOVERNANCE REQUIRED`(Wave 0 기존 결론 유지) |
| C6 | `hqs/development/mvp/ast_context.py` | `build_dependency_closure`, `resolve` | 재귀 nesting/분기 수치 높음 | 현행 유지 | 변경 없음 | — | — | — |
| C7 | `hqs/development/stages/01_context_analysis/reasoning.py` | `aggregate_reasoning` | 분기 수 16(선형, 독립 조건) | 현행 유지 | 변경 없음 | — | — | — |
| C8 | `projects/workflow-adapter-gate-c-real-engine-v1/domain/engine_cache.py` | 모듈 캐시 | `global` 사용 2회 | 현행 유지 | 변경 없음(비용 대비 이득 낮음) | — | — | — |
| C9 | 테스트 fixture 중복(`fake_design`/`_load` 등, §6 유형 3) | 다수 | 순수 테스트 헬퍼 중복 | 파일별 독립 fixture | 공유 conftest로 통합 가능 | 테스트 코드 중복 감소 | 낮음 | 없음 |

`POSSIBLE_BUG`, `NAMING`(단독), `CONTROL_FLOW`(단독), `ABSTRACTION`(단독,
불필요 wrapper 방향)으로 분류될 신규 항목은 Tier 2 범위에서 **발견되지
않았다**(0건) — Wave 0 §4/§6의 "Over-engineering/clever code 0건"
결론과 일치한다.

## 13. Priority

| 우선순위 | 항목 | 근거 |
|---|---|---|
| **P0**(bug/security) | 없음 | Tier 1/2 어디에서도 correctness 결함·security/data-loss risk 발견 안 됨 |
| **P1**(높은 Cognitive Load/명백한 중복/핵심 runtime 복잡도) | C1, C2 | Active Production 코드의 진짜 중복이자 반복 코드로 인한 가독성 저하 — Ponytail 권한 내, 낮은 regression risk |
| **P2**(readability/naming/작은 simplification) | C9 | 테스트 fixture 공유화, 영향 범위 좁음 |
| **P3**(cosmetic) | 없음으로 확인(§8 참고) — 이번 Wave에서 P3로 분류된 별도 항목 없음 | — |

C3/C4/C5는 우선순위 체계 밖의 `GOVERNANCE REQUIRED`로 별도 관리한다
(§11) — 개선 가치와 무관하게 Ponytail 권한을 넘어서므로 P1이어도
이번 Wave가 다루지 않는다.

## 14. WAVE 2 IMPLEMENT

**작은 범위·낮은 regression risk·높은 clarity gain 순으로 진행**한다.

1. **C2**(`auto_selection_client.py`) — 단일 파일, 순수 내부 헬퍼
   추출, 전용 테스트 15개로 즉시 검증 가능. **가장 먼저 진행**.
2. **C1**(`investment/teams/*.py` 3파일) — 3파일 동시 변경이지만 추출
   대상이 순수 제어 흐름 블록으로 명확히 분리되고, 통합 테스트로
   Contract(반환 dict) 무변경을 직접 검증 가능.

C9(테스트 fixture 공유화)는 IMPLEMENT 후보로 유효하나 이번 Wave의
범위를 "핵심 runtime code"(C1/C2)로 최소화하기 위해(RFC-0042 §7 원칙)
§15로 이관한다.

## 15. WAVE 2 DEFER

| 항목 | 이관 사유 |
|---|---|
| C9(테스트 fixture 공유화) | 개선 가치는 있으나 이번 Wave 범위를 P1 2건으로 최소화하기 위해 후속 Wave로 분리 |
| C3(`report_writer_final_report` 인자 구조 개선) | `GOVERNANCE REQUIRED` — RFC 제안 후 별도 진행 |
| C4(Historical Evidence 15개+ 통합) | `GOVERNANCE REQUIRED` — Wave 0 §6/§7 기존 결론 유지, 별도 RFC 필요 |
| C5(`core/execution/mvp_000N/` 통합) | `GOVERNANCE REQUIRED` — 각 MVP 독립 Evidence, 별도 RFC 필요 |

## 16. KEEP

- C6(`ast_context.py`), C7(`reasoning.py::aggregate_reasoning`),
  C8(`engine_cache.py`의 `global` 사용) — §10.3/§5/§8에서 근거 확인.
- Tier 2에 걸리지 않은 나머지 Active 파일 전체(약 350개, C1/C2/C9
  대상 제외) — Wave 0 §3 Tier 3 원칙과 동일하게 "적극적 개선 신호를
  발견하지 못함" 기본값 `KEEP`. 이는 "전부 완벽하다"는 뜻이 아니라
  이번 Audit의 표적 검토 범위에서 추가 조치가 필요한 신호를 찾지
  못했다는 뜻이며, 이 방법론적 한계를 명시적으로 공개한다(Wave 0 §3와
  동일 원칙).

## 17. Validation Plan

WAVE 2 IMPLEMENT(§14) 착수 시 다음을 수행한다(이번 Audit 문서
자체에는 아직 적용하지 않음 — Audit 단계는 코드 변경 0건, §18 확인):

1. C2 적용 → `python3 -m py_compile` + `ast.parse()` 재검증 →
   `projects/openrouter-auto-selection-v1/tests/` 실행(15 passed 유지
   확인) → `git diff`로 `AutoSelectionAttempt`/`AutoSelectionResult`
   필드·값 생성 로직이 동일한지 수동 대조.
2. C1 적용 → 3개 파일 개별 `py_compile`/`ast.parse()` → `hqs/` 전체
   pytest(380 passed/6 skipped 유지 확인, 특히
   `test_stock_team_integration.py`/`test_etf_team_integration.py`/
   `test_dividend_stock_team_integration.py`) → 각 팀 `run()`의 반환
   dict 키 집합이 변경 전후 동일한지 확인.
3. 두 변경 모두 완료 후 `hqs/` 전체 재실행 + `git diff`로 Comment/
   Docstring(Wave 1 결과) 변경 여부 재확인(변경 없어야 함).

## 18. Conclusion

- 전체 git-tracked `*.py` **453개**를 재검사했다(Active 371개 Tier 1
  전수 AST 스캔 + 이상 신호 파일 약 20개 Tier 2 심층 검토, `archive/`
  82개는 Wave 0/1과 동일하게 Historical로 재확인만 하고 후보 풀에서
  제외).
- 후보 9건(C1~C9) 확정 — `SIMPLIFY`/`DUPLICATION` 2건(C1, C2, P1),
  `NAMING`/`ABSTRACTION` 성격 1건(C3, `GOVERNANCE REQUIRED`),
  `DUPLICATION`(Historical) 2건(C4, C5, `GOVERNANCE REQUIRED`),
  `KEEP` 3건(C6~C8), `NAMING`/테스트 중복 1건(C9, P2, DEFER).
  `POSSIBLE_BUG`/`ARCHITECTURE-CONTRACT RISK`(단독) 0건.
- **WAVE 2 IMPLEMENT**: C2(`auto_selection_client.py`) →
  C1(`investment/teams/*.py`) 순서로 별도 커밋/PR에서 실행한다.
- **WAVE 2 DEFER**: C9(fixture 공유화), C3/C4/C5(`GOVERNANCE
  REQUIRED`, RFC 선행 필요).
- **KEEP**: C6~C8 및 Tier 2 미해당 나머지 Active 파일 전체.
- **Architecture/Contract**: 이번 Audit에서 임의 변경 0건, 발견된
  위험은 전부 §11/§15에 `GOVERNANCE REQUIRED`로 격리했다.
- **이번 단계 `*.py` 실제 변경**: **0건**(§2/§19에서 재확인) — Audit
  결과만 제출하며, 실제 Refactoring은 WAVE 2 IMPLEMENT 커밋에서
  별도로 진행한다.

## Related

- `docs/architecture/core/RFC-0042`, `ADC-0045`, `ADR-0028`
- `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
- `docs/research/PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001.md`
- `hqs/development/IMPLEMENTATION_RULES.md`
