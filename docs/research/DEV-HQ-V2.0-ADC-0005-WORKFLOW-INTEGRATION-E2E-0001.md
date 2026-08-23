# DEV-HQ-V2.0 — ADC-0005 Workflow Integration E2E

## 목적

PR #102(`ast_context.py`)에 이어, ADC-0005 §8 최소 범위를 실제
Workflow에 배선하고 real Engine으로 E2E 검증한다. 초기 적용 범위는
ADC-0005 §7이 권고한 대로 "기존 함수 1개 확장" Task로 제한한다.

## 배선

기존 `workflow_0008.py`는 수정하지 않았다 — 새 진입점
`hqs/development/mvp/workflow_ast_context.py`를 추가했다
(`workflow_project_intelligence.py`가 `run_issue_to_planning` 곁에
`run_issue_to_design`을 추가한 선례와 동일한 패턴).

- `identify_target(design: str)`: `build_function_candidate_index()` +
  Design을 `call_engine`에 직접 전달해 `FILE:`/`FUNCTION:` 두 줄을
  파싱한다(T17~T19와 동일 방법론, 새 Capability로 등록하지 않음).
- `run_pipeline_with_ast_context(issue, expose_target=False)`:
  Planning → Design → `identify_target` → `build_dependency_closure` →
  (`expose_target=True`일 때만) 대상 파일 전체 + Exposure 정책 지시문
  → `backend_agent_code_generation(build_input)`. 함수 시그니처는
  변경하지 않았다 — Context는 입력 문자열에 concatenate된다.

## 구현 중 발견/수정한 결함

`identify_target`이 처음에는 후보 인덱스의 `FILE:` 값을 저장소 상대
경로(`hqs/development/mvp/x.py`) 그대로 모듈명으로 취급해, 실제 real
Engine 호출 1회차에서 `AST closure를 계산할 대상을 찾지 못했다:
hqs/development/mvp/workflow_project_intelligence._summarize_context`
로 실패했다. `PurePosixPath(file_name).stem`으로 basename만 취하도록
수정하고, 이 회귀를 막는 단위 테스트
(`test_identify_target_strips_directory_prefix_from_file_line`)를
추가한 뒤 재실행했다.

## E2E Task

"Context를 요약하는 기존 함수가 각 카테고리의 파일 목록을 전부
나열해, 카테고리당 파일 수가 많아지면 요약 문자열이 지나치게
길어진다. 새 함수를 만들지 않고 기존 함수 1개를 확장해, 카테고리당
최대 2개까지만 파일명을 보여주고 그 이상은 '(+N more)' 형태로
축약한다." — 실제 대상 파일명/함수명은 issue에 언급하지 않았다
(T06~T19와 동일하게 Design은 blind로 실행).

`run_pipeline_with_ast_context(issue, expose_target=True)`를 real
Engine으로 1회 실행했다.

## 결과

| 단계 | 결과 |
|---|---|
| 시작점 식별(`identify_target`) | `("workflow_project_intelligence", "_summarize_context")` — **정답과 정확히 일치** |
| AST 폐쇄 | 1개 모듈(자기 자신) |
| Build 입력 | Design(4,688자) + AST 폐쇄 + 대상 파일 전체(노출) + Exposure 정책 지시문 |
| Build 출력 | 2,821자, 파일 전체 형태로 반환 |

### Scope 준수 검증(`diff`)

생성된 파일 전체를 원본과 `diff`로 직접 대조한 결과, 차이는
**`_summarize_context` 함수 본문 하나뿐**이었다 — 다른 함수
(`_enrich_issue`, `run_issue_to_planning`, `run_issue_to_design`),
import, docstring, 공백은 전부 문자 단위로 동일했다. `TARGET-FILE-
EXPOSURE-MITIGATION-0001.md`(B/C 2/2)에 이어 **3/3**으로 Scope 준수가
재현됐다.

```diff
 def _summarize_context(context: dict) -> str:
-    lines = [f"{category}: {', '.join(files)}" for category, files in context.items() if files and category != "directory_structure"]
+    lines = []
+    for category, files in context.items():
+        if not files or category == "directory_structure":
+            continue
+        shown = files[:2]
+        line = f"{category}: {', '.join(shown)}"
+        if len(files) > 2:
+            line += f" (+{len(files) - 2} more)"
+        lines.append(line)
     return "\n".join(lines) if lines else "(관련 자료 없음)"
```

### 기존 코드 보존 + pytest 검증

생성된 파일을 실제 `workflow_project_intelligence.py`에 임시로
적용해(백업 후 덮어쓰기) 검증했다:

```
pytest hqs/development/mvp/tests/test_workflow_project_intelligence.py -q
9 passed
pytest hqs/development/mvp/tests/ -q
52 passed
```

기존 9개 테스트(directory_structure 제외, 빈 카테고리 제외,
placeholder 등 기존 계약) 전부 통과 — 회귀 없음. 새 동작도 별도
스크립트로 직접 확인했다: 카테고리당 5개 파일 → `"source_code: a.py,
b.py (+3 more)"`, 정확히 2개일 때는 `"+N more"`가 붙지 않음(경계
케이스 정상).

검증 후 파일을 원본으로 복원(`.orig` 백업에서 복구)하고 `git status`
로 작업 트리가 깨끗함을 확인했다 — 이번 세션의 실제 커밋 대상은
`workflow_ast_context.py`(신규)와 `ast_context.py`의
`module_source_path` 추가뿐이다.

## Architecture / Contract 영향

- **Architecture**: 없음 — 새 Runtime/Registry/Capability 없음.
  `workflow_ast_context.py`는 기존 5-Stage Workflow(`workflow_0008.py`)
  를 수정하지 않고 별도 진입점으로만 추가됐다.
- **Contract**: `backend_agent_code_generation(design: str) -> str`
  시그니처 불변. `identify_target`는 `AGENT_CAPABILITY_MAP`에 등록되지
  않았다 — T17~T19와 동일하게 `call_engine` 직접 호출.

## 최종 판정

**E2E PASS(1건)** — 시작점 식별 정답 일치, Scope 100% 준수(3/3
누적), 기존 코드 완전 보존, pytest 회귀 없음. 표본은 1건이므로
일반화에는 한계가 있으나, ADC-0005가 요구한 "기존 함수 1개 확장"
초기 범위 안에서 배선이 실제로 동작함을 확인했다.

## Open Issues

- `run_pipeline_with_ast_context`는 아직 어떤 실제 workflow 진입점
  (`cli.py` 등)에서도 호출되지 않는다 — 이번 E2E는 함수를 직접
  호출해 검증했다. 실제 사용자 진입 경로에 연결할지는 별도 판단.
- `expose_target`는 여전히 호출자가 명시적으로 지정한다 — "노출
  여부/수정 의도를 Design에서 자동 판별"하는 것은 검증되지 않았다
  (RFC-0007 Open Issues, 이번 E2E도 확장하지 않음).
- 표본 1건 — 재현 검증 여부는 별도 Task.

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: YES (hqs/development/mvp/workflow_ast_context.py 신규,
hqs/development/mvp/ast_context.py에 module_source_path 추가)
Tests: 52 passed (mvp 전체, 신규 8건 포함 — test_workflow_ast_context.py 7건 +
identify_target 경로 파싱 회귀 테스트 1건), 임시 적용 파일은 검증 후
원본으로 복원, git status clean 확인
E2E: PASS (real Engine, 시작점 식별 1/1 정답, Scope 준수 diff로 직접 확인,
pytest 9/9 + 52/52 통과)
PR: NOT CREATED (기존 PR #102에 추가 커밋)
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: run_pipeline_with_ast_context를 실제 사용자
진입 경로(cli.py 등)에 연결할지 판단, "기존 함수 1개 확장" 시나리오
추가 재현으로 표본 확대
```
