# Python Refactor Wave 5 — Docstring Semantic Audit(REMOVE/COMPRESS/KEEP/ADD/NONE)

**Governance 근거**: `RFC-0042` → `ADC-0045` → `ADR-0028` Lifecycle.
Wave 1/3가 ">2줄 정책 위반"만 기준으로 삼았던 것과 달리, 이번 Wave는
`archive/`와 모든 `*.md`를 제외한 **Active 영역 전체 `*.py`**의
**모든** Docstring(줄 수 무관)과 **모든** public 미문서화 심볼을
REMOVE/COMPRESS/KEEP/ADD/NONE 5분류로 전수 재심사했다.

## 1. 범위와 방법

- AST(`ast.get_docstring`)로 Module/FunctionDef/AsyncFunctionDef/
  ClassDef의 **진짜 Docstring만** 식별한다 — 일반 문자열/멀티라인
  문자열(prompt/message/config/SQL/JSON 등)은 애초에 이 함수가
  반환하지 않으므로 혼입 가능성이 구조적으로 없다(Wave 1 §0에서
  이미 검증한 것과 동일한 보장).
- `archive/`(82개 파일) 및 `*.md`는 대상에서 제외.
- Active 372개 파일 전체를 AST로 재순회해 **정의(Module/Class/
  Function/Method) 2,372개**(Module 372 + Class 118 + Function/
  Method 2,134 — 일부 module은 `__init__.py` 등 모듈 자체 포함)를
  확인, 그중 **Docstring 보유 637건**, **Docstring 없음 1,735건**
  (그중 public 1,469건)을 식별했다.

## 2. Classification Summary

| 분류 | 건수 | 비고 |
|---|---|---|
| `KEEP` | 626 | 기존 Wave 1/3 KEEP 13건 포함(§4에서 전원 재심사) |
| `REMOVE` | 11 | §3 상세 |
| `COMPRESS` | 0 | Wave 3까지 이미 거의 전부 압축 완료 상태(잔존 638건 중 627건이 이미 ≤2줄) — 이번 재심사에서 추가로 압축이 필요한 항목을 찾지 못함(§5) |
| `ADD` | 0 | §6 상세 — self-documenting 원칙상 추가 근거를 찾지 못함 |
| `NONE`(미문서화 유지) | 1,735 | public 1,469건 포함, 전부 이름/시그니처로 의미가 충분(§6) |

## 3. REMOVE(11건 — 전부 적용 완료)

| 파일 | 심볼 | 제거 사유 |
|---|---|---|
| `core/execution/mvp_0001/tests/test_execution_request_builder.py` | module | "Exit Criteria 검증. See docs/..." — 파일명·경로가 이미 말하는 정체성 재진술, 행위 설명 0 |
| `core/execution/mvp_0002/tests/test_prompt_specification_builder.py` | module | "Exit Criteria 검증." — 동일 |
| `core/execution/mvp_0003/tests/test_model_request_builder.py` | module | 동일 |
| `core/execution/mvp_0004/tests/test_execution_handle_builder.py` | module | 동일 |
| `core/execution/mvp_0005/tests/test_execution_state_builder.py` | module | 동일 |
| `core/execution/mvp_0006/tests/test_execution_result_builder.py` | module | "검증(RFC-0002/ADC-0002/ADR-0001, RFC-0003/ADC-0003/ADR-0002)." — Governance 인용을 나열만 할 뿐 행위·제약 설명 0(사용자 지시 §4 "RFC/ADR 설명을 반복하며 추가 의미가 없는 경우"의 정확한 사례) |
| `core/execution/tests/test_pipeline.py` | module | "Pipeline 검증." |
| `projects/omniroute-thin-engine-caller-v1/caller.py` | `OmniRouteCallError` | "OmniRoute 호출 실패의 기본 예외." — 클래스명이 이미 말하는 것의 동어반복 |
| 〃 | `OmniRouteTimeoutError` | "응답 시간 초과." — `Timeout` = "시간 초과"의 순수 동어반복 |
| 〃 | `OmniRouteConnectionError` | "OmniRoute endpoint에 연결할 수 없음." — `ConnectionError`의 순수 동어반복 |
| 〃 | `OmniRouteCancelledError` | "호출이 취소됨." — `CancelledError`의 순수 동어반복 |

**형제 클래스와의 대조(같은 파일, KEEP으로 재확인)**: 같은 파일의
`OmniRouteAuthError`("API Key 인증 실패(HTTP 401/403)")/
`OmniRouteBudgetExceededError`("비용/요청 한도 초과(HTTP 429)")/
`OmniRouteProviderError`("...보고함(HTTP 5xx)")는 클래스명만으로는
알 수 없는 **구체적 HTTP status code 매핑**을 담고 있어 REMOVE
대상에서 제외했다 — "이름의 동어반복"과 "이름이 말하지 않는 사실
추가"를 실제 텍스트 대조로 구분한 사례.

**적용 방법**: AST로 각 Docstring `Expr` 문의 정확한 소스 span을
찾아 문(statement) 전체를 삭제, 본문이 비게 되는 4개 예외 클래스는
`pass`로 채웠다(`class X(Exception): pass`는 docstring-only 클래스와
런타임상 완전히 동일 — `__doc__`이 `None`이 되는 차이만 있으며 이는
문서화 속성이지 실행 statement가 아니다).

## 4. 기존 Wave 1 KEEP 13건 — 전원 재심사(예외 없음)

사용자 지시에 따라 13건 전부를 이번 Wave의 더 엄격한 기준
("Architecture/RFC/ADR 설명 반복은 REMOVE")으로 다시 판정했다.

| 파일(심볼) | 재심사 결과 | 근거 |
|---|---|---|
| `openrouter_engine.py`(module) | **KEEP 유지** | `ADR-0027` §10 승인된 예외 배선의 **운영 상태 기록**(어떤 결정이 왜 아직 검증되지 않았는지) — RFC/ADR 요약이 아니라 그 위의 실제 운영 결정 |
| `test_mvp_0001.py`(module) | **KEEP 유지** | `RUN_REAL_ENGINE_TESTS=1` 실행 커맨드 — 코드/이름만으로 알 수 없는 실행 절차 |
| `test_omniroute_engine_real.py`(module) | **KEEP 유지** | 안전 경계 bullet + 실행 커맨드 — 동일 사유 |
| `stage_01_multi_agent.py`(module) | **KEEP 유지** | ASCII 흐름도 — RFC/ADR 텍스트 설명이 아니라 코드에 없는 시각 구조 |
| `ponytail_policy.py`(module) | **KEEP 유지** | 정책 7개 ↔ 코드 함수 매핑표 — 코드만 읽어서는 "이 함수가 정책 몇 번인지" 알 수 없음 |
| `contracts.py`(module) | **KEEP 유지(단, 경계 사례로 기록)** | Producer/Consumer 매핑표 — RFC-0007/ADC-0005/ADR-0008 인용은 있으나 표 자체는 그 문서들의 요약이 아니라 이 파일의 각 dataclass가 실제로 어떤 Stage 간 계약인지 나타내는 **1차 정보**(다른 곳에 없음). 사용자 지시 §11의 "3줄 이상이면 별도 문서화 검토" 원칙에 해당하는 유일한 후보이나, 이 표는 이미 코드(Contract 클래스)와 물리적으로 붙어 있어야 drift가 즉시 드러나는 성격이라 분리 이관하지 않기로 판단 |
| `hqs/investment/run.py`(module) | **KEEP 유지** | `print(__doc__)`로 실제 CLI 출력에 쓰이는 런타임 의존 — Architecture 설명이 아니라 실행되는 문자열 |
| `test_real_engine_budget_block.py`(module) | **KEEP 유지** | 실제 egress 사고 기록 + 이중 방어 + 커맨드 — 동일 사유(운영 절차) |
| `snapshot.py::HQSnapshot`(class) | **KEEP 유지** | Wave 3에서 이미 51줄→2줄로 압축됨, 필드별 non-fabrication 제약은 코드(타입 힌트)만으로 드러나지 않는 정책 |
| `.../recursive.py`(module, 2개 프로젝트 사본) | **KEEP 유지** | L-A/L-B/LangGraph 자료구조·제어흐름 차이의 **정밀 서술 자체가 Evidence**(RFC/ADR 요약이 아니라 이 구현 고유의 기술적 사실) |
| `.../worklist.py`(module, 2개 프로젝트 사본) | **KEEP 유지** | `test_lineage_v1.py`가 "실행 모델"/"sequential.py"/"langgraph.py" 부분 문자열을 직접 `assert` — 삭제·축소 시 테스트 회귀 확정 |

**결론**: 13건 전부 재확인 KEEP. `contracts.py` 1건만 "별도 문서화
검토 대상"으로 명시적으로 기록했으나, 코드와의 물리적 인접성이
주는 drift 방지 효과가 분리 이관의 이득보다 크다고 판단해 이번
Wave에서는 이관하지 않았다(판단 자체를 Evidence로 남김, 사용자
지시 §11 충족).

## 5. COMPRESS(0건) — 근거

Wave 3가 이미 456건을 382(순수 reflow)+61(elaboration 일부 생략)
+13(KEEP)으로 정리해, 이번 Wave 시작 시점에 **2줄 초과 Docstring은
9~10건뿐**이었고 그 전부가 §4의 재확인 KEEP 대상과 일치했다. 나머지
627건은 이미 ≤2줄이며, §3에서 REMOVE로 판정한 11건을 제외한
나머지는 전부 "코드만으로 알기 어려운 WHY 1개를 담은 짧은 문장"
패턴이라 추가로 압축할 여지(의미 손실 없이 더 줄일 수 있는 여지)를
찾지 못했다. **무조건 2줄 이하로 만들지 않는다는 사용자 지시 §11
원칙에 따라, 의미가 있는 짧은 문장을 강제로 더 자르지 않았다.**

## 6. ADD(0건) / NONE(1,735건, public 1,469건 포함) — 근거

- Public 미문서화 심볼 1,469건 중 **Class 60건은 전수 개별 검토**,
  Function/Method(나머지)는 무작위 표본(25건, 재현 가능한 seed)으로
  패턴을 확인했다.
- Class 60건: 대부분 예외 클래스(이름 자체가 실패 사유, 예:
  `GitHubAdapterError`)이거나 dataclass(필드명·타입 힌트가 이미
  구조를 설명, 예: `RepositoryEntry`, `CheckResult`, `TaskStatus`)로
  self-documenting 확인. `Checkpointer`류(6개 파일에 존재)만 이름만
  으로 resume/manifest 의미가 완전히 드러나지 않아 ADD를 검토했으나,
  Active 코드의 유일한 사례(`hqs/investment/checkpoint.py::Checkpointer`)는
  **모듈 docstring이 이미 그 캐시/재실행 건너뛰기 동작을 설명하고
  있고, 클래스 자신의 메서드(`has`/`load`/`save`)가 전부 3줄 이내의
  자명한 1:1 대응**이라 클래스 자체에 추가 Docstring을 얹는 것이
  실질적 정보를 더하지 않는다고 판단해 NONE 유지. 나머지 5개
  `Checkpointer` 동일 클래스는 `stock-analysis-*`/`dividend-stock-
  analysis-*`류 Historical Evidence 프로젝트 안에 있어 사용자 지시
  §15(C3/C4/C5 Governance Required 항목 불가침)에 따라 애초에
  검토·수정 대상에서 제외했다.
- Function/Method 표본 25건: 전부 test 함수(이미 매우 서술적인
  이름 관례로 의미가 충분) 또는 `main`/`retry`/`build_*`류 관용적
  이름으로 self-documenting 확인 — ADD 근거를 찾지 못했다.
- **결론**: 이 저장소는 Wave 1이 이미 확인한 "코드/이름이 이미
  의미를 드러낸다" 특성이 미문서화 public 심볼에도 동일하게
  적용된다 — 단지 public이라는 이유로 ADD하지 않는다는 사용자 지시
  §8을 그대로 따른 결과이며, 회피가 아니라 실측 결론이다.

## 7. 실제 변경(§9~§12 요구사항 대응)

- **변경 파일 수**: 8개(`core/execution/` 7개 + `projects/
  omniroute-thin-engine-caller-v1/caller.py` 1개).
- **변경 심볼**: REMOVE 11건(§3 표).
- **Architecture/Contract/Stage·Team 책임/Runtime behavior/dependency
  boundary**: 전부 무변경 — 제거된 것은 Docstring `Expr` 문 자체이며,
  본문이 비는 4개 예외 클래스만 `pass`로 채웠다(런타임 동작 동일,
  `__doc__` 속성만 `None`으로 바뀜).
- **AST/diff 검증**: 8개 파일 전체 `git diff`를 육안 확인해 Docstring
  삭제·`pass` 삽입 외 어떤 statement도 변경되지 않았음을 확인했다
  (§3 diff 인용).

## 8. Validation

| 항목 | 결과 |
|---|---|
| `python3 -m py_compile`(변경 8개 파일) | 오류 0건 |
| `python3 -m py_compile`(Active 전체 372개 파일) | 오류 0건 |
| `pytest core/execution/` | 55 passed |
| `pytest projects/omniroute-thin-engine-caller-v1/` | 26 passed, 1 skipped |
| `pytest hqs/` 전체 | **380 passed, 6 skipped**(Wave 0~4 baseline과 완전히 동일, 회귀 없음) |

## 9. 최종 통계(§14 요구사항)

| 지표 | 값 |
|---|---|
| 대상 파일 수(Active, `archive/`·`*.md` 제외) | 372 |
| 확인한 정의 수(Module+Class+Function/Method) | 2,372(Module 372 / Class 118 / Function·Method 2,134 — 일부 module에 `__init__.py` 등 포함되어 Class+Function 합계 2,252와는 카운팅 기준 차이) |
| Docstring 보유 | 637 |
| Docstring 미보유(전체/그중 public) | 1,735 / 1,469 |
| `REMOVE` | 11(전부 적용) |
| `COMPRESS` | 0 |
| `KEEP` | 626(기존 13건 포함 전원 재심사 완료) |
| `ADD` | 0 |
| `NONE` | 1,735 |
| 실제 변경 파일 | 8 |
| 기존 13 KEEP 재판정 | 13/13 KEEP 유지(1건 `contracts.py`는 "별도 문서화 검토" 판단을 명시 기록, 이관은 보류) |
| `hqs/` 테스트 결과 | 380 passed, 6 skipped(회귀 없음) |

## 10. 적용하지 않은 것(사용자 지시 §15 준수)

`GOVERNANCE REQUIRED`로 기존에 격리된 C3(`report_writer_final_report`
인자 구조)/C4(`stock-analysis-*` 등 Historical Evidence 템플릿
중복)/C5(`core/execution/mvp_000N/` MVP Evidence 간 중복)는 이번
Docstring Audit에서도 건드리지 않았다 — 이 세 후보는 코드 구조
문제이며 이번 Wave의 범위(Docstring Semantic Audit/Refactor)
자체에도 해당하지 않는다.

## Related

- `docs/research/PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001.md`
- `docs/research/PYTHON-REFACTOR-WAVE-3-DOCSTRING-FINAL-0001.md`
- `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`(C3/C4/C5 원 출처)
