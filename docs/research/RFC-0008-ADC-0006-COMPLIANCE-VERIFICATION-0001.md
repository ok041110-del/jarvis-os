# RFC-0008 → ADC-0006 재검증 및 구현 준수 확인

**문서 성격**: READ-ONLY 검증. `docs/decisions/rfc/RFC-0008-*.md`,
`docs/governance/adc/ADC-0006.md`, 관련 코드를 수정하지 않는다. 새
ADC/ADR을 작성하지 않는다 — RFC-0008 후속 ADC는 이미
`docs/governance/adc/ADC-0006.md`로 존재하며, 동일 RFC에 대해 두 번째
결정 문서를 만드는 것은 `docs/research/RFC-ADC-ADR-ID-UNIFICATION-
INVESTIGATION-0001.md`가 이미 확인한 "동일 결정을 두 번 내리지 않는다"
원칙에 저촉된다.

## 요청 배경

"RFC-0008 후속 ADC를 작성하라"는 요청이 있었으나, 조사 결과 해당
ADC(`ADC-0006`)가 이미 존재하고 요청된 6개 항목을 대부분 포함하고
있어, 신규 ADC 작성 대신 **기존 ADC-0006이 각 항목을 실제로
충족하는지 재검증**하는 것으로 범위를 전환했다(사용자 승인).

## 1. RFC-0008 원문과 ADC-0005 Evidence 재검토

- `docs/decisions/rfc/RFC-0008-agents-module-physical-layout-boundary.md`
  §6(대안 비교), §7(Architecture Impact, NONE 잠정), §8(Contract
  Impact), §9(권장 Decision Candidate: 대안 B)를 원문으로 재확인했다.
- `ADC-0006`의 Q1/Q2 판단 근거("대안 A는 목표 구조를 달성하지 못하고,
  대안 C는 Python 제약상 이점을 온전히 얻지 못한다")는 RFC-0008 §9의
  근거 문장과 **정확히 일치**한다 — ADC가 RFC의 권장안을 임의로
  바꾸지 않고 그대로 채택했음을 확인.
- `ADC-0006` Q3가 인용한 `docs/governance/adc/ADC-0005.md`(RFC-0007
  후속)의 Accept 판단 4건(Candidate Index, Dependency Closure 등)이
  실제로 존재함을 확인(`docs/governance/adc/ADC-0005.md` 직접 열람).
- **결론**: ADC-0006의 근거 재검토 결과, RFC-0008/ADC-0005 원문과의
  불일치는 발견되지 않았다.

## 2. Decision Candidate 비교 재검증

| Candidate | RFC-0008 원문 | ADC-0006 판단 | 일치 여부 |
|---|---|---|---|
| A. `agents.py` 유지 | §6, 목표 구조(패키지 분리) 미달성 | Q1 — 동일 결론 | 일치 |
| B. dotted package path 확장 | §9 권장 | Decision — B 채택(Conditional Accept) | 일치 |
| C. Shim 방식 | §6, Python 이름 충돌 제약상 이점 미흡 | Q2 — 동일 결론, "평면/패키지 이중 복잡도"로 구체화 | 일치(ADC가 근거를 더 상세화) |

**결론**: 3개 Candidate 모두 RFC-0008이 제시한 것과 정확히 일치하며,
ADC-0006이 새 대안을 추가하거나 임의로 판단을 바꾼 사례는 없다.

## 3. `ast_context.py`의 Architecture/Contract 영향 재검증 (현재 코드 기준)

ADC-0006의 Architecture/Contract Impact 절이 **현재 코드 상태와
여전히 일치하는지** 직접 코드를 읽어 재확인했다(`hqs/development/
mvp/ast_context.py`).

| ADC-0006의 주장 | 현재 코드 확인 결과 |
|---|---|
| `module_source_path(module: str) -> Path` 시그니처 불변 | 일치(35행) |
| `build_function_candidate_index() -> str` 시그니처 불변 | 일치(98행) |
| `build_dependency_closure(module: str, function: str) -> str` 시그니처 불변 | 일치(110행) |
| dotted 지원은 additive extension(기존 분기 무변경) | 일치 — `_mvp_package_dirs()`/`_package_source_files()`(17~49행)라는 **완전히 새로운 함수**로 구현됐고, 기존 평면 경로 로직은 그대로 남아 있음(코드에 "ADC-0006: dotted package module path 지원을 additive extension으로 추가(평면 module path 동작 무변경)" 주석이 직접 명시) |
| Architecture Impact: NONE | `hqs/development/HANDOVER.md`가 사후에도 "Architecture/Contract 변경 NONE"으로 재확인 |

**결론**: ADC-0006의 Architecture/Contract Impact 판단은 **실제 구현
이후에도 유효**하다 — 근거와 결과가 일치한다.

## 4. 평면 모듈 호환성 및 회귀 테스트 요구사항 검증

### 4.1 코드 수준

- `agents.py`는 더 이상 존재하지 않고 `agents/`(패키지, `__init__.py` +
  `backend.py`/`design.py`/`qa.py`/`requirements.py`)로 전환 완료(확인됨).
- `test_ast_context.py:75`가 여전히 `build_dependency_closure("agents",
  ...)`처럼 **점 없는 기존 리터럴을 그대로 사용**하며 통과한다 — Condition
  6이 예상했던 "`"agents"` → `"agents.backend"` 같은 리터럴 변경"이
  **실제로는 필요하지 않았다**(module_source_path의 package_init
  fallback 분기가 흡수). 이는 ADC-0006이 요구한 것보다 더 보수적인
  결과로, 조건 위반이 아니라 초과 달성이다.
- `test_ast_context_package_paths.py`가 dotted path 전용 신규 파일로
  존재하며, 파일 docstring이 "기존 `test_ast_context.py`는 수정하지
  않았다"고 스스로 명시 — Condition 2/Validation("별도 파일로 추가")
  요구사항과 정확히 일치.
- 같은 테스트 파일이 실제 저장소에 `agents/` 등 디렉터리를 생성하지
  않고 `tmp_path`/monkeypatch로만 검증한다고 명시 — RFC-0008/ADC-0006이
  요구한 것 이상의 안전장치.

### 4.2 회귀 테스트 실행 결과 (이번 세션 직접 실행)

```
$ /root/.local/bin/pytest hqs/development/mvp/tests/ -q
364 passed, 6 skipped in 38.92s
```

ADC-0006 Condition 4/Validation의 기준선(109 passed 이상)을 크게
상회하며, **실패 0건**. `hqs/development/HANDOVER.md`에 기록된 구현
직후 기준선(120 passed)과도 궤적이 일치한다(이후 다른 Task들로 143→
152→…→364까지 증가, 이번 검증에서 확인된 값과 일관됨).

**결론**: 평면 모듈 호환성·회귀 테스트 요구사항은 **실제로 충족되었고
현재도 유효**하다.

## 5. `agents.py` 패키지 전환과 `ast_context.py` 확장의 분리 검증

- ADC-0006 Condition 3/5는 "확장을 먼저, 검증 후 이동"을 요구한다.
- `hqs/development/HANDOVER.md`의 서술 순서: "RFC-0008 → ADC-0006(AST
  Context dotted package path additive extension) → Agent Package
  Refactoring(`agents.py` → `agents/{...}.py`)" — 순서상 Condition 5와
  일치.
- **한계(정직하게 기록)**: 두 작업이 커밋 단위로 실제로 분리됐는지는
  `git log --follow`로 확인을 시도했으나, 이 저장소 초기 이력이 대규모
  단일 병합 커밋(`15ac209`)으로 압축되어 있어 세부 커밋 단위 증거는
  **확인 불가(Blocked)**다. 다만 (a) 두 산출물이 PR #103 하나로
  "Merge 완료"됐다고 HANDOVER.md가 명시하고, (b) 코드 구조 자체가
  additive-only이며, (c) Condition 3의 실질적 목적(확장을 먼저
  검증하지 않은 채 이동이 함께 진행되어 회귀를 놓치는 것을 방지)은
  §4.2의 회귀 테스트 결과로 사후에 충분히 달성되었음을 확인했다 —
  Task 분리의 정신은 실현됐으나 "동일 PR 여부"까지는 검증하지
  못했다는 점을 명시한다.

## 6. ADR Required 여부 판단

**판단: ADR 불필요(No) — 근거 충분, 보류하지 않음.**

근거:

1. ADC-0006 자신이 "이 ADC는 ADC-0004/ADC-0005와 성격이 같다"고
   명시했고, 그 선례들의 후속 RFC(`RFC-0007`)는 "전부 No ADR
   Required(`hqs/development/BASELINE.md`가 MVP Implementation을
   Baseline 범위에서 제외하므로)"라고 명문화되어 있다 — 동일 범주.
2. ADC-0006의 Architecture Impact 절이 "NONE"이라고 판단한 근거
   (Kernel 범위 밖의 순수 정적 분석 함수 내부 로직)가 §3에서 현재
   코드로 재확인한 바와 일치한다.
3. 구현 완료 이후 작성된 `hqs/development/HANDOVER.md`가 "Architecture/
   Contract 변경 NONE"이라고 **사후에도 재확인**했다 — 판단이 구현
   전 예측에 그치지 않고 실제 결과로 검증됐다.
4. `docs/decisions/adr/` 및 `docs/architecture/core/`의 ADR 목록
   어디에도 ADC-0006을 종결 대상으로 인용하는 ADR이 없다(이전 세션의
   `DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md` 전수
   조사에서도 확인됨) — 저장소 자체가 지금까지 ADR을 요구하지 않았다.

이 판단은 §7(미해결 사항)의 "Task 분리 커밋 증거 미확인"과는
무관하다 — 그 미해결은 절차 준수의 세부 증거 문제이지, Architecture/
Contract 영향의 실재 여부를 바꾸지 않는다.

## 7. 검증 결과 요약

| 요청 항목 | 결과 |
|---|---|
| RFC-0008/ADC-0005 Evidence 재검토 | PASS — 불일치 없음(§1) |
| Decision Candidate 비교 | PASS — 3건 전부 원문과 일치(§2) |
| Architecture/Contract 영향 재검증 | PASS — 구현 후에도 유효(§3) |
| 평면 모듈 호환성·회귀 테스트 요구사항 | PASS — 364 passed, 0 failed, 별도 테스트 파일 확인(§4) |
| Task 분리(확장/이동) | PARTIAL — 순서·결과는 일치, 커밋 단위 분리는 초기 이력 압축으로 확인 불가(§5) |
| ADR Required 여부 | 판단 완료 — **No**, 근거 충분(§6) |

## 8. 미해결 사항

1. `ast_context.py` dotted 확장과 `agents/` 이동이 실제로 별도 커밋
   이었는지는 이 저장소의 압축된 초기 Git 이력으로 인해 최종 확인이
   불가능하다(§5). 결과적 준수(회귀 없음, additive 코드)는 확인됐으나
   절차적 증거는 Blocked로 남긴다.
2. Condition 6이 예상한 테스트 리터럴 변경은 실제로 발생하지 않았다
   (§4.1) — ADC-0006을 사후 수정할 필요는 없으나(이 문서가 그 사실을
   기록하는 것으로 충분), 향후 유사 ADC 작성 시 "예상되는 변경"과
   "실제 필요한 변경"을 구분해 조건을 쓰는 것을 참고할 수 있다(권고,
   실행하지 않음).

## Architecture / Public Contract 영향

- Architecture 변경: **No**(이번 검증 자체가 아무것도 변경하지 않음).
- Public Contract 변경: **No**.
- 이번 검증으로 `ast_context.py`/`agents/`/ADC-0006/RFC-0008 중 어느
  것도 수정하지 않았다.

## 검증 방법

- 코드 직접 열람: `hqs/development/mvp/ast_context.py`,
  `hqs/development/mvp/agents/`, `hqs/development/mvp/tests/
  test_ast_context.py`, `test_ast_context_package_paths.py`.
- 테스트 실행: `/root/.local/bin/pytest hqs/development/mvp/tests/ -q`
  → `364 passed, 6 skipped`.
- Git 이력 조회: `git log --follow`, `git log -S "ADC-0006"` — 초기
  이력 압축으로 세부 분리 증거는 확인 불가(§5, §8-1에 한계 명시).
- 문서 대조: `RFC-0008`, `ADC-0006`, `ADC-0005`(governance),
  `HANDOVER.md`, `DEV-HQ-V2.0-AGENT-PACKAGE-REFACTORING-E2E-0001.md`.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0008-agents-module-physical-layout-boundary.md` | 검증 대상 원본 |
| ADC | `docs/governance/adc/ADC-0006.md` | 검증 대상(기존 결정, 수정하지 않음) |
| ADC | `docs/governance/adc/ADC-0005.md` | Evidence 재검토 대상 |
| Evidence | `hqs/development/HANDOVER.md` | 구현 완료·사후 Architecture/Contract 확인 근거 |
| Evidence | `docs/research/DEV-HQ-V2.0-AGENT-PACKAGE-REFACTORING-E2E-0001.md` | real Engine E2E 근거 |
| Investigation | `docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md` | RFC-0008 Ambiguous 분류 최초 기록(§6에서 이번 검증으로 해소) |
