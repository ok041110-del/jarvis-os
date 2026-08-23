# DEV-HQ-V2.0 — CLI Integration real Engine E2E

## 목적

`hqs/development/cli.py`가 사용자 입력(Issue JSON, `--expose-target`)을
정상 수신해 `workflow.run_workflow()`를 정확히 호출하고, Stage 01→05
전체 결과를 재해석 없이 출력하며, 실제 파일 적용 → pytest → 원상복구
까지 CLI 단일 실행으로 끝까지 자동 수행되는지 확인한다.

## 방법

셸에서 사용자가 실제로 실행할 명령 그대로 subprocess로 실행했다(mock
없음):

```bash
python hqs/development/cli.py issue.json --expose-target
```

```json
{
  "title": "Cap the number of listed files per category in context summaries",
  "description": "When summarizing collected context for the requirement-analysis prompt, each category's file list is currently included in full, which can make the prompt very long for categories with many matches. Limit each category's summary line to at most 2 file names, with an indicator of how many more were omitted.",
  "status": "Open"
}
```

## 결과

- exit code: `0`, stderr: 비어 있음
- stdout(JSON): `failed_at: None`, `error: None`
- `target`: `["workflow_project_intelligence", "_summarize_context"]`
  (Stage 04/05 단독 E2E, 통합 Workflow E2E와 동일한 대상 — 3번째 재현)
- `specification_check`: `{"target_in_scope": True}`
- `design_scope_check`: `{"scope_ok": True, "changed_names": []}`
- `test_execution`: `{"executed": True, "returncode": 0}` — 실제 파일에
  적용해 저장소 전체 pytest 실행, 통과
- `verdict`: **PASS**
- 실행 후 `git status --short` — 이번 커밋 대상 파일(`cli.py`,
  `test_cli_integrated.py`)만 남고, 대상 파일은 Stage 05의
  `try`/`finally`로 자동 원상복구되어 변경 없음

## 판정

**PASS(1건)** — CLI가 사용자 입력을 정상 수신하고 `run_workflow()`를
정확히 호출했으며(`--expose-target` 옵션 포함), Stage 01→05 전체가
기존과 동일한 순서로 실행됐고, 최종 Validation Result가 CLI 출력까지
재해석 없이 정상 전달됐다. CLI → Workflow → Stage 01~05 전체 real
Engine E2E가 실제 파일 적용 → pytest → 원상복구 → `git status` clean
까지 CLI 프로세스 단일 실행으로 자동 확인됐다.

## Open Issues

- 표본 1건 — Workflow 실패 시 CLI의 실패 출력(stderr + exit 1)은 mock
  단위 테스트(`test_cli_integrated.py`)로만 확인, real Engine 의도적
  실패는 미실행(범위 밖)
- `hqs/development/mvp/cli.py`(MVP-0001, code-review 파이프라인 전용)
  는 이번 변경과 무관 — 수정하지 않았고 별도 진입점으로 유지된다
