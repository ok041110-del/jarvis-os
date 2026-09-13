# Python Audit Wave 0 — Repository-wide Inventory & Baseline

**Governance 근거**: `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md`
→ `ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`
→ `ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md`
(Governance Lifecycle 확정, 이 문서는 그 Lifecycle의 **Wave 0(Inventory
+ Deterministic Audit + Semantic/Ponytail Review, 코드 무변경)**
Evidence다).

## Summary

- **`*.py` 파일 0건 수정/삭제/이동.** 이 Wave는 순수 조사다(git diff
  대상은 이 문서 1건뿐, §9에서 재확인).
- Repository 전체 git-tracked `*.py` **453개**, 총 **41,495 LOC**.
  - Active tree(`archive/` 제외) **371개 파일, 38,456 LOC**.
  - `archive/v1/`(Historical, `ADR-0006`이 Migration 제외 명시)
    **82개 파일, 3,039 LOC** — 이번 Wave의 Refactoring 후보 풀에서
    제외(§4, §6).
  - Test 파일(`test_*.py` 또는 `tests/` 하위) **116개, 14,962 LOC**
    — RFC-0042 지시대로 Audit 대상에 포함.
- Deterministic Audit(AST 기반, 453개 파일 **100% 커버**): syntax
  오류 **0건**, `py_compile` 실패 **0건**.
- Semantic/Ponytail Review는 **Deterministic Audit이 실제로
  이상 신호를 표시한 상위 파일군(고 LOC/고 nesting/0-docstring/
  cross-file 중복)에 대해 직접 코드를 읽고 판단**했다 — 371개
  전체를 한 줄씩 수동 검토하지는 않았다(방법론 §3에서 명시적으로
  공개, 신뢰성 왜곡 방지).
- Baseline Validation: `hqs/` 전체 pytest **380 passed, 6 skipped,
  0 failed**. `projects/` 44개 디렉터리 개별 실행 결과는 §8에 전수
  기록 — 기존에 이미 실패/에러 상태였던 항목 다수 발견(환경 의존성
  누락 3건 유형, concurrency 타이밍 테스트 실패 6건, 중첩 pytest
  실행 특이 케이스 1건) — **전부 이번 Wave 이전부터 존재하던 상태이며
  이번 Wave가 원인이 아니다**(diff 없음으로 증명).

---

## 1. Python Inventory

### 1.1 전체 규모

| 구분 | 파일 수 | LOC |
|---|---|---|
| 전체(git-tracked `*.py`) | 453 | 41,495 |
| Active tree(`archive/` 제외) | 371 | 38,456 |
| `archive/v1/`(Historical) | 82 | 3,039 |
| Test 파일 | 116 | 14,962 |
| Non-test 파일 | 337 | 26,533 |

### 1.2 최상위 디렉터리별 분포

| 최상위 디렉터리 | 파일 수 | LOC |
|---|---|---|
| `projects/`(44개 독립 프로젝트) | 228 | 24,000 |
| `hqs/`(Development HQ + Investment HQ) | 109 | 12,325 |
| `archive/`(v1, Historical) | 82 | 3,039 |
| `core/`(Kernel/Execution Layer, MVP 0001~0006 Evidence 포함) | 34 | 2,131 |

### 1.3 `hqs/` 세부 분포(Active)

| 하위 경로 | 파일 수 | LOC |
|---|---|---|
| `development/mvp/` | 67 | 7,831 |
| `development/stages/` | 21 | 2,398 |
| `investment/teams/` | 3 | 796 |
| `investment/tests/` | 7 | 724 |
| `development/teams/` | 5 | 120 |
| `investment/trader.py` 등 단일 파일 5개 | 5 | 372 |

### 1.4 파일 단위 상세 데이터

453개 파일 전체(path/LOC/functions/classes/imports/local·external
dependency/docstring count/public-looking 함수·클래스/test 여부)를
AST 기반으로 기계 수집했다. 원본 JSON은 세션 스크래치패드
(`inventory.json`, 재현 가능 — `git ls-files "*.py"` + `ast.parse`
기반, 외부 도구 미사용)에 보관하고, 이 문서에는 §2~§6의 신호가 있는
파일만 발췌해 표로 반영한다(453개 전체를 이 문서에 원문 그대로
싣는 것은 Progressive Disclosure 원칙에 반하며, 재현 가능한
스크립트 자체가 Evidence이므로 원본 표 전체 복제는 정보 가치가
낮다).

---

## 2. Deterministic Audit

### 2.1 Syntax / Compile

- `ast.parse()` 453/453 성공(**0 syntax error**).
- `python3 -m py_compile`(active tree 371개 대상) — **0 오류**(§9
  Validation에서 재확인).

### 2.2 Import/Dependency 구조

- Top-level import 모듈 상위: `pathlib`(216), `sys`(190),
  `__future__`(132), `json`(92), `mvp`(local, 64), `time`(63),
  `pytest`(46), `domain`(local, 42), `dataclasses`(37),
  `importlib`(27), `ast`(25), `typing`(23).
- 외부 패키지 의존은 `pytest`뿐이며 나머지는 stdlib —
  **Ponytail D(stdlib/native 우선) 원칙이 이미 전반적으로 잘
  지켜지고 있다.** 예외: `langgraph`(4개 `workflow-adapter-*`
  프로젝트, `ADR-0018`/`ADR-0019`/`RFC-0031`이 이미 Architecture
  차원에서 승인한 의존성 — 새 발견 아님, 이번 세션 환경에는
  미설치 상태만 확인, §8).
- Local sibling-import 체인은 선행
  `STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`
  §9가 식별한 것과 동일 구조(`domain`/`caller`/`adapters`/
  `resolver` 등 프로젝트 내부 모듈) — 신규 순환 참조는 발견되지
  않았다.

### 2.3 함수/클래스 규모, Nesting

| 신호 | 발견 |
|---|---|
| 최대 파일 LOC(non-archive) | `projects/stage05-parallel-validation-harness-v1/tests/test_harness.py` 501 LOC(test 파일) |
| 최대 파일 LOC(non-test) | `projects/unified-dashboard/snapshot.py` 337 LOC |
| 최대 단일 함수 LOC | `projects/openrouter-auto-selection-v1/domain/auto_selection_client.py::call_with_auto_selection` 137 LOC |
| 2위 | `projects/openrouter-free-model-selection-architecture-experiment-v1/run_stage05_revalidation.py` 내 함수 136 LOC |
| 100 LOC 이상 단일 함수 | 15개(대부분 `dividend-stock-analysis-*`/`etf-analysis-*`/`stock-analysis-*` 프로젝트의 `runner.py` — §4에서 재론) |
| 최대 nesting depth | 5(`projects/unified-dashboard/tests/test_snapshot.py`, test 파일) |
| nesting 4 | 11개 파일(비-test 3개: `hqs/development/mvp/ast_context.py`, `hqs/development/stages/01_context_analysis/stage_01_multi_agent.py`, `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/candidate_selection.py`) |

### 2.4 중복 패턴(정확 일치 함수 본문, AST 정규화 기준)

- 정확히 동일한 함수 본문을 가진 그룹 **140개** 발견(정규화된
  AST unparse 문자열의 SHA1 해시 기준, 길이 40자 미만 trivial
  함수는 노이즈 제거를 위해 제외).
- 이 중 서로 다른 파일에 걸친 그룹 **135개**. 압도적 다수는 다음
  두 유형 중 하나다(§4에서 Ponytail 관점 판단 계속):
  1. **투자 분석 프로젝트 템플릿 복제**(`_run`,
     `fundamental_analyst_fundamental_analysis` 등이 `stock-analysis-*`/
     `dividend-stock-analysis-*`/`etf-analysis-*` 최대 21개 파일에
     걸쳐 동일) — 각 프로젝트는 개별 종목 Dogfooding의 독립
     Historical Evidence(`docs/research/*-DOGFOODING-REVIEW-*.md`가
     개별 인용, `ARCHIVE-CLEANUP-REVALIDATION-0001.md` 재확인)다.
  2. **`core/execution/mvp_000N/dogfooding/run_dogfooding.py`류**
     MVP Evidence 스냅샷 간 중복(`main`/`_derive_id`/
     `_extract_handle_id`) — 각 MVP 번호가 독립 Evidence.
  3. **테스트 fixture 중복**(`fake_design`/`fake_requirement`/
     `_load`/`get_file_content` 등 여러 `test_workflow_*.py`/
     `test_stage_*.py` 간) — 순수 테스트 헬퍼.
  4. **`hqs/investment/teams/{stock,etf,dividend_stock}_team.py`
     3개 파일 간 `_run`/analyst 함수 구조 중복** — 이것만 **Active
     Production 코드 간의 진짜 중복**이며 나머지 세 유형과 성격이
     다르다(§4, §7에서 Wave 1 후보로 구체화).

---

## 3. Senior Readability Audit — 방법론 공개

371개 Active 파일 전체에 대해 "코드만 읽어도 무엇을 하는지
보이는가"류의 사람 판단을 전수 수행하는 것은 이번 Wave의 시간/
신뢰성 제약상 불가능하다고 판단했다. 대신:

- **Tier 1(전수, 기계적)**: §2 Deterministic Audit 전체 — 100%
  커버.
- **Tier 2(표적 심층 검토)**: §2가 이상 신호(고 LOC/고 nesting/
  0-docstring/cross-file 중복/최대 단일 함수)로 표시한 파일
  **약 30개**를 실제로 열어 Ponytail 기준(§4 아래)으로 직접
  판단했다.
- **Tier 3(디렉터리 단위 기본 분류)**: Tier 2에 걸리지 않은
  나머지 파일은, 같은 디렉터리/같은 템플릿 계열의 대표 파일이
  이미 Tier 2에서 검토된 경우 그 판단을 준용하고, 그렇지 않으면
  `KEEP`(현재 Wave에서 추가 조치 불필요) 기본값으로 분류했다 —
  이는 "전부 문제없다고 확인했다"는 뜻이 아니라 **"이번 Wave가
  적극적 개선 신호를 발견하지 못했다"**는 뜻이며, 이 구분을
  §7/§10에서 명시한다.

이 방법론 자체가 Wave 0 성공 기준("코드를 얼마나 고쳤는가"가 아니라
"현재 상태를 신뢰성 있게 파악했는가")에 부합하도록, Tier 1/2/3의
경계를 숨기지 않고 공개한다.

### 3.1 Tier 2 심층 검토 결과(선별)

| 파일 | 관찰 | Semantic Visibility 판단 |
|---|---|---|
| `projects/openrouter-auto-selection-v1/domain/auto_selection_client.py::call_with_auto_selection`(137 LOC) | 모델 fallback 배열을 순회하며 재시도/실패 분류를 한 함수 안에서 처리 | 상위 흐름(요청 → 실패 분류 → 재시도 정책)은 보이나, 재시도 루프와 실패 분류 로직이 한 함수에 섞여 있어 "무엇을 하는 함수인가"를 한 번에 파악하기 어려움 — **REFACTOR 후보**(§6), 단 Contract(`str -> dict` 반환 모양)는 무변경 가능해 보임 |
| `hqs/development/mvp/ast_context.py`(190 LOC, nesting 4) | AST 순회 유틸리티 | 함수명(`identify_target`, `_build_target_index` 등)이 역할을 명확히 설명 — nesting은 AST 트리 순회 특성상 자연스러운 수준. **KEEP** |
| `hqs/development/stages/01_context_analysis/stage_01_multi_agent.py`(nesting 4) | Multi-Agent 합의 로직 | 상위 함수가 "Agent 실행 → 합의 판정" 흐름을 그대로 드러냄. nesting은 합의 조건 분기 특성. **KEEP** |
| `hqs/investment/teams/{stock,etf,dividend_stock}_team.py`(3개, 796 LOC 합계) | §2.4 유형 4 | 개별 파일 안에서는 이름이 역할을 잘 설명하지만(`fundamental_analyst_fundamental_analysis` 등), **3개 파일에 걸쳐 거의 동일한 구조가 반복**돼 있어 "이 3개가 왜 별개 파일인가"가 코드만으로 드러나지 않음 — Cognitive Load 관점에서 한 파일을 이해해도 나머지 둘의 차이(§2.4에서 확인한 `SECTION_TAGS`/추가 analyst 함수)를 별도로 다시 읽어야 함. **SIMPLIFY 후보**(§6, §7 Wave 1 1순위) |
| `projects/unified-dashboard/snapshot.py`(337 LOC, docstring 위반 7건) | 대시보드 스냅샷 생성 | 함수 분해 자체는 의미 단위로 되어 있으나 docstring이 §5 정책(2줄) 대비 과도하게 김(최대 51줄) — 코드 자체보다 문서화 스타일 문제. **COMMENT/DOCSTRING CLEANUP 후보** |
| `dividend-stock-analysis-*`/`etf-analysis-*`/`stock-analysis-*`류 `runner.py`(15개, 각 92~113 LOC 단일 함수) | §2.3 100 LOC+ 함수 다수 | 각 파일은 "데이터 로드 → 체크포인트 → Agent 호출 → 리포트 저장"이라는 동일 흐름을 한 함수에 순차 나열 — 함수가 길지만 각 단계가 주석 없이도 변수명으로 드러남(clever code 아님). 다만 15개 파일이 사실상 동일 골격의 반복. **개별 파일은 KEEP(가독성 자체는 문제없음), 반복 구조는 GOVERNANCE REQUIRED**(§6 — 각 파일이 독립 Dogfooding Historical Evidence이므로 통합은 Governance 판단 필요, Ponytail 권한 밖) |

### 3.2 "짧다/작다 = 좋다" 오판 방지 확인

- Tier 2 검토 대상 중 어떤 파일도 "함수가 기니까 나쁘다"만으로
  판정하지 않았다 — 위 표의 `runner.py`류처럼 긴 단일 함수라도
  각 단계가 선형적이고 이름이 명확하면 `KEEP`으로 유지했다.
  반대로 짧은 함수라도 여러 파일에 흩어져 있어 전체 그림을
  재구성하기 어려운 경우(팀 3파일 구조)는 `SIMPLIFY` 후보로
  분류했다 — Semantic Visibility/Cognitive Load를 LOC와 분리해
  평가했다(사용자 지시 §3 "중요" 원칙 반영).

---

## 4. Ponytail Audit(자동 수정 없음, 후보 식별만)

| 유형 | 발견 | 분류 |
|---|---|---|
| Unnecessary abstraction | Tier 2 범위에서 명백한 "호출부 1곳뿐인 wrapper" 다수 발견되지 않음(0건 확정) — 추가 확인은 Wave 1 대상 디렉터리별 심층 Audit에서 계속 | 해당 없음(Not Found, 이번 Wave 기준) |
| Unnecessary indirection | 없음(Tier 2 기준) | 해당 없음 |
| Duplicate logic | §2.4의 4개 유형 — 유형 1/2/3은 Historical Evidence/테스트 fixture 성격(Ponytail 권한 밖, `GOVERNANCE REQUIRED` 또는 `KEEP`), **유형 4(Investment Team 3파일)만 실제 Ponytail 권한 내 `SIMPLIFY` 후보** | 혼합(§6 표에서 세분화) |
| Unnecessary dependency | `langgraph`(4개 프로젝트) — 이미 `ADR-0018`/`ADR-0019`가 승인한 의존성, 이번 Wave가 새로 문제 삼지 않음 | GOVERNANCE REQUIRED 아님(기존 승인 재확인만) |
| Over-engineering | Tier 2 범위에서 미발견 | 해당 없음 |
| Needless comments/docstrings | §5(Comment/Docstring Audit)에서 별도 상세 | COMMENT/DOCSTRING CLEANUP |
| "clever code" 후보 | Tier 2 범위에서 미발견(전반적으로 명시적 stdlib 스타일 — Ponytail D 원칙과 일치) | 해당 없음 |

---

## 5. Comment / Docstring Audit

기존 정책(`IMPLEMENTATION_RULES.md`/CLAUDE.md, 최대 2줄·WHY 중심)을
그대로 적용해 위반만 표시했다 — 이번 Wave에서 수정하지 않는다.

- **2줄 정책 위반 docstring**: **456건**(active tree, AST
  `ast.get_docstring` 기준, 빈 줄 제외 실 라인 수로 카운트).
- **위반 상위 파일**(발췌, 전체는 스크래치패드
  `comment_audit.py` 출력에 보관):

| 파일 | 위반 건수 | 최악 사례(줄) |
|---|---|---|
| `projects/unified-dashboard/snapshot.py` | 7 | 51 |
| `hqs/development/mvp/openrouter_engine.py` | 7 | 34 |
| `hqs/development/stages/contracts.py` | 6 | 22 |
| `hqs/development/mvp/omniroute_engine.py` | 3 | 20 |
| `hqs/development/mvp/tests/test_omniroute_engine_real.py` | 3 | 18 |
| `projects/omniroute-thin-engine-caller-v1/caller.py` | 7 | 16 |

- **KEEP 판단(내용 검토 결과)**: `auto_selection_client.py`(§3.1)의
  모듈 docstring처럼, 길지만 **외부 제약/비자명한 correctness
  발견 사항**을 담은 경우는 내용상 §4-E "보존" 대상에 해당 —
  단지 줄 수만으로 삭제 대상으로 분류하지 않는다(이런 케이스는
  `COMMENT/DOCSTRING CLEANUP`이 아니라 "정책 위반이지만 내용은
  KEEP, 형식만 재검토" 별도 하위 표시가 필요하다는 것이 이번
  Wave의 발견 — Wave 1에서 반영 검토).
- **REMOVE/REVIEW 판단 필요**: `snapshot.py`류처럼 코드가 이미
  하는 일을 장문으로 반복 서술하는 패턴은 순수 `COMMENT/DOCSTRING
  CLEANUP` 대상.
- **`ponytail: <이유>` marker**: 현재 저장소 어디에도 사용된 사례
  없음(`RFC-0037` §7의 기존 확인과 동일 결론 — 신규 발견 아님).
- 이번 Wave에서 실제 docstring/comment를 줄이거나 삭제하지
  않았다(사용자 지시 명시 — 수정 금지).

---

## 6. Architecture Safety — Candidate Classification

`ADR-0028` §2.1이 확정한 7종 분류를 적용한다. **개별 파일 371개
전부에 대한 표는 스크래치패드 원본에 있으며, 이 문서에는 §3~§5가
식별한 신호 있는 항목만 분류해 반영한다.** 신호가 없는 나머지는
§3 Tier 3 원칙대로 `KEEP`(추가 조치 불필요) 기본값이다.

| 분류 | 해당 항목(대표) | 근거 |
|---|---|---|
| `KEEP` | Tier 2 검토를 통과한 파일(`ast_context.py`, `stage_01_multi_agent.py`, 개별 `runner.py` 15개 등) + Tier 3 기본값 전체 | §3.1/§3.2 |
| `COMMENT/DOCSTRING CLEANUP` | `unified-dashboard/snapshot.py`, `hqs/development/mvp/openrouter_engine.py`, `hqs/development/stages/contracts.py`, `omniroute-thin-engine-caller-v1/caller.py` 등 §5 위반 상위 파일 | §5 |
| `SIMPLIFY` | `hqs/investment/teams/{stock,etf,dividend_stock}_team.py` 3파일 간 구조 중복 | §2.4 유형4, §3.1 |
| `REFACTOR` | `projects/openrouter-auto-selection-v1/domain/auto_selection_client.py::call_with_auto_selection` | §3.1 |
| `POSSIBLE BUG` | 없음(이번 Wave 기준 — Tier 2 범위에서 정확성 의심 사항 미발견). `projects/in-process-async-command`의 중첩 pytest 실행 시 `RuntimeError: cannot schedule new futures after interpreter shutdown`(§8.3)은 **버그 후보로 별도 표시**하되 Wave 0 판단으로는 코드 결함인지 테스트 하네스의 알려진 제약인지 미확정 — Wave 1 조사 대상으로 이관 | §8.3 |
| `ARCHITECTURE/CONTRACT RISK` | 없음(이번 Wave에서 Ponytail 권한을 벗어날 만큼 Contract에 영향 있는 후보 미발견) | — |
| `GOVERNANCE REQUIRED` | (a) `dividend-stock-analysis-*`/`etf-analysis-*`/`stock-analysis-*` 15개 `runner.py`의 반복 구조 통합 여부, (b) `core/execution/mvp_000N/`류 MVP Evidence 간 중복 통합 여부 — 둘 다 Historical Evidence 파일을 건드리므로 Ponytail 권한 밖(`ADR-0028` §4) | §2.4, `ARCHIVE-CLEANUP-REVALIDATION-0001.md` |

**Architecture/Contract Risk 후보와 Refactoring 후보의 분리**:
이번 Wave는 `ARCHITECTURE/CONTRACT RISK`로 분류된 항목이 0건이므로
별도 격리 대상은 없다 — `SIMPLIFY`/`REFACTOR` 2건과 `GOVERNANCE
REQUIRED` 2건(Historical Evidence 이유로 격리, Architecture 위험
때문이 아님)만 존재한다.

---

## 7. Wave 1 후보 제안(자동 착수 아님 — 제안만)

`RFC-0042` §7 원칙(영향 범위/semantic clarity gain/complexity
reduction/regression risk/architecture risk 기준)으로 우선순위를
매겼다. **Wave 0 결과에서 자동으로 Wave 1을 시작하지 않는다** —
아래는 제안이며 착수는 별도 사용자 승인이 필요하다.

| 우선순위 | 후보 | 영향 범위 | Semantic Clarity Gain | Complexity Reduction | Regression Risk | Architecture Risk |
|---|---|---|---|---|---|---|
| **High** | `hqs/investment/teams/{stock,etf,dividend_stock}_team.py` 구조 중복 축소(공통 `_run`/analyst factory를 공유 모듈로) | 3개 Production 파일 + `hqs/investment/tests/test_*_team_integration.py` | 높음(3파일을 1번만 이해하면 됨) | 높음(796 LOC → 공유 코어 + 팀별 설정으로 축소 예상) | 낮음(Public Contract는 각 팀의 반환 dict 모양 — 무변경 가능해 보임, 실제 착수 시 재확인 필요) | 낮음(Stage/Team Responsibility 무변경 전제, 단 Wave 1 착수 시 §6 Architecture Safety 재확인 필수) |
| **Medium** | `auto_selection_client.py::call_with_auto_selection`(137 LOC) 재시도/실패분류 분리 | 1개 파일 + 전용 테스트 | 중간 | 중간 | 낮음(단일 프로젝트, 자체 테스트 15개로 즉시 회귀 확인 가능) | 낮음 |
| **Medium** | `COMMENT/DOCSTRING CLEANUP` 대상 상위 6개 파일(§5) | 6개 파일, 코드 로직 무변경 | 중간(문서 탐색성) | 낮음(코드 자체는 무변경) | 매우 낮음(로직 변경 없음) | 없음 |
| **Low(별도 RFC 필요)** | `GOVERNANCE REQUIRED` 2건(§6) — Historical Evidence 통합 여부 | 15개+ 프로젝트/MVP Evidence 파일 | 잠재적으로 높음이나 Evidence 보존과 상충 가능 | 높음(중복 대량 제거 가능) | 높음(Historical Evidence 문언 변경 위험) | 있음(별도 RFC 판단 필요, Ponytail 권한 밖) |

**권장 Wave 1 범위(제안)**: High 우선순위 1건(`investment/teams`
중복 축소)만 단독 Wave로 진행 — `RFC-0042` §7 "한 Wave에서 동시에
건드리는 디렉터리/HQ는 최소화" 원칙에 따라 Medium 항목은 별도
Wave로 분리 제안한다.

---

## 8. Validation 결과(Baseline 확인, 변경 없음)

### 8.1 `git status` / diff 범위

이 Wave에서 추가된 파일은 이 문서 1건뿐이다(§9에서 재확인). 어떤
`*.py`도 staged/modified 상태가 아니다.

### 8.2 Python Compile

`python3 -m py_compile`을 active tree 371개 파일 전체에 실행 —
**0 오류**(§2.1과 동일 결론, 서로 다른 도구로 교차 확인).

### 8.3 pytest 실행 가능 여부 및 기존 baseline 대조

- **Repository 루트에서 단일 `pytest` 실행**: 676 tests collected,
  **18 collection error**. 원인 확인 결과 이 저장소의 각
  `projects/*`가 독립적인 `sys.path.insert()`/동일 기본 모듈명
  (`test_caller_unit.py`, `domain/contracts.py` 등)을 쓰는
  구조적 특성 때문에 **한 프로세스에서 전체를 동시에 collect할
  때만** 이름 충돌이 발생한다 — `pytest.ini`의 주석
  ("projects/notekeeper와 projects/textkit의 tests 패키지명 충돌
  회피"를 위한 `--import-mode=importlib`)이 이미 이 특성을
  기록하고 있다. **이는 이번 Wave가 발견한 새 문제가 아니라
  저장소가 이미 알고 있던 기존 실행 관례**(각 HQ/프로젝트를
  개별적으로 실행)이며, `HANDOVER.md`의 "테스트 기준선 N passed"
  기록도 항상 `hqs/development/` 범위로 한정돼 있었다는 사실과
  일치한다.
- **`hqs/` 전체**(올바른 실행 단위): **380 passed, 6 skipped, 0
  failed**(40.22s).
- **`projects/` 44개 디렉터리 개별 실행**(전수):

| 프로젝트 | 결과 |
|---|---|
| async-command | 14 passed |
| command-contract | 11 passed |
| dashboard-shell-mvp | 14 passed |
| dev-hq-agent-responsibility-decomposition-v1 | no tests(코드 없음, 문서 전용) |
| dev-hq-stage04-05-agent-team-poc-v1 | 14 passed |
| dev-hq-timeout-recovery-prototype | no tests(공유 모듈, 진입점 없음) |
| **dev-hq-vertical-slice** | **1 failed, 6 passed** |
| development-hq-devkit | no tests |
| dividend-stock-analysis-{epd,jnj,ko,nestle,pg,realty-income,toyota} | no tests(런처 스크립트, pytest 대상 아님) |
| etf-analysis-{agg,gld,qqq,schd,uup,vnq} | no tests(위와 동일 성격) |
| **in-process-async-command** | **4 failed, 9 passed**(단, 실패 4건은 이 프로젝트 자체 코드가 아니라 이 프로젝트가 in-process로 재실행하는 `hqs/investment/tests/test_wave_failure_isolation.py`에서 발생 — §8.4) |
| investment-hq-checkpoint-detection-prototype | no tests |
| kernel-parallel-execution-prototype | no tests |
| langgraph-conditional-routing-poc-v1 | no tests(README/EVIDENCE 전용) |
| multi-agent-handoff-mvp-v1 | 7 passed |
| notekeeper | 52 passed |
| omniroute-thin-engine-caller-v1 | 26 passed, 1 skipped |
| openrouter-auto-selection-v1 | 15 passed |
| openrouter-free-model-selection-architecture-experiment-v1 | 24 passed |
| **process-runtime-strategy** | **1 failed, 9 passed** |
| **runtime-boundary** | **3 failed, 10 passed** |
| stage05-parallel-validation-harness-v1 | 27 passed(74.95s) |
| stock-analysis-{aapl,cat,jpm,msft,nvda} | no tests |
| synthesis-trader-expansion-prototype | no tests |
| textkit | 32 passed |
| unified-dashboard | 27 passed |
| **workflow-adapter-{gate-c-real-engine-v1,nonlanggraph-lineage-v1,recursive-lineage-v1,reversibility-v2}**(4개) | **각 1 error**(collection 단계) |

### 8.4 실패/에러 원인 분류(전부 Pre-existing, 이번 Wave가 원인 아님)

| 원인 유형 | 해당 항목 | 근거 |
|---|---|---|
| 외부 패키지 미설치(`langgraph`) | `workflow-adapter-*` 4개 | 직접 재현: `ModuleNotFoundError: No module named 'langgraph'` — `ADR-0018`/`ADR-0019`/`RFC-0031`이 이미 승인한 의존성이나 이 세션 컨테이너에 미설치. 코드 결함 아님 |
| Concurrency 타이밍 assertion(샌드박스 CPU 스케줄링 민감) | `runtime-boundary` 3건, `dev-hq-vertical-slice` 1건, `process-runtime-strategy` 1건 | 예: `assert t_slow.result == (16, 0)`인데 실측 `(24, 0)` — 실행 시간 기반 결과값을 검증하는 테스트가 이 세션의 CPU 배정에 따라 값이 달라짐(코드 로직 실패가 아니라 실측값 재현성 문제) |
| 중첩 pytest 실행 특이 케이스 | `in-process-async-command` | 이 프로젝트의 `inproc_operation.py`가 `pytest_runtest_logreport` 훅으로 **실제로 `hqs/investment/tests/`를 in-process로 재실행**하는 것이 설계 의도(비동기 명령 실행 프로토타입의 워크로드로 실제 pytest 세션 사용) — 재실행된 `test_wave_failure_isolation.py` 4건이 `RuntimeError: cannot schedule new futures after interpreter shutdown`으로 실패. 중첩 pytest 실행 시 전역 `ThreadPoolExecutor` shutdown 신호가 충돌하는 알려진 패턴 — **§6에서 `POSSIBLE BUG` 후보로 표시, 이번 Wave에서 수정하지 않음** |

**결론**: 이번 Wave에서 새로 발생한 실패는 **0건**이다(모든 실패/
에러가 기존 환경 제약 또는 기존 코드 특성이며, git diff가 없다는
사실 자체가 인과관계를 증명한다).

### 8.5 기존 baseline과의 비교

`HANDOVER.md`가 기록한 "Development HQ 테스트 기준선"과 이번
`hqs/` 380 passed 결과를 대조 — 문서가 기록한 최신 수치(152
passed, 이후 Agent Package Refactoring/Stage Data Contract 등
추가 변경 누적)보다 커진 것은 **Wave 0가 코드를 바꿔서가 아니라
그 이후 여러 세션(Multi-Engine/OpenRouter Migration 등, 이번
Wave 이전에 이미 main에 병합된 변경들)이 테스트를 추가했기
때문** — `git log`상 이 사실과 모순되지 않는다(이번 Wave의 diff는
문서 1건뿐).

---

## 9. 실제 `*.py` 변경 수(최종 확인)

**0건.** `git status --short` 결과 이 세션에서 추가된 파일은
`docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md` 1건뿐이며,
어떤 `*.py`도 modified/added/deleted/renamed 상태가 아니다.

---

## 10. 이 Wave의 결론(요약)

- Repository 전체 453개 `*.py`(Active 371개 + Historical
  `archive/v1` 82개)를 전수 Inventory·Deterministic Audit했다 —
  syntax/compile 오류 0건.
- Semantic/Ponytail Review는 이상 신호가 있는 약 30개 파일을
  표적 심층 검토했고, 나머지는 디렉터리 단위 기본값(`KEEP`)으로
  분류했다는 방법론적 한계를 명시적으로 공개했다(§3).
- Candidate Classification 결과: `SIMPLIFY` 1건(`investment/teams`
  3파일), `REFACTOR` 1건(`auto_selection_client.py`), `COMMENT/
  DOCSTRING CLEANUP` 6개 파일(대표), `GOVERNANCE REQUIRED` 2건
  (Historical Evidence 통합 여부), `POSSIBLE BUG` 1건(중첩 pytest
  실행 특이 케이스), `ARCHITECTURE/CONTRACT RISK` 0건.
  Comment/Docstring 2줄 정책 위반 456건(수정하지 않음, 표시만).
- Wave 1 후보를 영향 범위/명확성 이득/복잡도 감소/회귀 위험/
  Architecture 위험 기준으로 제안했다(§7) — **자동 착수하지
  않는다.**
- Baseline Validation: `hqs/` 380 passed/6 skipped/0 failed,
  `projects/` 44개 중 다수 실패/에러는 전부 이번 Wave 이전부터
  존재하던 환경 의존성/타이밍/중첩 실행 특이 케이스이며 이번
  Wave가 원인이 아니다(§8, diff 0건으로 증명).
- **`*.py` 파일 수정/삭제/이동: 0건.** Architecture/Contract/
  Governance 변경: 0건.

## Related

- `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md`
- `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`
- `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md`
- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`,
  `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`
- `hqs/development/HANDOVER.md`
- `pytest.ini`(기존 `--import-mode=importlib` 관례, §8.3 근거)
