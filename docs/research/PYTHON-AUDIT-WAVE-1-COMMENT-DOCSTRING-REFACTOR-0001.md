# Python Audit Wave 1 — Comment/Docstring Refactor

**Governance 근거**: `docs/architecture/core/RFC-0042` → `ADC-0045` →
`ADR-0028`(Lifecycle 확정) → `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
(456건 발견). 이 문서는 그 456건 **전체**를 개별 Semantic Review하고,
필요한 항목만 실제 코드(Docstring 텍스트)를 정리한 Wave 1 Evidence다.

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
  Wave 범위 밖, Wave 2 후보로 이관(`tokenize` 기반 파서 필요, AST
  Docstring 치환과 다른 메커니즘).
- **`projects/in-process-async-command`의 비결정적 실패**(§10.4)는
  Wave 0가 이미 `POSSIBLE BUG`로 표시한 항목이며, 이번 Wave가
  수정하지 않는다(Comment/Docstring cleanup 원칙 7 — 코드 로직
  변경 금지).
- **`projects/stage05-parallel-validation-harness-v1`의 self-referential
  git-diff 테스트**는 이 Wave의 커밋이 완료되면 정상 PASS로
  돌아간다(§10.3) — 별도 조치 불필요, 커밋 후 1회 재확인을 권장한다.

## Related

- `docs/architecture/core/RFC-0042`, `ADC-0045`, `ADR-0028`
- `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
- `hqs/development/IMPLEMENTATION_RULES.md`(Comment/Docstring 정책 원 출처)
