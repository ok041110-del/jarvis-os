# DEV-HQ-V2.0 — Agent Package Refactoring real Engine E2E

## 목적

`hqs/development/mvp/agents.py` → `hqs/development/mvp/agents/` 분리
(ADC-0006 Implementation) 이후, CLI → Workflow → Stage 01~05 전체
파이프라인이 기존과 동일하게 동작하는지 real Engine으로 확인한다.
`DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001.md`와 동일한 Issue를 재사용해
Refactoring 전후를 비교 가능하게 했다.

## 방법

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
- `failed_at`: `None`, `error`: `None`
- `target`: `["project_intelligence", "_relevant_files"]`(이전 CLI E2E와
  다른 대상 식별 — Engine의 자유 식별 결과이며, Stage 02/03이 실제로
  `agents.requirements`/`agents.design`을 호출해 만든 Specification/
  Design을 근거로 Stage 04가 다시 식별한 것)
- `structural_check`: `{"valid": True, "engine_failed": False}`
- `specification_check`: `{"target_in_scope": True}`
- `design_scope_check`: `{"scope_ok": True, "changed_names": []}`
- `test_execution`: `{"executed": True, "returncode": 0}` — 실제
  `project_intelligence.py`에 적용해 저장소 전체 pytest 실행,
  **120 passed**(Agent Package Refactoring으로 추가된 11개 포함)
- `verdict`: **PASS**
- 실행 후 `git status --short` — `project_intelligence.py`가 Stage 05의
  `try`/`finally`로 자동 원상복구되어 diff 없음(Refactoring 대상 파일
  외 변경 없음 확인)

## Agent Package 경로 확인

Stage 02가 Engine에 전달한 Specification Skeleton의 Implementation
Scope Candidates에 `hqs/development/mvp/agents/backend.py`가 실제로
포함된 것을 프로세스 출력에서 직접 확인했다 — Stage 01의 AST Function
Candidate Index가 새 `agents/` 패키지 하위 파일을 정상적으로
색인했다는 뜻이다(ADC-0006 additive extension이 실제로 이 E2E에서
쓰였다).

## 판정

**PASS(1건)** — Agent Package Refactoring 이후에도 CLI → Workflow →
Stage 01~05 전체가 기존과 동일한 순서로 실행됐고, Requirements/Design/
Backend Agent(각 `agents/requirements.py`/`agents/design.py`/
`agents/backend.py`)가 정상적으로 호출됐으며, 최종 Validation Result가
PASS로 산출됐다. 실제 파일 적용 → pytest 120 passed → 원상복구 →
`git status` clean까지 CLI 프로세스 단일 실행으로 확인됐다.

## Open Issues

- 표본 1건 — `DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001.md`와 동일 Issue를
  썼으나 Engine이 다른 target(`project_intelligence._relevant_files`)을
  식별했다 — Non-deterministic Engine 특성이며 Refactoring 자체의
  결함이 아니다(전체 파이프라인 구조 재현이 목적, 동일 target 재현이
  목적이 아님).
- QA Agent(`agents/qa.py`, `test_execution` Capability)는 Stage
  01~05 Integrated Workflow에서 호출되지 않는다(기존과 동일 — Hello
  SDLC/MVP-0002 전용, `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §4 참고).
  QA Agent 분리 후 정상 동작은 `test_mvp_0001.py`(real Engine, Backend
  + QA 양쪽 patch)로 별도 확인됨.
