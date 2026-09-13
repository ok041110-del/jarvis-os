# Python Refactor Wave 3 — Docstring 의미 기반 재분류 완료

**Governance 근거**: `RFC-0042` → `ADC-0045` → `ADR-0028` Lifecycle.
Wave 0(456건 발견) → Wave 1(443건 정리, 13건 KEEP) → Wave 2(Audit +
C1/C2 코드 중복 제거) 이후, Wave 3는 Wave 1이 KEEP으로 남긴 항목을
포함해 **repository 전체 Docstring을 다시 한번 의미 기준으로
재검토**하고, 순수 reflow로 남아있던 줄바꿈 위반을 마저 정리했다.

## 진행 경과

`snapshot 1~6` 커밋(`8f85c08`~`ef1bba1`)으로 대부분의 잔여 위반을
배치 단위로 정리했고, 이번 세션에서 마지막 배치를 마무리했다:

- **자동 reflow(내용 손실 0건) 26건**: 문단이 1개뿐인 항목(줄바꿈만
  된 단일 문장)을 물리적 1줄로 재정렬 — `hqs/development/mvp/
  agents/backend.py`, `engine.py`, `chatgpt_engine.py`,
  `omniroute_engine.py`, `github_adapter.py`,
  `architecture_validation/{ponytail_adapter,quality_heuristics}.py`
  등 23개 파일.
- **최종 잔존 KEEP 9건**: Wave 1 §6이 이미 근거를 문서화한 항목과
  동일 — `openrouter_engine.py`(module, deviation), `test_mvp_0001.py`
  (module, gate), `test_omniroute_engine_real.py`(module, safety),
  `contracts.py`(module, reference-table), `hqs/investment/run.py`
  (module, runtime-doc), `test_real_engine_budget_block.py`(module,
  safety), `workflow-adapter-{gate-c-real-engine-v1,recursive-lineage-v1}/
  adapters/recursive.py`(module, technical-contrast, 2개 프로젝트 사본),
  `workflow-adapter-{gate-c-real-engine-v1,nonlanggraph-lineage-v1}/
  adapters/worklist.py`(module, test-asserted, 2개 프로젝트 사본).

## 발견한 회귀 1건과 수정

Wave 3 스냅샷 5(`befb19b`)가 `hqs/development/mvp/project_intelligence.py::
validate_issue`의 docstring을 REMOVE 판정으로 삭제했으나, 이 함수는
`build_function_candidate_index()`가 색인화하는 대상이고
`hqs/development/mvp/tests/test_ast_context.py::
test_candidate_index_lists_known_function_signature_and_docstring`가
그 docstring 첫 줄 문자열을 정확히 `assert`한다 — 이 삭제가 실제
테스트 실패(`380 passed` → `379 passed, 1 failed`)를 유발했다.
원인은 이 함수의 docstring이 "`title`/`description`만 필수 Issue
필드로 검사한다"는, 이름만으로는 드러나지 않는 실제 WHY(정확히
어떤 필드가 검사되는지)를 담고 있었는데도 WHAT으로 오판된 것이다
— **원문 그대로 복원**했다(1줄, 정책 위반도 아니었음). 같은 커밋이
지운 `IssueValidationError`(예외 클래스) docstring은 어떤 테스트도
참조하지 않아 삭제된 상태를 그대로 유지했다(순수 WHAT 반복 확인).

이 사례는 Wave 1이 §4에서 세운 "REMOVE 0건" 원칙(전수 정독 결과
순수 WHAT 반복 대상 없음)이 실제로 유효했음을 역설적으로 재확인한다
— Wave 3가 그 원칙을 지키지 못하고 REMOVE를 시도한 유일한 사례가
바로 실제 회귀로 이어졌다.

## Validation

- `python3 -m py_compile`(전체 active tree): 오류 0건.
- Docstring 2줄 초과 잔존: **9건**(전부 의도적 KEEP, Wave 1 §6과
  동일 근거).
- `hqs/` pytest: **380 passed, 6 skipped**(Baseline과 동일, 회귀
  0건 — 위 1건은 발견 즉시 수정 후 재검증 완료).
- Docstring-content-dependent 테스트 전수 재확인(`grep -rl
  "get_docstring\|__doc__"`): `test_lineage_v1.py`(worklist.py
  "실행 모델"/"sequential.py"/"langgraph.py" 부분 문자열)까지 포함해
  전부 원문 보존 확인(코드로 직접 재확인, `langgraph` 미설치로 pytest
  collection 자체는 환경 제약상 실행 불가 — Wave 0/1과 동일한 기존
  제약).

## Architecture/Contract 영향

없음 — 이번 배치도 Docstring 텍스트만 수정했다(코드 로직 0줄 변경).

## Related

- `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`
- `docs/research/PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001.md`
- `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`
