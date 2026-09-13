# main 최신 상태 기준 최종 Regression Validation — Evidence

**Date**: 2026-09-13
**검증 대상**: `main` 최신 상태(PR #187 merge 직후)
**작업 브랜치**: `claude/regression-validation-main`
**작업 성격**: 검증만 수행. Production 코드/Architecture/Contract/
Governance 문서는 전혀 수정하지 않았다 — 실제 결함이 발견되지 않아
수정할 대상 자체가 없었다.

## Summary

- `main` 최신 커밋: `7808f03`(`Merge pull request #187`).
- `hqs/development/mvp/tests/`(OpenRouter Migration 관련 실제 회귀
  기준선): **356 passed, 6 skipped** — PR #187 merge 직전과 완전히
  동일. **회귀 없음.**
- `py_compile`/`compileall`: 저장소 전체(레포 루트부터 `hqs/`,
  `projects/`, `archive/` 포함) 문법 오류 **0건**.
- Repo-root에서 `pytest`를 전체 실행하면 18건의 collection error가
  나오지만, 이 중 **13건은 PR #187 merge 이전에도 이미 존재하던
  것**(`langgraph` 미설치, `archive/v1` 등)이고, **5건은 이번
  merge로 새로 나타났으나 OpenRouter Migration 코드의 결함이 아니라
  서로 다른 `projects/*` 실험이 전부 `domain`이라는 동일 패키지명을
  써서 repo-root 일괄 collection 시 충돌하는, 이미 알려진 기존
  구조적 제약의 재발**이다(저장소 자신의 `pytest.ini` 주석이 이미
  이 문제 유형을 명시). `mvp/tests/`(OpenRouter Migration이 실제로
  건드린 유일한 테스트 영역)는 이 충돌과 무관하며 전혀 영향받지
  않았다.
- **결론: OpenRouter Production Migration으로 인한 regression 없음.**
  발견된 5건의 신규 collection error는 실제 코드 결함이 아니라
  repo-root 전체 collection이라는, 애초에 이 저장소가 지원 대상으로
  삼지 않은 실행 방식의 환경적 한계다 — 코드 수정을 하지 않았다.

## 1. main 최신 커밋 확인

```
$ git log -1 --oneline
7808f03 Merge pull request #187 from ok041110-del/claude/jarvis-openrouter-validation-bin9aj
```

`git fetch --all --prune` 이후 로컬 `origin/main`과 일치 확인.

## 2. 전체 pytest 실행

### 2-a. `hqs/development/mvp/tests/`(확립된 회귀 기준선)

```
$ /root/.local/bin/pytest -q mvp/tests/
356 passed, 6 skipped in 38.26s
```

skip 6건은 전부 기존과 동일한 opt-in 전용 실제 Engine 호출
테스트(`RUN_REAL_ENGINE_TESTS=1`/`RUN_REAL_OMNIROUTE_TESTS=1` 필요) —
새로 생긴 skip 없음.

### 2-b. Repo-root 전체 `pytest`(참고용, 이 저장소의 공식 회귀
기준선이 아님)

```
$ pytest -q  (repo root)
676 tests collected, 18 errors during collection
```

18건 전부 `ModuleNotFoundError`/`ImportError` — **테스트 실패(assertion
실패)가 아니라 collection 단계 오류**다. 아래 §4/§5/§6에서 원인을
구분한다.

## 3. py_compile / compileall 검증

```
$ python3 -m compileall -q hqs/development   → exit 0(오류 없음)
$ python3 -m compileall -q .                 → exit 0(오류 없음, 저장소 전체)
$ python3 -m py_compile mvp/openrouter_engine.py mvp/workflow_ast_context.py \
    mvp/tests/fake_openrouter_server.py mvp/tests/test_openrouter_engine.py \
    mvp/tests/test_workflow_ast_context.py mvp/tests/test_engine_boundary.py \
    stages/04_implementation/stage_04.py
  → OK
```

문법 오류 0건 — 저장소 전체 기준.

## 4. 기존 대비 실패/skip 변화 확인

| 항목 | PR #187 merge 직전(마지막 세션 기록) | main 최신(이번 검증) | 변화 |
|---|---|---|---|
| `mvp/tests/` passed | 356 | 356 | 없음 |
| `mvp/tests/` skipped | 6 | 6 | 없음 |
| `mvp/tests/` failed | 0 | 0 | 없음 |
| Repo-root pytest collection error | (측정한 적 없음 — 이 저장소의 공식 기준선이 아니었음) | 18건 | 아래 §5/§6에서 원인 분리 |

`mvp/tests/` 기준으로는 **완전히 동일** — 회귀 없음.

## 5. OpenRouter Production Migration으로 인한 regression 여부

**없음.** 근거:

- OpenRouter Migration이 실제로 변경한 파일은 전부
  `hqs/development/mvp/`(`openrouter_engine.py`,
  `workflow_ast_context.py`, `agents/backend.py`,
  `agents/design.py`, `agents/requirements.py`) 와
  `hqs/development/stages/`(`01_context_analysis/reasoning.py`,
  `02_planning_specification/task_dependency_agent.py`),
  그리고 이들을 검증하는 `mvp/tests/` 안이다 — 이 범위의 테스트가
  `356 passed, 6 skipped`로 merge 전후 완전히 동일하다.
- Repo-root의 18건 collection error 중 어느 것도 위 OpenRouter
  Migration 대상 파일을 import 실패의 직접 원인으로 지목하지 않는다
  (모든 traceback이 `langgraph` 미설치 또는 서로 다른 `projects/*`
  실험 간 `domain` 패키지명 충돌만 가리킨다 — §6 상세).

## 6. 실패(collection error) 분류 — 신규 결함 vs 기존/환경성

Merge 전(`b8c41c0`, PR #187 base) 상태를 별도 clone에서 재현해
직접 비교했다:

```
$ git clone --quiet <repo> /tmp/premerge_check
$ cd /tmp/premerge_check && git checkout b8c41c08cfbf456cc302f598057ce6ce5778c235
$ pytest -q   → 13 errors during collection
```

| 분류 | 개수 | 내용 | 원인 |
|---|---|---|---|
| **기존(merge 이전부터 존재)** | 13 | `archive/v1/tests/*`(7건), `projects/multi-agent-handoff-mvp-v1`, `projects/omniroute-thin-engine-caller-v1`, `projects/workflow-adapter-gate-c-real-engine-v1`, `projects/workflow-adapter-nonlanggraph-lineage-v1`, `projects/workflow-adapter-recursive-lineage-v1`, `projects/workflow-adapter-reversibility-v2` | `langgraph` 패키지 미설치(이 환경에 설치돼 있지 않음) — OpenRouter Migration과 완전히 무관, PR #187 merge 이전부터 동일하게 실패 |
| **신규(merge로 새로 나타남)** | 5 | `openrouter-auto-selection-v1/tests/test_auto_selection_harness.py`, `openrouter-free-model-selection-architecture-experiment-v1/tests/test_architecture_experiment.py`, `.../test_stage05_revalidation.py`, `stage05-parallel-validation-harness-v1/domain/test_node.py`, `.../tests/test_harness.py` | `ModuleNotFoundError: No module named 'domain.<x>'` — 이 5개 실험 프로젝트도 각자 로컬 `domain` 패키지를 쓰는데, repo-root에서 전체 `pytest`를 collect하면 먼저 import된 **다른** `projects/*/domain` 패키지가 `sys.modules['domain']`을 선점해버려 이후 이름이 같은 다른 프로젝트의 `domain`을 찾지 못한다 — **저장소 자신의 `pytest.ini` 주석("projects/notekeeper와 projects/textkit의 tests 패키지명 충돌... 회피")이 이미 문서화한 것과 동일한 유형의 구조적 충돌**이며, 각 프로젝트를 개별 디렉터리에서 실행하면 발생하지 않는다(다른 세션들에서 이 프로젝트들 각각의 격리된 offline 테스트가 정상 PASS했음을 이미 확인한 바 있다). |

**판정**: 5건 모두 **환경성/구조적 기존 제약의 재발**이지 OpenRouter
Migration 코드나 Stage/Team 로직의 **신규 결함이 아니다** — (a) 실패
지점이 전부 OpenRouter Migration이 건드리지 않은 `projects/*`
실험 코드 자체의 import 구문이고, (b) 실패 원인이 "코드가 틀렸다"가
아니라 "여러 독립 프로젝트를 같은 프로세스에서 한꺼번에 collect하면
동일 패키지명이 충돌한다"는, 이 저장소가 이미 알고 있던 실행 방식의
한계이며, (c) 이 실행 방식(repo-root 전체 pytest)은애초에 이
저장소의 공식 회귀 기준선이었던 적이 없다(공식 기준선은 항상
`hqs/development/mvp/tests/`였다).

## 7. 코드 수정 여부

**수정하지 않았다.** 실제 결함(코드 로직 오류, Contract 위반, Stage
동작 이상)이 하나도 확인되지 않았으므로 수정 대상이 없다 — 사용자
지시("결함이 실제로 확인된 경우에만 수정")에 따라 임의의 "개선"
(예: repo-root pytest 실행을 위한 `domain` 패키지 이름 변경, 각
`projects/*`에 독립 `pytest.ini` 추가 등)도 하지 않았다.

## 8. 최종 결과

| 항목 | 결과 |
|---|---|
| main 최신 커밋 | `7808f03` |
| `mvp/tests/` 결과 | 356 passed, 6 skipped(변화 없음) |
| `py_compile`/`compileall` | 저장소 전체 0건 오류 |
| OpenRouter Migration regression | **없음** |
| Repo-root pytest collection error | 18건(기존 13 + 신규 5, 전부 환경성/구조적, OpenRouter 결함 아님) |
| 코드 수정 | 없음(결함 미확인) |
| Architecture/Contract/Governance | 무변경 |
| Production Code | 무변경 |
| 다음 필요 조치 | 없음(선택 사항: repo-root 전체 pytest를 지원 대상으로 삼으려면 별도 결정 필요 — 이번 검증 범위 밖) |

**Validation 결과: PASS(OpenRouter Production Migration 기준 회귀
없음 확정).**
