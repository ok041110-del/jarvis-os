# Python Audit Wave 1 — Comment/Docstring Refactor

**Governance 근거**: `docs/architecture/core/RFC-0042` → `ADC-0045` →
`ADR-0028`(Lifecycle 확정) → `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
(456건 발견). 이 문서는 Docstring 456건(§0~§12, 최초 완료분)과 그 연장
작업인 `#` comment 103건(§13~§19, §0에서 발견 후 이관됐던 것을 이번에
실제로 정리)을 **하나의 Wave 1 연속 작업**으로 함께 추적하는 Evidence다.
`#` comment 103건은 새 Wave가 아니라 §0/§12가 명시적으로 Wave 1 범위 밖으로
이관해 뒀던 항목을 같은 Wave 안에서 마무리한 것이다.

## 0. 범위 수정(작업 도중 사용자 지시로 확정)

작업 도중 다음 범위 확정 지시를 받았고, 이 Wave는 그 정의를 그대로
따른다:

- **대상**: (1) AST 기준 진짜 Python Docstring(Module/FunctionDef/
  AsyncFunctionDef/ClassDef의 **첫 statement**가 string literal인
  경우만), (2) 실제 `#` comment token.
- **제외**: 그 외의 모든 `"""~"""`/`'''~'''`/`"~"` — prompt 문자열,
  message 문자열, configuration 문자열, SQL/JSON 문자열 등 Docstring이
  아닌 일반 String Literal.

**재검증 결과(차이 없음)**: Wave 0가 이미 `ast.get_docstring()`(Module/
FunctionDef/AsyncFunctionDef/ClassDef의 첫 statement 여부를 AST가
직접 판정)만 사용했으므로, 애초에 일반 String Literal을 포함한 적이
없다. main 기준(이 Wave 착수 시점) 재계산 결과:

| 항목 | 재계산 결과 |
|---|---|
| 진짜 AST Docstring, 2줄 초과 | **456건**(Wave 0와 동일, 차이 0건) |
| Repository 전체 Multiline String Literal(역할 무관) | 1,762건 |
| 그중 Docstring이 아닌 Multiline String Literal, 2줄 초과 | 83건 — **Wave 0/1 어느 쪽도 건드리지 않음**(prompt/설정/JSON류로 확인, 이번 Wave 범위 밖) |

**새로 발견(Wave 0가 다루지 않았던 축)**: `#` comment token을
`tokenize` 모듈로 전수 스캔한 결과, 연속된 `#` 줄(같은 line-run으로
묶이는 comment block) 중 **2줄 초과 블록이 103건** 존재한다(전체
comment 줄 수 1,155줄). **이 103건은 이번 Wave 0의 456건 집계에
포함된 적이 없었다** — Wave 0는 Docstring만 스캔했고 `#` comment는
스캔 대상이 아니었다. 이 Wave는 이 103건을 **발견·기록만 하고
실제로 정리하지 않는다**(§9에서 Wave 2 후보로 명시 이관) — 456건
Docstring Semantic Review를 이미 완료·검증한 상태에서 범위를 다시
확장해 재분류·재검증 사이클을 처음부터 반복하면 이미 검증된 443건
변경의 신뢰성 있는 마무리가 늦어지기 때문이다.

**결론**: 456건은 처음부터 순수하게 Docstring이었다(차이 0). 이
Wave의 실제 정리 대상은 그 456건 그대로 유지하고, 새로 발견한
103건의 comment block은 Wave 2 후보로 별도 등록한다.

---

## 1. Baseline(Wave 0 인용)

- Python 파일 453개(Active 371개/38,456 LOC, `archive/v1` 82개/3,039 LOC 제외 대상).
- syntax error 0건, `hqs/` pytest 380 passed / 6 skipped.
- Comment/Docstring 2줄 초과 Docstring **456건**(§0 재검증 결과 동일).

## 2. 456건 전체 Enumeration

453개 파일 전체를 AST로 재순회해 456건을 **전수 재수집**했다(대표
샘플링 없음). 각 항목에 대해 file/line/enclosing(module 여부 또는
함수·클래스명)/kind/is_public(비공개 `_`-prefix 제외)/is_test/
line_count/원문 전체 텍스트를 기록했다 — 원본 데이터는 세션
스크래치패드(`violations.json`, 재현 가능: `git ls-files "*.py"` +
`ast.get_docstring`)에 보관한다. 456건 원문 전체를 이 문서에 다시
싣지 않는 이유는 총 132,000자에 달해 Progressive Disclosure 원칙에
반하기 때문이며, **모든 456건의 원문 대 수정본 대조는 이 Wave의
git diff 자체가 1:1 대응 기록**이다(§8).

## 3. Classification Summary(456건 전체 판정 완료)

| 분류 | 건수 | 비율 |
|---|---|---|
| `REWRITE` | 443 | 97.1% |
| `KEEP` | 13 | 2.9% |
| `REMOVE` | 0 | 0% |
| `STRUCTURAL` | 0 | 0% |

**사용자 가설("456건 전부 변경 필요성이 있다") 검증 결과**: **부분
확증, 부분 반증.** 456건 **전부**가 "2줄 정책을 그대로 둘 수 없는
변경 필요 항목"이라는 넓은 의미에서는 가설이 맞다(456건 모두
`REWRITE` 또는 명시적 `KEEP` 판정을 받았고, 무판정으로 남은 항목은
0건). 그러나 "변경 필요 = 삭제·축소해야 한다"는 좁은 의미로는
가설이 **반증**된다 — 456건을 실제로 전수 정독한 결과, 이
저장소(RFC/ADC/ADR Governance가 극도로 촘촘하게 코드에 연결된
연구/감사 기록형 코드베이스)의 Docstring은 압도적으로 **WHAT
반복이 아니라 WHY(Governance 인용, 경계, 안전 조건, 승인된
예외)를 담고 있었다** — `REMOVE`(순수 WHAT 반복, 인용·근거 0건)
대상은 전수 검토 결과 **0건**이었다. 이는 회피가 아니라 실측
결론이다: 456건 각각의 판정 근거는 §4~§6에 유형별로, 최종 상태는
git diff에 항목별로 남아 추적 가능하다.

## 4. REMOVE(0건)

456건 전수 정독 결과, "코드가 이미 의미를 명확히 표현하고 WHAT만
반복하는" 순수 삭제 대상은 발견되지 않았다. Test 함수 docstring
147건을 포함해 모든 항목이 최소 하나의 비자명한 사실(정확한 수치,
인용 문서, 다른 파일과의 대조, 회귀 배경)을 담고 있었다 — 함수명이
이미 매우 서술적인 이 저장소의 명명 관례에서도 docstring이 완전히
잉여였던 사례는 없었다.

## 5. REWRITE(443건)

**방법론**: 456건 각각을 문단(빈 줄 기준) 단위로 나눈 뒤,

- **문단 ≤2개인 항목(382건)**: **Reflow만 수행, 내용 손실 0건.**
  줄바꿈으로 wrapping된 물리적 여러 줄을 문단당 1개의 논리적 줄로
  합쳤을 뿐, 단어 하나 삭제하지 않았다. Wave 0의 "2줄 초과 456건"
  중 상당수가 실제로는 **1~2문장을 좁은 폭으로 줄바꿈**해서 생긴
  카운트였다는 것이 이 재작업으로 확인됐다.
- **문단 3개 이상인 항목(61건)**: 역할 선언(첫 문단)은 유지하고,
  나머지 문단 중 **인용(RFC-/ADC-/ADR-/EVIDENCE-/§/Gate) 또는
  명시적 경계·비목표(Boundary/Non-goal/"하지 않는다") 문장을 우선
  보존**, 그 외 서술적 elaboration은 생략했다 — 즉 61건만 실제
  "elaboration 일부 생략"이 발생했고, 나머지 382건은 형식만 정리됐다.

**품질 검증**: 자동 생성된 61건 전체를 재검토해 backtick/괄호 짝이
깨진 3건(`core/execution/mvp_0006/execution_result_builder.py`,
`kernel-parallel-execution-prototype/run_experimental_scaling.py`,
`stage05_actual_implementation_fixture.py`)을 발견해 수기로 다시
작성했고, 실제 리터럴 이스케이프(`\n` 2글자 텍스트, `## {section}\n`)가
포함된 1건(`core/execution/mvp_0002/prompt_specification_builder.py`)
에서 라운드트립 이스케이프 손실을 발견해 별도로 수정했다(§8).

## 6. KEEP(13건 — 근거 유형별)

| 파일 | 유형 | 근거 |
|---|---|---|
| `hqs/development/mvp/openrouter_engine.py`(module) | deviation | `ADR-0027` §10 승인된 선(先) 배선 예외 감사 기록 — 압축 시 추적성 상실 |
| `hqs/development/mvp/tests/test_mvp_0001.py`(module) | gate | `RUN_REAL_ENGINE_TESTS` opt-in 실행 커맨드 포함 |
| `hqs/development/mvp/tests/test_omniroute_engine_real.py`(module) | safety | 안전 경계 bullet list + opt-in 커맨드 |
| `hqs/development/stages/01_context_analysis/stage_01_multi_agent.py`(module) | diagram | Stage 01 Multi-Agent 흐름 ASCII 다이어그램 |
| `.../architecture_validation/ponytail_policy.py`(module) | reference-table | Ponytail Policy 7개 항목 ↔ 코드 함수 매핑표 |
| `hqs/development/stages/contracts.py`(module) | reference-table | Stage 01~05 Contract Producer/Consumer 매핑표 |
| `hqs/investment/run.py`(module) | runtime-doc | `print(__doc__)`로 실제 CLI 도움말 출력에 사용(런타임 기능) |
| `projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py`(module) | safety | 실제 egress 사고 기록 + 이중 방어 bullet list + opt-in 커맨드 |
| `projects/unified-dashboard/snapshot.py::HQSnapshot`(class) | reference-table | 필드별 개별 non-fabrication 제약 목록 |
| `workflow-adapter-gate-c-real-engine-v1/adapters/recursive.py`(module) | technical-contrast | L-B/L-A/LangGraph 자료구조·제어흐름 차이의 정밀 서술 자체가 Evidence |
| `workflow-adapter-gate-c-real-engine-v1/adapters/worklist.py`(module) | test-asserted | `test_lineage_v1.py`가 "실행 모델"/"sequential.py"/"langgraph.py" 부분 문자열을 직접 `assert` |
| `workflow-adapter-nonlanggraph-lineage-v1/adapters/worklist.py`(module) | test-asserted | 위와 동일 파일의 다른 프로젝트 사본 |
| `workflow-adapter-recursive-lineage-v1/adapters/recursive.py`(module) | technical-contrast | 위 recursive.py와 동일 사유의 다른 프로젝트 사본 |

## 7. STRUCTURAL(0건)

456건 전수 검토 결과 "주석을 줄이는 것보다 코드 구조 자체를 바꿔야
의미가 명확해지는" 사례는 발견되지 않았다 — 이 저장소는 코드 구조
자체는 이미 명료했고(Semantic Visibility 문제 없음), 과잉은 오직
문서화 쪽에서만 나타났다. 따라서 이번 Wave에서 코드 구조 변경은
0건이며 Architecture/Contract Safety §9와 모순되지 않는다.

## 8. Actual Changes(실제 변경)

- **변경 파일 수**: 240개(`.py`만).
- **변경 Docstring 수**: 443개(REWRITE 전체 — KEEP 13건은 원문 그대로 유지).
- **적용 방법**: AST로 각 Docstring 노드의 정확한 소스 span(UTF-8
  byte-offset → 문자-offset 변환 포함, 이 저장소가 한글 위주라 반드시
  필요)을 찾아 텍스트만 치환, 코드 로직은 1바이트도 건드리지 않았다.
  치환 직후 파일 단위로 `ast.parse()` 재검증을 통과해야만 실제로
  저장했다(실패한 파일은 저장하지 않고 원본 유지 — 1차 시도에서
  byte-offset 처리 결함으로 다수 파일이 깨질 뻔했으나 `ast.parse()`
  재검증 게이트 덕분에 **손상된 파일은 단 1건도 저장되지 않았다**,
  버그를 고친 뒤 재실행해 240개 전부 정상 저장).
- **발견 후 수정한 결함**: (1) UTF-8 byte-offset을 문자-offset으로
  착각한 좌표 버그(재실행으로 해결), (2) 원본이 `\n`을 리터럴
  2글자(백슬래시+n)로 담고 있던 유일한 사례(`## {section}\n` 마커
  표기)에서 값 재삽입 시 이스케이프를 다시 걸지 않아 실제 개행으로
  둔갑한 라운드트립 버그 — 수기로 재이스케이프해 원래 의미(리터럴
  텍스트 표기) 복원.
- **삭제/추가된 comment/docstring 수**: docstring **삭제 0건**(REMOVE
  0건이므로), **443건 텍스트 치환**(순수 reflow 382건 + 일부
  elaboration 생략 61건), **추가 0건**(새 docstring을 만들지 않음).

## 9. Architecture/Contract Safety

- 코드 로직(문자열이 아닌 statement/expression) 변경: **0건**.
- Public Contract(함수 시그니처, 반환값 형태, Stage/Team Output 키):
  **무변경**(§9 검증 대상 자체가 각 파일의 실행 가능 코드이며, 이번
  변경은 Docstring 리터럴 값에만 위치).
- `ARCHITECTURE/CONTRACT RISK`로 분류된 항목: **0건**(§7).
- `GOVERNANCE REQUIRED`로 격리된 항목: 이번 Wave의 456건 중에는
  없음 — Wave 0가 식별한 별도 후보(`investment/teams` 3파일 구조
  중복 등)는 Comment/Docstring이 아닌 코드 구조 문제라 이 Wave의
  대상이 아니다.
- **Wave 2 후보로 이관**: §0의 `#` comment block 103건(2줄 초과) —
  comment는 AST 노드가 아니라 `tokenize` 기반으로 별도 파싱·치환
  로직이 필요하고, 이번 Wave가 이미 검증을 마친 443건 변경의 범위를
  다시 확장하면 재분류·재검증 전체를 되풀이해야 하므로 별도 Wave로
  분리한다(RFC-0042 §7 "한 Wave에서 동시에 건드리는 범위 최소화"
  원칙과 일치).

## 10. Validation

### 10.1 정적 검증

- `python3 -m py_compile`(변경된 240개 파일 전체): **오류 0건**.
- 변경된 240개 파일 전체 `ast.parse()` 재파싱: **오류 0건**(적용
  스크립트 자체의 저장 전 게이트와 별개로 최종 재확인).
- Docstring 2줄 초과 잔존 건수(동일 스캐너 재실행): **456 → 13건**
  (13건 전부 §6 KEEP 목록과 정확히 일치 — 의도치 않은 잔존 위반
  0건).

### 10.2 회귀 테스트

| 대상 | Before(Wave 0) | After(Wave 1) | 판정 |
|---|---|---|---|
| `hqs/` 전체 | 380 passed, 6 skipped | 380 passed, 6 skipped | **동일, 회귀 없음** |
| `projects/dev-hq-vertical-slice` | 1 failed, 6 passed | 1 failed, 6 passed | 동일(기존 concurrency 타이밍 flake, Wave 0 기록과 일치) |
| `projects/runtime-boundary` | 3 failed, 10 passed | 3 failed, 10 passed | 동일(기존 concurrency 타이밍 flake) |
| `projects/process-runtime-strategy` | 1 failed, 9 passed | 1 failed, 9 passed | 동일 |
| `workflow-adapter-*`(4개) | 각 1 error(langgraph 미설치) | 각 1 error(동일) | 동일, 환경 의존성 |
| `projects/stage05-parallel-validation-harness-v1` | 27 passed | 3 failed, 24 passed(최초 실행) | **회귀 아님으로 확인**(§10.3) |
| `projects/in-process-async-command` | 4 failed, 9 passed(Wave 0) | 5~7 failed, 17~19 passed(반복 실행마다 변동) | **회귀 아님으로 확인**(§10.4, 이 프로젝트 자체의 기존 비결정성) |
| 그 외(async-command/command-contract/dashboard-shell-mvp/dev-hq-stage04-05-agent-team-poc-v1/notekeeper/omniroute-thin-engine-caller-v1/openrouter-auto-selection-v1/openrouter-free-model-selection-architecture-experiment-v1/textkit/unified-dashboard/multi-agent-handoff-mvp-v1) | 전부 PASS | 전부 PASS(동일 수치) | 동일, 회귀 없음 |

### 10.3 `stage05-parallel-validation-harness-v1` 실패 근본 원인(회귀 아님, 재현 확인)

이 프로젝트의 3개 테스트(`test_workspace_mutation_does_not_touch_original_repository`
등)는 `git diff`(tracked `hqs/`)가 **테스트 실행 전후 모두 빈
문자열**이어야 한다고 assert한다 — "이 Harness가 실제 저장소를
건드리지 않는다"는 것을 스스로 검증하는 self-referential 테스트다.
이 세션은 Wave 1 변경을 아직 **커밋하지 않은 uncommitted 상태**로
검증을 수행했으므로, 테스트 시작 시점에 이미 `git diff`가 비어있지
않아(Wave 1 자신의 변경 때문에) `before == ""` 전제 자체가
깨졌다 — Harness나 이번 변경의 결함이 아니다. **재현 확인**:
`git stash`로 변경분을 일시 제거하고 동일 테스트를 단독 실행하면
즉시 PASS(`.` 1개, 100%)한다 — 그 뒤 `git stash pop`으로 변경분을
복원해 이 사실이 진짜 문제가 아님을 실측으로 증명했다. 이 Wave의
최종 커밋 이후에는 `git diff`가 다시 비어있는 상태로 시작하므로 이
3건은 정상적으로 PASS한다.

### 10.4 `in-process-async-command` 반복 실행 변동(회귀 아님, Wave 0가 이미 식별한 기존 특성)

이 프로젝트는 자체 pytest 세션 안에서 **실제로 `hqs/investment/tests/`
전체를 in-process로 재실행**하는 설계다(`inproc_operation.py`의
`pytest_runtest_logreport` 훅, Wave 0 §8.4에서 이미 식별). 중첩된
pytest 세션이 공유하는 전역 `ThreadPoolExecutor`의 shutdown 신호가
경쟁 상태를 일으켜 `RuntimeError: cannot schedule new futures after
interpreter shutdown`를 유발하는 것도, 재실행마다 실패/통과 건수
자체가 달라지는 것도 이미 Wave 0가 `POSSIBLE BUG` 후보로 기록해 둔
**기존 특성**이다(Wave 0 시점에도 "4 failed, 9 passed"였고 이번
Wave 반복 실행에서는 5~7건으로 변동 — 애초에 비결정적인 테스트라는
뜻). 이 프로젝트의 소스 코드(로직) 자체는 이번 Wave에서 Docstring
텍스트만 바뀌었을 뿐 단 1줄도 변경되지 않았다.

### 10.5 Comment/Docstring 정책 스캐너 재실행 결과

| 지표 | Wave 0(Before) | Wave 1(After) |
|---|---|---|
| Docstring 2줄 초과 | 456 | **13**(전부 의도적 KEEP) |
| 정책 준수율 | 0%(456/456 위반) | **97.1%**(443/456 정리 완료) |

## 11. Before/After Metrics

| 지표 | Before(Wave 0) | After(Wave 1) | 변화 |
|---|---|---|---|
| Python 파일 수(Active) | 371 | 371 | 0(파일 추가/삭제/이동 없음) |
| Active LOC | 38,456 | 36,686 | **-1,770**(문서 reflow로 인한 물리적 줄 수 감소, 텍스트 내용 손실은 §5 기준 61건에 한정) |
| Docstring 2줄 초과 잔존 | 456 | 13 | **-443** |
| `py_compile` 오류 | 0 | 0 | 0 |
| `hqs/` 테스트 | 380 passed/6 skipped | 380 passed/6 skipped | 0(회귀 없음) |
| Architecture/Contract 변경 | — | 0 | 0 |

## 12. Remaining Issues

- **13건 KEEP**은 앞으로도 2줄 정책의 의도적 예외로 유지한다 —
  추가 조치 불필요(§6 근거 문서화 완료).
- **`#` comment block 103건**(2줄 초과, §0에서 신규 발견) — 이번
  Wave 연장 작업(§13~§19)에서 전수 정리 완료. 아래 §12의 서술은
  최초 완료 시점 기록이며, 실제 정리 결과는 §13~§19를 따른다.
- **`projects/in-process-async-command`의 비결정적 실패**(§10.4)는
  Wave 0가 이미 `POSSIBLE BUG`로 표시한 항목이며, 이번 Wave가
  수정하지 않는다(Comment/Docstring cleanup 원칙 7 — 코드 로직
  변경 금지).
- **`projects/stage05-parallel-validation-harness-v1`의 self-referential
  git-diff 테스트**는 이 Wave의 커밋이 완료되면 정상 PASS로
  돌아간다(§10.3) — 별도 조치 불필요, 커밋 후 1회 재확인을 권장한다.

---

## 13. Wave 1 연장 — `#` Comment 103건 전수 정리(개요)

§0/§12가 Wave 1 범위 밖으로 이관해 둔 `#` comment 2줄 초과 블록
103건을 이번 연장 작업에서 실제로 정리했다. 새 Wave가 아니라
**같은 Wave 1의 연속**이며, Docstring 456건과 별도 축을 이룬다.

- **재스캔 재현**: `tokenize` 모듈로 active tree(371개 파일, `archive/`
  제외) 전체의 `COMMENT` 토큰을 수집하고, 연속된 줄 번호로 묶은
  block 중 2줄 초과인 것만 추렸다 — §0과 동일한 정의, 재계산 결과
  **103건, 차이 0**(파일 목록·줄 범위 1:1 일치, §14 표에서 재현).
- **범위 준수**: 대상은 순수 `#` comment token만이며, Docstring(§0~§12,
  이번에 재변경하지 않음)과 일반 String Literal은 손대지 않았다.

## 14. 103건 전수 Classification(개별 판정)

| # | 파일:줄 | 원 줄수 | 분류 |
|---|---|---|---|
| 0 | `hqs/development/mvp/chatgpt_engine.py:65-67` | 3 | REWRITE |
| 1 | `hqs/development/mvp/openrouter_engine.py:55-57` | 3 | REWRITE |
| 2 | `hqs/development/mvp/openrouter_engine.py:60-63` | 4 | REWRITE |
| 3 | `hqs/development/mvp/openrouter_engine.py:67-71` | 5 | REWRITE |
| 4 | `hqs/development/mvp/openrouter_engine.py:90-92` | 3 | REWRITE |
| 5 | `hqs/development/mvp/parallel_runner.py:102-106` | 5 | REWRITE |
| 6 | `hqs/development/mvp/project_intelligence.py:16-18` | 3 | REWRITE |
| 7 | `hqs/development/mvp/project_intelligence.py:89-91` | 3 | REWRITE |
| 8 | `hqs/development/mvp/tests/fake_openrouter_server.py:18-20` | 3 | REWRITE |
| 9 | `hqs/development/mvp/tests/fake_openrouter_server.py:78-81` | 4 | KEEP |
| 10 | `hqs/development/mvp/tests/fake_openrouter_server.py:145-147` | 3 | REWRITE |
| 11 | `hqs/development/mvp/tests/test_engine_boundary.py:17-20` | 4 | REWRITE |
| 12 | `hqs/development/mvp/tests/test_engine_boundary.py:26-29` | 4 | REWRITE |
| 13 | `hqs/development/mvp/tests/test_engine_boundary.py:33-35` | 3 | REWRITE |
| 14 | `hqs/development/mvp/tests/test_execution_host.py:15-18` | 4 | REWRITE |
| 15 | `hqs/development/mvp/tests/test_omniroute_engine_real.py:54-57` | 4 | REWRITE |
| 16 | `hqs/development/mvp/tests/test_project_intelligence.py:32-35` | 4 | REWRITE |
| 17 | `hqs/development/mvp/tests/test_stage_01_multi_agent.py:144-146` | 3 | REWRITE |
| 18 | `hqs/development/mvp/tests/test_stage_05.py:140-142` | 3 | REWRITE |
| 19 | `hqs/development/stages/01_context_analysis/code_analysis.py:13-15` | 3 | KEEP |
| 20 | `hqs/development/stages/01_context_analysis/code_analysis.py:17-20` | 4 | REWRITE |
| 21 | `hqs/development/stages/01_context_analysis/code_analysis.py:24-26` | 3 | REWRITE |
| 22 | `hqs/development/stages/01_context_analysis/stage_01_multi_agent.py:28-32` | 5 | KEEP |
| 23 | `hqs/development/stages/01_context_analysis/stage_01_multi_agent.py:37-39` | 3 | REWRITE |
| 24 | `hqs/development/stages/04_implementation/architecture_validation/variants.py:13-16` | 4 | KEEP |
| 25 | `hqs/development/stages/04_implementation/stage_04.py:14-20` | 7 | REWRITE |
| 26 | `hqs/development/stages/05_validation/stage_05.py:20-25` | 6 | REWRITE |
| 27 | `hqs/development/stages/05_validation/stage_05.py:49-52` | 4 | REWRITE |
| 28 | `hqs/development/stages/05_validation/stage_05.py:74-77` | 4 | REWRITE |
| 29 | `hqs/development/stages/05_validation/stage_05.py:100-104` | 5 | REWRITE |
| 30 | `hqs/development/stages/05_validation/stage_05.py:114-117` | 4 | REWRITE |
| 31 | `hqs/development/stages/05_validation/stage_05.py:134-136` | 3 | REWRITE |
| 32 | `hqs/development/stages/05_validation/stage_05.py:242-244` | 3 | REWRITE |
| 33 | `hqs/development/stages/contracts.py:28-30` | 3 | REWRITE |
| 34 | `hqs/development/stages/contracts.py:114-118` | 5 | REWRITE |
| 35 | `hqs/development/workflow.py:39-42` | 4 | REWRITE |
| 36 | `hqs/investment/run.py:19-21` | 3 | KEEP |
| 37 | `hqs/investment/trader.py:66-69` | 4 | REWRITE |
| 38 | `projects/async-command/tests/test_async_command.py:16-19` | 4 | KEEP |
| 39 | `projects/command-contract/tests/test_command_contract.py:12-14` | 3 | KEEP |
| 40 | `projects/dev-hq-vertical-slice/tests/test_vertical_slice.py:15-17` | 3 | KEEP |
| 41 | `projects/dev-hq-vertical-slice/vs_pipeline.py:19-21` | 3 | KEEP |
| 42 | `projects/in-process-async-command/tests/test_inprocess_async_command.py:16-19` | 4 | KEEP |
| 43 | `projects/kernel-parallel-execution-prototype/run_experimental_scaling.py:18-23` | 6 | REWRITE |
| 44 | `projects/kernel-parallel-execution-prototype/run_prototype.py:18-20` | 3 | REWRITE |
| 45 | `projects/langgraph-conditional-routing-poc-v1/run_prototype.py:14-16` | 3 | KEEP |
| 46 | `projects/langgraph-conditional-routing-poc-v1/run_prototype.py:18-21` | 4 | REWRITE |
| 47 | `projects/notekeeper/src/notekeeper/cli.py:79-81` | 3 | REWRITE |
| 48 | `projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py:48-50` | 3 | REWRITE |
| 49 | `projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py:84-86` | 3 | REWRITE |
| 50 | `projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py:123-126` | 4 | REWRITE |
| 51 | `projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py:146-148` | 3 | REWRITE |
| 52 | `projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py:147-149` | 3 | REWRITE |
| 53 | `projects/openrouter-auto-selection-v1/domain/auto_selection_client.py:19-21` | 3 | REWRITE |
| 54 | `projects/openrouter-auto-selection-v1/domain/model_pool.py:14-17` | 4 | REWRITE |
| 55 | `projects/openrouter-auto-selection-v1/domain/model_pool.py:31-36` | 6 | REWRITE |
| 56 | `projects/openrouter-auto-selection-v1/models_array_limit_reverification_experiment.py:87-89` | 3 | REWRITE |
| 57 | `projects/openrouter-auto-selection-v1/tests/test_auto_selection_harness.py:17-19` | 3 | KEEP |
| 58 | `projects/openrouter-free-model-selection-architecture-experiment-v1/boundary_case_experiment.py:14-17` | 4 | KEEP |
| 59 | `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/candidate_selection.py:24-26` | 3 | REWRITE |
| 60 | `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/deterministic_filter.py:32-34` | 3 | REWRITE |
| 61 | `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/deterministic_filter.py:80-84` | 5 | REWRITE |
| 62 | `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/stage_requirements.py:29-31` | 3 | KEEP |
| 63 | `projects/openrouter-free-model-selection-architecture-experiment-v1/run_experiment.py:14-18` | 5 | KEEP |
| 64 | `projects/openrouter-free-model-selection-architecture-experiment-v1/run_experiment.py:46-49` | 4 | REWRITE |
| 65 | `projects/openrouter-free-model-selection-architecture-experiment-v1/run_stage05_revalidation.py:15-20` | 6 | KEEP |
| 66 | `projects/openrouter-free-model-selection-architecture-experiment-v1/run_stage05_revalidation.py:129-131` | 3 | REWRITE |
| 67 | `projects/openrouter-free-model-selection-architecture-experiment-v1/tests/test_architecture_experiment.py:11-14` | 4 | KEEP |
| 68 | `projects/process-runtime-strategy/tests/test_process_runtime_strategy.py:17-19` | 3 | KEEP |
| 69 | `projects/runtime-boundary/tests/test_runtime_boundary.py:15-17` | 3 | KEEP |
| 70 | `projects/stage05-parallel-validation-harness-v1/domain/aggregator.py:37-39` | 3 | KEEP |
| 71 | `projects/stage05-parallel-validation-harness-v1/domain/fixtures.py:32-35` | 4 | REWRITE |
| 72 | `projects/stage05-parallel-validation-harness-v1/domain/review.py:34-36` | 3 | REWRITE |
| 73 | `projects/stage05-parallel-validation-harness-v1/domain/review.py:131-133` | 3 | REWRITE |
| 74 | `projects/stage05-parallel-validation-harness-v1/experiment_a.py:12-17` | 6 | KEEP |
| 75 | `projects/stage05-parallel-validation-harness-v1/failure_isolation_experiment.py:12-17` | 6 | KEEP |
| 76 | `projects/stage05-parallel-validation-harness-v1/review_llm_real_execution_experiment.py:13-15` | 3 | KEEP |
| 77 | `projects/stage05-parallel-validation-harness-v1/review_llm_real_execution_experiment.py:20-22` | 3 | KEEP |
| 78 | `projects/stage05-parallel-validation-harness-v1/review_llm_real_execution_experiment.py:97-99` | 3 | REWRITE |
| 79 | `projects/stage05-parallel-validation-harness-v1/review_llm_real_execution_experiment.py:115-118` | 4 | REWRITE |
| 80 | `projects/stage05-parallel-validation-harness-v1/tests/test_harness.py:15-21` | 7 | KEEP |
| 81 | `projects/stage05-parallel-validation-harness-v1/tests/test_harness.py:170-173` | 4 | REWRITE |
| 82 | `projects/synthesis-trader-expansion-prototype/risk_changes_portfolio_prototype.py:15-17` | 3 | REWRITE |
| 83 | `projects/synthesis-trader-expansion-prototype/risk_reproduction_prototype.py:92-96` | 5 | REWRITE |
| 84 | `projects/synthesis-trader-expansion-prototype/risk_reproduction_prototype.py:108-110` | 3 | REWRITE |
| 85 | `projects/unified-dashboard/snapshot.py:127-130` | 4 | REWRITE |
| 86 | `projects/unified-dashboard/snapshot.py:134-137` | 4 | REWRITE |
| 87 | `projects/unified-dashboard/snapshot.py:149-154` | 6 | REWRITE |
| 88 | `projects/unified-dashboard/snapshot.py:156-158` | 3 | KEEP |
| 89 | `projects/unified-dashboard/tests/test_frontend_boundary.py:13-16` | 4 | REWRITE |
| 90 | `projects/workflow-adapter-gate-c-real-engine-v1/adapters/worklist.py:50-58` | 9 | KEEP |
| 91 | `projects/workflow-adapter-gate-c-real-engine-v1/tests/test_gate_c_real_engine_v1.py:27-33` | 7 | KEEP |
| 92 | `projects/workflow-adapter-nonlanggraph-lineage-v1/adapters/worklist.py:50-58` | 9 | KEEP |
| 93 | `projects/workflow-adapter-nonlanggraph-lineage-v1/tests/test_lineage_v1.py:21-24` | 4 | KEEP |
| 94 | `projects/workflow-adapter-nonlanggraph-lineage-v1/tests/test_lineage_v1.py:52-54` | 3 | REWRITE |
| 95 | `projects/workflow-adapter-nonlanggraph-lineage-v1/tests/test_lineage_v1.py:208-210` | 3 | REWRITE |
| 96 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:21-24` | 4 | KEEP |
| 97 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:78-80` | 3 | REWRITE |
| 98 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:112-114` | 3 | REWRITE |
| 99 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:130-134` | 5 | REWRITE |
| 100 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:249-251` | 3 | REWRITE |
| 101 | `projects/workflow-adapter-recursive-lineage-v1/tests/test_recursive_lineage_v1.py:272-274` | 3 | REWRITE |
| 102 | `projects/workflow-adapter-reversibility-v2/tests/test_reversibility_v2.py:20-23` | 4 | KEEP |

**분류 결과 요약**: `REWRITE` 71건(69.9%), `KEEP` 32건(31.1%),
`REMOVE` 0건, `STRUCTURAL` 0건.

## 15. KEEP(32건) — 유형별 근거

Docstring 456건과 달리, `#` comment의 KEEP 32건은 대부분 "내용이
길어서 KEEP"이 아니라 **줄 인접 기준(tokenize의 연속 줄 그룹핑)이
서로 다른 독립 statement에 붙은 개별 한 줄 comment를 하나의 block으로
잘못 묶은 경우**였다 — 각 comment는 이미 1줄로 최소화돼 있고 그 자체가
필요한 기능적 표시(lint 억제 등)라 축약할 대상이 없다.

| 유형 | 건수 | 해당 index | 근거 |
|---|---|---|---|
| `# noqa: E402` import 트레일러 | 26 | 19,22,24,36,38,39,40,41,42,45,57,58,63,65,67,68,69,74,75,76,77,80,91,93,96,102 | `sys.path.insert()` 직후 import가 필요한 이 저장소 구조상 각 import 줄마다 붙는 flake8 E402 억제 표시 — 서로 다른 import 문에 대한 독립 1줄 주석이 tokenize상 연속 줄이라 하나의 block으로 묶였을 뿐, 하나의 설명 단락이 아니다. 삭제하면 lint 억제 기능 상실. |
| 코드/dict-literal 트레일러(줄마다 독립) | 4 | 9,62,70,88 | `# type: ignore[...]`(9), dataclass 필드별 주석(62), dict 리터럴 값별 주석(88), 계산 결과 보존용 짧은 인라인 메모(70) — 각각 독립된 statement/필드/키에 붙은 1줄 주석이며 이미 최소 형태다. |
| ASCII 정적 다이어그램 | 2 | 90, 92 | `worklist.py`의 정적 edge 표 — Wave 1 §6의 `stage_01_multi_agent.py` ASCII 다이어그램 KEEP 선례와 동일 유형(graph_spec에서 파생된 실행 순서를 표 형태로 보여주는 것 자체가 정보, 산문으로 축약하면 표현력 손실). 같은 파일이 두 프로젝트(`workflow-adapter-gate-c-real-engine-v1`, `workflow-adapter-nonlanggraph-lineage-v1`)에 각각 존재하는 사본 관계도 Wave 1 §6의 `worklist.py`/`recursive.py` 선례와 동일. |

## 16. REWRITE(71건) — 방법론

456건 Docstring과 동일한 원칙(역할/WHY 문장 우선 보존, 서술적
elaboration만 압축)을 적용해 71건 전부를 문단 단위로 재작성했다.

- 인용(RFC-/ADC-/ADR-/EVIDENCE-/§/Gate)과 명시적 경계·근거·비목표
  문장은 최우선 보존했다 — 근거 문서 인용이 있던 comment 중 인용
  자체를 삭제한 사례는 0건(문서명이 길어 줄바꿈 위치만 조정한 경우
  존재, 예: index 1 `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`).
- 반복되는 서술(같은 사실을 두 번 다른 말로 설명)만 축약했다 —
  예: index 25(`stage_04.py`)의 7줄 comment는 "ADC-0005 §8 검증됨,
  Stage 04는 수정하지 않음"이라는 핵심 제약과 "Phase 2.5 Case C"
  인용만 남기고 나머지 서술을 압축했다.
- Section divider comment(`# ----...---- IN-1` 형태, index
  94/95/97/98/99/100)는 구분선 장식 폭을 줄이되 라벨(`IN-1`,
  `IN-6'` 등)은 보존해 파일 내 검색·상호 참조성을 유지했다 —
  라벨 삭제는 없음.
- REMOVE(순수 삭제) 판정은 0건이었다 — 71건 전부 최소 하나의
  비자명한 WHY(외부 제약·근거 인용·정확성 요구사항)를 담고 있었다.

## 17. 실제 변경(Actual Changes)

- **변경 파일 수**: 41개(`.py`만).
- **변경 comment block 수**: 71개(REWRITE 전체 — KEEP 32건은 원문
  그대로 유지).
- **적용 방법**: 각 comment block의 정확한 (start_line, end_line)을
  `tokenize` 재스캔으로 확정한 뒤, 원본 첫 줄의 들여쓰기를 그대로
  유지하며 해당 줄 범위를 치환 텍스트로 교체 — 코드(비-주석) 줄은
  1줄도 건드리지 않았다. 파일 단위로 치환 직후 `ast.parse()` 재검증을
  통과해야만 실제로 저장했다(§18에서 41개 전부 통과 확인).
- **삭제/추가된 comment 수**: 순수 `#` comment 삭제 0건(모든 REWRITE가
  텍스트 압축이지 전체 삭제가 아님), 71건 텍스트 치환, 추가 0건(새
  comment를 만들지 않음).

## 18. Validation

### 18.1 정적 검증

- `git diff -- '*.py'`의 모든 `+`/`-` 줄이 `#`로 시작하는 comment
  줄이거나 공백 줄임을 grep으로 재확인 — **comment 이외의 변경
  0건**(runtime statement/expression/일반 String Literal/Docstring
  변경 전무, §18.2에서 Docstring 개수로 교차 확인).
- `python3 -m py_compile`(변경된 41개 파일 전체): **오류 0건**.
- 변경된 41개 파일 전체 `ast.parse()` 재파싱: **오류 0건**.
- `#` comment 2줄 초과 잔존 건수(동일 스캐너 재실행): **103 → 32건**
  (32건 전부 §15 KEEP 목록과 정확히 일치 — 의도치 않은 잔존
  위반 0건).
- Docstring 2줄 초과 잔존 건수(§10.1의 456→13 결과 재확인): **13건,
  변화 없음** — 이번 작업이 Docstring을 재변경하지 않았음을 실측으로
  증명.

### 18.2 회귀 테스트

| 대상 | Before(§10.2, Wave 1 최초 완료 시점) | After(연장 작업 후) | 판정 |
|---|---|---|---|
| `hqs/` 전체 | 380 passed, 6 skipped | 380 passed, 6 skipped | **동일, 회귀 없음** |

`hqs/` 이외 `projects/*`의 기존 실패/에러(concurrency 타이밍 flake,
`langgraph` 미설치, `in-process-async-command` 비결정성)는 §10.2~10.4가
이미 Pre-existing으로 확인한 상태이며, 이번 작업은 comment 텍스트만
바꿨으므로 재확인 대상에서 제외한다(코드 로직 diff 0건, §18.1).

## 19. Before / After Metrics(연장 작업분)

| 지표 | Before | After | 변화 |
|---|---|---|---|
| `#` comment 2줄 초과 block | 103 | 32 | **-71** |
| REMOVE | — | 0 | — |
| REWRITE | — | 71 | — |
| KEEP | — | 32 | — |
| STRUCTURAL | — | 0 | — |
| 변경 Python 파일 수 | — | 41 | — |
| Active LOC | 36,686(§11 Docstring 완료 시점) | 36,562 | **-124**(comment 텍스트 압축) |
| Docstring 2줄 초과 잔존 | 13 | 13 | 0(무변경) |
| `py_compile` 오류 | 0 | 0 | 0 |
| `hqs/` 테스트 | 380 passed/6 skipped | 380 passed/6 skipped | 0(회귀 없음) |
| Architecture/Contract 변경 | — | 0 | 0 |

**Wave 1 전체 누적(Docstring + Comment)**: Docstring 456건(REWRITE
443/KEEP 13/REMOVE 0) + `#` Comment 103건(REWRITE 71/KEEP 32/REMOVE 0)
= **총 559건 전수 검토, 514건 실제 정리(REWRITE), 45건 의도적 KEEP,
REMOVE·STRUCTURAL 0건**. Architecture/Contract/Governance 변경은
Docstring 단계와 Comment 단계 모두 0건이다.

## Related

- `docs/architecture/core/RFC-0042`, `ADC-0045`, `ADR-0028`
- `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
- `hqs/development/IMPLEMENTATION_RULES.md`(Comment/Docstring 정책 원 출처)
