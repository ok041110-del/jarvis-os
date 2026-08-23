# DEV-HQ-V2.0 — 01→05 Integrated Workflow real Engine E2E

## 목적

`workflow.py`가 문서화된 Stage Handover 그대로 5개 Stage를 정확한
순서로 연결하고, 중간 실패 시 즉시 중단하며, 실제 Engine으로 끝까지
실행했을 때 Stage 05 Validation이 `PASS`를 반환하는지 확인한다. 이전
Stage 05 E2E(`DEV-HQ-V2.0-STAGE-05-E2E-0001.md`)는 5개 Stage를 세션
스크립트가 수동으로 순서대로 호출한 것이었다 — 이번은 `workflow.py`의
`run_workflow()` 자체를 호출해 orchestration 코드 경로를 직접 검증한다.

## 방법

```text
Title: Cap the number of listed files per category in context summaries
Description: (Stage 04/05 E2E와 동일한 Issue — 재현성 확인 겸용)
```

`workflow.run_workflow(ISSUE, expose_target=True)` 1회 호출.

## 결과

- `failed_at`: `None`, `error`: `None` — 5개 Stage 전부 정상 실행
- `target`: `("workflow_project_intelligence", "_summarize_context")` —
  실제 저장소 함수(Stage 04/05 단독 E2E와 동일한 대상 — 재현 확인)
- `specification_check`: `{"target_in_scope": True}`
- `design_scope_check`: `{"scope_ok": True, "changed_names": []}`
- `test_execution`: `{"executed": True, "returncode": 0}` — 실제 파일에
  적용해 저장소 전체 pytest 실행, 통과
- `verdict`: **PASS**
- 실행 후 `git status --short` — `workflow.py`/`test_workflow_
  integrated.py`(이번 커밋 대상)만 남고, 대상 파일은 Stage 05의
  `try`/`finally`로 자동 원상복구되어 변경 없음

## 판정

**PASS(1건)** — `workflow.py`가 Stage 01→05를 정확한 순서로 실행했고,
문서화된 Handover(Stage01→02, Stage01+02→03, Stage03→04,
Stage02+03+04→05)가 실제로 그대로 지켜졌으며, `run_stage_05()`의
`verdict`를 재해석 없이 그대로 반환했다. 실제 Engine 호출 + 실제 파일
적용 + pytest 실행 + 원상복구까지 전 과정이 `run_workflow()` 단일
호출로 끝까지 자동 수행됨을 확인했다.

## Open Issues

- 표본 1건 — 중간 실패(`failed_at` 채워지는 경로)는 mock 단위 테스트
  (`test_workflow_integrated.py`)로만 확인, real Engine으로는
  의도적 실패 재현을 하지 않음(범위 밖)
- CLI 통합은 이번 범위 밖 — `run_workflow()`는 아직 어떤 진입점에서도
  호출되지 않는다(Production 경로 미연결, 검증 완료 상태로만 존재)
