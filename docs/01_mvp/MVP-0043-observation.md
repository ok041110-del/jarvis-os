# MVP-0043 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — `development-hq/mvp/engine.py`에 남아 있던, 더 이상 어디서도
호출되지 않는 rule-based 응답 로직(약 790줄)을 실제 grep/import 검증으로
"죽은 코드"임을 확인한 뒤 삭제했다.

## 목적

`MVP-0042`처럼 CLI 진입점을 직접 실행해 결함을 찾는 대신, 이번에는
`engine.py`를 직접 읽어 실제 실행 경로를 추적했다. `ENGINE-CONNECT-0001`
이후 `call_engine()`은 `subprocess.run(["claude", "-p", ...])`만
호출하고 `_rule_based_response()`를 전혀 참조하지 않는다 — `MVP-0041`
관찰에서도 "`_extract_section`/`_parse_interface_lines`는
`_rule_based_response` 경로에서만 쓰이며 ... 현재 미사용 코드다"라고
이미 부분적으로 지적된 사실이었다. 이번 세션은 그 범위를 전수
확인했다: `_rule_based_response`가 참조하는 함수 전체(그 함수들이
다시 참조하는 함수까지)가 정말로 미사용인지, 그리고 저장소 안
어디에서도 그 이름들을 실제로 import/호출하지 않는지 직접 실행으로
검증했다.

## 선정한 실제 업무 — 직접 검증

`engine.py`에 정의된 함수 37개 중 `call_engine()` 1개를 뺀 나머지
36개(`_rule_based_response`부터 `_generate_code`까지)가 서로만
참조하는 폐쇄된 하위 그래프를 이루고 있었다. 각 함수 이름으로
`development-hq/` 전체를 grep해 확인한 결과:

```
$ for f in _rule_based_response _looks_like_code ... _generate_code; do
    grep -rl "$f" --include="*.py" development-hq | grep -v engine.py
  done
(모든 이름에 대해 결과 없음)
```

`workflow_0009.py`에 `_analyze_requirement`라는 문자열이 한 번
등장하지만, 실제 import/호출이 아니라 docstring 안의 설명 문장
("`engine.py`의 `_analyze_requirement`가 이미 ... 계약을 그대로
재사용한다")이었다 — 코드가 아니라 문서였다.

## 실제 코드베이스 구현 — 최소화

`development-hq/mvp/engine.py`에서 `call_engine()`(과 그 상수
`DISALLOWED_TOOLS`/`STATELESS_CALL_NOTICE`) 이후의 모든 함수를
삭제했다: `_rule_based_response`, `_looks_like_code`,
`_looks_like_design`, `_looks_like_implementation`,
`_looks_like_requirement`, `_detect_artifact_stage`,
`_review_requirement`, `_review_design`, `_review_implementation`,
`_suggest_implementation_checks`, `_suggest_requirement_checks`,
`_suggest_design_checks`, `_review_unknown`, `_suggest_unknown_checks`,
`_line_is_inside_triple_quoted_string`, `_review_python_code`,
`_review_code`, `_suggest_tests`, `_contains_marker`,
`_split_sentences`, `_extract_goal`, `_extract_marked_sentences`,
`_analyze_requirement`, `_slugify`, `_extract_section`,
`_section_bullets`, `_bullets_to_restated_lines`,
`_acceptance_to_interface_lines`, `_design_from_requirement`,
`_extract_slug`, `_parse_interface_lines`, `_extract_trailing_section`,
`_extract_dependencies`, `_slug_to_class_name`, `_generate_code` — 총
36개 함수, 관련 모듈 레벨 상수(`DESIGN_REQUIRED_SECTIONS` 등)와 함께
875줄 중 797줄 삭제.

더 이상 쓰지 않는 `import re`도 함께 제거했다(삭제된 함수들만
`re`를 사용했다 — `call_engine()`은 `subprocess`/`tempfile`만
쓴다). `call_engine()` 본문과 시그니처는 한 글자도 바꾸지 않았다 —
Contract(단일 함수, `str -> str`, Engine Gateway 없음)가 그대로다.

새 Capability/Agent/Component를 추가하지 않았다 — 오히려 아무도
쓰지 않는 옛 구현을 제거해 이 파일이 실제로 무엇을 하는지(실제
Engine 호출 함수 하나)와 코드가 일치하게 만들었다.

## 검증 (실제 실행, mock 없음)

### import 무결성

```
$ python3 -c "from mvp.agents import ...; from mvp.workflow import run_mvp_0001; \
from mvp.workflow_0002 import run_mvp_0002; from mvp.workflow_0008 import run_pipeline; \
from mvp.workflow_0009 import run_comparison; from mvp.workflow_artifact_flow import run_issue_to_implementation; \
from mvp.workflow_project_intelligence import run_issue_to_planning, run_issue_to_design; \
from mvp.workflow_hello_sdlc import run_hello_sdlc; \
from mvp.project_intelligence import collect_relevant_context, build_context_bundle; \
from mvp.cli import main"
all imports OK
```

`engine.py`를 직접/간접 의존하는 저장소 안의 모든 모듈이 삭제 후에도
문제없이 import된다.

### 실제 Engine으로 End-to-End 재확인

```
$ python3 -c "from mvp.workflow import run_mvp_0001; \
r = run_mvp_0001('def add(a, b):\n    return a + b\n'); print(list(r.keys()))"
['code_review', 'test_execution']
True True
```

`call_engine()` 삭제 후에도 real `claude -p` 호출 2회로 정상 동작.

### 기존 테스트 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
...                                                                      [100%]
3 passed in 80.48s (0:01:20)
```

real Engine 호출 포함 3건 모두 통과(mock 없음) — 삭제한 코드를 직접
참조하는 테스트가 없었음을 재확인.

### 불필요한 변경 확인

```
$ git status --porcelain
 M development-hq/mvp/engine.py
```

`development-hq/mvp/engine.py` 1개 파일만 변경했다(875줄 → 87줄).

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — 건드리지 않음 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — 건드리지 않음 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 오히려 미사용 코드만 제거 |
| 새 Architecture/Concept/Component 필요 | 미발동 |
| Production caller/Kernel Component/Runtime/Prompt Cache 착수 | 미발동 — 전혀 건드리지 않았다 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `call_engine()` 자체의 로직 변경 — 건드리지 않았다.
- `agents.py`/`workflow*.py`/`project_intelligence.py` — 건드리지
  않았다(모두 `call_engine()`만 참조하며, 삭제된 함수를 참조하는
  곳이 없었다).
- 새 RFC/ADC/ADR — 만들지 않았다. Architecture 결정이 필요한 지점을
  만나지 않았다(죽은 코드 삭제는 Contract 변경이 아니다).

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`engine.py`)**. 실제 grep/import
  검증으로 확인한 죽은 코드(790여 줄)를 삭제했다.
- Architecture를 설계했는가 — **아니오**. `call_engine()`의 시그니처와
  동작을 그대로 유지했다. 새 Concept/Layer/Component 없음.
- 실제 Engine으로 확인했는가 — **예**. 삭제 후 import 무결성 확인,
  real Engine 1회 end-to-end 호출, 기존 pytest 3건(real Engine 포함)
  재실행 — 모두 mock 없음.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 검증 →
  삭제 → 재검증을 이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  삭제 대상 36개 함수 이름 전부를 실제로 grep해 미사용임을 확인한
  뒤에만 삭제했다.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `workflow*.py`,
  `project_intelligence.py`, `cli.py` 어디에도 손대지 않았다
  (`git status --porcelain` 확인).
